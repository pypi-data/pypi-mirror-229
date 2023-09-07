from rest_framework import exceptions
from .models import Scope


def check_groups(lookups, user, raise_exception=True):
    if lookups is None:
        checked = True
    elif user.is_superuser:
        checked = True
    else:
        group_names = [k for k in lookups.keys()]
        if group_names:
            checked = None in group_names or user.groups.filter(name__in=group_names).exists()
        else:
            checked = False
    if raise_exception and not checked:
        raise exceptions.PermissionDenied(' You do not have permission to perform this action.', 403)
    return checked

def check_lookups(instance, lookups, user, raise_exception=True):
    queryset = type(instance).objects.filter(pk=instance.pk)
    checked = user.is_superuser or apply_lookups(queryset, lookups, user).exists()
    if raise_exception and not checked:
        raise exceptions.PermissionDenied(' You do not have permission to perform this action.', 403)
    return checked

def apply_lookups(queryset, lookups, user):
    if user.is_superuser:
        return queryset
    qs = queryset.none()
    scopes = Scope.objects.filter(username=user.username)
    group_names = set(user.groups.values_list('name', flat=True))
    group_names.add(None)
    for group_name, lookup in lookups.items():
        if group_name in group_names:
            if lookup:
                for scope_lookup, scopename in lookup.items():
                    if scopename == 'username':
                        kwargs = {scope_lookup: user.username}
                    else:
                        pks = scopes.filter(scopename=scopename).values_list('value', flat=True)
                        kwargs = {'{}__in'.format(scope_lookup): pks}
                    qs = qs | queryset.filter(**kwargs)
            else:
                qs = queryset
                break
    return qs