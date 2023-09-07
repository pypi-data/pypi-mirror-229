import json
import re
import datetime
import traceback
from django.apps import apps
from django.db import models
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import Scope
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .permissions import check_groups
from .icons import ICONS
from .utils import to_snake_case, as_choices, generic_search, generic_filter
from .exceptions import JsonResponseReadyException
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.cache import cache

ACTIONS = {}

CharField = serializers.CharField
BooleanField = serializers.BooleanField
IntegerField = serializers.IntegerField
DateField = serializers.DateField
FileField = serializers.FileField
DecimalField = serializers.DecimalField


class RelatedField(serializers.RelatedField):
    def to_internal_value(self, value):
        return self.queryset.get(pk=value) if value else None


def actions_metadata(source, actions, context, base_url, instances=(), viewer=None):
    l = []
    for name, action in actions.items():
        cls = ACTIONS[action['input']]
        serializer = cls(context=context, source=source)
        if issubclass(cls, BatchAction):
            ids = []
            target = 'instances'
            url = f'{base_url}{name}/'
            append = serializer.has_permission()
        elif issubclass(cls, QuerySetAction):
            ids = []
            target = 'queryset'
            url = f'{base_url}{name}/'
            append = serializer.has_permission()
        else:
            target = 'instance'
            if name == 'view':
                url = f'{base_url}{{id}}/' if viewer is None else f'{base_url}{{id}}/{viewer}/'
            else:
                url = f'{base_url}{{id}}/{name}/'
            ids = serializer.check_permission(instances)
            append = bool(ids)
        if append:
            l.append(dict(name=name, url=url, target=target, modal=cls.modal, ids=ids))
    return l


class ActionMetaclass(serializers.SerializerMetaclass):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        ACTIONS[re.sub(r'(?<!^)(?=[A-Z0-9])', '_', name).lower()] = cls
        return cls


class Action(serializers.Serializer, metaclass=ActionMetaclass):
    # parser_classes = MultiPartParser, FormParser
    cache = None
    modal = True
    sync = True
    fieldsets = {}

    def __init__(self, *args, **kwargs):
        self.user_task = None
        self.user_message = None
        self.user_redirect = None
        self.source = None
        self.controls = dict(hide=[], show=[], set={})
        super().__init__(*args, **kwargs)

    def execute(self, task):
        print(task.key)
        self.user_task = task.key
        task.start()

    def load(self):
        pass

    def hide(self, *names):
        self.controls['hide'].extend(names)

    def show(self, *names):
        self.controls['show'].extend(names)

    def get(self, name, default=None):
        value = self.request.POST.get(name)
        if value is None:
            return default
        else:
            try:
                value = self.fields[name].to_internal_value(value)
            except ValidationError:
                pass
            return default if value is None else value

    def set(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, models.Model):
                v = dict(id=v.id, text=str(v))
            if isinstance(v, bool):
                v = str(v).lower()
            elif isinstance(v, datetime.datetime):
                v = v.strftime('%Y-%m-%d %H:%M')
            elif isinstance(v, datetime.date):
                v = v.strftime('%Y-%m-%d')
            self.controls['set'][k] = v

    def watchable_field_names(self):
        l = []
        for name in self.fields:
            attr_name = f'on_{name}_change'
            if hasattr(self, attr_name):
                l.append(name)
        return l

    def is_valid(self, *args, **kwargs):
        self.load()
        return super().is_valid(*args, **kwargs)

    def submit(self):
        print(self.source)
        return {}

    def has_permission(self):
        return self.user.is_superuser

    def notify(self, message):
        self.user_message = str(message).replace('\n', '<br>')

    def redirect(self, url):
        self.user_redirect = url

    @property
    def user(self):
        return super().context['request'].user

    @property
    def request(self):
        return super().context['request']

    def check_permission(self, instances=()):
        ids = []
        for instance in instances:
            self.source = instance
            if self.has_permission():
                ids.append(instance.id)
        return ids

    def objects(self, model):
        return apps.get_model(model).objects

    def to_response(self, metadata=None, key=None):
        from .serializers import serialize_value, serialize_fields
        on_change = self.request.query_params.get('on_change')
        if on_change:
            self.load()
            self.controls['show'].clear()
            self.controls['hide'].clear()
            self.controls['set'].clear()
            values = {}
            for k, v in self.request.POST.items():
                if k in self.fields:
                    values[k] = self.fields[k].to_internal_value(v)
            getattr(self, f'on_{on_change}_change')(**values)
            return Response(self.controls)
        only = self.request.query_params.get('only')
        choices = self.request.query_params.get('choices_field')
        metadata = metadata or {}
        if choices and not only:
            self.load()
            term = self.request.query_params.get('choices_search')
            field = self.fields[choices]
            if isinstance(field, serializers.ManyRelatedField):
                qs = field.child_relation.queryset.all()
            else:
                qs = field.queryset.all()
            attr_name = f'get_{choices}_queryset'
            if hasattr(self, attr_name):
                qs = getattr(self, attr_name)(qs)
            return Response(as_choices(generic_search(qs, term)))

        if self.request.method == 'GET':
            if self._declared_fields or not isinstance(self, ActionView):
                self.is_valid()
                form = dict(
                    type='form', name=metadata['input'], fields=serialize_fields(self, self.fieldsets),
                    controls=self.controls, watch=self.watchable_field_names()
                )
                fields = metadata.get('display')
                if self.source and fields:
                    self.source._wrap = True
                    try:
                        display = serialize_value(self.source, self.context, output=dict(fields=fields))
                    except JsonResponseReadyException as e:
                        return Response(e.data)
                    form.update(display=display)
                return Response(form)
            else:
                result = self.submit()
                if isinstance(result, dict) or isinstance(result, list):
                    value = serialize_value(result, self.context, metadata['output'])
                    if key and not (isinstance(result, models.Model) or isinstance(result, models.QuerySet) or isinstance(result, models.Manager)):
                        value = {'type': key, 'result': value}
                else:
                    value = json.dumps(result)
                return Response(value, status=status.HTTP_200_OK)
        else:
            if self.is_valid():
                try:
                    result = self.submit()
                except Exception as e:
                    traceback.print_exc()
                    return Response({'non_field_errors': 'Ocorreu um erro no servidor ({}).'.format(e)}, status=status.HTTP_400_BAD_REQUEST)
                value = serialize_value(result, self.context, metadata['output'])
                if key and not (isinstance(result, models.Model) or isinstance(result, models.QuerySet) or isinstance(result, models.Manager)):
                    value = {'type': key, 'result': value}
                response = Response(value, status=status.HTTP_200_OK)
                if self.user_message:
                    response['USER_MESSAGE'] = self.user_message
                if self.user_redirect:
                    response['USER_REDIRECT'] = self.user_redirect
                if self.user_task:
                    response['USER_TASK'] = self.user_task
                return response
            else:
                return Response(self.errors, status=status.HTTP_400_BAD_REQUEST)


class ActionView(Action):
    pass

class BatchAction(Action):
    modal = True

class QuerySetAction(Action):
    modal = True


class Icons(ActionView):
    def submit(self):
        return ICONS


class UserScopes(Action):
    def submit(self):
        return Scope.objects.filter(username=self.source.username).order_by('id')


class UserResources(Action):
    def submit(self):
        from .i18n import translate
        from .viewsets import specification
        q = self.request.GET.get('choices_search')
        resources = []
        for item in specification.items.values():
            name = translate(item.prefix)
            if q is None or q.lower() in name.lower():
                if check_groups(item.list_lookups, self.user, False):
                    resources.append({'name': name, 'url': item.url})
        for name, cls in ACTIONS.items():
            name = translate(name)
            if issubclass(cls, ActionView) and cls != ActionView:
                if q is None or q.lower() in name.lower():
                    serializer = cls(context=self.context)
                    if serializer.has_permission():
                        resources.append({'name': name, 'url': f'/api/v1/{name}/'})
        return resources

    def has_permission(self):
        return self.user.is_authenticated


class ChangePassword(Action):
    senha = serializers.CharField(label='Senha')

    def submit(self):
        self.source.set_password(self.data['senha'])
        self.source.save()
        token = Token.objects.get_or_create(user=self.user)[0]
        return {'token': token.key}


class ChangePasswords(BatchAction):
    senha = serializers.CharField(label='Senha')

    def submit(self):
        for user in self.source.all():
            user.set_password(self.data['senha'])
            user.save()


class VerifyPassword(Action):
    senha = serializers.CharField(label='Senha')

    def submit(self):
        return self.notify(self.source.check_password(self.data['senha']))

class TaskProgress(ActionView):
    def submit(self):
        value = cache.get(self.request.GET.get('key'), 0)
        return value

class X(Action):
    modal = True
    x = serializers.CharField()

    fieldsets = {'teste': ['x']}

    def has_permission(self):
        return self.source.id % 2 == 0

    def submit(self):
        from .tasks import TestTask
        print(self.source)
        self.notify('It is working!!!')
        self.execute(TestTask())

class Y(BatchAction):
    y = serializers.CharField()

    def submit(self):
        print(self.source.count())
        self.notify('It is working!!!')
        return self.objects('auth.user').all()

class Z(QuerySetAction):
    z = serializers.CharField()

    def submit(self):
        print(self.source.count())
        self.redirect('/api/v1/user/')
        self.notify('It is working!!!')


class W(ActionView):

    def submit(self):
        return self.objects('pnp.matricula')

