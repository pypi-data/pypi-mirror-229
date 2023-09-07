import re
import operator
from datetime import datetime
from django.db import models
from functools import reduce
from inspect import isfunction
from django.db.models.fields import related_descriptors
from django.db import models


def as_choices(qs, limit=20):
    return [{'id': value.pk, 'text': str(value)} for value in qs[0:limit]]


def to_choices(model, request, relation_name=None):
    from .actions import ACTIONS
    field_name = request.query_params.get('choices_field')
    if field_name:
        if relation_name:
            if relation_name in ACTIONS:
                model = ACTIONS[relation_name](context=dict(request=request)).submit().none().model
            else:
                model = related_model(model, relation_name)
        term = request.query_params.get('choices_search')
        related = related_model(model, field_name)
        if related:
            qs = related.objects.all()
            return as_choices(generic_search(qs, term))
        else:
            return [{'id': choice[0], 'text': choice[1]} for choice in getattr(model, field_name).field.choices]
    return None


def related_model(model, relation_name):
 attr = getattr(model, relation_name, None)
 if attr is None:
  attr = getattr(model, f'get_{relation_name}')
  value = attr(model(id=0))
  if isinstance(value, models.QuerySet):
    return value.model
  elif isinstance(value, models.Model):
    return type(value)
 if isinstance(attr, related_descriptors.ForwardManyToOneDescriptor):
    return attr.field.related_model
 elif isinstance(attr, related_descriptors.ManyToManyDescriptor):
    return attr.field.related_model
 elif isinstance(attr, related_descriptors.ReverseManyToOneDescriptor):
    return attr.rel.related_model


def to_snake_case(name):
    return name if name.islower() else re.sub(r'(?<!^)(?=[A-Z0-9])', '_', name).lower()


def to_camel_case(name):
    return ''.join(word.title() for word in name.split('_'))


def generic_filter(queryset, lookup, value):
    booleans = dict(true=True, false=False, null=None)
    if len(value) == 10 and '-' in value:
        value = datetime.strptime(value, '%Y-%m-%d');
    if value in booleans:
        value = booleans[value]
    return queryset.filter(**{lookup: value})


def generic_search(qs, term, lookups=None):
    if lookups is None:
        lookups = [f'{field.name}__icontains' for field in qs.model._meta.get_fields() if isinstance(field, models.CharField)] or []
    if lookups:
        terms = term.split(' ') if term else []
        conditions = []
        for term in terms:
            queries = [
                models.Q(**{lookup: term})
                for lookup in lookups
            ]
            conditions.append(reduce(operator.or_, queries))

        return qs.filter(reduce(operator.and_, conditions)) if conditions else qs
    return qs