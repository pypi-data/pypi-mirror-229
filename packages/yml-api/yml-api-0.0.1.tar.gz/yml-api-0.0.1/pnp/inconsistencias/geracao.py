from datetime import date, datetime
from django.core.files import File
from django.db.models import Count, Value
from django.db.models import F, CharField
from django.db.models.functions import Concat
from django.db.models.functions import ExtractDay
from ..models import Matricula, Ciclo, TipoInconsistencia, Curso, Inconsistencia, SituacaoInconsistencia, Configuracao, TipoCurso, SituacaoMatricula, Modalidade, Servidor, UnidadeOrganizacional, \
    TipoUnidade, Instituicao, VagasCiclo, Unidade


def gerar_inconsistencias(tipo, objeto, inicial=False):
    unidade = None
    if isinstance(objeto, Unidade):
        unidade = objeto
    elif isinstance(objeto, Curso):
        unidade = objeto.unidade
    elif isinstance(objeto, Ciclo):
        unidade = objeto.curso.unidade
    elif isinstance(objeto, Matricula):
        unidade = objeto.ciclo.curso.unidade

    configuracao = Configuracao.objects.order_by('id').last()

    if isinstance(objeto, Curso):
        if qs.model == Curso:
            qs = qs.filter(pk=objeto.pk)
        elif qs.model == Ciclo:
            qs = qs.filter(curso=objeto)
        elif qs.model == Matricula:
            qs = qs.filter(ciclo__curso=objeto)
        else:
            qs = qs.none()
    elif isinstance(objeto, Ciclo):
        if qs.model == Ciclo:
            qs = qs.filter(pk=objeto.pk)
        elif qs.model == Matricula:
            qs = qs.filter(ciclo=objeto)
        else:
            qs = qs.none()
    elif isinstance(objeto, Matricula):
        if qs.model == Matricula:
            qs = qs.filter(pk=objeto.pk)
        else:
            qs = qs.none()

    # INCONSISTÊNCIAS DE CURSO
    # REGRA 1 - ASSOCIAÇÃO AO CATÁLOGO
    if tipo.id == TipoInconsistencia.ASSOCIACAO_CATALOGO:
        qs = Curso.objects.filter(ativo=True, excluido=False)
        qs = qs.filter(unidade=unidade) if unidade else qs
        for curso in qs:
            situacao = SituacaoInconsistencia.INCONSISTENTE_RA if curso.curso_catalogo is None else SituacaoInconsistencia.ALTERADO_RA
            Inconsistencia.objects.get_or_create(
                tipo=tipo, curso=curso, configuracao=configuracao,
                defaults=dict(unidade=curso.unidade, situacao_id=situacao,
                              alteracao_anterior=curso.curso_catalogo is not None)
            )
    # REGRA 2 - NOME DE CURSO IMPRÓPRIO
    elif tipo.id == TipoInconsistencia.NOMENCLATURA_CURSO:
        qs = Curso.objects.filter(ativo=True, excluido=False)
        qs = qs.filter(unidade=unidade) if unidade else qs
        for curso in qs:
            if not curso.possui_nomenclatura_correta():
                Inconsistencia.objects.get_or_create(
                    curso=curso, tipo=tipo, configuracao=configuracao,
                    defaults=dict(unidade=curso.unidade,
                                  situacao_id=SituacaoInconsistencia.ALTERADO_RA if curso.justificativa_nome else SituacaoInconsistencia.INCONSISTENTE_RA,
                                  alteracao_anterior=curso.justificativa_nome is not None)
                )
    # INCONSISTÊNCIAS DE CICLO
    # REGRA 3 - EVASÃO 0%
    elif tipo.id == TipoInconsistencia.EVASAO_ZERO:
        segundo_semestre = date(configuracao.ano - 1, 7, 1)
        qs_ids = Ciclo.objects.filter(ativo=True, excluido=False, curso__unidade=unidade).exclude(
            matricula__situacao__in=SituacaoMatricula.SITUACOES_EVASAO
        )
        qs_ids = qs_ids.exclude(curso__tipo_id=TipoCurso.FIC).filter(
            data_inicio__lt=segundo_semestre) | qs_ids.filter(curso__tipo_id=TipoCurso.FIC)
        qs = Ciclo.objects.filter(id__in=qs_ids.values_list('id').order_by('id').distinct())
        qs = qs.filter(curso__unidade=unidade) if unidade else qs
        for ciclo in qs:
            Inconsistencia.objects.get_or_create(
                ciclo=ciclo, tipo=tipo, configuracao=configuracao,
                defaults=dict(unidade=ciclo.curso.unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # REGRA 4 - CH INSUFICIENTE
    elif tipo.id == TipoInconsistencia.CARGA_HORARIA_INSUFICIENTE:
        qs = Ciclo.objects.filter(ativo=True, excluido=False).filter(carga_horaria__lt=20)
        qs = qs.filter(curso__unidade=unidade) if unidade else qs
        for ciclo in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, ciclo=ciclo, tipo=tipo,
                defaults=dict(unidade=ciclo.curso.unidade,
                              situacao_id=SituacaoInconsistencia.ALTERADO_RA if ciclo.justificativa_carga_horaria else SituacaoInconsistencia.INCONSISTENTE_RA,
                              alteracao_anterior=ciclo.justificativa_carga_horaria is not None),
            )
    # REGRA 5 - PROGRAMAS ASSOCIADOS
    elif tipo.id == TipoInconsistencia.PROGRAMAS_ASSOCIADOS:
        qs = Ciclo.objects.filter(ativo=True, excluido=False)
        qs = qs.filter(curso__unidade=unidade) if unidade else qs
        for ciclo in qs:
            situacao = SituacaoInconsistencia.INCONSISTENTE_RA if ciclo.programa is None else SituacaoInconsistencia.ALTERADO_RA
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, ciclo=ciclo, tipo=tipo,
                defaults=dict(unidade=ciclo.curso.unidade, situacao_id=situacao,
                              alteracao_anterior=ciclo.programa is not None)
            )
    # REGRA 6 - DURANÇA DE CICLO IMPRÓPRIA
    elif tipo.id == TipoInconsistencia.DURACAO_CICLO:
        qs = Ciclo.objects.filter(ativo=True, excluido=False).annotate(
            days=(ExtractDay(F('data_fim') - F('data_inicio')) + 1))
        qs = qs.filter(days__lt=F('curso__tipo__duracao_minima')) | qs.filter(days__gt=F('curso__tipo__duracao_maxima'))
        qs = qs.filter(curso__unidade=unidade) if unidade else qs
        for ciclo in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, ciclo=ciclo, tipo=tipo,
                defaults=dict(unidade=ciclo.curso.unidade,
                              situacao_id=SituacaoInconsistencia.ALTERADO_RA if ciclo.justificativa_duracao_impropria else SituacaoInconsistencia.INCONSISTENTE_RA,
                              alteracao_anterior=ciclo.justificativa_duracao_impropria is not None),
            )
    # REGRA 7 - NÚMERO DE VAGAS
    elif tipo.id == TipoInconsistencia.NUMERO_VAGAS:
        qs = Ciclo.objects.filter(ativo=True, excluido=False, data_inicio__gte=date(configuracao.ano - 1, 1, 1)).all()
        qs = qs.filter(curso__unidade=unidade) if unidade else qs
        for ciclo in qs:
            vagas = ciclo.vagasciclo_set.first()
            if vagas is None:
                vagas = VagasCiclo.objects.create(ciclo=ciclo)
            Inconsistencia.objects.get_or_create(
                ciclo=ciclo, tipo=tipo, configuracao=configuracao,
                defaults=dict(unidade=ciclo.curso.unidade,
                              situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA if vagas.get_total() < ciclo.vagas else SituacaoInconsistencia.ALTERADO_RA)
            )
    # Regra 8 - INGRESSANTE MAIOR QUE INSCRITO
    elif tipo.id == TipoInconsistencia.INGRESSANTES_MAIOR_INSCRITOS:
        qs = Ciclo.objects.filter(ativo=True, excluido=False).filter(ingressantes__gt=F('inscritos'))
        qs = qs.filter(curso__unidade=unidade) if unidade else qs
        for ciclo in qs:
            Inconsistencia.objects.get_or_create(
                ciclo=ciclo, tipo=tipo, configuracao=configuracao,
                defaults=dict(unidade=ciclo.curso.unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # REGRA 9 - TURNO - CICLO
    elif tipo.id == TipoInconsistencia.TURNO_OFERTA_CICLO:
        qs = Ciclo.objects.filter(ativo=True, excluido=False).exclude(curso__modalidade_id=Modalidade.EAD)
        qs = qs.filter(curso__unidade=unidade) if unidade else qs
        for ciclo in qs:
            situacao = SituacaoInconsistencia.ALTERADO_RA if ciclo.turnos.exists() else SituacaoInconsistencia.INCONSISTENTE_RA
            Inconsistencia.objects.get_or_create(
                ciclo=ciclo, tipo=tipo, configuracao=configuracao,
                defaults=dict(unidade=ciclo.curso.unidade, situacao_id=situacao,
                              alteracao_anterior=ciclo.turnos.exists())
            )
    # INCONSISTÊNCIAS DE MATRÍCULA
    # REGRA 10 - MATRICULA ANTERIOR
    elif tipo.id == TipoInconsistencia.MATRICULA_ANTERIOR:
        qs = Matricula.objects.filter(atendida=True, excluido=False, ciclo__excluido=False,
                                      ciclo__curso__excluido=False)
        qs = qs.filter(ciclo__curso__unidade=unidade) if unidade else qs
        qs = qs.filter(data_matricula__year__lt=F('ciclo__data_inicio__year')) | \
             qs.filter(data_matricula__year=F('ciclo__data_inicio__year'),
                       data_matricula__month__lt=F('ciclo__data_inicio__month'))
        for matricula in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, matricula=matricula, tipo=tipo,
                defaults=dict(unidade=matricula.ciclo.curso.unidade,
                              situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA),
            )
    # REGRA 11 - MATRICULA POSTERIOR
    elif tipo.id == TipoInconsistencia.MATRICULA_POSTERIOR:
        qs = Matricula.objects.filter(atendida=True, excluido=False, ciclo__excluido=False,
                                      ciclo__curso__excluido=False).filter(data_matricula__gt=F('data_ocorrencia'))
        qs = qs.filter(ciclo__curso__unidade=unidade) if unidade else qs
        for matricula in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, matricula=matricula, tipo=tipo,
                defaults=dict(unidade=matricula.ciclo.curso.unidade,
                              situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 12
    elif tipo.id == TipoInconsistencia.ALUNO_DUPLICADO:
        qs = Matricula.objects.filter(atendida=True, excluido=False, ciclo__excluido=False,
                                      ciclo__curso__excluido=False).exclude(
            situacao_id=SituacaoMatricula.EXCLUIDO).annotate(
            aluno_ciclo=Concat('aluno_id', Value('_'), 'ciclo_id', output_field=CharField())
        ).values('aluno_ciclo').annotate(qtd=Count('aluno_ciclo')).filter(qtd__gt=1)
        qs = qs.filter(ciclo__curso__unidade=unidade) if unidade else qs
        for registro in qs:
            aluno_id, ciclo_id = registro['aluno_ciclo'].split('_')
            for matricula in Matricula.objects.filter(aluno_id=aluno_id, ciclo_id=ciclo_id):
                Inconsistencia.objects.get_or_create(
                    configuracao=configuracao, matricula=matricula, tipo=tipo,
                    defaults=dict(unidade=matricula.ciclo.curso.unidade,
                                  situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
                )
    # Regra 13
    elif tipo.id == TipoInconsistencia.RETENCAO_CRITICA:
        data_fim = configuracao.data_fim
        qs = Matricula.objects.filter(atendida=True, excluido=False, ciclo__excluido=False,
                                      ciclo__curso__excluido=False).filter(
            situacao_id=SituacaoMatricula.EM_CURSO).exclude(
            ciclo__curso__tipo_id=TipoCurso.FIC
        )
        qs = qs.filter(ciclo__data_fim__lte=date(data_fim.year-1, data_fim.month, data_fim.day))
        qs = qs.filter(ciclo__curso__unidade=unidade) if unidade else qs
        for matricula in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, matricula=matricula, tipo=tipo,
                defaults=dict(unidade=matricula.ciclo.curso.unidade,
                              situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 14
    elif tipo.id == TipoInconsistencia.RETENCAO_FIC:
        data_fim = configuracao.data_fim
        qs = Matricula.objects.filter(atendida=True, excluido=False, ciclo__excluido=False,
                                      ciclo__curso__excluido=False).filter(
            situacao_id=SituacaoMatricula.EM_CURSO, ciclo__curso__tipo_id=TipoCurso.FIC
        )
        qs = qs.filter(ciclo__data_fim__lt=data_fim)
        qs = qs.filter(ciclo__curso__unidade=unidade) if unidade else qs
        for matricula in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, matricula=matricula, tipo=tipo,
                defaults=dict(unidade=matricula.ciclo.curso.unidade,
                              situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 15
    elif tipo.id == TipoInconsistencia.COR_RACA:
        bulk = []
        qs = Matricula.objects.filter(atendida=True, excluido=False, ciclo__excluido=False,
                                      ciclo__curso__excluido=False)
        qs = qs.filter(ciclo__curso__unidade=unidade) if unidade else qs
        for matricula in qs:
            curso = matricula.ciclo.curso
            situacao = SituacaoInconsistencia.INCONSISTENTE_RA if matricula.aluno.raca_id is None else SituacaoInconsistencia.ALTERADO_RA
            if inicial:
                bulk.append(
                    Inconsistencia(configuracao=configuracao, matricula=matricula, tipo=tipo, unidade=curso.unidade,
                                   situacao_id=situacao, alteracao_anterior=matricula.aluno.raca_id is not None))
            else:
                Inconsistencia.objects.get_or_create(
                    configuracao=configuracao, matricula=matricula, tipo=tipo,
                    defaults=dict(unidade=curso.unidade, situacao_id=situacao,
                                  alteracao_anterior=matricula.aluno.raca_id is not None)
                )
        if bulk: Inconsistencia.objects.bulk_create(bulk)
    # Regra 16
    elif tipo.id == TipoInconsistencia.RENDA:
        bulk = []
        qs = Matricula.objects.filter(atendida=True, excluido=False, ciclo__excluido=False,
                                      ciclo__curso__excluido=False)
        qs = qs.filter(ciclo__curso__unidade=unidade) if unidade else qs
        for matricula in qs:
            curso = matricula.ciclo.curso
            situacao = SituacaoInconsistencia.INCONSISTENTE_RA if matricula.aluno.renda_per_capita_id is None else SituacaoInconsistencia.ALTERADO_RA
            if inicial:
                bulk.append(
                    Inconsistencia(configuracao=configuracao, matricula=matricula, tipo=tipo, unidade=curso.unidade,
                                   situacao_id=situacao,
                                   alteracao_anterior=matricula.aluno.renda_per_capita_id is not None))
            else:
                Inconsistencia.objects.get_or_create(
                    configuracao=configuracao, matricula=matricula, tipo=tipo,
                    defaults=dict(unidade=curso.unidade, situacao_id=situacao,
                                  alteracao_anterior=matricula.aluno.renda_per_capita_id is not None)
                )
        if bulk: Inconsistencia.objects.bulk_create(bulk)
    # Regra 17
    elif tipo.id == TipoInconsistencia.TURNO_ALUNO:
        bulk = []
        qs = Matricula.objects.filter(atendida=True, excluido=False, ciclo__excluido=False,
                                      ciclo__curso__excluido=False).exclude(ciclo__curso__modalidade_id=Modalidade.EAD)
        qs = qs.filter(ciclo__curso__unidade=unidade) if unidade else qs
        turnos_ciclos = {}
        for ciclo in Ciclo.objects.filter(pk__in=qs.values_list('ciclo', flat=True).distinct()):
            turnos_ciclos[ciclo.pk] = ciclo.turnos.values_list('pk', flat=True)
        for matricula in qs:
            ciclo = matricula.ciclo
            curso = ciclo.curso
            situacao = SituacaoInconsistencia.INCONSISTENTE_RA if matricula.turno_id is None or matricula.turno_id not in \
                                                                  turnos_ciclos[
                                                                      ciclo.pk] else SituacaoInconsistencia.ALTERADO_RA
            if inicial:
                bulk.append(
                    Inconsistencia(configuracao=configuracao, matricula=matricula, tipo=tipo, unidade=curso.unidade,
                                   situacao_id=situacao, alteracao_anterior=matricula.turno_id is not None))
            else:
                Inconsistencia.objects.get_or_create(
                    configuracao=configuracao, matricula=matricula, tipo=tipo,
                    defaults=dict(unidade=curso.unidade, situacao_id=situacao,
                                  alteracao_anterior=matricula.turno_id is not None)
                )
        if bulk: Inconsistencia.objects.bulk_create(bulk)
    # Regra 18
    elif tipo.id == TipoInconsistencia.DOCENTE_LOTADO_REITORIA:
        qs = Servidor.objects.filter(lotacao__unidade=unidade, lotacao__unidade__tipo_id=TipoUnidade.REITORIA,
                                     cargo__grupo__categoria='D')
        for servidor in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, tipo=tipo, servidor=servidor,
                defaults=dict(unidade=unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 19
    elif tipo.id == TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_TITULACAO:
        qs = Servidor.objects.filter(lotacao__unidade=unidade, titulacao__nivel_ensino__isnull=False,
                                     escolaridade__nivel_ensino__isnull=False)
        qs = qs.exclude(titulacao__nivel_ensino__lte=F('escolaridade__nivel_ensino'))
        for servidor in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, tipo=tipo, servidor=servidor,
                defaults=dict(unidade=unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 20
    elif tipo.id == TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_CARGO:
        qs = Servidor.objects.filter(lotacao__unidade=unidade, cargo__nivel_ensino__isnull=False,
                                     escolaridade__nivel_ensino__isnull=False)
        qs = qs.exclude(cargo__nivel_ensino__lte=F('escolaridade__nivel_ensino'))
        for servidor in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, tipo=tipo, servidor=servidor,
                defaults=dict(unidade=unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 21
    elif tipo.id == TipoInconsistencia.TITULACAO_NAO_INFORMADA:
        qs = Servidor.objects.filter(lotacao__unidade=unidade, titulacao__isnull=True)
        for servidor in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, tipo=tipo, servidor=servidor,
                defaults=dict(unidade=unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 22
    elif tipo.id == TipoInconsistencia.ESCOLARIDADE_NAO_INFORMADA:
        qs = Servidor.objects.filter(lotacao__unidade=unidade, escolaridade__isnull=True)
        for servidor in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, tipo=tipo, servidor=servidor,
                defaults=dict(unidade=unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 23
    elif tipo.id == TipoInconsistencia.CARGO_SEM_DESCRICAO:
        qs = Servidor.objects.filter(lotacao__unidade=unidade)
        qs = qs.filter(cargo__nome='') | qs.filter(cargo__nome__isnull=True)
        for servidor in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, tipo=tipo, servidor=servidor,
                defaults=dict(unidade=unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 24
    elif tipo.id == TipoInconsistencia.DUPLICIDADE_LOTACAO:
        cpfs = [v['cpf'] for v in
                Servidor.objects.values('cpf').annotate(Count('id')).order_by().filter(id__count__gt=1)]
        qs = Servidor.objects.filter(lotacao__unidade=unidade).filter(cpf__in=cpfs)
        for servidor in qs:
            Inconsistencia.objects.get_or_create(
                configuracao=configuracao, tipo=tipo, servidor=servidor,
                defaults=dict(unidade=unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
            )
    # Regra 25
    elif tipo.id == TipoInconsistencia.UORG_NAO_VINCULADA:
        for uo in UnidadeOrganizacional.objects.filter(unidade__isnull=True):
            for instituicao in Instituicao.objects.filter(codigo__startswith=uo.codigo[0:5]):
                unidade = instituicao.unidade_set.filter(
                    tipo_id=TipoUnidade.REITORIA
                ).order_by('id').first() or instituicao.unidade_set.first()
                Inconsistencia.objects.get_or_create(
                    configuracao=configuracao, tipo=tipo, unidadeorganizacional=uo,
                    defaults=dict(unidade=unidade, situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA)
                )
    # atualizando a situação dos objetos
    if tipo.id < TipoInconsistencia.EVASAO_ZERO:
        objetos = Curso.objects.filter(unidade=unidade, inconsistencia__curso__isnull=False)
    elif tipo.id < TipoInconsistencia.MATRICULA_ANTERIOR:
        objetos = Ciclo.objects.filter(curso__unidade=unidade, inconsistencia__ciclo__isnull=False)
    elif tipo.id < TipoInconsistencia.DOCENTE_LOTADO_REITORIA:
        objetos = Matricula.objects.filter(ciclo__curso__unidade=unidade, inconsistencia__matricula__isnull=False)
    elif tipo.id < TipoInconsistencia.UORG_NAO_VINCULADA:
        objetos = Servidor.objects.filter(inconsistencia__servidor__isnull=False)
    else:
        objetos = UnidadeOrganizacional.objects.filter(inconsistencia__unidadeorganizacional__isnull=False)
    objetos.exclude(situacao_inconsistencia_id=SituacaoInconsistencia.INCONSISTENTE_RA).filter(
        inconsistencia__situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA).update(
        situacao_inconsistencia=SituacaoInconsistencia.INCONSISTENTE_RA)
    objetos.exclude(situacao_inconsistencia_id=SituacaoInconsistencia.ALTERADO_RA).exclude(
        inconsistencia__situacao_id=SituacaoInconsistencia.INCONSISTENTE_RA).filter(
        inconsistencia__situacao_id=SituacaoInconsistencia.ALTERADO_RA).update(
        situacao_inconsistencia=SituacaoInconsistencia.ALTERADO_RA)
