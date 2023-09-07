import os.path

import yaml
from django.conf import settings


class API:

    _instance = None

    def __init__(self):
        self.items = {}
        data = yaml.safe_load(open('api.yml')).get('api')
        self.i18n = yaml.safe_load(open('{}.yml'.format(data.get('lang'))))
        groups = data.get('groups', {})
        for k, v in data.get('models').items():
            name = k.split('.')[-1]
            lookups = to_lookups_dict(v, groups)
            list_lookups = to_lookups_dict(v.get('endpoints', {}).get('list', {}), groups)
            view_lookups = to_lookups_dict(v.get('endpoints', {}).get('view', {}), groups)
            add_lookups = to_lookups_dict(v.get('endpoints', {}).get('add', {}), groups)
            edit_lookups = to_lookups_dict(v.get('endpoints', {}).get('edit', {}), groups)
            delete_lookups = to_lookups_dict(v.get('endpoints', {}).get('delete', {}), groups)
            item = Item(dict(
                icon = v.get('icon'),
                prefix = v.get('prefix'),
                url = '/api/v1/{}/'.format(v.get('prefix')),
                filters = str_to_list(v.get('filters')),
                search = to_search_list(v.get('search')),
                ordering = str_to_list(v.get('ordering')),
                renderers = to_renderers_dict(v.get('renderers', {})),
                actions = to_action_dict(v),
                fieldsets = to_fieldset_dict(v.get('fieldsets', {}), groups),
                relations = to_relation_dict(v.get('relations', {}), groups),
                add_fields = to_fields(v.get('endpoints', {}).get('add', {})),
                add_fieldsets = to_fieldsets(v.get('endpoints', {}).get('add', {})),
                edit_fields=to_fields(v.get('endpoints', {}).get('edit', {})),
                edit_fieldsets=to_fieldsets(v.get('endpoints', {}).get('edit', {})),
                list_display = to_fields(v.get('endpoints', {}).get('list', {}), id_required=True),
                list_extends = to_extension_dict(v.get('endpoints', {}).get('list', {}), groups),
                view_fields = to_fields(v.get('endpoints', {}).get('view', {})),
                view_extends = to_extension_dict(v.get('endpoints', {}).get('view', {}), groups),
                list_actions = to_action_dict(v.get('endpoints', {}).get('list', {}), add_default=True),
                view_actions = to_action_dict(v.get('endpoints', {}).get('view', {})),
                roles = to_roles_dict(v.get('roles', {}), groups),

                list_lookups = list_lookups or lookups,
                view_lookups = view_lookups or lookups,
                add_lookups = add_lookups or lookups,
                edit_lookups = edit_lookups or add_lookups or lookups,
                delete_lookups = delete_lookups or lookups,
            ))
            item.view_methods = [
                name for name in (item.view_fields + item.list_display) if name.startswith('get_')
            ]
            item.action_serializers = {k:item.view_actions[k]['input'] for k in item.view_actions} | {k:item.list_actions[k]['input'] for k in item.list_actions}
            item.view_fields = [name[4:] if name.startswith('get_') else name for name in item.view_fields]
            item.list_display = [name[4:] if name.startswith('get_') else name for name in item.list_display]
            self.items[k] = item

        self.app = data.get('app') and not os.path.exists('/opt/pnp')
        self.groups = groups
        self.user_actions = to_action_dict(data, key='user')
        self.dashboard_actions = to_action_dict(data, key='dashboard')
        if self.app:
            settings.MIDDLEWARE.append('api.middleware.AppMiddleware')
        settings.MIDDLEWARE.append('api.middleware.CorsMiddleware')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = API()
        return cls._instance


class Item(object):
    def __init__(self, d):
        self.__dict__ = d


def to_renderers_dict(value):
    renderers = {}
    for k, v in value.items():
        for name in str_to_list(v):
            renderers[name] = k
    return renderers

def to_action_dict(value, key='actions', add_default=False):
    if isinstance(value, dict):
        actions = value.get(key, {})
        if isinstance(actions, str):
            actions = {name: None for name in str_to_list(actions)}
        for k, v in actions.items():
            if v is None:
                actions[k] = dict(input=k, output={})
            elif isinstance(v, str):
                actions[k] = dict(input=v, output={})
            if 'input' not in actions[k]:
                actions[k]['input'] = k
            if 'display' in actions[k]:
                actions[k]['display'] = str_to_list(actions[k]['display'])
            if 'output' in actions[k] and 'fields' in actions[k]['output']:
                actions[k]['output']['fields'] = str_to_list(actions[k]['output']['fields'])
    else:
        actions = {}
    if add_default and not actions:
        for k in ['add', 'view', 'edit', 'delete']:
            actions[k] = dict(input=k, output={})
    return actions

def str_to_list(s, id_required=False):
    return [name.strip() for name in s.split(',')] if s else []

def to_search_list(s):
    return [(f'{lookup}__icontains' if 'exact' not in lookup else lookup) for lookup in str_to_list(s)]

def iter_to_list(i):
    return [o for o in i]

def to_fields(value, id_required=False):
    if value:
        if isinstance(value, str):
            l = str_to_list(value)
        else:
            l = str_to_list(value.get('fields'))
    else:
        l = []
    if l and id_required and 'id' not in l:
        l.insert(0, 'id')
    return l

def to_fieldsets(value):
    if value:
        if isinstance(value, dict):
            fieldsets = {}
            for k, v in value.get('fieldsets', {}).items():
                fieldsets[k] = str_to_list(v)
            return fieldsets
    return {}

def to_roles_dict(value, groups):
    roles = {}
    for k, v in value.items():
        roles[groups[k]] = v
    return roles

def to_extension_dict(value, groups):
    if value:
        if isinstance(value, dict):
            extensions = value.get('extends', {})
            for k in extensions:
                if extensions[k] is None:
                    extensions[k] = {}
                else:
                    if isinstance(extensions[k], str):
                        extensions[k] = dict(fields=str_to_list(extensions[k]))
                    else:
                        if 'requires'in extensions[k]:
                            extensions[k]['requires'] = to_lookups_dict(extensions[k], groups)
                        else:
                            extensions[k]['requires'] = {}
                        if 'fields' in extensions[k]:
                            extensions[k]['fields'] = str_to_list(extensions[k]['fields'])
                        else:
                            extensions[k]['fields'] = []
                        if 'actions' in extensions[k]:
                            extensions[k]['actions'] = to_action_dict(extensions[k])
                        else:
                            extensions[k]['actions'] = {}
            return extensions
    return {}

def to_relation_dict(value, groups):
    for k, relation in value.items():
        if relation is None:
            value[k] = dict(name=k, fields=[], filters=[], actions={}, related_field=None)
        elif isinstance(relation, str):
            value[k] = dict(name=k, fields=str_to_list(relation), filters=[], actions={}, related_field=None)
        else:
            relation['actions'] = to_action_dict(relation)
            relation['search'] = to_search_list(relation['search']) if 'search' in relation else []
            relation['name'] = relation.get('name', k)
            relation['related_field'] = relation.get('related_field')
            for key in ['fields', 'filters']:
                relation[key] = str_to_list(relation[key]) if key in relation else []
        if 'id' not in value[k]['filters']:
            value[k]['filters'].insert(0, 'id')
    return value

def to_fieldset_dict(value, groups):
    for k, v in value.items():
        if isinstance(v, str):
            value[k] = dict(name=k, fields=str_to_list(v))
        else:
            v['name'] = k
            if 'fields' in v:
                v['fields'] = str_to_list(v['fields'])
    return value


def to_lookups_dict(value, groups):
    if isinstance(value, dict):
        requires = value.get('requires') or {}
        lookups = {}
        if isinstance(requires, str):
            lookups[None] = {}
            for k in str_to_list(requires):
                lookups[None][k] = 'username'
        else:
            for k, v in requires.items():
                group_name = None if k == 'user' else groups[k]
                lookups[group_name] = {}
                if isinstance(v, str):
                    for lookup in str_to_list(v):
                        lookups[group_name][lookup] = 'username'
                elif v:
                    for k1, v1 in v.items():
                        lookups[group_name][k1] = v1
        return lookups
    return {}

