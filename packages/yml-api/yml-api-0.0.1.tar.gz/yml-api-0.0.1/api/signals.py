from django.contrib.auth.models import User, Group

from .models import Scope


def pre_save_func(sender, **kwargs):
    kwargs['instance'].__usernames__ = {}
    for group_name, role in sender.__roles__.items():
        kwargs['instance'].__usernames__[group_name] = []
        for username in sender.objects.filter(pk=kwargs['instance'].pk).values_list(role['username'], flat=True):
            if username:
             kwargs['instance'].__usernames__[group_name].append(username)


def post_save_func(sender, **kwargs):
    pk = kwargs['instance'].pk
    modelname = '{}.{}'.format(sender._meta.model_name, sender._meta.app_label)
    for group_name, role in sender.__roles__.items():
        group = Group.objects.get(name=group_name)
        for username in sender.objects.filter(pk=pk).values_list(role['username'], flat=True):
            if username is None:
                for scopename in role.get('scopes', {}).keys():
                    Scope.objects.filter(
                        groupname=group.name, scopename=scopename, modelname=modelname, value=pk
                    ).delete()
            else:
                user = User.objects.filter(username=username).first()
                if user is None:
                    user = User.objects.create(username=username)
                user.groups.add(group)
                if role.get('scopes'):
                    for scopename, value_lookup in role.get('scopes').items():
                        for value in sender.objects.filter(pk=pk).values_list(value_lookup, flat=True):
                            Scope.objects.get_or_create(
                                username=username, groupname=group.name, modelname=modelname, scopename=scopename, value=value
                            )
                else:
                    Scope.objects.get_or_create(
                        username=username, groupname=group.name, modelname=modelname, scopename='pk', value=pk
                    )
        for username in kwargs['instance'].__usernames__[group_name]:
            if not Scope.objects.filter(username=username, groupname=group_name).exists():
                User.objects.get(username=username).groups.remove(group)


def m2m_save_func(sender, **kwargs):
    if kwargs['action'] in ('pre_add', 'pre_remove'):
        func = pre_save_func
    else:
        func = post_save_func
    func(type(kwargs['instance']), instance=kwargs['instance'])


def post_delete_func(sender, **kwargs):
    pk = kwargs['instance'].pk
    modelname = '{}.{}'.format(sender._meta.model_name, sender._meta.app_label)
    Scope.objects.filter(modelname=modelname, value=pk).delete()
    for group_name, usernames in kwargs['instance'].__usernames__.items():
        group = Group.objects.get(name=group_name)
        for username in usernames:
            if not Scope.objects.filter(username=username, groupname=group_name).exists():
                User.objects.get(username=username).groups.remove(group)
