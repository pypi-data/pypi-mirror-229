import csv
import tempfile
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from api import actions

from pnp.models import CursoCatalogo, Alteracao, TipoInconsistencia, Configuracao, TipoCurso, \
    Programa, Eixo, SituacaoMatricula, Turno, Raca, Unidade, Instituicao, FaixaRenda, \
    Inconsistencia, VagasCiclo, Justificativa, RegraAssociacaoPrograma, \
    CargoEmprego, Titulacao, Escolaridade, Papel


class AlterarInconsistencia(actions.Action):
    acao = serializers.ChoiceField(choices=[['corrigir', 'Corrigir']])

    def load(self):
        referencia = self.source.get_referencia()
        self.fieldsets = {'Ação': ['acao']}
        if self.source.pode_ser_resolvida(self.request):
            # INCONSISTÊNCIAS DE CURSO
            # REGRA 1 - ASSOCIAÇÃO AO CATÁLOGO
            if self.source.tipo_id == TipoInconsistencia.ASSOCIACAO_CATALOGO:
                self.set_acoes('corrigir', 'excluir')
                self.fields['nome_curso'] = actions.CharField(
                    label='Nome do Curso', read_only=True, initial=referencia.nome
                )
                self.fields['filtrar_por_eixo'] = actions.BooleanField(label='Filtrar por Eixo Tecnológico',
                                                                       required=False)
                self.fields['eixo'] = actions.RelatedField(
                    queryset=Eixo.objects.all(), label='Eixo', required=False, initial=referencia.curso_catalogo_id
                )
                self.fields['curso_catalogo'] = actions.RelatedField(
                    queryset=CursoCatalogo.objects.all(), label='Curso', required=False,
                    initial=referencia.curso_catalogo_id,
                    help_text='ATENÇÃO: Filtrar por eixo tecnológico caso nenhuma sugestão seja adequada ou nenhum resultado for encontrado'
                )
                self.fieldsets['Correção'] = 'nome_curso', 'filtrar_por_eixo', 'eixo', 'curso_catalogo',
                self.fields['acao'].initial = 'corrigir'
            # REGRA 2 - NOME DE CURSO IMPRÓPRIO
            elif self.source.tipo_id == TipoInconsistencia.NOMENCLATURA_CURSO:
                self.set_acoes('justificar', 'excluir')
                self.fields['nome_curso'] = actions.CharField(
                    label='Nome do Curso', read_only=True, initial=referencia.nome
                )
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo), label='Justificativa',
                    required=False, initial=referencia.justificativa_nome_id
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Justificativa'] = 'nome_curso', 'justificativa',
                self.fields['acao'].initial = 'justificar'
            # INCONSISTÊNCIAS DE CICLO
            # REGRA 3 - EVASÃO 0%
            elif self.source.tipo_id == TipoInconsistencia.EVASAO_ZERO:
                self.set_acoes('corrigir', 'justificar')
                campos_correcao = []
                for i in range(0, 10):
                    campo_matricula = 'matricula_aluno_{}'.format(i)
                    self.fields[campo_matricula] = actions.RelatedField(
                        queryset=referencia.matricula_set.all(), label='Matrícula' if i == 0 else '', required=False
                    )
                    campo_situacao = 'st_{}'.format(i)
                    self.fields[campo_situacao] = actions.RelatedField(
                        queryset=SituacaoMatricula.objects.filter(pk__in=SituacaoMatricula.SITUACOES_EVASAO),
                        label='Situação' if i == 0 else '', required=False
                    )
                    campo_data_ocorrencia = 'dt_{}'.format(i)
                    self.fields[campo_data_ocorrencia] = actions.DateField(
                        label='Data' if i == 0 else '', required=False
                    )
                    campos_correcao.append((campo_matricula, campo_situacao, campo_data_ocorrencia))
                self.fieldsets['Correção'] = campos_correcao
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo), label='',
                    required=False,
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Justificativa'] = 'justificativa',
                self.fields['acao'].initial = 'corrigir'
            # REGRA 4 - CH INSUFICIENTE
            elif self.source.tipo_id == TipoInconsistencia.CARGA_HORARIA_INSUFICIENTE:
                self.set_acoes('corrigir', 'justificar', 'excluir')
                self.fields['carga_horaria'] = actions.IntegerField(
                    label='Carga-Horária', required=True, initial=referencia.carga_horaria
                )
                self.fieldsets['Correção'] = 'carga_horaria',
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo), label='',
                    required=False,
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Justificativa'] = 'justificativa',
                self.fields['acao'].initial = 'corrigir'
            # REGRA 5 - PROGRAMAS ASSOCIADOS
            elif self.source.tipo_id == TipoInconsistencia.PROGRAMAS_ASSOCIADOS:
                self.set_acoes('corrigir')
                pks = RegraAssociacaoPrograma.objects.filter(
                    tipos_curso=referencia.curso.tipo,
                    modalidade=referencia.curso.modalidade
                ).values_list('programas')
                self.fields['programa'] = actions.RelatedField(
                    queryset=Programa.objects.filter(pk__in=pks), label='Programa', required=True, initial=referencia.programa,
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Correção'] = 'programa',
                self.fields['acao'].initial = 'corrigir'
            # REGRA 6 - DURANÇA DE CICLO IMPRÓPRIA
            elif self.source.tipo_id == TipoInconsistencia.DURACAO_CICLO:
                self.set_acoes('corrigir', 'justificar')
                self.fields['data_inicio'] = actions.DateField(
                    label='Data de Início', required=True, initial=referencia.data_inicio
                )
                self.fields['data_fim'] = actions.DateField(
                    label='Data de Fim', required=True, initial=referencia.data_fim
                )
                self.fieldsets['Correção'] = ('data_inicio', 'data_fim',),
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo), label='',
                    required=False,
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Justificativa'] = 'justificativa',
                self.fields['acao'].initial = 'corrigir'
            # REGRA 47 - NÚMERO DE VAGAS
            elif self.source.tipo_id == TipoInconsistencia.NUMERO_VAGAS:
                self.set_acoes('corrigir')
                campos_correcao = []
                ciclo = self.source.get_referencia()
                vagas_ciclo = VagasCiclo.objects.filter(ciclo=ciclo).first() or VagasCiclo()
                self.fields['vagas'] = actions.CharField(
                    label='Número de Vagas Atual', read_only=True, initial=ciclo.vagas
                )
                self.fields['ingressantes'] = actions.CharField(
                    label='Número de Ingressantes', read_only=True,
                    initial=ciclo.ingressantes
                )
                campos_correcao.append(('vagas', 'ingressantes'))
                for i, tipo in enumerate(('ac', 'l1', 'l2', 'l5', 'l6', 'l9', 'l10', 'l13', 'l14')):
                    regular = 'vagas_regulares_{}'.format(tipo)
                    extra = 'vagas_extras_{}'.format(tipo)
                    self.fields[tipo] = actions.CharField(
                        label='Tipo de Vaga' if i == 0 else '', read_only=True, initial=tipo.upper()
                    )
                    self.fields[regular] = actions.IntegerField(
                        label='Vagas Regulares' if i == 0 else '', initial=getattr(vagas_ciclo, regular), required=tipo=='ac'
                    )
                    self.fields[extra] = actions.IntegerField(
                        label='Vagas Extraordinárias' if i == 0 else '', initial=getattr(vagas_ciclo, extra),
                        required=False
                    )
                    campos_correcao.append((tipo, regular, extra))
                self.fieldsets['Correção'] = campos_correcao
                if 1 or ciclo.ingressantes > ciclo.vagas:
                    self.fields['matriculas_excluidas'] = actions.RelatedField(
                        queryset=ciclo.matricula_set.all(), many=True, label='Matrículas Excluídas', required=False,
                    )
                    self.fields['matriculas_excluidas'].initial = ciclo.matricula_set.filter(
                        situacao=SituacaoMatricula.EXCLUIDO)
                    self.fields['matriculas_substituidas'] = actions.RelatedField(
                        queryset=ciclo.matricula_set.all(), many=True, label='Matrículas Substituídas', required=False
                    )
                    self.fields['matriculas_substituidas'].initial = ciclo.matricula_set.filter(
                        situacao=SituacaoMatricula.SUBSTITUIDO)
                    self.fieldsets['Matrículas'] = 'matriculas_excluidas', 'matriculas_substituidas'
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.INGRESSANTES_MAIOR_INSCRITOS:
                ciclo = self.source.get_referencia()
                self.set_acoes('corrigir')
                self.fields['ingressantes'] = actions.IntegerField(
                    label='Ingressantes', read_only=True, initial=ciclo.ingressantes
                )
                self.fields['inscritos'] = actions.IntegerField(
                    label='Inscritos', required=True, initial=ciclo.inscritos
                )
                self.fieldsets['Correção'] = (('ingressantes', 'inscritos'),)
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.TURNO_OFERTA_CICLO:
                # REGRA 9 - TURNO - CICLO
                self.set_acoes('corrigir')
                turnos = referencia.turnos.values_list('id', flat=True)
                self.fields['turnos'] = actions.RelatedField(
                    queryset=Turno.objects.all(), many=True, label='Turno(s)', required=True,
                    ### widget=actions.CheckboxSelectMultiple,
                    initial=[pk for pk in referencia.turnos.values_list('id', flat=True)]
                )
                self.fieldsets['Correção'] = ('turnos',)
                self.fields['acao'].initial = 'corrigir'
            # INCONSISTÊNCIAS DE MATRÍCULA
            elif self.source.tipo_id == TipoInconsistencia.MATRICULA_ANTERIOR:
                # REGRA 10 - MATRICULA ANTERIOR
                self.set_acoes('corrigir', 'excluir')
                matricula = self.source.get_referencia()
                self.fields['data_inicio'] = actions.DateField(
                    label='Data de Início do Ciclo', read_only=True, initial=matricula.ciclo.data_inicio
                )
                self.fields['data_matricula'] = actions.DateField(
                    label='Data da Matrícula', required=True, initial=matricula.data_matricula
                )
                self.fields['situacao_matricula'] = actions.CharField(
                    label='Situação da Matrícula', read_only=True, initial=str(matricula.situacao)
                )
                self.fields['data_ocorrencia'] = actions.DateField(
                    label='Data da Ocorrência', required=True, initial=matricula.data_ocorrencia
                )
                self.fieldsets['Correção'] = ('data_inicio', 'data_matricula'), (
                'situacao_matricula', 'data_ocorrencia'),
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.MATRICULA_POSTERIOR:
                # REGRA 11 - MATRICULA POSTERIOR
                self.set_acoes('corrigir')
                matricula = self.source.get_referencia()
                self.fields['data_matricula'] = actions.DateField(
                    label='Data da Matrícula', required=True, initial=matricula.data_matricula
                )
                self.fields['data_ocorrencia'] = actions.DateField(
                    label='Data de Ocorrência', required=True, initial=matricula.data_ocorrencia
                )
                self.fieldsets['Correção'] = ('data_matricula', 'data_ocorrencia'),
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.ALUNO_DUPLICADO:
                # REGRA 12 - Aluno Duplicado
                self.set_acoes('excluir')
            elif self.source.tipo_id == TipoInconsistencia.RETENCAO_CRITICA:
                # REGRA 13 - Retenção Critica
                self.set_acoes('corrigir', 'justificar')
                matricula = self.source.get_referencia()
                self.fields['data_inicio'] = actions.DateField(
                    label='Data de Início do Ciclo', read_only=True, initial=matricula.ciclo.data_inicio
                )
                self.fields['data_fim'] = actions.DateField(
                    label='Data de Fim do Ciclo', read_only=True, initial=matricula.ciclo.data_fim
                )
                self.fields['situacao'] = actions.RelatedField(
                    queryset=SituacaoMatricula.objects.exclude(nome="Não Declarada"), label='Situação da Matrícula',
                    required=True, initial=matricula.situacao_id
                )
                self.initial['situacao'] = matricula.situacao_id
                self.fields['data_ocorrencia'] = actions.DateField(
                    label='Data de Ocorrência', required=True, initial=matricula.data_ocorrencia
                )
                self.fieldsets['Correção'] = ('data_inicio', 'data_fim'), ('situacao', 'data_ocorrencia')
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo), label='',
                    required=False,
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Justificativa'] = 'justificativa',
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.RETENCAO_FIC:
                # REGRA 14
                self.set_acoes('corrigir', 'justificar')
                matricula = self.source.get_referencia()
                self.fields['data_inicio'] = actions.DateField(
                    label='Data de Início do Ciclo', read_only=True, initial=matricula.ciclo.data_inicio
                )
                self.fields['data_fim'] = actions.DateField(
                    label='Data de Fim do Ciclo', read_only=True, initial=matricula.ciclo.data_fim
                )
                self.fields['situacao'] = actions.RelatedField(
                    queryset=SituacaoMatricula.objects.exclude(nome="Não Declarada"), label='Situação da Matrícula',
                    required=True, initial=matricula.situacao_id
                )
                self.fields['data_ocorrencia'] = actions.DateField(
                    label='Data de Ocorrência', required=True, initial=matricula.data_ocorrencia
                )
                self.fieldsets['Correção'] = ('data_inicio', 'data_fim'), ('situacao', 'data_ocorrencia')
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo), label='',
                    required=False,
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Justificativa'] = 'justificativa',
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.COR_RACA:
                # REGRA 15
                self.set_acoes('corrigir')
                aluno = referencia.aluno
                self.fields['raca'] = actions.RelatedField(
                    queryset=Raca.objects, label='Cor/Raça',
                    required=False, initial=aluno.raca_id,
                    ### widget=actions.RadioSelect()
                )
                self.fields['arquivo'] = actions.FileField(
                    label='Informar Raça em Lote', required=False,
                    help_text='Para baixar o arquivo com os CPFs dos alunos <a href="?arquivo=raca">clique aqui</a>.<br><b>IMPORTANTE</b>: <span style="color:green">Para facilitar a importação, serão aceitas variações entre letras maiúsculas e minúsculas, incluindo com ou sem acentos</span>. Ex: Branco, Branca, BRANCO, Indígena, INDIGENA, indigena, Não declarado, Não-declarado, NÃO DECLARADO, etc.<br>Exemplo do arquivo depois de preenchido: <img width="200" src="/static/images/raca.png"/>.'
                )
                self.fieldsets['Correção'] = ('raca', 'arquivo')
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.RENDA:
                # REGRA 16
                self.set_acoes('corrigir')
                aluno = referencia.aluno
                self.fields['renda_per_capita'] = actions.RelatedField(
                    queryset=FaixaRenda.objects, label='Renda Per Capta', required=False, initial=aluno.renda_per_capita_id,
                    ### widget=actions.RadioSelect()
                )
                self.fields['arquivo'] = actions.FileField(
                    label='Informar Renda Per Capta em Lote', required=False,
                    help_text='Para baixar o arquivo com os CPFs dos alunos <a href="?arquivo=renda_per_capita">clique aqui</a>.<br>Exemplo do arquivo depois de preenchido: <img width="200" src="/static/images/renda.png"/>'
                )
                self.fieldsets['Correção'] = ('renda_per_capita', 'arquivo')
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.TURNO_ALUNO:
                # REGRA 17
                self.set_acoes('corrigir')
                matricula = self.source.get_referencia()
                self.fields['turno'] = actions.RelatedField(
                    queryset=matricula.ciclo.turnos.all(), label='Turno',
                    required=False, initial=matricula.turno_id,
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Correção'] = 'turno',
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.DOCENTE_LOTADO_REITORIA:
                # REGRA 18
                self.set_acoes('corrigir', 'justificar')
                self.fields['lotacao'] = actions.RelatedField(
                    queryset=referencia.lotacao.instituicao.unidadeorganizacional_set.all(), label='Lotação',
                    required=False, initial=referencia.lotacao_id
                )
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo),
                    label='Justificativa', required=False,
                    ### widget=actions.RadioSelect()
                )
                self.initial['lotacao'] = referencia.lotacao_id
                self.fieldsets['Correção'] = 'lotacao',
                self.fieldsets['Justificativa'] = 'justificativa',
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_TITULACAO:
                # REGRA 19
                self.set_acoes('corrigir')
                self.fields['escolaridade'] = actions.RelatedField(
                    Escolaridade.objects.all(), label='Escolaridade',
                    required=False, initial=referencia.escolaridade_id
                )
                self.fields['titulacao'] = actions.RelatedField(
                    Titulacao.objects.filter(nivel_ensino__isnull=False), label='Titulação',
                    required=False, initial=referencia.titulacao_id,
                )
                self.initial['escolaridade'] = referencia.escolaridade_id
                self.initial['titulacao'] = referencia.titulacao_id
                self.fieldsets['Correção'] = ('escolaridade', 'titulacao')
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_CARGO:
                # REGRA 20
                self.set_acoes('corrigir', 'justificar')
                self.fields['escolaridade'] = actions.RelatedField(
                    Escolaridade.objects.filter(
                        nivel_ensino_id__gte=referencia.cargo.nivel_ensino_id) | Escolaridade.objects.filter(
                        pk=referencia.escolaridade_id), label='Escolaridade',
                    required=False, initial=referencia.escolaridade_id
                )
                self.fields['cargo'] = actions.RelatedField(
                    CargoEmprego.objects.filter(pk=referencia.cargo_id, ), label='Cargo',
                    required=False, initial=referencia.cargo_id,
                )
                self.fields['nivel_ensino_minimo'] = actions.CharField(
                    label='Nível de Ensino Mínimo',
                    required=False, initial=referencia.cargo.nivel_ensino.nome,
                )
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo),
                    label='Justificativa', required=False,
                    ### widget=actions.RadioSelect()
                )
                self.fields['cargo'].widget.attrs.update(readonly='readonly')
                self.fields['nivel_ensino_minimo'].widget.attrs.update(readonly='readonly')
                self.initial['cargo'] = referencia.cargo_id
                self.initial['escolaridade'] = referencia.escolaridade_id
                self.fieldsets['Correção'] = ('cargo', 'nivel_ensino_minimo'), 'escolaridade'
                self.fieldsets['Justificativa'] = ('justificativa',)
                self.fields['acao'].initial = 'corrigir'

            elif self.source.tipo_id == TipoInconsistencia.TITULACAO_NAO_INFORMADA:
                # REGRA 21
                self.set_acoes('corrigir')
                self.fields['titulacao'] = actions.RelatedField(
                    Titulacao.objects.filter(nivel_ensino__isnull=False,
                                             nivel_ensino_id__lte=referencia.escolaridade.nivel_ensino_id),
                    label='Titulação',
                    required=False, initial=referencia.titulacao_id,
                )
                self.fieldsets['Correção'] = 'titulacao',
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.ESCOLARIDADE_NAO_INFORMADA:
                # REGRA 22
                self.set_acoes('corrigir')
                self.fields['escolaridade'] = actions.RelatedField(
                    Escolaridade.objects.filter(nivel_ensino__isnull=False), label='Escolaridade',
                    required=False, initial=referencia.escolaridade_id,
                )
                self.fieldsets['Correção'] = 'escolaridade',
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.CARGO_SEM_DESCRICAO:
                # REGRA 23
                self.set_acoes('corrigir')
                self.fields['cargo'] = actions.RelatedField(
                    CargoEmprego.objects.all(), label='Cargo',
                    required=True, initial=referencia.cargo_id
                )
                self.fields['descricao'] = actions.CharField(
                    label='Descrição do cargo', required=True,
                )
                self.initial['cargo'] = referencia.cargo_id
                self.fields['cargo'].widget.attrs.update(readonly='readonly')
                self.fieldsets['Correção'] = ('cargo', 'descricao'),
                self.fields['acao'].initial = 'corrigir'
            elif self.source.tipo_id == TipoInconsistencia.DUPLICIDADE_LOTACAO:
                # REGRA 25
                self.set_acoes('justificar', 'excluir')
                self.fields['nome'] = actions.CharField(
                    label='Nome do Servidor', required=True, initial=referencia.nome
                )
                self.fields['nome'].widget.attrs.update(readonly='readonly')
                self.fields['lotacao'] = actions.CharField(
                    label='Lotação', required=True, initial=referencia.lotacao
                )
                self.fields['lotacao'].widget.attrs.update(readonly='readonly')
                self.fields['justificativa'] = actions.RelatedField(
                    queryset=Justificativa.objects.filter(tipo_inconsistencia=self.source.tipo),
                    label='Justificativa', required=False,
                    ### widget=actions.RadioSelect()
                )
                self.fieldsets['Justificativa'] = ('nome', 'lotacao', 'justificativa',)
                self.fields['acao'].initial = 'justificar'
            elif self.source.tipo_id == TipoInconsistencia.UORG_NAO_VINCULADA:
                # REGRA 25
                self.set_acoes('corrigir')
                uo = self.source.get_referencia()
                instituicao = Instituicao.objects.get(pk=self.request.session['role']['scope_id'])
                self.fields['unidade'] = actions.RelatedField(
                    instituicao.unidade_set.all(), label='Unidade',
                    required=True, initial=None
                )
                self.fieldsets['Correção'] = 'unidade',
                self.fields['acao'].initial = 'corrigir'
        else:
            self.set_acoes('restaurar')
            self.fields['acao'].initial = 'restaurar'
            if self.source.tipo_id == TipoInconsistencia.NUMERO_VAGAS:
                campos_correcao = [('acao',)]
                vagas_ciclo = VagasCiclo.objects.filter(ciclo=self.source.ciclo).first() or VagasCiclo()
                if vagas_ciclo:
                    for i, tipo in enumerate(('ac', 'l1', 'l2', 'l5', 'l6', 'l9', 'l10', 'l13', 'l14')):
                        regular = 'vagas_regulares_{}'.format(tipo)
                        extra = 'vagas_extras_{}'.format(tipo)
                        self.fields[tipo] = actions.CharField(label='Tipo de Vaga' if i == 0 else '', required=False, initial=tipo.upper(), read_only=True)
                        valor = getattr(vagas_ciclo, regular)
                        self.fields[regular] = actions.IntegerField(label='Vagas Regulares' if i == 0 else '', initial=valor, read_only=True)
                        valor = getattr(vagas_ciclo, extra)
                        self.fields[extra] = actions.IntegerField(label='Vagas Extraordinárias' if i == 0 else '', initial=valor, required=False, read_only=True)
                        campos_correcao.append((tipo, regular, extra))
                self.fieldsets['Ação'] = campos_correcao

            justificativa_anterior = self.source.get_justificativa()
            if justificativa_anterior:
                self.fields['justificativa_anterior'] = actions.CharField(
                    label='Justifiticativa', initial=justificativa_anterior.justificativa, read_only=True
                )
                self.fieldsets['Ação'].append('justificativa_anterior')
        #
        self.on_acao_change(self.fields['acao'].initial)

    def validate(self, *args, **kwargs):
        validated_data = super().validate(*args, **kwargs)
        referencia = self.source.get_referencia()
        acao = self.get('acao')
        if acao == 'justificar':
            if not self.get('justificativa'):
                raise ValidationError({'justificativa': 'Selecione uma Justificativa.'})
                self.on_acao_change(acao)

        elif self.source.tipo_id == TipoInconsistencia.ASSOCIACAO_CATALOGO:
            if acao == 'corrigir':
                if not self.get('curso_catalogo'):
                    raise ValidationError({'curso_catalogo': 'Selecione um Curso.'})

        elif self.source.tipo_id == TipoInconsistencia.EVASAO_ZERO:
            if acao == 'corrigir':
                evadidos = 0
                for i in range(0, 10):
                    matricula = self.get('matricula_aluno_{}'.format(i))
                    situacao = self.get('st_{}'.format(i))
                    dt = self.get('dt_{}'.format(i))

                    if matricula and situacao and dt and situacao.id in SituacaoMatricula.SITUACOES_EVASAO:
                        evadidos += 1
                if evadidos == 0:
                    raise ValidationError('Justifique a evazão zero caso nenhum aluno tenha evadido.')
        elif self.source.tipo_id == TipoInconsistencia.DURACAO_CICLO:
            if acao == 'corrigir':
                data_inicio = self.get('data_inicio')
                data_fim = self.get('data_fim')
                if data_inicio > data_fim:
                    raise ValidationError('A data de início do clico não pode ser posterior a data fim.')
                days = (data_fim - data_inicio).days + 1
                #
                if days < referencia.curso.tipo.duracao_minima:
                    raise ValidationError(
                        f'O ciclo contém duração de {days} sendo menor que a mínima de {referencia.curso.tipo.duracao_minima}.')
                if days > referencia.curso.tipo.duracao_maxima:
                    raise ValidationError(
                        f'O ciclo contém duração de {days} sendo maior que a máxima de {referencia.curso.tipo.duracao_maxima}.')
        elif self.source.tipo_id == TipoInconsistencia.COR_RACA:
            if acao == 'corrigir':
                arquivo = self.request.FILES.get('arquivo')
                raca = self.get('raca')
                if raca is None and arquivo is None:
                    raise ValidationError('O campo cor/raça é obrigatório')

        elif self.source.tipo_id == TipoInconsistencia.RENDA:
            if acao == 'corrigir':
                arquivo = self.request.FILES.get('arquivo')
                renda_per_capita = self.get('renda_per_capita')
                if renda_per_capita is None and arquivo is None:
                    raise ValidationError('O campo renda é obrigatório')

        elif self.source.tipo_id in [TipoInconsistencia.RETENCAO_CRITICA, TipoInconsistencia.RETENCAO_FIC]:
            if acao == 'corrigir':
                situacao = self.get('situacao')
                if situacao.id == SituacaoMatricula.EM_CURSO:
                    raise ValidationError('Justifique a retenção caso a situação da matrícula permaneça "EM_CURSO".')

        elif self.source.tipo_id == TipoInconsistencia.TURNO_OFERTA_CICLO:
            if acao == 'corrigir':
                if not self.get('turnos'):
                    raise ValidationError('Informe um ou mais turnos.')

        elif self.source.tipo_id == TipoInconsistencia.INGRESSANTES_MAIOR_INSCRITOS:
            if acao == 'corrigir':
                ingressantes = self.get('ingressantes')
                inscritos = self.get('inscritos')
                if ingressantes > inscritos:
                    raise ValidationError(f'O número de ingressantes é maior do que o inscritos')

        elif self.source.tipo_id in [TipoInconsistencia.MATRICULA_ANTERIOR, TipoInconsistencia.MATRICULA_POSTERIOR]:
            if acao == 'corrigir':
                data_matricula = self.get('data_matricula')
                data_ocorrencia = self.get('data_ocorrencia')
                if data_matricula > data_ocorrencia:
                    raise ValidationError(
                        f"Data da matrícula posterior a data da ocorrência ({data_ocorrencia.strftime('%d/%m/%Y')}).")

        elif self.source.tipo_id == TipoInconsistencia.RETENCAO_CRITICA:
            if acao == 'corrigir':
                situacao = self.get('situacao')
                if situacao.id == SituacaoMatricula.EM_CURSO:
                    raise ValidationError('A situação da matrícula é invalida.')

        elif self.source.tipo_id == TipoInconsistencia.TURNO_ALUNO:
            if acao == 'corrigir':
                if not self.get('turno'):
                    raise ValidationError('Informe o turno do aluno.')

        return validated_data

    def validate_data_ocorrencia(self, value):
        referencia = self.source.get_referencia()
        data_ocorrencia = self.get('data_ocorrencia')
        data_inicio = self.get('data_inicio', referencia.ciclo.data_inicio)
        if data_ocorrencia < data_inicio:
            msg = f"A data da ocorrência deve ser posterior a data de início do ciclo ({data_inicio.strftime('%d/%m/%Y')})."
            raise ValidationError({'data_ocorrencia': msg})
        return data_ocorrencia

    def validate_data_matricula(self, value):
        referencia = self.source.get_referencia()
        data_matricula = self.get('data_matricula')
        data_inicio = self.get('data_inicio', referencia.ciclo.data_inicio)
        if data_matricula < data_inicio:
            msg = f"Data da matrícula anterior a data de início do ciclo ({data_inicio.strftime('%d/%m/%Y')})."
            raise ValidationError(msg)
        if data_matricula > referencia.ciclo.data_fim:
            msg = f"Data da matrícula posterior a data de final do ciclo ({referencia.ciclo.data_fim.strftime('%d/%m/%Y')})."
            raise ValidationError(msg)
        return data_matricula

    def validate_titulacao(self, value):
        titulacao = self.get('titulacao', self.source.get_referencia().titulacao)
        escolaridade = self.get('escolaridade', self.source.get_referencia().escolaridade)
        if titulacao and escolaridade and escolaridade.nivel_ensino_id < titulacao.nivel_ensino_id:
            raise ValidationError('Titulação incompatível com a escolaridade.')
        return titulacao

    def validate_escolaridade(self, value):
        escolaridade = self.get('escolaridade', self.source.get_referencia().escolaridade)
        cargo = self.get('cargo', self.source.get_referencia().cargo)
        if escolaridade and cargo and escolaridade.nivel_ensino_id < cargo.nivel_ensino_id:
            raise ValidationError('Escolaridade incompatível com o cargo.')
        return escolaridade

    def validate_carga_horaria(self, value):
        carga_horaria = self.get('carga_horaria')
        acao = self.get('acao')
        if acao == 'corrigir' and carga_horaria < 20:
            raise ValidationError('A carga-horária não pode ser inferior a 20 horas')
        return carga_horaria

    def validate_turno(self, value):
        arquivo = self.request.FILES.get('arquivo')
        turno = self.get('turno')
        acao = self.get('acao')
        if acao == 'corrigir' and turno is None and arquivo is None:
            raise ValidationError('O campo turno é orbigatório')
        return turno

    def validate_vagas_regulares_ac(self, value):
        if self.request.POST.get('acao') == 'restaurar':
            return self.get('vagas_regulares_ac')
        ciclo = self.source.get_referencia()
        if self.source.tipo_id == TipoInconsistencia.NUMERO_VAGAS:
            total = 0
            regulares = 0
            for tipo in ('ac', 'l1', 'l2', 'l5', 'l6', 'l9', 'l10', 'l13', 'l14'):
                regular = 'vagas_regulares_{}'.format(tipo)
                extra = 'vagas_extras_{}'.format(tipo)
                regulares += int(self.get(regular) or 0)
                total += int(self.get(regular) or 0)
                total += int(self.get(extra) or 0)
            total += len(self.request.POST.getlist('matriculas_excluidas', []))
            total += len(self.request.POST.getlist('matriculas_substituidas', []))
            if total < ciclo.ingressantes:
                mensagem = 'Número de vaga inferior ao número de alunos atentidos. Revise o detalhamento de vagas ou informe as matrículas que foram "substituídas" ou "excluídas".'
                self.show('Matrículas')
                raise ValidationError(mensagem)
        return self.get('vagas_regulares_ac')

    def validate_carga_horaria(self, value):
        carga_horaria = self.get('carga_horaria')
        acao = self.get('acao')
        if acao == 'corrigir' and carga_horaria < 20:
            raise ValidationError('A carga-horária não pode ser inferior a 20 horas')
        return carga_horaria

    def set_acoes(self, *acoes):
        choices = []
        if 'corrigir' in acoes:
            choices.append(['corrigir', 'Corrigir'])
        if 'confirmar' in acoes:
            choices.append(['confirmar', 'Confirmar'])
        if 'excluir' in acoes:
            choices.append(['excluir', 'Excluir'])
        if 'justificar' in acoes:
            choices.append(['justificar', 'Justificar'])
        if 'restaurar' in acoes:
            choices.append(['restaurar', 'Restaurar'])
        self.fields['acao'].choices = choices

    def get_fieldsets(self):
        return self.fieldsets

    def hide_fieldsets(self):
        self.hide(*[name for name in self.fieldsets.keys() if name != 'Ação'])

    def on_acao_change(self, acao, **kwargs):
        self.hide_fieldsets()
        # INCONSISTÊNCIAS DE CURSO
        if self.source.tipo_id == TipoInconsistencia.ASSOCIACAO_CATALOGO:
            if acao == 'corrigir':
                self.show('Correção')
            if self.request.POST.get('filtrar_por_eixo'):
                self.show('eixo')
            else:
                self.hide('eixo')
        elif self.source.tipo_id == TipoInconsistencia.NOMENCLATURA_CURSO:
            if acao == 'justificar':
                self.show('Justificativa')
        # INCONSISTÊNCIAS DE CICLO
        elif self.source.tipo_id == TipoInconsistencia.EVASAO_ZERO:
            if acao == 'corrigir':
                self.show('Correção')
            if acao == 'justificar':
                self.show('Justificativa')
        elif self.source.tipo_id == TipoInconsistencia.CARGA_HORARIA_INSUFICIENTE:
            if acao == 'corrigir':
                self.show('Correção')
            if acao == 'justificar':
                self.show('Justificativa')
        elif self.source.tipo_id == TipoInconsistencia.PROGRAMAS_ASSOCIADOS:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.DURACAO_CICLO:
            if acao == 'corrigir':
                self.show('Correção')
            elif acao == 'justificar':
                self.show('Justificativa')
        elif self.source.tipo_id == TipoInconsistencia.NUMERO_VAGAS:
            if acao == 'corrigir':
                self.show('Correção')
            elif acao == 'restaurar':
                self.show('Ação')
        elif self.source.tipo_id == TipoInconsistencia.INGRESSANTES_MAIOR_INSCRITOS:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.TURNO_OFERTA_CICLO:
            if acao == 'corrigir':
                self.show('Correção')
        # INCONSISTÊNCIAS DE MATRÍCULA
        elif self.source.tipo_id == TipoInconsistencia.MATRICULA_ANTERIOR:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.MATRICULA_POSTERIOR:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.ALUNO_DUPLICADO:
            pass
        elif self.source.tipo_id == TipoInconsistencia.RETENCAO_CRITICA:
            if acao == 'corrigir':
                self.show('Correção')
            elif acao == 'justificar':
                self.show('Justificativa')
            # elif acao == 'restaurar' and 'Justificativa' in self.fieldsets:
            #     self.show('Justificativa')
        elif self.source.tipo_id == TipoInconsistencia.RETENCAO_FIC:
            if acao == 'corrigir':
                self.show('Correção')
            elif acao == 'justificar':
                self.show('Justificativa')
        elif self.source.tipo_id == TipoInconsistencia.COR_RACA:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.RENDA:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.TURNO_ALUNO:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_CARGO:
            if acao == 'corrigir':
                self.show('Correção')
            elif acao == 'justificar':
                self.show('Justificativa')
        elif self.source.tipo_id == TipoInconsistencia.DOCENTE_LOTADO_REITORIA:
            if acao == 'corrigir':
                self.show('Correção')
            elif acao == 'justificar':
                self.show('Justificativa')
        elif self.source.tipo_id == TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_TITULACAO:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.TITULACAO_NAO_INFORMADA:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.ESCOLARIDADE_NAO_INFORMADA:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.CARGO_SEM_DESCRICAO:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.UORG_NAO_VINCULADA:
            if acao == 'corrigir':
                self.show('Correção')
        elif self.source.tipo_id == TipoInconsistencia.DUPLICIDADE_LOTACAO:
            if acao == 'justificar':
                self.show('Justificativa')

    def on_filtrar_por_eixo_change(self, filtrar_por_eixo=None, **kwargs):
        if filtrar_por_eixo:
            self.show('eixo')
        else:
            self.hide('eixo')

    def get_curso_catalogo_queryset(self, queryset):
        if self.request.POST.get('filtrar_por_eixo') and self.request.POST.get('eixo'):
            return CursoCatalogo.objects.filter(
                tipo=self.source.get_referencia().tipo, eixo_id=self.request.POST.get('eixo')
            )
        return self.source.get_referencia().identificar_candidatos_catalogo()

    def _validar_raca(self, valor, index=None):
        if valor:
            if valor.upper().startswith('NÃO') or valor.upper().startswith('NAO'):
                valor = 'Não declarada'
            elif valor.upper().startswith('BRANC'):
                valor = 'Branca'
            elif valor.upper().startswith('PRET'):
                valor = 'Preta'
            elif valor.upper().startswith('PARD'):
                valor = 'Parda'
            elif valor.upper().startswith('IND'):
                valor = 'Indígena'
            elif valor.upper().startswith('AMAREL'):
                valor = 'Amarela'
        raca = {obj.nome: obj for obj in cache.get_or_set('racas', Raca.objects.all())}.get(valor)
        if not raca:
            msg = f"Error na Linha {index}: Raça \"{valor}\" é inválida" if index else f"Raça \"{valor}\" inválida ou nula"
            raise ValidationError(msg)
        return raca

    def _validar_renda(self, valor, index=None):
        if valor:
            if valor.upper() == 'NAO DECLARADA':
                valor = 'Não declarada'
            if valor == '0,5<RFP<=1':
                valor = '0,5<RFP<=1,0'
        renda_per_capita = {obj.nome: obj for obj in cache.get_or_set('faixas_renda', FaixaRenda.objects.all())}.get(
            valor)
        if not renda_per_capita:
            msg = f"Error na Linha {index}: Renda \"{valor}\" é inválida" if index else f"Renda \"{valor}\" inválida ou nula"
            raise ValidationError(msg)
        return renda_per_capita

    def submit(self):
        alteracoes = []
        referencia = self.source.get_referencia()

        if self.validated_data['acao'] == 'restaurar':
            self.source.restaurar(self.request.user)
        elif self.validated_data['acao'] == 'corrigir':
            alterar = True
            self.source.alteracao_set.all().delete()
            # INCONSISTÊNCIAS DE CURSO
            if self.source.tipo_id == TipoInconsistencia.ASSOCIACAO_CATALOGO:
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='curso_catalogo',
                    valor_anterior=referencia.curso_catalogo,
                    valor_atual=self.validated_data['curso_catalogo'], usuario=self.request.user
                ))
            elif self.source.tipo_id == TipoInconsistencia.NOMENCLATURA_CURSO:
                pass
            # INCONSISTÊNCIAS DE CICLO
            elif self.source.tipo_id == TipoInconsistencia.EVASAO_ZERO:
                evadidos = 0
                for i in range(0, 10):
                    matricula = self.validated_data.get('matricula_aluno_{}'.format(i))
                    situacao = self.validated_data.get('st_{}'.format(i))
                    data_ocorrencia = self.validated_data.get('dt_{}'.format(i))
                    if not (matricula and situacao and data_ocorrencia):
                        continue
                    if situacao.id in SituacaoMatricula.SITUACOES_EVASAO:
                        evadidos += 1
                    if matricula.situacao != situacao:
                        alteracoes.append(Alteracao.objects.create(
                            inconsistencia=self.source, objeto=matricula, campo='situacao',
                            valor_anterior=matricula.situacao, valor_atual=situacao, usuario=self.request.user
                        ))
                    if matricula.data_ocorrencia != data_ocorrencia:
                        alteracoes.append(Alteracao.objects.create(
                            inconsistencia=self.source, objeto=matricula, campo='data_ocorrencia',
                            valor_anterior=matricula.data_ocorrencia, valor_atual=data_ocorrencia,
                            usuario=self.request.user
                        ))
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, objeto=referencia, campo='evadidos',
                    valor_anterior=referencia.evadidos, valor_atual=evadidos,
                    usuario=self.request.user
                ))
                if referencia.justificativa_evasao_zero:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=referencia, campo='justificativa_evasao_zero',
                        valor_anterior=referencia.justificativa_evasao_zero, valor_atual=None,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.CARGA_HORARIA_INSUFICIENTE:
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='carga_horaria',
                    valor_anterior=referencia.carga_horaria,
                    valor_atual=self.validated_data['carga_horaria'], usuario=self.request.user
                ))
                if referencia.justificativa_carga_horaria:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=referencia, campo='justificativa_carga_horaria',
                        valor_anterior=referencia.justificativa_carga_horaria, valor_atual=None,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.PROGRAMAS_ASSOCIADOS:
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='programa',
                    valor_anterior=referencia.programa,
                    valor_atual=self.validated_data['programa'], usuario=self.request.user
                ))
            elif self.source.tipo_id == TipoInconsistencia.DURACAO_CICLO:
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='data_inicio',
                    valor_anterior=referencia.data_inicio,
                    valor_atual=self.validated_data['data_inicio'], usuario=self.request.user
                ))
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='data_fim',
                    valor_anterior=referencia.data_fim,
                    valor_atual=self.validated_data['data_fim'], usuario=self.request.user
                ))
                if referencia.justificativa_duracao_impropria:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=referencia, campo='justificativa_duracao_impropria',
                        valor_anterior=referencia.justificativa_duracao_impropria, valor_atual=None,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.NUMERO_VAGAS:
                vagas = 0
                ciclo = self.source.get_referencia()
                ingressantes = ciclo.matricula_set.filter(ingressante=True).count()
                vagas_ciclo = VagasCiclo.objects.filter(ciclo=ciclo).first() or VagasCiclo.objects.create(
                    ciclo=self.source.get_referencia())
                for i, tipo in enumerate(('ac', 'l1', 'l2', 'l5', 'l6', 'l9', 'l10', 'l13', 'l14')):
                    regular = 'vagas_regulares_{}'.format(tipo)
                    extra = 'vagas_extras_{}'.format(tipo)
                    for campo in (regular, extra):
                        valor_anterior = getattr(vagas_ciclo, campo)
                        valor_atual = self.validated_data.get(campo)
                        vagas += valor_atual or 0
                        if valor_anterior != valor_atual:
                            alteracoes.append(Alteracao.objects.create(
                                inconsistencia=self.source, objeto=vagas_ciclo, campo=campo,
                                valor_anterior=valor_anterior,
                                valor_atual=valor_atual, usuario=self.request.user
                            ))
                if ciclo.ingressantes > ciclo.vagas:
                    for field_name in ('matriculas_excluidas', 'matriculas_substituidas'):
                        for i, matricula in enumerate(self.validated_data[field_name]):
                            if field_name == 'matriculas_excluidas':
                                situacao_atual = SituacaoMatricula.objects.get(pk=SituacaoMatricula.EXCLUIDO)
                            else:
                                situacao_atual = SituacaoMatricula.objects.get(pk=SituacaoMatricula.SUBSTITUIDO)
                            if matricula.situacao != situacao_atual:
                                alteracoes.append(Alteracao.objects.create(
                                    inconsistencia=self.source, objeto=matricula, campo='situacao',
                                    valor_atual=situacao_atual, usuario=self.request.user
                                ))
                            if matricula.ingressante:
                                ingressantes -= 1
                if vagas != ciclo.vagas:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=ciclo, campo='vagas',
                        valor_anterior=ciclo.vagas, valor_atual=vagas, usuario=self.request.user
                    ))
                if ingressantes != ciclo.ingressantes:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=ciclo, campo='ingressantes',
                        valor_anterior=ciclo.ingressantes, valor_atual=ingressantes, usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.INGRESSANTES_MAIOR_INSCRITOS:
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='inscritos',
                    valor_anterior=referencia.inscritos,
                    valor_atual=self.validated_data['inscritos'],
                    usuario=self.request.user
                ))
            elif self.source.tipo_id == TipoInconsistencia.TURNO_OFERTA_CICLO:
                turnos = self.validated_data['turnos']
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='turnos',
                    valor_anterior=[pk for pk in referencia.turnos.values_list('id', flat=True)],
                    valor_atual=[turno.pk for turno in turnos], usuario=self.request.user
                ))
                if len(turnos) == 1:
                    turno = turnos[0]
                    inconsistencias_indiretas = Inconsistencia.objects.filter(
                        tipo_id=TipoInconsistencia.TURNO_ALUNO, matricula__ciclo=referencia,
                        situacao__in=Inconsistencia.INCONSISTENTE + Inconsistencia.ALTERADA
                    )
                    for inconsistencia in inconsistencias_indiretas:
                        alteracoes_indiretas = []
                        matricula = inconsistencia.get_referencia()
                        alteracoes_indiretas.append(Alteracao.objects.create(
                            inconsistencia=inconsistencia, objeto=matricula, campo='turno',
                            valor_anterior=matricula.turno, valor_atual=turno, usuario=self.request.user
                        ))
                        inconsistencia.alterar(*alteracoes_indiretas)
                        matricula.atualizar_situacao_inconsistencia()
            # INCONSISTÊNCIAS DE MATRÍCULA
            elif self.source.tipo_id == TipoInconsistencia.MATRICULA_ANTERIOR:
                matricula = self.source.get_referencia()
                if matricula.data_matricula != self.validated_data['data_matricula']:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=matricula, campo='data_matricula',
                        valor_anterior=matricula.data_matricula,
                        valor_atual=self.validated_data['data_matricula'],
                        usuario=self.request.user
                    ))
                if matricula.data_ocorrencia != self.validated_data['data_ocorrencia']:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=matricula, campo='data_ocorrencia',
                        valor_anterior=matricula.data_ocorrencia,
                        valor_atual=self.validated_data['data_ocorrencia'],
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.MATRICULA_POSTERIOR:
                matricula = self.source.get_referencia()
                if matricula.data_matricula != self.validated_data['data_matricula']:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=matricula, campo='data_matricula',
                        valor_anterior=matricula.data_matricula,
                        valor_atual=self.validated_data['data_matricula'],
                        usuario=self.request.user
                    ))
                if matricula.data_ocorrencia != self.validated_data['data_ocorrencia']:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=matricula, campo='data_ocorrencia',
                        valor_anterior=matricula.data_matricula,
                        valor_atual=self.validated_data['data_ocorrencia'],
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.ALUNO_DUPLICADO:
                pass
            elif self.source.tipo_id == TipoInconsistencia.RETENCAO_CRITICA:
                matricula = self.source.get_referencia()
                if matricula.situacao != self.validated_data['situacao']:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=matricula, campo='situacao',
                        valor_anterior=matricula.situacao,
                        valor_atual=self.validated_data['situacao'], usuario=self.request.user
                    ))
                if matricula.data_ocorrencia != self.validated_data['data_ocorrencia']:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=matricula, campo='data_ocorrencia',
                        valor_anterior=matricula.data_ocorrencia,
                        valor_atual=self.validated_data['data_ocorrencia'], usuario=self.request.user
                    ))
                if referencia.justificativa_retencao:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=referencia, campo='justificativa_retencao',
                        valor_anterior=referencia.justificativa_retencao, valor_atual=None,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.RETENCAO_FIC:
                matricula = self.source.get_referencia()
                if matricula.situacao != self.validated_data['situacao']:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=matricula, campo='situacao',
                        valor_anterior=matricula.situacao,
                        valor_atual=self.validated_data['situacao'], usuario=self.request.user
                    ))
                if matricula.data_ocorrencia != self.validated_data['data_ocorrencia']:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=matricula, campo='data_ocorrencia',
                        valor_anterior=matricula.data_ocorrencia,
                        valor_atual=self.validated_data['data_ocorrencia'], usuario=self.request.user
                    ))
                if referencia.justificativa_retencao:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=referencia, campo='justificativa_retencao',
                        valor_anterior=referencia.justificativa_retencao, valor_atual=None,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.COR_RACA:
                arquivo = self.request.FILES.get('arquivo')
                if arquivo:
                    try:
                        alterar = False
                        dados = []
                        blob = arquivo.read()
                        try:
                            csv_file = blob.decode('iso8859-3').splitlines()
                        except Exception:
                            csv_file = blob.decode('utf-8').splitlines()
                        dialect = csv.Sniffer().sniff(csv_file[0])
                        dialect.delimiter = ';'
                        csv_reader = csv.DictReader(csv_file, dialect=dialect, fieldnames=['CPF', 'Valor'])
                        for index, row in enumerate(csv_reader):
                            if index == 0:
                                if 'CPF' not in row or 'Valor' not in row:
                                    raise ValidationError('O arquivo deve conter a primeira linha com o seguinte conteúdo: CPF,Valor')
                                continue
                            cpf = row['CPF'].zfill(11)
                            raca = self._validar_raca(row['Valor'], index)
                            dados.append((cpf, raca))
                        print(dados)
                    except ValidationError as e:
                        raise e
                    except Exception as e:
                        raise ValidationError(f"Erro ao processar aquivo: {str(e)}")
                else:
                    aluno = referencia.aluno
                    valor_atual = self.validated_data.get('raca', None)
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=aluno, campo='raca',
                        valor_anterior=aluno.raca,
                        valor_atual=valor_atual,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.RENDA:
                arquivo = self.request.FILES.get('arquivo')
                if arquivo:
                    try:
                        alterar = False
                        dados = []
                        blob = arquivo.read()
                        try:
                            csv_file = blob.decode('iso8859-3').splitlines()
                        except Exception:
                            csv_file = blob.decode('utf-8').splitlines()
                        dialect = csv.Sniffer().sniff(csv_file[0])
                        dialect.delimiter = ';'
                        csv_reader = csv.DictReader(csv_file, dialect=dialect, fieldnames=['CPF', 'Valor'])
                        for index, row in enumerate(csv_reader):
                            if index == 0:
                                if 'CPF' not in row or 'Valor' not in row:
                                    raise ValidationError(
                                        'O arquivo deve conter a primeira linha com o seguinte conteúdo: CPF,Valor')
                                continue
                            cpf = row['CPF'].zfill(11)
                            renda_per_capita = self._validar_renda(row['Valor'], index)
                            dados.append((cpf, renda_per_capita))
                        print(dados)
                    except ValidationError as e:
                        raise e
                    except Exception as e:
                        raise ValidationError(f"Erro ao processar aquivo: {str(e)}")
                else:
                    aluno = referencia.aluno
                    valor_atual = self.validated_data.get('renda_per_capita', None)
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, objeto=aluno, campo='renda_per_capita',
                        valor_anterior=referencia.aluno.renda_per_capita,
                        valor_atual=valor_atual,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.TURNO_ALUNO:
                valor_atual = self.validated_data.get('turno', None)
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='turno',
                    valor_anterior=referencia.turno,
                    valor_atual=valor_atual,
                    usuario=self.request.user
                ))
            elif self.source.tipo_id == TipoInconsistencia.DOCENTE_LOTADO_REITORIA:
                lotacao = referencia.lotacao
                valor_atual = self.validated_data.get('lotacao', None)
                if lotacao != valor_atual:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, campo='lotacao',
                        valor_anterior=lotacao, valor_atual=valor_atual, usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_TITULACAO:
                escolaridade = referencia.escolaridade
                valor_atual = self.validated_data.get('escolaridade', None)
                if escolaridade != valor_atual:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, campo='escolaridade',
                        valor_anterior=escolaridade,
                        valor_atual=valor_atual,
                        usuario=self.request.user
                    ))
                titulacao = referencia.titulacao
                valor_atual = self.validated_data.get('titulacao', None)
                if titulacao != valor_atual:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, campo='titulacao',
                        valor_anterior=titulacao,
                        valor_atual=valor_atual,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_CARGO:
                escolaridade = referencia.escolaridade
                valor_atual = self.validated_data.get('escolaridade', None)
                if escolaridade != valor_atual:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, campo='escolaridade',
                        valor_anterior=escolaridade,
                        valor_atual=valor_atual,
                        usuario=self.request.user
                    ))
                #
                cargo = referencia.cargo
                valor_atual = self.validated_data.get('cargo', None)
                if cargo != valor_atual:
                    alteracoes.append(Alteracao.objects.create(
                        inconsistencia=self.source, campo='cargo',
                        valor_anterior=cargo,
                        valor_atual=valor_atual,
                        usuario=self.request.user
                    ))
            elif self.source.tipo_id == TipoInconsistencia.TITULACAO_NAO_INFORMADA:
                titulacao = referencia.titulacao
                valor_atual = self.validated_data.get('titulacao', None)
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='titulacao',
                    valor_anterior=titulacao,
                    valor_atual=valor_atual,
                    usuario=self.request.user
                ))
            elif self.source.tipo_id == TipoInconsistencia.ESCOLARIDADE_NAO_INFORMADA:
                escolaridade = referencia.escolaridade
                valor_atual = self.validated_data.get('escolaridade', None)
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='escolaridade',
                    valor_anterior=escolaridade,
                    valor_atual=valor_atual,
                    usuario=self.request.user
                ))
            elif self.source.tipo_id == TipoInconsistencia.CARGO_SEM_DESCRICAO:
                valor_atual = self.validated_data.get('descricao', None)
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, objeto=referencia.cargo, campo='nome',
                    valor_anterior=referencia.cargo.nome,
                    valor_atual=valor_atual,
                    usuario=self.request.user
                ))
            elif self.source.tipo_id == TipoInconsistencia.DUPLICIDADE_LOTACAO:
                pass
            elif self.source.tipo_id == TipoInconsistencia.UORG_NAO_VINCULADA:
                valor_atual = self.validated_data.get('unidade', None)
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, campo='unidade',
                    valor_anterior=referencia,
                    valor_atual=valor_atual,
                    usuario=self.request.user
                ))
            if alterar:
                self.source.alterar(*alteracoes)
        elif self.validated_data['acao'] == 'confirmar':
            self.source.alterar(*alteracoes)
        elif self.validated_data['acao'] == 'justificar':
            justificativa = self.validated_data['justificativa']
            nome_campo = {
                TipoInconsistencia.NOMENCLATURA_CURSO: 'justificativa_nome',
                TipoInconsistencia.EVASAO_ZERO: 'justificativa_evasao_zero',
                TipoInconsistencia.CARGA_HORARIA_INSUFICIENTE: 'justificativa_carga_horaria',
                TipoInconsistencia.DURACAO_CICLO: 'justificativa_duracao_impropria',
                TipoInconsistencia.RETENCAO_CRITICA: 'justificativa_retencao',
                TipoInconsistencia.RETENCAO_FIC: 'justificativa_retencao',
                TipoInconsistencia.DUPLICIDADE_LOTACAO: 'justificativa_duplicidade_lotacao',
                TipoInconsistencia.DIVERGENCIA_ESCOLARIDADE_CARGO: 'justificativa_escolaridade_cargo',
                TipoInconsistencia.DOCENTE_LOTADO_REITORIA: 'justificativa_lotacao_reitoria'
            }[self.source.tipo_id]
            alteracoes.append(Alteracao.objects.create(
                inconsistencia=self.source, campo=nome_campo,
                valor_atual=self.validated_data['justificativa'], usuario=self.request.user
            ))
            self.source.alterar(*alteracoes)
        elif self.validated_data['acao'] == 'excluir':
            if self.source.tipo_id == TipoInconsistencia.ALUNO_DUPLICADO:
                qs = Inconsistencia.objects.filter(tipo=self.source.tipo,
                                                   matricula__aluno=self.source.matricula.aluno_id).exclude(
                    pk=self.source.pk)
                if qs.count() == 1:
                    qs.first().alterar()
                    qs.first().matricula.atualizar_situacao_inconsistencia()
            if self.source.tipo_id == TipoInconsistencia.DUPLICIDADE_LOTACAO:
                qs = Inconsistencia.objects.filter(tipo=self.source.tipo, servidor__cpf=referencia.cpf).exclude(
                    pk=self.source.pk)
                if qs.count() == 1:
                    qs.first().alterar()
                    qs.first().servidor.atualizar_situacao_inconsistencia()
            if not referencia.excluido:
                alteracoes.append(Alteracao.objects.create(
                    inconsistencia=self.source, objeto=referencia, campo='excluido',
                    valor_anterior=False, valor_atual=True, usuario=self.request.user
                ))
            self.source.alterar(*alteracoes)
        referencia.atualizar_situacao_inconsistencia()
        self.notify('Ação realizada com sucesso.')

    def has_permission(self):
        return 1 or self.source.pode_ser_resolvida(self.request) or self.source.pode_ser_restaurada(self.request)
