
from django.db import models
from rest_framework import pagination
from rest_framework import relations
from . import permissions
from .specification import API
from .actions import actions_metadata
from .utils import to_snake_case, to_choices, generic_filter, generic_search
from .exceptions import JsonResponseReadyException


specification = API.instance()


def filter_type(model, lookups):
    field = None
    ignore = 'icontains', 'contains', 'gt', 'gte', 'lt', 'lte', 'id'
    for lookup in lookups.split('__'):
        if lookup not in ignore:
            for field in model._meta.get_fields():
                if field.name == lookup:
                    model = field.related_model
                    break
    if field:
        if getattr(field, 'choices'):
            return [{'id': k, 'text': v} for k, v in field.choices]
        elif isinstance(field, models.CharField):
            return 'text'
        elif isinstance(field, models.BooleanField):
            return 'bool'
        elif isinstance(field, models.DateField):
            return 'date'
        elif isinstance(field, models.ForeignKey):
            return 'select'
        elif isinstance(field, models.ManyToManyField):
            return 'select'
    return None


class PageNumberPagination(pagination.PageNumberPagination):
    page_size = 10

    def __init__(self, *args, **kwargs):
        self.url = None
        self.model = None
        self.relation_name = None
        self.context = None
        self.instances = []
        super().__init__(*args, **kwargs)

    def paginate_queryset(self, queryset, request, view=None, relation_name=None):
        self.url = request.path
        self.model = queryset.model
        self.relation_name = relation_name
        self.context = dict(request=request, view=view)
        queryset = queryset.order_by('id') if not queryset.ordered else queryset
        return super().paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data, metadata=None, keep_path=False):
        relation_name = self.relation_name
        key = '{}.{}'.format(self.model._meta.app_label, self.model._meta.model_name)
        item = specification.items[key]
        base_url = self.context['request'].path if keep_path else '/api/v1/{}/'.format(item.prefix)
        actions = []
        filters = {}
        search = []
        if metadata:
            relation_name = metadata.get('name') or relation_name
            if relation_name:
                relation_name = relation_name[4:] if relation_name.startswith('get_') else relation_name
            actions.extend(actions_metadata(data, metadata.get('actions', {}), self.context, base_url, self.instances, viewer=metadata.get('viewer')))
            related_field = metadata.get('related_field')
            if related_field:
                url = '{}{}/add/'.format(self.context['request'].path, metadata['name'])
                actions.append(dict(name='append', url=url, target='queryset', modal=True, ids=[]))

            for name in metadata.get('search', {}):
                search.append(name)

            for name in metadata.get('filters', {}):
                filters[name] = None
            for lookup in filters:
                filters[lookup] = filter_type(self.model, lookup)
        response = super().get_paginated_response(data)
        model_name = to_snake_case(self.model.__name__)
        response.data.update(type='queryset', model=model_name, icon=item.icon, url=self.url, actions=actions, filters=filters, search=search, relation=self.relation_name)
        response.data.update(renderers=specification.items[key].renderers)
        if relation_name:
            for k in ['next', 'previous']:
                if response.data[k]:
                    if 'only=' not in response.data[k]:
                        response.data[k] = '{}&only={}'.format(response.data[k], relation_name)
        return response


class RelationPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'relation_page'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PaginableManyRelatedField(relations.ManyRelatedField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paginator = None
        self.relation = None

    def check_choices_response(self):
        if self.source_attrs[0] == self.context['request'].GET.get('only'):
            choices = to_choices(self.child_relation.queryset.model, self.context['request'])
            if choices:
                raise JsonResponseReadyException(choices)

    def get_attribute(self, instance):
        model = type(instance)
        key = '{}.{}'.format(model._meta.app_label, model._meta.model_name)
        item = specification.items.get(key)
        self.relation = item.relations.get(self.source_attrs[0])
        self.child_relation.relation_name = self.source_attrs[0]
        queryset = super().get_attribute(instance)
        if isinstance(queryset, models.QuerySet):
            self.paginator = RelationPageNumberPagination()
            if self.context['view'].action == 'retrieve' or self.source_attrs[0] == self.context['request'].GET.get('only'):
                for backend in list(self.context['view'].filter_backends):
                    queryset = backend().filter_queryset(self.context['request'], queryset, self)
            queryset = self.paginator.paginate_queryset(queryset, self.context['request'], self.context['view'], relation_name=self.source_attrs[0])

        return queryset

    def to_representation(self, value):
        if self.relation and not permissions.check_groups(self.relation.get('requires'), self.context['request'].user, False):
            return NONE
        if self.context['view'].action in ['update']:
            return [obj.pk for obj in value]
        elif self.context['view'].action == 'list':
            if specification.app:
                data = [str(obj) for obj in value]
            else:
                data = [dict(id=obj.id, text=str(obj)) for obj in value]
        else:
            data = super().to_representation(value)
        if self.paginator:
            self.paginator.instances = [obj for obj in value]
            return self.paginator.get_paginated_response(data, self.relation).data
        return data

    def get_choices(self, cutoff=None):
        if self.relation:
            return {obj.id: str(obj) for obj in getattr(self.root.instance, self.relation['name']).all()}
        return {}