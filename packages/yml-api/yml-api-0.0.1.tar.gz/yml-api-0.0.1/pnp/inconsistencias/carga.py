import csv
import json
import re
import requests
import sys
import time
import traceback
from datetime import datetime, date
from django.conf import settings
from django.core.cache import cache
from django.utils.text import slugify
from psycopg2 import errors
from uuid import uuid1

from pnp.models import Unidade, Aluno, Curso, TipoCurso, Modalidade, Eixo, Ciclo, Matricula, \
    SituacaoMatricula, TipoErroCarga, TipoOferta, Arquivo, HistoricoSincronizacaoSistec

COLUMNS = {
    0: "co_matricula",
    1: "co_ciclo_matricula",
    2: "co_simec",
    3: "id",
    4: "unidade_ensino",
    5: "estado",
    6: "dt_data_inicio",
    7: "dt_data_fim_previsto",
    8: "ds_eixo_tecnologico",
    9: "co_curso",
    10: "no_curso",
    11: "co_tipo_curso",
    12: "tipo_curso",
    13: "nome_ciclo",
    14: "carga_horaria",
    15: "nome_aluno",
    16: "periodo_cadastro_matricula_aluno",
    17: "situacao_matricula",
    18: "tipo_oferta",
    19: "numero_cpf",
    20: "cod_municipio",
    21: "modalidade_ensino",
    22: "dt_ocorrencia_matricula",
    23: "vagas_ofertadas",
    24: "total_inscritos",
    25: "mes_de_ocorrencia",
    26: "sg_etec",
    27: "co_aluno",
    28: "sexo_aluno",
    29: "dt_nascimento_aluno",
    30: "co_tipo_unidade_ensino",
    31: "nome_completo_agrupador",
    32: "co_agrupador"
}

UNIDADES_IGNORADAS = ["45332", "13645", "1019", "46064", "14180", "21449", "13860", "44226"]

class Situation:
    ABANDONO      = 'ABANDONO'
    CANCELADA     = 'CANCELADA'
    CONCLUIDA     = 'CONCLUIDA'
    DESLIGADA     = 'DESLIGADA'
    EM_CURSO      = 'EM_CURSO'
    EXCLUIDO      = 'EXCLUIDO'
    INTEGRALIZADA = 'INTEGRALIZADA'
    REPROVADA     = 'REPROVADA'
    SUBSTITUIDO   = 'SUBSTITUIDO'
    TRANSF_EXT    = 'TRANSF_EXT'
    TRANSF_INT    = 'TRANSF_INT'

TOTAIS = {}

def consultar_totais(codigo=None):
    global TOTAIS
    data = {
        'token_acesso': settings.ODATA_TOKEN,
        'servico': settings.ODATA_SERVICE_TOTAL, 'filtro[$top]': str(1000),
    }
    if not TOTAIS:
        if settings.ODATA_URL and not 'test' in sys.argv:
            response = requests.post(settings.ODATA_URL, data=data)
            for registro in sorted(response.json()['body'], key=lambda d: int(d['quantidade'])):
                TOTAIS[registro['id']] = int(registro['quantidade'])
        else:
            for registro in sorted(json.load(open('pnp/fixtures/teste/carga-totais.json'))['body'], key=lambda d: int(d['quantidade'])):
                TOTAIS[registro['id']] = int(registro['quantidade'])
    return TOTAIS if codigo is None else TOTAIS[codigo]


def consultar_dados(top=10, skip=0, code=None, retry=20):
    print('Consultando dados do SISTEC... {} registros a partir de {}. ID: {}'.format(top, skip, code))
    if settings.ODATA_URL and not 'test' in sys.argv:
        data = {
            'token_acesso': settings.ODATA_TOKEN,
            'servico': settings.ODATA_SERVICE, 'filtro[$top]': str(top), 'filtro[$skip]': str(skip),
        }
        if code:
            data['filtro[$filter]'] = "ID eq {}".format(code)
        data['filtro[$orderby]'] = 'CO_MATRICULA'
        response = requests.post(settings.ODATA_URL, data=data)
        # print(response.text)
        if 'body' in response.text:
            body = response.json()['body']
            # print('Total: {}'.format(len(body)))
            return body
        else:
            time.sleep(1)
            return consultar_dados(top, skip, code, retry - 1) if retry else []
    else:
        file_name = 'pnp/fixtures/teste/carga-{}.json'.format(code)
        return json.load(open(file_name))['body'][skip:skip+top]


def processar_linha(linha_arquivo, linha=None):
    if not linha:
        linha = linha_arquivo.conteudo
    linha_arquivo.erro = None
    linha_arquivo.tipo_erro_id = None
    csv_reader = csv.reader([linha], delimiter=";")
    for colunas in csv_reader:
        if len(colunas) == 33:
            dados = {nome: colunas[indice] for indice, nome in COLUMNS.items()}
            if dados["co_tipo_curso"] == "2":
                dados["co_tipo_curso"] = "1"
            if Unidade.objects.filter(codigo_sistec=dados["id"]).exists():
                try:
                    linha_arquivo.unidade = get_unidade(dados)
                    parse_aluno(dados)
                    parse_curso(dados)
                    parse_ciclo(dados)
                    try:
                        parse_matricula(dados)
                    except StopIteration as error:
                        traceback.print_exc()
                        linha_arquivo.erro = str(error)
                        linha_arquivo.tipo_erro_id = TipoErroCarga.GENERICO
                except errors.UniqueViolation as error:
                        traceback.print_exc()
                        linha_arquivo.erro = str(error)
                        linha_arquivo.tipo_erro_id = TipoErroCarga.VIOLACAO_UNICIDADE
                except Exception as error:
                    traceback.print_exc()
                    linha_arquivo.erro = str(error)
                    linha_arquivo.tipo_erro_id = TipoErroCarga.GENERICO
            else:
                if dados["id"] not in UNIDADES_IGNORADAS:
                    linha_arquivo.erro = dados["id"]
                    linha_arquivo.tipo_erro_id = TipoErroCarga.UNIDADE_INEXISTENTE
        else:
            if "&amp;".upper() in linha.upper():
                linha = substituicao_ecomercial_recursiva(linha)
                processar_linha(linha_arquivo, linha)
            elif "&nbsp;".upper() in linha.upper():
                linha = re.sub(r"&nbsp;", " ", linha, flags=re.IGNORECASE)
                processar_linha(linha_arquivo, linha)
            else:
                linha_arquivo.erro = "Número de colunas diferente de 33"
                linha_arquivo.tipo_erro_id = TipoErroCarga.NUMERO_COLUNAS
    linha_arquivo.data_processamento = datetime.now()
    linha_arquivo.save()

def identifica_registro_excluidos(linha_arquivo, ciclos_ativos, matriculas_ativas):
    csv_reader = csv.reader([linha_arquivo.conteudo], delimiter=";")
    for colunas in csv_reader:
        dados = {nome: colunas[indice] for indice, nome in COLUMNS.items() if nome in ("co_ciclo_matricula", "co_matricula")}
        codigo_ciclo = dados["co_ciclo_matricula"]
        codigo_matricula = dados["co_matricula"]
        if codigo_ciclo in ciclos_ativos:
            ciclos_ativos.remove(codigo_ciclo)
        if codigo_matricula in matriculas_ativas:
            matriculas_ativas.remove(codigo_matricula)


def substituicao_ecomercial_recursiva(linha):
    """
    # Exemplo de uso
    text = "Este texto tem &amp;amp; no meio"
    print(recursive_replace(text))
    output: Este texto tem & no meio
    """
    linha = re.sub(r"&amp;", "&", linha, flags=re.IGNORECASE)
    if "&amp;".upper() in linha.upper():
        return substituicao_ecomercial_recursiva(linha)
    return linha


def parse_aluno(dados):
    agora = datetime.now()
    Aluno.objects.get_or_create(
        codigo=dados["co_aluno"],
        defaults=dict(
            nome=dados["nome_aluno"],
            cpf=None if dados["numero_cpf"] == "-" else dados["numero_cpf"],
            sexo=dados["sexo_aluno"],
            data_nascimento=parse_data(dados["dt_nascimento_aluno"], "dt_nascimento_aluno"),
            data_cadastro=agora,
            data_atualizacao=agora,
        )
    )


def parse_curso(dados):
    codigo = uuid1().hex
    agora = datetime.now()
    nome = dados["no_curso"]
    unidade = get_unidade(dados)
    tipo = get_tipo_curso(dados)
    modalidade = get_modalidade(dados)
    eixo = get_eixo(dados)
    key = '{}:{}:{}:{}:{}'.format(slugify(nome), unidade.id, tipo.id, modalidade.id, eixo.id if eixo else 0)
    curso = cache.get(key)
    if curso is None:
        curso = Curso.objects.get_or_create(
            nome=nome,
            unidade=unidade,
            tipo=tipo,
            modalidade=modalidade,
            eixo=eixo,
            defaults=dict(
                codigo=codigo,
                data_cadastro=agora,
                data_atualizacao=agora,
            )
        )[0]
    cache.set(key, curso)


def get_curso(dados):
    nome = dados["no_curso"]
    unidade = get_unidade(dados)
    tipo = get_tipo_curso(dados)
    modalidade = get_modalidade(dados)
    eixo = get_eixo(dados)
    key = '{}:{}:{}:{}:{}'.format(slugify(nome), unidade.id, tipo.id, modalidade.id, eixo.id if eixo else 0)
    curso = cache.get(key)
    return curso or Curso.objects.get(nome=nome, unidade=unidade, tipo=tipo, modalidade=modalidade, eixo=eixo)


def parse_ciclo(dados):
    curso = get_curso(dados)
    agora = datetime.now()
    Ciclo.objects.get_or_create(
        codigo=dados["co_ciclo_matricula"],
        defaults=dict(
            nome=dados["nome_ciclo"],
            data_inicio=parse_data(dados["dt_data_inicio"], "dt_data_inicio"),
            data_fim=parse_data(dados["dt_data_fim_previsto"], "dt_data_fim_previsto"),
            vagas=int(dados["vagas_ofertadas"] or 0),
            inscritos=int(dados["total_inscritos"] or 0),
            evadidos=0,
            tipo_oferta=get_tipo_oferta(dados),
            sg_etec=dados["sg_etec"],
            curso=curso,
            data_cadastro=agora,
            data_atualizacao=agora,
            ingressantes=0,
            carga_horaria=dados["carga_horaria"]
        )
    )


def merge_ciclo(atualizar=False):
    COLUMNS = {1: 'co_ciclo_matricula', 3: 'id', 9: 'co_curso', 10: 'no_curso', 11: 'co_tipo_curso', 12: 'tipo_curso', 21: 'modalidade_ensino', 8: 'ds_eixo_tecnologico'}
    geral = {}
    for arquivo in Arquivo.objects.order_by('id'):
        merge = {}
        ciclos = []
        for linha in arquivo.linhaarquivo_set.all():
            csv_reader = csv.reader([linha.conteudo], delimiter=';')
            for colunas in csv_reader:
                dados = {nome: colunas[indice] for indice, nome in COLUMNS.items()}
                codigo = dados['co_ciclo_matricula']
                if codigo in ciclos: continue
                ciclos.append(codigo)
                ciclo = Ciclo.objects.get(codigo=codigo)
                unidade = Unidade.objects.get(codigo_sistec=dados['id'])
                modalidade = Modalidade.objects.get(nome=dados['modalidade_ensino'])
                modalidade = Modalidade.objects.get(id=Modalidade.EAD) if modalidade.id == Modalidade.TODOS else modalidade
                if ciclo.curso.unidade_id != unidade.id or ciclo.curso.modalidade_id != modalidade.id:
                    codigo_tipo_curso = TipoCurso.FIC if int(dados['co_tipo_curso']) == 2 else dados['co_tipo_curso']
                    tipo_curso = TipoCurso.objects.get(codigo=codigo_tipo_curso)
                    eixo = Eixo.objects.filter(nome__iexact=dados['ds_eixo_tecnologico']).first()
                    curso = Curso.objects.get(nome=dados['no_curso'], unidade=unidade, tipo=tipo_curso, modalidade=modalidade, eixo=eixo)
                    merge[ciclo.id] = curso.id
        if merge:
            geral[arquivo.unidade.id] = merge

    if atualizar:
        for registro in geral.values():
            for ciclo_id, curso_id in registro.items():
                ciclo = Ciclo.objects.get(pk=ciclo_id)
                Ciclo.objects.filter(pk=ciclo_id).update(curso_id=curso_id)
                historico = f'ALTERANDO "curso" DO CICLO "{ciclo.codigo}" DE "{ciclo.curso.id}" PARA "{curso_id}"'
                HistoricoSincronizacaoSistec.objects.create(historico=historico)
    return geral

def parse_matricula(dados):
    agora = datetime.now()
    data_matricula = parse_data(dados["dt_ocorrencia_matricula"], "dt_ocorrencia_matricula")
    data_ocorrencia = parse_data(dados["mes_de_ocorrencia"], "mes_de_ocorrencia")
    data_matricula = date(data_matricula.year, data_matricula.month, 1)
    data_ocorrencia = date(data_ocorrencia.year, data_ocorrencia.month, 25)
    matricula, criou = Matricula.objects.get_or_create(
        codigo=dados["co_matricula"],
        defaults=dict(
            aluno=get_aluno(dados),
            ciclo=get_ciclo(dados),
            situacao=get_situacao(dados),
            data_ocorrencia=data_ocorrencia,
            data_matricula=data_matricula,
            data_cadastro=agora,
            data_atualizacao=agora,
        )
    )
    # Fazer o Merge
    if not criou:
        merge_matricula(matricula, dados)


def atualizar_matricula(matricula, campo, valor_novo):
    valor_antigo = getattr(matricula, campo)
    historico = f'ALTERANDO "{campo}" DA MATRÍCULA "{matricula.codigo}" DE "{valor_antigo}" PARA {valor_novo}'
    setattr(matricula, campo, valor_novo)
    HistoricoSincronizacaoSistec.objects.create(historico=historico)

def merge_matricula(matricula, dados):
    atualizar = False
    data_atualizacao = datetime.now()
    if matricula.ciclo.codigo != dados["co_ciclo_matricula"]:
        atualizar_matricula(matricula, "ciclo", get_ciclo(dados))
        atualizar_matricula(matricula, "data_atualizacao", data_atualizacao)
        atualizar = True

    # Se
    # matricula.deleted = false
    # E
    # (SISTEC.Situação de matricula= “EM_CURSO” OU “INTEGRALIZADA” OU “CONCLUIDO” ou “REPROVADA”
    # E
    # matricula.SITUATION = “ABANDONO” OU “CANCELADA” OU “DESLIGADA” OU “TRANF. INT” OU “TRANF. EXT”)
    # E
    # SISTEC.dt_ocorrencia_alteracao_matricula > matricula.updated
    if not matricula.excluido \
            and dados["situacao_matricula"] in [Situation.EM_CURSO, Situation.INTEGRALIZADA, Situation.CONCLUIDA, Situation.REPROVADA] \
            and matricula.situacao_id in [SituacaoMatricula.ABANDONO, SituacaoMatricula.CANCELADA, SituacaoMatricula.DESLIGADA, SituacaoMatricula.TRANSF_INT, SituacaoMatricula.TRANSF_EXT] \
            and get_ocorrencia_alteracao_matricula(dados) > matricula.data_atualizacao.date():
        atualizar_matricula(matricula, "data_ocorrencia", get_ocorrencia_alteracao_matricula(dados))
        atualizar_matricula(matricula, "situacao", get_situacao(dados))
        atualizar_matricula(matricula, "data_atualizacao", data_atualizacao)
        atualizar = True

    # Se
    # matricula.deleted = false
    # E
    # (SISTEC.Situação de matricula= “EM_CURSO”
    # E
    # matricula.SITUATION = ”INTEGRALIZADA” OU “CONCLUIDA” OU “REPROVADA” OU “SUBSTITUIDO” OU “EXCLUIDO”
    if not matricula.excluido \
            and dados["situacao_matricula"] == Situation.EM_CURSO \
            and matricula.situacao_id in [SituacaoMatricula.INTEGRALIZADA, SituacaoMatricula.CONCLUIDA, SituacaoMatricula.REPROVADA, SituacaoMatricula.SUBSTITUIDO, SituacaoMatricula.EXCLUIDO]:
        atualizar_matricula(matricula, "data_atualizacao", data_atualizacao)
        atualizar = True

    # Se
    # matricula.deleted = false
    # E
    # (SISTEC.Situação de matricula= (“ABANDONO” OU “CANCELADA” OU “DESLIGADA” OU “TRANF. INT” OU “TRANF. EXT”)
    # E
    # matricula.SITUATION =(“INTEGRALIZADA” OU “CONCLUIDO”)
    if not matricula.excluido \
            and dados["situacao_matricula"] in [Situation.ABANDONO, Situation.CANCELADA, Situation.DESLIGADA, Situation.TRANSF_INT, Situation.TRANSF_EXT] \
            and matricula.situacao_id in [SituacaoMatricula.INTEGRALIZADA, SituacaoMatricula.CONCLUIDA]:
        atualizar_matricula(matricula, "data_atualizacao", data_atualizacao)
        atualizar = True

    # Se
    # matricula.deleted = false
    # E
    # (SISTEC.Situação de matricula= “EM_CURSO” OU “INTEGRALIZADA” OU “CONCLUIDO” OU “REPROVADA”
    # E
    # matricula.SITUATION = “ABANDONO” OU “CANCELADA” OU “DESLIGADA” OU “TRANF. INT” OU “TRANF. EXT”)
    # E
    # SISTEC.dt_ocorrencia_alteracao_matricula < matricula.updated
    if not matricula.excluido \
            and dados["situacao_matricula"] in (Situation.EM_CURSO, Situation.INTEGRALIZADA, Situation.CONCLUIDA, Situation.REPROVADA) \
            and matricula.situacao_id in (SituacaoMatricula.ABANDONO, SituacaoMatricula.CANCELADA, SituacaoMatricula.DESLIGADA, SituacaoMatricula.TRANSF_INT, SituacaoMatricula.TRANSF_EXT) \
            and get_ocorrencia_alteracao_matricula(dados) < matricula.data_atualizacao.date():
        atualizar_matricula(matricula, "data_atualizacao", data_atualizacao)
        atualizar = True

    # Se
    # matricula.deleted = false
    # E
    # (SISTEC.Situação de matricula<>”EM_CURSO”
    # E
    # matricula.SITUATION =(“EM_CURSO”)
    if not matricula.excluido \
            and dados["situacao_matricula"] != Situation.EM_CURSO \
            and matricula.situacao_id == SituacaoMatricula.EM_CURSO:
        atualizar_matricula(matricula, "data_ocorrencia", get_ocorrencia_alteracao_matricula(dados))
        atualizar_matricula(matricula, "situacao", get_situacao(dados))
        atualizar_matricula(matricula, "data_atualizacao", data_atualizacao)
        atualizar = True

    # Se
    # matricula.deleted = false
    # E
    # (SISTEC.Situação de matricula=”CONCLUIDO”
    # E
    # matricula.SITUATION =(“INTEGRALIZADA”)
    if not matricula.excluido \
            and dados["situacao_matricula"] == Situation.CONCLUIDA \
            and matricula.situacao_id == SituacaoMatricula.INTEGRALIZADA:
        atualizar_matricula(matricula, "data_ocorrencia", get_ocorrencia_alteracao_matricula(dados))
        atualizar_matricula(matricula, "situacao", get_situacao(dados))
        atualizar_matricula(matricula, "data_atualizacao", data_atualizacao)
        atualizar = True


    # Se
    # matricula.deleted = false
    # E
    # matricula.SITUATION = “SUBSTITUIDO” OU “EXCLUIDO”
    if not matricula.excluido \
            and matricula.situacao_id in [SituacaoMatricula.SUBSTITUIDO, SituacaoMatricula.EXCLUIDO]:
        atualizar_matricula(matricula, "data_atualizacao", data_atualizacao)
        atualizar = True

    # Se
    # matricula.code = SISTEC.co_matricula
    # E
    # matricula.student_code != SISTEC.co_aluno
    # ENTÃO
    # matricula.student_code = SISTEC.co_aluno
    if matricula.codigo == dados["co_matricula"] \
            and matricula.aluno.codigo != dados["co_aluno"]:
        atualizar_matricula(matricula, "aluno", get_aluno(dados))
        atualizar = True

    if atualizar:
        matricula.save()


def cached(key):
    def inner(func):
        def wrapper(dados):
            cache_key = '{}:{}'.format(func.__name__, slugify(dados[key]))
            value = cache.get(cache_key)
            if value is None:
                value = func(dados)
                cache.set(cache_key, value)
            return value
        return wrapper
    return inner


@cached('id')
def get_unidade(dados):
    return Unidade.objects.get(codigo_sistec=dados["id"])


@cached('co_tipo_curso')
def get_tipo_curso(dados):
    codigo = TipoCurso.FIC if int(dados["co_tipo_curso"]) == 2 else dados["co_tipo_curso"]
    return TipoCurso.objects.get(codigo=codigo)


@cached('modalidade_ensino')
def get_modalidade(dados):
    modalidade = Modalidade.objects.get_or_create(nome=dados["modalidade_ensino"])[0]
    if modalidade.id == Modalidade.TODOS:
        modalidade = Modalidade.objects.get(id=Modalidade.EAD)
    return modalidade


@cached('ds_eixo_tecnologico')
def get_eixo(dados):
    return Eixo.objects.filter(nome__iexact=dados["ds_eixo_tecnologico"]).first()


def get_aluno(dados):
    return Aluno.objects.get(codigo=dados["co_aluno"])


@cached('co_ciclo_matricula')
def get_ciclo(dados):
    return Ciclo.objects.get(codigo=dados["co_ciclo_matricula"])


@cached('situacao_matricula')
def get_situacao(dados):
    return SituacaoMatricula.objects.get(nome__startswith=dados["situacao_matricula"][0:-1])


@cached('tipo_oferta')
def get_tipo_oferta(dados):
    return TipoOferta.objects.get(nome=dados["tipo_oferta"])


def get_ocorrencia_alteracao_matricula(dados):
    mes_ocorrencia = dados["mes_de_ocorrencia"]
    matches = re.match(r"^[\w:\s/]+(?P<mes>\d{2})\/(?P<ano>\d{4})$", mes_ocorrencia)
    if matches:
        matches_dict = matches.groupdict()
        ano = matches_dict['ano']
        mes = matches_dict['mes']
    else:
        mes, ano = re.split(r'[\s|/]', mes_ocorrencia)
        mes = Meses.get_numero(mes)

    return parse_data(f'25/{mes}/{ano}', "mes_de_ocorrencia")


def parse_data(data, campo):
    try:
        if not data[0].isdigit():
            mes, ano = re.split(r'[\s|/]', data)
            mes = Meses.get_numero(mes)
            return parse_data(f'25/{mes}/{ano}', campo)

        if len(data) > 10:
            if data[4] == '-':
                data = datetime.strptime(data[0:10], "%Y-%d-%m").date()
            else:
                data = datetime.strptime(data[0:10], "%d/%m/%Y").date()
        elif len(data) == 7:
            data = datetime.strptime('01/{}'.format(data), "%d/%m/%Y").date()
        else:
            data = datetime.strptime(data, "%d/%m/%Y").date()
    except Exception as error:
        raise Exception(f'{campo}: {str(error)}')
    return data


class Meses:
    JANEIRO = 'Janeiro'
    FEVEREIRO = 'Fevereiro'
    MARCO = 'Março'
    ABRIL = 'Abril'
    MAIO = 'Maio'
    JUNHO = 'Junho'
    JULHO = 'Julho'
    AGOSTO = 'Agosto'
    SETEMBRO = 'Setembro'
    OUTUBRO = 'Outubro'
    NOVEMBRO = 'Novembro'
    DEZEMBRO = 'Dezembro'

    @classmethod
    def get_choices(cls):
        return [
            [1, cls.JANEIRO],
            [2, cls.FEVEREIRO],
            [3, cls.MARCO],
            [4, cls.ABRIL],
            [5, cls.MAIO],
            [6, cls.JUNHO],
            [7, cls.JULHO],
            [8, cls.AGOSTO],
            [9, cls.SETEMBRO],
            [10, cls.OUTUBRO],
            [11, cls.NOVEMBRO],
            [12, cls.DEZEMBRO],
        ]

    @classmethod
    def get_dict(cls):
        return {mes.upper(): numero for numero, mes in cls.get_choices()}

    @classmethod
    def get_numero(cls, mes):
        return cls.get_dict()[mes]
