# -*- coding: utf-8 -*-
from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        Instituicao = apps.get_model('pnp.instituicao')
        Pessoa = apps.get_model('pnp.pessoa')
        p = Pessoa.objects.order_by('id').first()
        i = Instituicao.objects.first()
        i.pesquisadores_institucionais.add(p)
        i.pesquisadores_institucionais.remove(p)
        print(i)
