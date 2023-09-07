import decimal

import datetime
from inspect import isfunction, ismethod

from django.db import models
from django.db.models.query import ModelIterable
from rest_framework import serializers
from rest_framework.relations import MANY_RELATION_KWARGS
from rest_framework.serializers import RelatedField, ManyRelatedField, ChoiceField

from . import permissions
from .utils import to_snake_case, generic_search, generic_filter, to_choices
from .actions import ACTIONS, actions_metadata
from .pagination import PageNumberPagination, PaginableManyRelatedField
from .specification import API
from .exceptions import JsonResponseReadyException

specification = API.instance()

NONE = '__NONE__'


def serialize_fields(serializer, fieldsets=None):
    l = []
    for name, field in serializer.fields.items():
        if name == 'id': continue
        extra = {}
        if isinstance(field, ChoiceField):
            field_type = 'select'
            extra.update(multiple=False)
            value = getattr(serializer.instance, name) if serializer.instance else field.initial
            choices = [dict(id=k, text=v) for k, v in field.choices.items()]
            extra.update(choices=choices)
        elif isinstance(field, ManyRelatedField):
            field_type = 'select'
            extra.update(multiple=True)
            qs = getattr(serializer.instance, name) if serializer.instance else field.child_relation.queryset.filter(pk__in=field.initial)
            value = [dict(id=obj.id, text=str(obj)) for obj in qs.all()] if qs else []
        elif isinstance(field, RelatedField):
            field_type = 'select'
            extra.update(multiple=False)
            obj = getattr(serializer.instance, name) if serializer.instance else field.queryset.filter(pk=field.initial).first()
            value = dict(id=obj.id, text=str(obj)) if obj else None
        elif isinstance(field, serializers.FileField):
            field_type = 'file'
            value = None
        else:
            field_type = type(field).__name__.lower().replace('field', '')
            value = getattr(serializer.instance, name) if serializer.instance else field.initial
            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%d %H:%M')
            elif isinstance(value, datetime.date):
                value = value.strftime('%Y-%m-%d')

            if field_type == 'char':
                field_type = 'text'
            if field_type == 'integer':
                field_type = 'number'
            elif field_type ==  'datetime':
                field_type = 'datetime-local'
            elif field_type == 'decimal':
                field_type = 'text'
                extra.update(mask='decimal')
            elif field.style.get('input_type'):
                field_type = field.style.get('input_type')
        field = dict(name=name, type=field_type, label=field.label, value=value, help_text=field.help_text, read_only=field.read_only)
        field.update(extra)
        l.append(field)

    if fieldsets:
        fields = {}
        for k, v in fieldsets.items():
            allowed = {}
            for name in v:
                if isinstance(name, str):
                    allowed[name] = 100
                else:
                    for x in name:
                        allowed[x] = int(100/len(name))
            fields[k] = []
            for f in l:
                if f['name'] in allowed:
                    f['width'] = allowed[f['name']]
                    fields[k].append(f)
    else:
        fields = l
    return fields


def serialize_value(value, context, output=None, is_relation=False, relation_name=None):

    if value is None:
        return None
    elif isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%dT%H:%M:%S')
    elif isinstance(value, decimal.Decimal):
        return str(value)
    elif isinstance(value, dict) or isinstance(value, list):
        return value
    if isinstance(value, models.QuerySet) and value._iterable_class != ModelIterable:
        return value
    if isinstance(value, models.Manager) or isinstance(value, models.QuerySet):
        if isinstance(value, models.Manager):
            value = value.all()
        paginator = PageNumberPagination()
        queryset = paginator.paginate_queryset(value, context['request'], context['view'], relation_name)
        fields = output.get('fields') if output else None
        meta = dict(model=value.model, fields=fields or '__all__')
        serializer = DynamicFieldsModelSerializer(
            queryset, many=True, read_only=True, context=context, meta=meta, is_relation=is_relation
        )
        data = serializer.data
        for obj in queryset:
            # TODO checar se está fazendo consulta ou se está usando cache do queryset
            paginator.instances.append(obj)
        return paginator.get_paginated_response(data, metadata=output).data
    elif isinstance(value, models.Model):
        if output:
            meta = dict(model=type(value), fields=output['fields'])
            serializer = DynamicFieldsModelSerializer(
                value, read_only=True, context=context, meta=meta, is_relation=is_relation
            )
            return serializer.data
        else:
            if specification.app:
                return str(value)
            else:
                return dict(id=value.id, text=str(value)) if value else None
    else:
        return value if is_relation else dict(value=value)


class MethodField(serializers.Field):

    def __init__(self, *args, method_name=None, **kwargs):
        self.method_name = method_name
        super().__init__(*args, **kwargs)

    def check_choices_response(self):
        if self.method_name == self.context['request'].GET.get('only'):
            choices = to_choices(getattr(self.parent.instance, self.method_name)().model, self.context['request'])
            if choices:
                raise JsonResponseReadyException(choices)

    def to_representation(self, instance):
        model = type(instance)
        key = '{}.{}'.format(model._meta.app_label, model._meta.model_name)
        item = specification.items.get(key)
        value = getattr(instance, self.method_name)()
        relation = item.relations.get(self.method_name)
        if relation:
            if not permissions.check_groups(relation.get('requires'), self.context['request'].user, False):
                return NONE
            if isinstance(value, models.QuerySet):
                filters = relation.get('filters', ())
                for lookup in filters:
                    if lookup in self.context['request'].GET:
                        value = generic_filter(value, lookup, self.context['request'].GET[lookup])
                search = relation.get('search', ())
                if search and 'q' in self.context['request'].GET:
                    value = generic_search(value, self.context['request'].GET['q'], search)
        data = serialize_value(value, self.context, output=relation, is_relation=True)
        if isinstance(value, models.QuerySet):
            data['relation'] = self.method_name.replace('get_', '')
        return data


class RelationSerializer(serializers.RelatedField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if self.context['view'].action in ['update']:
            return value.pk if value else None
        relation_name = self.parent.field_name or self.source
        if not isinstance(self.root, serializers.ListSerializer):
            model = type(self.root.instance)
            key = '{}.{}'.format(model._meta.app_label, model._meta.model_name)
            item = specification.items.get(key)
            relation = item.relations.get(relation_name)
            if relation:
                if not permissions.check_groups(relation.get('requires'), self.context['request'].user, False):
                    return NONE
                if relation.get('fields'):
                    self.serializer = DynamicFieldsModelSerializer(
                        instance=value, meta=dict(model=type(value), fields=relation.get('fields')),
                        context=self.context, is_relation=True
                    )
                    return self.serializer.data
        if specification.app:
            return str(value)
        else:
            return dict(id=value.id, text=str(value)) if value else None

    def to_internal_value(self, data):
        if data is None:
            return None
        elif isinstance(data, list):
            return self.queryset.filter(pk__in=data)
        return self.queryset.get(pk=data)

    def get_choices(self, cutoff=None):
        if self.root.instance:
            obj = getattr(self.root.instance, self.field_name) if self.field_name else None
            return {obj.pk: str(obj)} if obj else {}
        return {}

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs:
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return PaginableManyRelatedField(**list_kwargs)


def remove_unrequested_fields(request, data):
    names = request.query_params.get('only')
    if names:
        allowed = set()
        for name in names.split(','):
            name = name.strip()
            allowed.add(name)
            allowed.add(f'get_{name}')
        existing = set(data.keys())
        for field_name in existing - allowed:
            data.pop(field_name)


class ActionField(serializers.DictField):

    def __init__(self, field_name, serializer_class, context, *args, **kwargs):
        self.field_name = field_name
        self.serializer_class = serializer_class
        super().__init__(*args, **kwargs)
        self.context.update(context)

    def check_choices_response(self):
        if self.field_name == self.context['request'].GET.get('only'):
            choices = to_choices(self.serializer_class().submit().model, self.context['request'])
            if choices:
                raise JsonResponseReadyException(choices)

    def to_representation(self, value):
        output = None
        serializer = self.serializer_class()
        serializer.source = value
        result = serializer.submit()
        model = type(value)
        key = '{}.{}'.format(model._meta.app_label, model._meta.model_name)
        item = specification.items.get(key)
        relation = item.relations.get(self.field_name)
        if relation:
            output = relation
            filters = output.get('filters') if output else ()
            search = output.get('search') if output else ()
            for lookup in filters:
                if lookup in self.context['request'].GET:
                    result = generic_filter(result, lookup, self.context['request'].GET[lookup])
            if search and 'q' in self.context['request'].GET:
                result = generic_search(result, self.context['request'].GET['q'], search)
        data = serialize_value(
            result, context=self.context, output=output, is_relation=True, relation_name=self.field_name
        )
        return data

    def to_internal_value(self, data):
        return {}


class FieldsetField(serializers.DictField):

    def __init__(self, *args, fieldset=None, request=None, **kwargs):
        self.only = []
        self.fieldset = fieldset
        super().__init__(*args, **kwargs)
        if 'only' in request.GET:
            self.only = [name.strip() for name in request.GET['only'].split(',')]

    def to_representation(self, value):
        data = {}
        model = type(value)
        key = '{}.{}'.format(model._meta.app_label, model._meta.model_name)
        item = specification.items.get(key)
        requires = self.fieldset.get('requires')
        if requires and not permissions.check_groups(requires, self.context['request'].user, False):
            return NONE
        for attr_name in self.fieldset['fields']:
            api_attr_name = attr_name[4:] if attr_name.startswith('get_') else attr_name
            if self.only and api_attr_name not in self.only:
                continue
            attr_value = getattr(value, attr_name)
            if isfunction(attr_value) or ismethod(attr_value):
                attr_value = attr_value()
            data[api_attr_name] = serialize_value(
                attr_value, self.context, item.relations.get(attr_name), is_relation=True
            )
        return data

    def to_internal_value(self, data):
        return {attr: data[attr] for attr in self.fieldset['fields']}


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    serializer_related_field = RelationSerializer


    def __init__(self, *args, is_relation=False, **kwargs):
        meta = kwargs.pop('meta', None)
        if meta:
            self.Meta = type("Meta", (), meta)
        self.item  = specification.items[
            '{}.{}'.format(self.Meta.model._meta.app_label, self.Meta.model._meta.model_name)
        ]
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        if not is_relation:
            remove_unrequested_fields(self.context['request'], self.fields)
        if is_relation:
            for name in list(self.fields):
                if type(self.fields[name]) == PaginableManyRelatedField:
                    self.fields.pop(name)
        # threadlocals.data.request = self.context.get('request')
        #self.fields['reitor'].style['base_template'] = 'autocomplete.html'

    def build_property_field(self, field_name, model_field):
        field_cls, field_kwargs = super().build_property_field(field_name, model_field)
        if issubclass(field_cls, serializers.ReadOnlyField) and field_name.startswith('get_'):
            return MethodField, dict(source='*', method_name=field_name)
        return field_cls, field_kwargs

    def build_standard_field(self, field_name, model_field):
        field_cls, field_kwargs = super().build_standard_field(field_name, model_field)
        if issubclass(field_cls, serializers.DecimalField):
            field_kwargs.update(localize=True)
        return field_cls, field_kwargs

    def build_unknown_field(self, field_name, model_class):
        method_name = 'get_{}'.format(field_name)
        if method_name in self.item.view_methods:
            return MethodField, dict(source='*', method_name=method_name)
        if field_name in self.item.fieldsets:
            fieldset = self.item.fieldsets[field_name]
            return FieldsetField, dict(
                source='*', fieldset=fieldset, request=self.context['request'],
                help_text='Returns {}'.format(fieldset['fields'])
            )
        if field_name in self.item.action_serializers:
            serializer_class = ACTIONS[self.item.action_serializers[field_name]]
            return ActionField, dict(
                source='*', field_name=field_name, serializer_class=serializer_class, context=self.context
            )
        if field_name in ACTIONS:
            return ActionField, dict(
                source='*', field_name=field_name, serializer_class=ACTIONS[field_name], context=self.context
            )
        super().build_unknown_field(field_name, model_class)

    def to_representation(self, instance):
        for field in self._readable_fields:
            if isinstance(field, PaginableManyRelatedField) or isinstance(field, ActionField) or isinstance(field, MethodField):
                field.check_choices_response()
        self.context['view'].paginator.instances.append(instance)
        representation = super().to_representation(instance)
        representation = {k[4:] if k.startswith('get_') else k: v for k, v in representation.items() if v is not NONE}
        if specification.app and getattr(instance, '_wrap', False):
            base_url = '/api/v1/{}/'.format(self.item.prefix)
            actions = self.item.view_actions
            if self.context['view'].action in self.item.view_extends:
                actions = self.item.view_extends.get(self.context['view'].action).get('actions') or actions
            representation = {
                'type': 'instance', 'id': instance.id, 'str': str(instance), 'icon': self.item.icon, 'result': representation,
                'actions': actions_metadata(
                    instance, actions, self.context, base_url, [instance]
                )
            }
            for action in representation['actions']:
                action['url'] = action['url'].format(id=instance.id)
            if self.item.renderers:
                representation.update(renderers=self.item.renderers)
        return representation
