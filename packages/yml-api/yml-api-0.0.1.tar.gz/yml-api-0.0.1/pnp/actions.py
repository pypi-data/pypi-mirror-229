import csv
import tempfile
from rest_framework import serializers
from api import actions
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Instituicao, Administrador, LinhaArquivo, TipoInconsistencia, Unidade, Pessoa
from .inconsistencias.alteracao import AlterarInconsistencia
from .inconsistencias import carga, identificacao, geracao


class ImportarPessoas(actions.QuerySetAction):
    arquivo = actions.FileField(label='Arquivo', help_text='Arquivo CSV separado por ";". Para baixar o arquivo modelo <a href="/static/docs/pessoas.csv">clique aqui</a>.<br>Exemplo do arquivo depois de preenchido: <br><img width="500" src="/static/images/pessoas.png"/>', required=False)

    def submit(self):
        blob = self.request.FILES['arquivo'].read()
        try:
            csv_file = blob.decode('iso8859-3').splitlines()
        except Exception:
            csv_file = blob.decode('utf-8').splitlines()
        dialect = csv.Sniffer().sniff(csv_file[0])
        dialect.delimiter = ';'
        csv_reader = csv.DictReader(csv_file, dialect=dialect, fieldnames=['Nome', 'E-mail', 'CPF', 'Papel', 'Instituição', 'Unidade'])
        dados = []
        instituicoes = {}
        unidades = {}
        for index, row in enumerate(csv_reader):
            if index:
                nome, email, cpf, papel, sigla_instituicao, nome_unidade = (
                    row['Nome'], row['E-mail'], row['CPF'], row['Papel'], row['Instituição'], row['Unidade']
                )
                cpf = cpf.zfill(11).replace('.', '').replace('-', '')
                if len(cpf) != 11:
                    raise ValidationError('O CPF "{}" é inválido'.format(cpf))
                unidade = None
                if sigla_instituicao not in instituicoes:
                    instituicoes[sigla_instituicao] = Instituicao.objects.filter(sigla=sigla_instituicao).first()
                if instituicoes[sigla_instituicao] is None:
                    raise ValidationError('Instituição com sigla "{}" não localizada.'.format(sigla_instituicao))
                if nome_unidade:
                    if nome_unidade not in unidades:
                        unidades[nome_unidade] = Unidade.objects.filter(nome=nome_unidade).first()
                    if unidades[nome_unidade] is None:
                        raise ValidationError('Unidade com nome "{}" não localizada.'.format(nome_unidade))
                elif papel in ('RA', 'EA'):
                    raise ValidationError('Informe a unidade de {} ({})'.format(nome, cpf))
                dados.append((nome, email, cpf, papel, sigla_instituicao, nome_unidade))
        self.processar(dados, instituicoes, unidades)
        self.notify('Importação realizada com sucesso')

    def processar(self, dados, instituicoes, unidades):
        pessoas = {}
        for nome, email, cpf, papel, sigla_instituicao, nome_unidade in dados:
            if cpf not in pessoas:
                pessoas[cpf] = Pessoa.objects.filter(cpf=cpf).first() or Pessoa()
                pessoa = pessoas[cpf]
                pessoa.cpf = cpf
                pessoa.nome = nome
                pessoa.email = email
                pessoa.save()
            if papel == 'RE':
                instituicoes[sigla_instituicao].reitor = pessoa
            elif papel == 'PI':
                instituicoes[sigla_instituicao].pesquisadores_institucionais.add(pessoa)
            elif papel == 'GP':
                instituicoes[sigla_instituicao].gestao_pessoas.add(pessoa)
            elif papel == 'RH':
                instituicoes[sigla_instituicao].recursos_humanos.add(pessoa)
            elif papel == 'RA':
                unidades[nome_unidade].registradores_academicos.add(pessoa)
            elif papel == 'EA':
                unidades[nome_unidade].executores_academicos.add(pessoa)
        for instituicao in instituicoes.values():
            instituicao.save()
        for unidade in unidades.values():
            unidade.save()


class Capacitacao(actions.Action):
    def submit(self):
        return {'realizada': True, 'url': 'http://capacitacao.ifrn.edu.br'}

    def has_permission(self):
        return self.user.is_authenticated


class Papeis(actions.Action):
    def submit(self):
        return [
            {'id': 1, 'nome': 'Administrador'},
            {'id': 2, 'nome': 'Registrador Acadêmico'},
        ]

    def has_permission(self):
        return self.user.is_authenticated

class AcessoRapido(actions.Action):
    def submit(self):
        return [
            dict(icon='clipboard-list', label='Programas', url='/api/v1/programas/'),
            dict(icon='clock', label='Duração dos Cursos', url='/api/v1/tipos_curso/duracao/'),
            dict(icon='align-justify', label='Catálogos de Curso', url='/api/v1/cursos_catalogo/'),
            dict(icon='building-user', label='Instituições', url='/api/v1/instituicoes/'),
            dict(icon='circle-check', label='Regras de Consistência', url='/api/v1/regras_inconsistencia/'),
            dict(icon='signs-post', label='Regras de Associação a Programas', url='/api/v1/regras_associacao_programa/'),
            dict(icon='border-none', label='Descrição das Cotas', url='/api/v1/cotas/'),
            dict(icon='clipboard-user', label='Gerenciamento de Usuários', url='/api/v1/pessoas/'),
            dict(icon='user-gear', label='Monitoramento de Usuários', url='#')
        ]

    def has_permission(self):
        return self.user.is_authenticated

class PercentualCargaDados(actions.Action):
    sync = False

    def submit(self):
        import time; time.sleep(2)
        return {"total": "100", "finalizadas": "50", "percentual": "50"}

    def has_permission(self):
        return self.user.is_authenticated


class PercentualResolucaoInconsistencia(actions.Action):
    def submit(self):
        return {"processados": "50", "com_erro": "25", "pendentes": "25", "percentual": "50"}

    def has_permission(self):
        return self.user.is_authenticated


class ConfirmarCapacitacao(actions.Action):
    modal = False

    def submit(self):
        pessoa = self.objects('pnp.pessoa').filter(cpf=self.user.username).first()
        if pessoa:
            pessoa.capacitacao_concluida = not pessoa.capacitacao_concluida
            pessoa.save()
        self.notify('Capacitação confirmada com sucesso.')

    def has_permission(self):
        return self.user.is_authenticated


class RealizarCarga(actions.Action):
    
    def submit(self):
        try:
            for i in list(range(0, self.source.numero_linhas)):
                if i % 500 == 0:
                    registros = carga.consultar_dados(top=500, skip=i, code=self.source.unidade.codigo_sistec)
                conteudo = ';'.join([str(x) if x is not None else '' for x in registros[i % 500].values()])
                LinhaArquivo.objects.create(arquivo=self.source, numero=i+1, conteudo=conteudo)
            self.notify('Carga realizada com sucesso')
        except Exception as e:
            self.source.linhaarquivo_set.all().delete()
            raise e


class ProcessarCarga(actions.Action):
    apenas_com_erro = actions.BooleanField(label='Apenas com Erro')
    def submit(self):
        qs = self.source.linhaarquivo_set.all()
        if self.get('apenas_com_erro'):
            qs = qs.filter(erro__isnull=False) or qs.filter(tipo_erro__isnull=False)
        else:
            qs = qs.filter(data_processamento__isnull=True)
        for linha_arquivo in qs:
            carga.processar_linha(linha_arquivo)
        self.source.atualizar_total_processado()
        self.notify('Carga processada com sucesso')


class IdentificarRegistros(actions.Action):
    unidade = actions.RelatedField(queryset=Unidade.objects, label='Unidade')
    def submit(self):
        unidade = self.validated_data['unidade']
        message = identificacao.identificar_registros_ativos(unidade)
        self.notify('Registros identificados com sucesso. {}'.format(message))


class GerarInconsistencias(actions.Action):
    tipo = actions.RelatedField(queryset=TipoInconsistencia.objects, label='Tipo', required=False)
    unidade = actions.RelatedField(queryset=Unidade.objects, label='Unidade')

    def get_tipo_queryset(self, queryset):
        return queryset.filter(id__in=TipoInconsistencia.ENSINO)

    def submit(self):
        tipo = self.validated_data.get('tipo')
        unidade = self.validated_data['unidade']
        tipos = [tipo] if tipo else TipoInconsistencia.objects.filter(id__in=TipoInconsistencia.ENSINO)
        for tipo in tipos:
            geracao.gerar_inconsistencias(tipo, unidade)
            self.notify('Inconsistências geradas com sucesso.')
