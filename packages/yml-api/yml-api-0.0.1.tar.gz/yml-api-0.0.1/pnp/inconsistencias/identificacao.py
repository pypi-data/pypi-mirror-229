from . import carga
from django.db.models import Count
from ..models import Configuracao, Ciclo, Matricula, HistoricoSincronizacaoSistec, Curso, SituacaoMatricula


def identificar_registros_ativos(unidade):
    mensagem = []
    configuracao = Configuracao.objects.order_by('id').last()
    arquivo = configuracao.arquivo_set.get(unidade=unidade)
    ano = configuracao.ano - 1
    for i in range(0, 9):
        if i == 0:
            ciclos_ativos = list(
                Ciclo.objects.filter(
                    curso__unidade=unidade, excluido=False
                ).values_list('codigo', flat=True)
            )
            matriculas_ativas = list(
                Matricula.objects.filter(
                    ciclo__curso__unidade=unidade, excluido=False
                ).values_list('codigo', flat=True)
            )
            for linha_arquivo in arquivo.linhaarquivo_set.all():
                carga.identifica_registro_excluidos(linha_arquivo, ciclos_ativos, matriculas_ativas)
            total_ciclo = Ciclo.objects.filter(codigo__in=ciclos_ativos).update(excluido=True)
            total_matricula = Matricula.objects.filter(codigo__in=matriculas_ativas).update(excluido=True)
            mensagem.append('Ciclos excluídos ({}), '.format(total_ciclo))
            mensagem.append('Matrículas excluídas ({}), '.format(total_matricula))
            for codigo in ciclos_ativos:
                historico = f'MARCANDO exclusão DO DICLO {codigo}'
                HistoricoSincronizacaoSistec.objects.create(historico=historico)
            for codigo in matriculas_ativas:
                historico = f'MARCANDO exclusão DA MATRÍCULA {codigo}'
                HistoricoSincronizacaoSistec.objects.create(historico=historico)
        elif i == 1:
            Curso.objects.filter(unidade=unidade).filter(ativo=True).update(ativo=False)
        elif i == 2:
            Ciclo.objects.filter(curso__unidade=unidade).filter(ativo=True).update(ativo=False)
        elif i == 3:
            matriculas = Matricula.objects.filter(ciclo__curso__unidade=unidade)
            matriculas.filter(atendida=True).update(atendida=False)
            matriculas.filter(ingressante=True).update(ingressante=False)
        elif i == 4:
            # Matrículas atendidas
            matriculas_atendidas = Matricula.objects.atendidas(ano).filter(ciclo__curso__unidade=unidade)
            total = matriculas_atendidas.update(atendida=True)
            mensagem.append('Matrículas atendidas ({}), '.format(total))
        elif i == 5:
            # Ingressantes
            ingressantes = Matricula.objects.ingressantes(ano).filter(ciclo__curso__unidade=unidade)
            total = ingressantes.update(ingressante=True)
            mensagem.append('ingressantes ({}), '.format(total))
        elif i == 6:
            # Ciclos ativos
            pks = matriculas_atendidas.order_by('ciclo_id').values_list('ciclo_id', flat=True).distinct()
            total = Ciclo.objects.filter(pk__in=pks).update(ativo=True)
            mensagem.append('ciclos ({}) e '.format(total))
        elif i == 7:
            # Cursos ativos
            pks = Ciclo.objects.filter(curso__unidade=unidade, ativo=True).order_by('curso').values_list(
                'curso', flat=True).distinct()
            total = Curso.objects.filter(pk__in=pks).update(ativo=True)
            mensagem.append('cursos ({}).'.format(total))
        elif i == 8:
            for pk, n in Ciclo.objects.filter(curso__unidade=unidade, ativo=True).filter(
                    matricula__ingressante=True).exclude(
                    matricula__situacao__in=[SituacaoMatricula.SUBSTITUIDO, SituacaoMatricula.EXCLUIDO]).annotate(
                    n=Count('matricula')).values_list('pk', 'n'):
                Ciclo.objects.filter(pk=pk).update(ingressantes=n)
            for pk, n in Ciclo.objects.filter(curso__unidade=unidade, ativo=True).filter(
                    matricula__situacao__in=SituacaoMatricula.SITUACOES_EVASAO).annotate(
                    n=Count('matricula')).values_list('pk', 'n'):
                Ciclo.objects.filter(pk=pk).update(evadidos=n)
    arquivo.registros_ativos_identificados = True
    arquivo.save()
    return '\n'.join(mensagem)
