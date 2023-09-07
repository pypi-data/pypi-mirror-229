
import datetime
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import m2m_changed, pre_save, post_save, pre_delete, post_delete
from django.utils.autoreload import autoreload_started
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework import filters
from rest_framework import routers
from rest_framework import serializers, viewsets
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.compat import coreapi, coreschema
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import i18n
from . import permissions
from . import signals
from .actions import ACTIONS, Action, BatchAction, QuerySetAction, ActionView
from .serializers import *
from .specification import API
from .utils import to_snake_case, generic_search, generic_filter, related_model, as_choices, to_choices


q_field = openapi.Parameter('q', openapi.IN_QUERY, description="Keywords used to execute the search.", type=openapi.TYPE_STRING)
only_fields = openapi.Parameter('only', openapi.IN_QUERY, description="The name of the fields to be retrieved separated by comma (,).", type=openapi.TYPE_STRING)
page = openapi.Parameter('page', openapi.IN_QUERY, description="Number of the page of the relation.", type=openapi.TYPE_STRING)
relation_page = openapi.Parameter('relation_page', openapi.IN_QUERY, description="Number of the page of the relation.", type=openapi.TYPE_STRING)
choices_field = openapi.Parameter('choices_field', openapi.IN_QUERY, description="Name of the field from which the choices will be displayed.", type=openapi.TYPE_STRING)
choices_search = openapi.Parameter('choices_search', openapi.IN_QUERY, description="Term to be used in the choices search.", type=openapi.TYPE_STRING)
id_parameter = openapi.Parameter('id', openapi.IN_PATH, description="The id of the object.", type=openapi.TYPE_INTEGER)
ids_parameter = openapi.Parameter('ids', openapi.IN_PATH, description="The ids of the objects separated by comma (,).", type=openapi.TYPE_STRING)


class AutoSchema(SwaggerAutoSchema):

    def get_tags(self, operation_keys=None):
        tags = self.overrides.get('tags', None)
        if not tags:
            model = getattr(self.view, 'model', None)
            if model:
                tags = [model.__name__.lower()]
        if not tags:
            tags = [operation_keys[0]]

        return tags


class ObtainAuthToken(ObtainAuthToken):

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        form = dict(type='form', name='login', fields=serialize_fields(serializer))
        return Response(form)


class Router(routers.DefaultRouter):
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        if specification.app:
            for prefix, viewset, basename in self.registry:
                if prefix:
                    urls.insert(0, path(f'{prefix}/add/'.format(prefix), viewset.as_view({'get': 'create', 'post': 'create'}), name=f'add-{prefix}'))
                    urls.insert(0, path(f'{prefix}/<int:pk>/edit/'.format(prefix), viewset.as_view({'get': 'update', 'put': 'update'}), name=f'edit-{prefix}'))
                    urls.insert(0, path(f'{prefix}/<int:pk>/delete/'.format(prefix), viewset.as_view({'get': 'destroy', 'delete': 'destroy'}), name=f'edit-{prefix}'))
        return urls


class ChoiceFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        return queryset

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name='choices',
                required=False,
                location='query',
                schema=coreschema.String(
                    title='Name of the field',
                    description='Name of the field to display choices'
                )
            )
        ]

    def get_schema_operation_parameters(self, view):
        return [
            {
                'name': 'choices',
                'required': False,
                'in': 'query',
                'description': 'Name of the field',
                'schema': {
                    'type': 'string',
                },
            },
        ]


class FilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        search = []
        filters = []
        if hasattr(view, 'context'):
            if 'only' in request.GET:
                filters = view.context['view'].item.relations.get(request.GET['only'], {}).get('filters')
                search = view.context['view'].item.relations.get(request.GET['only'], {}).get('search')
        else:
            filters = view.item.filters
            search = view.item.search
        for lookup in filters:
            if lookup in request.GET:
                queryset = generic_filter(queryset, lookup, request.GET[lookup])
        if search and 'q' in request.GET:
            queryset = generic_search(queryset, request.GET['q'], search)

        return queryset


class List(QuerySetAction):
    def has_permission(self):
        return super().has_permission() or permissions.check_groups(self.context['view'].item.list_lookups, self.user, False)


class Add(QuerySetAction):
    def has_permission(self):
        return super().has_permission() or permissions.check_groups(self.context['view'].item.add_lookups, self.user, False)


class Edit(Action):
    def has_permission(self):
        return super().has_permission() or permissions.check_groups(self.context['view'].item.edit_lookups, self.user, False)


class Delete(Action):
    def has_permission(self):
        return super().has_permission() or permissions.check_groups(self.context['view'].item.delete_lookups, self.user, False)


class View(Action):
    def has_permission(self):
        return permissions.check_groups(self.context['view'].item.view_lookups, self.user, False)


class ModelViewSet(viewsets.ModelViewSet):
    SERIALIZERS = {}
    filter_backends = FilterBackend,
    pagination_class = PageNumberPagination
    serializer_class = DynamicFieldsModelSerializer
    permission_classes = AllowAny,

    def __init__(self, *args, **kwargs):
        self.queryset = self.get_queryset()
        self.fieldsets = kwargs.pop('fieldsets', ())
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all().order_by('id')

    def apply_lookups(self, queryset):
        if self.request.user.is_superuser:
            lookups = None
        elif self.action == 'list':
            lookups = self.item.list_lookups
        elif self.action == 'retrieve':
            lookups = self.item.view_lookups

        if lookups:
            return permissions.apply_lookups(queryset, lookups, self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action in self.item.action_serializers:
            return ACTIONS[self.item.action_serializers.get(self.action, self.action)]
        else:
            _exclude = None
            _model = self.model
            key = '{}_{}'.format(self.action, self.model.__name__)
            cls = ModelViewSet.SERIALIZERS.get(key)
            if cls is None:
                if self.action == 'create':
                    if self.item.add_fieldsets:
                        _fields = []
                        for v in self.item.add_fieldsets.values():
                            _fields.extend(v)
                    else:
                        _fields = self.item.add_fields
                elif self.action == 'list':
                    _fields = self.item.list_display
                elif self.action == 'retrieve':
                    _fields = self.item.view_fields
                elif self.action == 'update' or self.action == 'partial_update':
                    if self.item.edit_fieldsets:
                        _fields = []
                        for v in self.item.edit_fieldsets.values():
                            _fields.extend(v)
                    else:
                        _fields = self.item.edit_fields
                elif self.action == 'destroy':
                    _fields = 'id',
                elif self.action in self.item.list_extends:
                    _fields = self.item.list_extends[self.action].get('fields')
                elif self.action in self.item.relations:
                    _exclude = self.item.relations[self.action]['related_field'],
                    _model = getattr(_model, self.action).field.remote_field.related_model
                elif self.action in self.item.view_extends:
                    _fields = self.item.view_extends[self.action].get('fields')
                else:
                    _fields = self.item.list_display
                class cls(DynamicFieldsModelSerializer):
                    class Meta:
                        ref_name = key
                        model = _model
                        if _exclude is None:
                            fields = _fields or '__all__'
                        else:
                            exclude = _exclude

                ModelViewSet.SERIALIZERS[key] = cls
            return cls

    def get_object(self):
        object = super().get_object()
        if self.action == 'retrieve':
            object._wrap = True
        return object

    @swagger_auto_schema(manual_parameters=[only_fields, page])
    def retrieve(self, request, *args, **kwargs):
        permissions.check_groups(self.item.view_lookups, request.user)
        return self.choices_response(request, relation_name=request.GET.get('only')) or super().retrieve(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        if self.action != 'retrieve':
            queryset = super().filter_queryset(queryset)
        if self.action == 'list' or self.action == 'retrieve':
            return self.apply_lookups(queryset)
        return queryset

    # auto_schema=None
    def list(self, request, *args, **kwargs):
        permissions.check_groups(self.item.list_lookups, request.user)
        return self.choices_response(request) or super().list(request, *args, **kwargs)

    def get_paginated_response(self, data):
        metadata = dict(actions= self.item.list_actions, search=self.item.search, filters=self.item.filters)
        return self.paginator.get_paginated_response(data, metadata, True)

    def create_form(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer()
            name = '{}_{}'.format(i18n.translate('add'), i18n.translate(self.model.__name__.lower()))
            form = dict(type='form', name=name, fields=serialize_fields(serializer, self.item.add_fieldsets))
            return Response(form)

    @swagger_auto_schema(manual_parameters=[choices_field, choices_search])
    def create(self, request, *args, **kwargs):
        permissions.check_groups(self.item.add_lookups, request.user)
        return self.choices_response(request) or self.create_form(request) or self.post_create(
            super().create(request, *args, **kwargs)
        )

    def post_create(self, response):
        response = Response({}) if specification.app else response
        response['USER_MESSAGE'] = 'Cadastro realizado com sucesso.'
        return response

    def perform_create(self, serializer):
        if False: #TODO performe check_lookups with self.item.add_lookups and serializer.validated_data
            raise exceptions.PermissionDenied(' You do not have permission to perform this action.', 403)
        super().perform_create(serializer)

    def update_form(self, request):
        if request.method == 'GET':
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=instance.__dict__)
            serializer.is_valid()
            name = '{}_{}'.format(i18n.translate('edit'), i18n.translate(self.model.__name__.lower()))
            form = dict(type='form', name=name, fields=serialize_fields(serializer))
            return Response(form)

    @swagger_auto_schema(manual_parameters=[choices_field, choices_search])
    def update(self, request, *args, **kwargs):
        permissions.check_groups(self.item.edit_lookups, request.user)
        return self.choices_response(request) or self.update_form(request) or self.post_update(
            super().update(request, *args, **kwargs)
        )

    def post_update(self, response):
        response = Response({}) if specification.app else response
        response['USER_MESSAGE'] = 'Atualização realizada com sucesso.'
        return response

    def perform_update(self, serializer):
        if False:  # TODO performe check_lookups with self.item.edit_lookups and serializer.validated_data
            raise exceptions.PermissionDenied(' You do not have permission to perform this action.', 403)
        super().perform_update(serializer)

    def destroy_form(self, request):
        if request.method == 'GET':
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=instance.__dict__)
            serializer.is_valid()
            name = '{}_{}'.format(i18n.translate('delete'), i18n.translate(self.model.__name__.lower()))
            form = dict(type='form', name=name, fields=serialize_fields(serializer))
            return Response(form)

    @swagger_auto_schema(manual_parameters=[])
    def destroy(self, request, *args, **kwargs):
        permissions.check_groups(self.item.delete_lookups, request.user)
        return self.destroy_form(request) or self.post_destroy(super().destroy(request, *args, **kwargs))

    def post_destroy(self, response):
        response = Response({}) if specification.app else response
        response['USER_MESSAGE'] = 'Exclusão realizada com sucesso.'
        return response

    def perform_destroy(self, instance):
        if False:  # TODO performe check_lookups with self.item.delete_lookups and serializer.validated_data
            raise exceptions.PermissionDenied(' You do not have permission to perform this action.', 403)
        super().perform_destroy(instance)

    def choices_response(self, request, relation_name=None):
        choices = to_choices(self.model, request, relation_name)
        return Response(choices) if choices is not None else None


class UserSerializer(serializers.Serializer):

    def to_representation(self, instance):
        if instance.is_authenticated:
            only = self.context['request'].GET.get('only')
            data = dict(
                id=self.instance.id,
                username=self.instance.username,
                # groups=serialize_value(self.instance.groups, self.context, output={'fields': ['name']}),
                # permissions=serialize_value(self.instance.user_permissions, self.context, output={'fields': ['name']}),
                # scopes=serialize_value(Scope.objects.filter(username=self.instance.username), self.context, output={'fields': ['groupname', 'scopename', 'value']}),
            ) if only is None else {}
            for k, v in self.context['view'].DASHBOARD.items():
                if only is None or k == only:
                    cls = ACTIONS[v['input']]
                    action = cls(context=self.context, source=self.context['request'].user)
                    if action.has_permission():
                        if action.sync or k == only:
                            obj = action.submit()
                            data[k] = serialize_value(obj, context=self.context, output=v.get('output'))
                        else:
                            data[k] = {'async': '{}?only={}'.format(self.context['request'].path, k)}
            if specification.app:
                return {'type': 'dashboard', 'result': data}
            else:
                return data
        return {}

    def has_permission(self):
        return True


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = AllowAny,
    ACTIONS = {}
    DASHBOARD = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_serializer_class(self):
        return ACTIONS.get(UserViewSet.ACTIONS.get(self.action), UserSerializer)

    def get_queryset(self):
        return apps.get_model('auth.user').objects.filter(pk=self.request.user.id)

    @swagger_auto_schema(manual_parameters=[only_fields])
    @action(detail=False, methods=["get"], url_path='user', url_name='user')
    def user(self, request, format=None):
        return Response(self.get_serializer(request.user).data, status=status.HTTP_200_OK)

    @classmethod
    def create_actions(cls, actions, dashboard=False):
        for k, v in actions.items():
            method = 'post' if ACTIONS[v['input']]._declared_fields else 'get'
            manual_parameters = [choices_field, choices_search] if method == 'post' else []
            function = create_user_action_func(k, v['input'])
            swagger_auto_schema(manual_parameters=manual_parameters)(function)
            action(detail=False, methods=['get', 'post'] or [method], url_path=f'user/{k}', url_name=k, name=k)(function)
            setattr(cls, k, function)
            cls.ACTIONS[k] = v['input']
            if dashboard:
                cls.DASHBOARD[k] = v


class ActionViewSet(viewsets.GenericViewSet):
    permission_classes = AllowAny,
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        return ACTIONS.get(self.action, serializers.Serializer)

    def get_queryset(self):
        return apps.get_model('auth.user').objects.filter(pk=self.request.user.id)

    @classmethod
    def create_actions(cls):
        for k, action_class in ACTIONS.items():
             if issubclass(action_class, ActionView) and action_class != ActionView:
                method = 'get' # 'post' if action_class._declared_fields else 'get'
                manual_parameters = [choices_field, choices_search] if method == 'post' else []
                function = create_action_view_func(k, {'input': to_snake_case(action_class.__name__), 'output': None})
                swagger_auto_schema(manual_parameters=manual_parameters)(function)
                action(detail=False, methods=[method], url_path=f'{k}', url_name=k, name=k)(function)
                setattr(cls, k, function)


class HealthViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.Serializer
    permission_classes = AllowAny,

    def get_queryset(self):
        return User.objects.none()

    @swagger_auto_schema(tags=['health'])
    @action(detail=False, methods=["get"], url_path='check', url_name='check')
    def check(self, request):
        return Response({'status': 'UP',}, status=status.HTTP_200_OK)


def model_view_set_factory(model_name):
    _model = apps.get_model(model_name)
    _item = specification.items[model_name]
    if not _item.filters:
        for field in model._meta.get_fields():
            if isinstance(field, models.ForeignKey):
                _item.filters.append(field.name)
            elif isinstance(field, models.BooleanField):
                _item.filters.append(field.name)
            elif getattr(field, 'choices', None):
                _item.filters.append(field.name)
    if 'id' not in _item.filters:
        _item.filters.append('id')
    if not _item.search:
        for field in model._meta.get_fields():
            if isinstance(field, models.CharField):
                _item.search.append(field.name)
    class ViewSet(ModelViewSet):
        model = _model
        item = _item
        ordering_fields = item.ordering

        @swagger_auto_schema(manual_parameters=[q_field, only_fields, choices_field, choices_search, relation_page] + [filter_param(name) for name in _item.filters])
        def list(self, *args, **kwargs):
            return super().list(*args, **kwargs)

    for k in item.actions:
        if k in ('add', 'view', 'edit', 'delete', 'list'): continue
        url_path = k
        serializer_name = item.actions[k]['input']
        cls = ACTIONS[serializer_name]
        function = create_action_func(k, item.actions[k])
        method = 'post' if cls._declared_fields else 'get'
        manual_parameters = [only_fields, choices_field, choices_search]
        if issubclass(cls, BatchAction) or issubclass(cls, QuerySetAction):
            detail = False
            if issubclass(ACTIONS[serializer_name], BatchAction):
                url_path = f'{k}/(?P<ids>[0-9,]+)'
                manual_parameters.append(ids_parameter)
        else:
            detail = True
            manual_parameters.append(id_parameter)
        swagger_auto_schema(manual_parameters=manual_parameters)(function)
        action(detail=detail, methods=['post', 'get'] or [method], url_path=url_path, url_name=k, name=k)(function)
        setattr(ViewSet, k, function)

    for k in item.list_extends:
        function = create_list_func(k, item.list_extends[k])
        manual_parameters = [choices_field, choices_search]
        swagger_auto_schema(manual_parameters=manual_parameters)(function)
        action(detail=False, methods=["get"], url_path=k, url_name=k, name=k)(function)
        setattr(ViewSet, k, function)

    for k in item.view_extends:
        function = create_view_func(k, item.view_extends[k])
        manual_parameters = [only_fields]
        swagger_auto_schema(manual_parameters=manual_parameters)(function)
        action(detail=True, methods=["get"], url_path=k, url_name=k, name=k)(function)
        setattr(ViewSet, k, function)

    for k in item.relations:
        if item.relations[k].get('related_field'):
            function = create_relation_func(k, item.relations[k])
            manual_parameters = [only_fields]
            swagger_auto_schema(manual_parameters=manual_parameters)(function)
            action(detail=True, methods=["post"], url_path=k, url_name=k, name=k)(function)
            setattr(ViewSet, k, function)

    return ViewSet


def filter_param(name):
    return openapi.Parameter(name, openapi.IN_QUERY, description=name, type=openapi.TYPE_STRING)


def create_user_action_func(func_name, serializer_name):
    def func(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST or None, context=dict(request=request, view=self), source=request.user)
        if not serializer.has_permission():
            raise exceptions.PermissionDenied(' You do not have permission to perform this action.', 403)

        if request.method == 'GET':
            if serializer._declared_fields:
                serializer.is_valid()
                form = dict(type='form', name=func_name, fields=serialize_fields(serializer))
                return Response(form)
            else:
                return Response(serializer.submit(), status=status.HTTP_200_OK)

        if serializer._declared_fields:
            if serializer.is_valid():
                return Response(serializer.submit(), status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.submit(), status=status.HTTP_200_OK)

    func.__name__ = func_name
    return func


def create_view_func(func_name, extension):
    def func(self, request, **kwargs):
        instance = self.model.objects.get(pk=kwargs['pk'])
        instance._wrap = True
        permissions.check_lookups(instance, (extension.get('requires') or self.item.view_lookups), request.user, True)
        meta = dict(model=self.model, fields=extension.get('fields') or '__all__')
        serializer = self.get_serializer_class()(
            instance, meta=meta, context=dict(request=request, view=self)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    func.__name__ = func_name
    return func


def create_relation_func(func_name, relation):
    def func(self, request, **kwargs):
        instance = self.model.objects.get(pk=kwargs['pk'])
        serializer = self.get_serializer_class()(
            data=request.POST or None, context=dict(request=request, view=self)
        )

        choices = request.query_params.get('choices_field')
        if choices:
            term = request.query_params.get('choices_search')
            field = serializer.fields[choices]
            if isinstance(field, PaginableManyRelatedField):
                qs = field.child_relation.get_queryset()
            else:
                qs = field.queryset.all()
            return Response(as_choices(generic_search(qs, term)))

        if request.method == 'GET':
            serializer.is_valid()
            form = dict(type='form', name=func_name, fields=serialize_fields(serializer))
            return Response(form)

        if serializer.is_valid():
            serializer.validated_data[relation['related_field']] = instance
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    func.__name__ = func_name
    return func


def create_list_func(func_name, extension):
    def func(self, request):
        lookups = extension.get('requires') or self.item.list_lookups
        permissions.check_groups(lookups, request.user, True)
        queryset = getattr(self.model.objects, func_name, self.model.objects.all)()
        queryset = permissions.apply_lookups(queryset, lookups, request.user)
        data = serialize_value(queryset, context=dict(request=request, view=self), output=extension)
        return Response(data, status=status.HTTP_200_OK)

    func.__name__ = func_name
    return func


def create_action_view_func(func_name, metadata):
    def func(self, request, *args, **kwargs):
        serializer = ACTIONS[metadata['input']](data=request.POST or None, context=dict(request=request, view=self))
        return serializer.to_response(metadata, func_name if specification.app else None)

    func.__name__ = func_name
    return func


def create_action_func(func_name, metadata):
    def func(self, request, *args, **kwargs):
        if request.method.upper() == 'POST':
            data = request.POST or {}
        else:
            data = None
        serializer = ACTIONS[metadata['input']](data=data, context=dict(request=request, view=self))
        if 'pk' in kwargs:
            serializer.source = self.model.objects.get(pk=kwargs['pk'])
        elif 'ids' in kwargs:
            serializer.source = self.model.objects.filter(pk__in=kwargs['ids'].split(','))
        else:
            serializer.source = self.model.objects.all()
        return serializer.to_response(metadata)

    func.__name__ = func_name
    return func


router = Router()
specification = API.instance()

for app_label in settings.INSTALLED_APPS:
    try:
        if app_label != 'api':
            __import__('{}.{}'.format(app_label, 'actions'), fromlist=app_label.split('.'))
    except ImportError as e:
        if not e.name.endswith('actions'):
            raise e
    except BaseException as e:
        raise e

for name in specification.groups.values():
    try:
        Group.objects.get_or_create(name=name)
    except Exception:
        pass
for k, item in specification.items.items():
    model = apps.get_model(k)
    if item.roles:
        model = apps.get_model(k)
        model.__roles__ = item.roles
        pre_save.connect(signals.pre_save_func, model)
        pre_delete.connect(signals.pre_save_func, model)
        post_save.connect(signals.post_save_func, model)
        post_delete.connect(signals.post_delete_func, model)
        for field in model._meta.many_to_many:
            m2m_changed.connect(signals.m2m_save_func, sender=getattr(model, field.name).through)
    router.register(item.prefix, model_view_set_factory(k), name)
UserViewSet.create_actions(specification.user_actions)
UserViewSet.create_actions(specification.dashboard_actions, True)
ActionViewSet.create_actions()

router.register('', UserViewSet, 'user')
router.register('', ActionViewSet, 'actionview')
router.register('health', HealthViewSet, 'check')


def api_watchdog(sender, **kwargs):
    sender.extra_files.add(Path('api.yml'))

autoreload_started.connect(api_watchdog)

