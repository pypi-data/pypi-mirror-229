# -*- coding: utf-8 -*-
from django import template
from datetime import datetime
from django.template import Library
from django.utils.safestring import mark_safe
from api.i18n import translate
from django.template.loader import select_template

register = Library()


@register.filter
def is_list(value):
    return isinstance(value, list)\


@register.filter
def renderer(renderers, name):
    return 'renderers/{}.html'.format(renderers[name])


@register.filter
def template(name, default='default.html'):
    selected = select_template(['{}.html'.format(name), default])
    return selected


@register.filter
def is_dict(value):
    return isinstance(value, dict)


@register.filter
def format(value):
    if value is None:
        return '-'
    if value is True:
        return 'Sim'
    if value is False:
        return 'Não'
    if value == '':
        return '-'
    if isinstance(value, str) and len(value) == 26 and value[4] == '-' and value[7] == '-':
        dt = datetime.strptime(value[0:10+6], '%Y-%m-%dT%H:%M')
        return dt.strftime('%d/%m/%Y %H:%M') if dt.hour and dt.minute else dt.strftime('%d/%m/%Y')
    return value

@register.filter
def i18n(term):
    return translate(term)


@register.filter
def has_instance_actions(actions):
    return bool([action for action in actions if action['target'] == 'instance'])


@register.filter
def has_instances_actions(actions):
    return bool([action for action in actions if action['target'] == 'instances'])


@register.filter
def has_queryset_actions(actions):
    return bool([action for action in actions if action['target'] == 'queryset'])


@register.filter
def ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


@register.filter
def format_url(url, id):
    return url.format(id=id)
