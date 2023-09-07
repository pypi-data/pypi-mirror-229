import json
import unicodedata
from datetime import datetime, date
from django.db.transaction import atomic
from django.db import models
from .fields import GenericField
from api.statistics import Statistics


models.GenericField = GenericField


class Papel:
    ADMINISTRADOR = 'Administrador'
    REITOR = 'Reitor'
    PESQUISADOR_INSTITUCIONAL = 'Pesquisador Institucional'
    GESTAO_DE_PESSOAS = 'Gestão de Pessoas'
    RECURSOS_HUMANOS = 'Recursos Humanos'
    REGISTRO_ACADEMICO = 'Registro Acadêmico'
    EXECUCAO_ACADEMICA = 'Execução Acadêmica'


class ProgramaManager(models.Manager):
    def all(self):
        return self.filter()


class Programa(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)

    objects = ProgramaManager()

    class Meta:
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return self.nome


class TipoInconsistencia(models.Model):

    ASSOCIACAO_CATALOGO = 1
    NOMENCLATURA_CURSO = 2
    EVASAO_ZERO = 3
    CARGA_HORARIA_INSUFICIENTE = 4
    PROGRAMAS_ASSOCIADOS = 5
    DURACAO_CICLO = 6
    NUMERO_VAGAS = 7
    INGRESSANTES_MAIOR_INSCRITOS = 8
    TURNO_OFERTA_CICLO = 9
    MATRICULA_ANTERIOR = 10
    MATRICULA_POSTERIOR = 11
    ALUNO_DUPLICADO = 12
    RETENCAO_CRITICA = 13
    RETENCAO_FIC = 14
    COR_RACA = 15
    RENDA = 16
    TURNO_ALUNO = 17

    DOCENTE_LOTADO_REITORIA = 18
    DIVERGENCIA_ESCOLARIDADE_TITULACAO = 19
    DIVERGENCIA_ESCOLARIDADE_CARGO = 20
    TITULACAO_NAO_INFORMADA = 21
    ESCOLARIDADE_NAO_INFORMADA = 22
    CARGO_SEM_DESCRICAO = 23
    DUPLICIDADE_LOTACAO = 24
    UORG_NAO_VINCULADA = 25

    CURSO = [
        ASSOCIACAO_CATALOGO,
        NOMENCLATURA_CURSO
    ]
    CICLO = [
        EVASAO_ZERO,
        CARGA_HORARIA_INSUFICIENTE,
        PROGRAMAS_ASSOCIADOS,
        DURACAO_CICLO,
        NUMERO_VAGAS,
        INGRESSANTES_MAIOR_INSCRITOS,
        TURNO_OFERTA_CICLO
    ]
    MATRICULA = [
        MATRICULA_ANTERIOR,
        MATRICULA_POSTERIOR,
        ALUNO_DUPLICADO,
        RETENCAO_CRITICA,
        RETENCAO_FIC,
        COR_RACA,
        RENDA,
        TURNO_ALUNO
    ]
    UNIDADE_ORGANIZACIONAL = [
        UORG_NAO_VINCULADA
    ]
    SERVIDOR = [
        DOCENTE_LOTADO_REITORIA,
        DIVERGENCIA_ESCOLARIDADE_TITULACAO,
        DIVERGENCIA_ESCOLARIDADE_CARGO,
        TITULACAO_NAO_INFORMADA,
        ESCOLARIDADE_NAO_INFORMADA,
        CARGO_SEM_DESCRICAO,
        DUPLICIDADE_LOTACAO
    ]

    ENSINO = CURSO + CICLO + MATRICULA
    RH = UNIDADE_ORGANIZACIONAL + SERVIDOR

    nome = models.CharField(verbose_name='Nome', max_length=50)
    escopo = models.CharField(verbose_name='Escopo', choices=[[x, x] for x in ('Curso', 'Ciclo', 'Matrícula', 'Unidade Organizacional', 'Servidor')], null=True, max_length=255)

    class Meta:
        verbose_name = 'Tipo de Inconsistência'
        verbose_name_plural = 'Tipos de Inconsistência'

    def __str__(self):
        return self.nome


class JustificativaManager(models.Manager):
    def all(self):
        return self.filter()


class Justificativa(models.Model):
    tipo_inconsistencia = models.ForeignKey(TipoInconsistencia, verbose_name='Tipo', on_delete=models.CASCADE)
    justificativa = models.CharField(verbose_name='Justificativa', max_length=255)

    objects = JustificativaManager()

    class Meta:
        verbose_name = 'Justificativa'
        verbose_name_plural = 'Justificativas'

    def __str__(self):
        return self.justificativa


class Acao(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)
    justificar = models.BooleanField(verbose_name='Requer Justificativa', blank=True)

    class Meta:
        verbose_name = 'Ação'
        verbose_name_plural = 'Açoes'

    def __str__(self):
        return '{} [Justificar]'.format(self.nome) if self.justificar else self.nome


class RegraInconsistenciaManager(models.Manager):

    def all(self):
        return self.filter()


class RegraInconsistencia(models.Model):
    codigo = models.IntegerField(verbose_name='Código')
    tipo = models.CharField(verbose_name='Tipo', choices=[[tipo, tipo] for tipo in ('Curso', 'Ciclo', 'Matrícula')], max_length=255)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    descricao = models.TextField(verbose_name='Descrição', max_length=255)
    acoes = models.ManyToManyField(Acao, verbose_name='Ações')

    objects = RegraInconsistenciaManager()

    class Meta:
        verbose_name = 'Regra de Consistência'
        verbose_name_plural = 'Regras de Consistência'
        ordering = 'id',

    def get_acoes(self):
        return self.acoes

    def __str__(self):
        return self.nome


class ConfiguracaoManager(models.Manager):
    def all(self):
        return self.filter()


class Configuracao(models.Model):
    ano = models.IntegerField(verbose_name='Ano')
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(verbose_name='Data de Fim')
    data_envio = models.DateField(verbose_name='Data de Envio', null=True, blank=True)

    objects = ConfiguracaoManager()

    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'

    def __str__(self):
        return 'Configuração do ano {}'.format(self.ano)

    def get_calendario(self):
        return [
            ('Período de Validação', self.data_inicio, self.data_fim),
            ('Envio dos Dados', self.data_envio),
        ]

    def get_arquivos(self):
        return self.arquivo_set.order_by('unidade__instituicao__sigla')

    def get_arquivos_processados(self):
        return self.get_arquivos().filter(data_processamento__isnull=False)

    def get_arquivos_nao_processados(self):
        return self.get_arquivos().filter(data_processamento__isnull=True)

    def get_inconsistencias_por_instituicao(self):
        return Statistics(self.inconsistencia_set).count('unidade__instituicao')

    def get_inconsistencias_por_tipo(self):
        return Statistics(self.inconsistencia_set).count('tipo')

    def get_total_cursos(self):
        return Curso.objects.filter(ativo=True).count()

    def get_total_ciclos(self):
        return Ciclo.objects.filter(ativo=True).count()

    def get_total_matriculas_atendidas(self):
        return Matricula.objects.filter(atendida=True).count()

    def get_total_ingressantes(self):
        return Matricula.objects.filter(ingressante=True).count()

    def get_total_inconsistencias(self):
        return self.inconsistencia_set.count()

    def get_totais(self):
        return self.value_set(
            ('get_total_cursos', 'get_total_ciclos'),
            ('get_total_matriculas_atendidas', 'get_total_ingressantes'),
            'get_total_inconsistencias'
        )


    @atomic()
    def save(self, *args, **kwargs):
        pk = self.pk
        super().save(*args, **kwargs)
        if self.ano > 2021 and not pk:
            self.criar_arquivos_carga()

    def criar_arquivos_carga(self):
        from .inconsistencias import carga
        for codigo_sistec, quantidade in carga.consultar_totais().items():
            unidade = Unidade.objects.filter(codigo_sistec=codigo_sistec).first()
            if unidade:
                Arquivo.objects.create(configuracao=self, numero_linhas=quantidade, unidade=unidade)


class AreaCNPqMananger(models.Manager):
    def all(self):
        return self.filter()


class AreaCNPq(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=15)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = AreaCNPqMananger()

    class Meta:
        verbose_name = 'Área CNPq'
        verbose_name_plural = 'Áreas CNPq'

    def __str__(self):
        return self.nome


class Turno(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'

    def __str__(self):
        return self.nome


class NivelEnsino(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=1)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    nivel_verticalizacao = models.CharField(verbose_name='Nível de Verticalização', max_length=1)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    class Meta:
        verbose_name = 'Nível de Ensino'
        verbose_name_plural = 'Níveis de Ensino'

    def __str__(self):
        return self.nome


class EixoManager(models.Manager):
    def all(self):
        return self.filter()


class Eixo(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=2)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = EixoManager()

    class Meta:
        verbose_name = 'Eixo'
        verbose_name_plural = 'Eixos'

    def __str__(self):
        return self.nome


class SubEixoManager(models.Manager):
    def all(self):
        return self.filter()


class SubEixo(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=4)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = SubEixoManager()

    class Meta:
        verbose_name = 'Sub-eixo'
        verbose_name_plural = 'Sub-eixos'

    def __str__(self):
        return self.nome


class TipoCursoManager(models.Manager):
    def all(self):
        return self.filter()

    def get_duracao_dos_ciclos(self):
        return


class TipoCurso(models.Model):

    FIC = 1

    codigo = models.CharField(verbose_name='Código', max_length=4)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    fator = models.DecimalField(verbose_name='Fator', max_length=4, max_digits=9, decimal_places=6, null=True)
    nivel_verticalizacao = models.CharField(verbose_name='Nível de Verticalização', max_length=1, null=True)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    duracao_minima = models.IntegerField(verbose_name='Duração Mímina', help_text='Em dias. Ex: 365 (1 ano).', null=True, blank=True)
    duracao_maxima = models.IntegerField(verbose_name='Duração Máxima', help_text='Em dias. Ex: 365 (1 ano).', null=True, blank=True)

    objects = TipoCursoManager()

    class Meta:
        verbose_name = 'Tipo de Curso'
        verbose_name_plural = 'Tipos de Curso'

    def __str__(self):
        return self.nome


class MesorregiaoManager(models.Manager):
    def all(self):
        return self.filter()


class Mesorregiao(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=6)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = MesorregiaoManager()

    class Meta:
        verbose_name = 'Mesorregião'
        verbose_name_plural = 'Mesorregiões'

    def __str__(self):
        return self.nome


class MicrorregiaoManager(models.Manager):
    def all(self):
        return self.filter()


class Microrregiao(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=6)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    mesorregiao = models.ForeignKey(Mesorregiao, verbose_name='Mesorregião', on_delete=models.CASCADE, null=True)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = MicrorregiaoManager()

    class Meta:
        verbose_name = 'Microrregião'
        verbose_name_plural = 'Microrregiões'

    def __str__(self):
        return self.nome


class MunicipioManager(models.Manager):
    def all(self):
        return self.filter()


class Municipio(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=7)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    microrregiao = models.ForeignKey(Microrregiao, verbose_name='Microrregião', on_delete=models.CASCADE, null=True)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = MunicipioManager()

    class Meta:
        verbose_name = 'Município'
        verbose_name_plural = 'Municípios'

    def __str__(self):
        return self.nome


class TipoInstituicaoManager(models.Manager):
    def all(self):
        return self.filter()


class TipoInstituicao(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=6)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = TipoInstituicaoManager()

    class Meta:
        verbose_name = 'Tipo de Instituição'
        verbose_name_plural = 'Tipos de Instituição'

    def __str__(self):
        return self.nome


class TipoUnidadeManager(models.Manager):
    def all(self):
        return self.filter()


class TipoUnidade(models.Model):

    REITORIA = 6

    codigo = models.CharField(verbose_name='Código', max_length=6)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = TipoUnidadeManager()

    class Meta:
        verbose_name = 'Tipo de Unidade'
        verbose_name_plural = 'Tipos de Unidade'

    def __str__(self):
        return self.nome


class CursoCatalogoManager(models.Manager):
    def all(self):
        return self.filter()


class CursoCatalogo(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=6)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    tipo = models.ForeignKey(TipoCurso, verbose_name='Tipo', on_delete=models.CASCADE)
    fator = models.DecimalField(verbose_name='Fator', max_length=4, max_digits=9, decimal_places=6, null=True)
    duracao_minima = models.IntegerField(verbose_name='Duração Mínima', help_text='Em anos')
    carga_horaria_minima = models.IntegerField(verbose_name='Carga Horária Mínima', help_text='Em horas')
    observacao = models.CharField(verbose_name='Observação', max_length=255, blank=True)
    capacitacao = models.BooleanField(verbose_name='Curso de Capacitação', default=False)
    area_cnpq = models.ForeignKey(AreaCNPq, verbose_name='Área', on_delete=models.CASCADE, null=True, blank=True)
    nivel_ensino = models.ForeignKey(NivelEnsino, verbose_name='Nível de Ensino', on_delete=models.CASCADE)
    eixo = models.ForeignKey(Eixo, verbose_name='Eixo', on_delete=models.CASCADE)
    sub_eixo = models.ForeignKey(SubEixo, verbose_name='Sub-Eixo', on_delete=models.CASCADE)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = CursoCatalogoManager()

    class Meta:
        verbose_name = 'Curso do Catálogo'
        verbose_name_plural = 'Cursos do Catálogo'

    def __str__(self):
        return self.nome


class PessoaManager(models.Manager):
    def all(self):
        return self.filter()


class Pessoa(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)
    cpf = models.CharField(verbose_name='CPF', max_length=16, null=True)
    email = models.EmailField(verbose_name='E-mail', max_length=100, null=True)
    telefone = models.CharField(verbose_name='Telefone', max_length=50, null=True, blank=True)

    capacitacao_concluida = models.BooleanField(verbose_name='Capacitação Concluída', default=False)
    cadastro_ativo = models.BooleanField(verbose_name='Cadastro Ativo', default=True)

    objects = PessoaManager()

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'

    def __str__(self):
        return '{} ({})'.format(self.nome, self.cpf)


class AdministradorManager(models.Manager):
    def all(self):
        return self.filter()


class Administrador(models.Model):

    pessoa_fisica = models.ForeignKey(Pessoa, verbose_name='Pessoa', on_delete=models.CASCADE)

    objects = AdministradorManager()

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'

    def __str__(self):
        return '{}'.format(self.pessoa_fisica)

    def get_cpf(self):
        return self.pessoa_fisica.cpf

    def get_nome(self):
        return self.pessoa_fisica.nome

    def get_email(self):
        return self.pessoa_fisica.email


class InstituicaoManager(models.Manager):
    def all(self):
        return self.filter()

    def monitoramento(self):
        return self.filter()

    def ativas(self):
        return self.filter(pk__in=[1, 2])


class Instituicao(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=6)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    sigla = models.CharField(verbose_name='Sigla', max_length=25)
    uf = models.CharField(verbose_name='UF', max_length=2)
    tipo = models.ForeignKey(TipoInstituicao, verbose_name='Tipo', on_delete=models.CASCADE)
    reitor = models.ForeignKey(Pessoa, verbose_name='Reitor', null=True, blank=True, on_delete=models.SET_NULL)
    pesquisadores_institucionais = models.ManyToManyField(Pessoa, verbose_name='Pesquisadores Institucionais', blank=True, related_name='instituicoes_pesquisadas')
    gestao_pessoas = models.ManyToManyField(Pessoa, verbose_name='Gestão de Pessoas', blank=True, related_name='instituicoes_gestao_pessoas')
    recursos_humanos = models.ManyToManyField(Pessoa, verbose_name='Recursos Humanos', blank=True, related_name='instituicoes_recursos_humanos')
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    objects = InstituicaoManager()

    class Meta:
        verbose_name = 'Instituição'
        verbose_name_plural = 'Instituições'

    def __str__(self):
        return self.nome

    def get_pessoas(self):
        return Pessoa.objects.all()

    def get_reitor(self):
        return self.reitor

    def get_unidades(self):
        return self.unidade_set.select_related('tipo')

    def get_matriculas(self):
        return Matricula.objects.all()
        return Matricula.objects.filter(ciclo__curso__unidade__instituicao=self)

    def get_matriculas_por_unidade(self):
        return Statistics(self.get_matriculas()).count('ciclo__curso__unidade')

    def get_matriculas_por_situacao(self):
        return Statistics(self.get_matriculas()).count('situacao')

    def get_monitoramento(self):
        return Statistics(Inconsistencia.objects.filter(unidade__instituicao=self)).count('situacao', 'unidade')

    def get_pesquisadores_institucionais(self):
        return self.pesquisadores_institucionais

    def get_gestao_pessoas(self):
        return self.gestao_pessoas

    def get_recursos_humanos(self):
        return self.recursos_humanos

    def get_registradores_academicos(self):
        return Pessoa.objects.filter(unidades_registradas__instituicao=self)

    def get_executores_academicos(self):
        return Pessoa.objects.filter(unidades_executadas__instituicao=self)

    def get_equipe_tecnica_local(self):
        return self.unidade_set.order_by('id')


class UnidadeManager(models.Manager):
    def all(self):
        return self.filter()


class Unidade(models.Model):
    instituicao = models.ForeignKey(Instituicao, verbose_name='Instituição', on_delete=models.CASCADE)
    codigo = models.CharField(verbose_name='Código', max_length=6)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    tipo = models.ForeignKey(TipoUnidade, verbose_name='Tipo', on_delete=models.CASCADE)
    municipio = models.ForeignKey(Municipio, verbose_name='Município', on_delete=models.CASCADE, null=True)
    caracteristica = models.CharField(verbose_name='Característica', max_length=255, null=True, blank=True)
    periodo_criacao = models.CharField(verbose_name='Período da Criação', max_length=255, null=True, blank=True)
    codigo_inep = models.CharField(verbose_name='Código INEP', max_length=10, null=True)
    codigo_simec = models.CharField(verbose_name='Código SIMEC', max_length=10, null=True)
    codigo_sistec = models.CharField(verbose_name='Código SISTEC', max_length=10, null=True, db_index=True)
    sigla = models.CharField(verbose_name='Sigla', max_length=25, null=True, blank=True)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)

    registradores_academicos = models.ManyToManyField(Pessoa, verbose_name='Registradores Acadêmicos', blank=True, related_name='unidades_registradas')
    executores_academicos = models.ManyToManyField(Pessoa, verbose_name='Executores Acadêmicos', blank=True, related_name='unidades_executadas')

    objects = UnidadeManager()

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'

    def __str__(self):
        return '{} - {}'.format(self.nome, self.instituicao.sigla)

    def get_matriculas(self):
        return Matricula.objects.filter(ciclo__curso__unidade=self)

    def get_matriculas_por_curso(self):
        return Statistics(self.get_matriculas()).count('ciclo__curso')

    def get_registradores_academicos(self):
        return self.registradores_academicos

    def get_executores_academicos(self):
        return self.executores_academicos

    def get_monitoramento(self):
        return Statistics(Inconsistencia.objects.filter(unidade=self)).count('situacao', 'tipo')


class ModalidadeManager(models.Manager):
    def all(self):
        return self.filter()


class Modalidade(models.Model):
    PRESENCIAL = 1
    EAD = 2
    TODOS = 3

    nome = models.CharField(verbose_name='Nome', max_length=255)

    objects = ModalidadeManager()

    class Meta:
        verbose_name = 'Modalidade'
        verbose_name_plural = 'Modalidades'

    def __str__(self):
        return self.nome


class TipoOfertaManager(models.Manager):
    def all(self):
        return self.filter()


class TipoOferta(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)

    objects = TipoOfertaManager()

    class Meta:
        verbose_name = 'Tipo de Oferta'
        verbose_name_plural = 'Tipos de Oferta'

    def __str__(self):
        return self.nome


class FaixaRendaManager(models.Manager):
    def all(self):
        return self.filter()


class FaixaRenda(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)

    objects = FaixaRendaManager()

    class Meta:
        verbose_name = 'Faixa de Renda'
        verbose_name_plural = 'Faixas de Renda'

    def __str__(self):
        return self.nome


class SituacaoInconsistencia(models.Model):

    INCONSISTENTE_RA = 1
    ALTERADO_RA = 2
    VALIDADO_RA = 3
    INCONSISTENTE_PI = 4
    ALTERADO_PI = 5
    VALIDADO_PI = 6
    INCONSISTENTE_RE = 7
    ALTERADO_RE = 8
    VALIDADO_RE = 9

    nome = models.CharField(verbose_name='Nome', max_length=50)

    class Meta:
        verbose_name = 'Situação de Inconsistência'
        verbose_name_plural = 'Situações de Inconsistência'

    def __str__(self):
        return self.nome


class CursoManager(models.Manager):
    def all(self):
        return self.filter()

    def filter_by_session(self, session):
        papel = session['role']['name'] if 'role' in session else None
        if papel in (Papel.REGISTRO_ACADEMICO, Papel.EXECUCAO_ACADEMICA):
            qs = self.filter(ativo=True, unidade_id=session['role']['scope_id'])
        elif papel == Papel.PESQUISADOR_INSTITUCIONAL:
            qs = self.filter(ativo=True, situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RA, unidade__instituicao_id=session['role']['scope_id'])
        elif papel == Papel.REITOR:
            qs = self.filter(ativo=True, situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_PI, unidade__instituicao_id=session['role']['scope_id'])
        else:
            qs = self
        if 'unidade' in session:
            qs = qs.filter(unidade_id=session['unidade']['pk'])
        return qs

    def com_justificativas_pendentes(self):
        return self.append('com_justificativa_nome_pendente')

    def com_justificativa_nome_pendente(self):
        return self.filter(
            justificativa_nome__isnull=False, justificativa_nome_aceita__isnull=True
        )


class Curso(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=36)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.CASCADE)
    nome = models.CharField(verbose_name='Nome', max_length=255)

    tipo = models.ForeignKey(TipoCurso, verbose_name='Tipo', on_delete=models.CASCADE)
    modalidade = models.ForeignKey(Modalidade, verbose_name='Modalidade', on_delete=models.CASCADE)
    eixo = models.ForeignKey(Eixo, verbose_name='Eixo', on_delete=models.CASCADE, null=True)
    curso_catalogo = models.ForeignKey(CursoCatalogo, verbose_name='Curso do Catálogo', on_delete=models.CASCADE, null=True, blank=True)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now_add=True)
    excluido = models.BooleanField(verbose_name='Excluído', default=False)

    situacao_inconsistencia = models.ForeignKey(SituacaoInconsistencia, verbose_name='Situação da Inconsistência', null=True, on_delete=models.CASCADE)
    justificativa_nome = models.ForeignKey(Justificativa, verbose_name='Justificativa do Nome', null=True, related_name='s1', on_delete=models.CASCADE)
    justificativa_nome_aceita = models.BooleanField(verbose_name='Justificativa do Nome Aceita', null=True)
    candidatos_catalogo = models.ManyToManyField(CursoCatalogo, verbose_name='Candidatos do Catálogo', related_name='candidatos')

    ativo = models.BooleanField(verbose_name='Ativo', default=False)

    objects = CursoManager()

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return self.nome

    @property
    def duracao_minima(self):
        return self.tipo.duracao_minima

    @property
    def duracao_maxima(self):
        return self.tipo.duracao_maxima

    def get_ciclos(self):
        return self.ciclo_set

    def get_alunos(self):
        return Aluno.objects.filter(
            id__in=self.ciclo_set.values_list('matricula__aluno', flat=True).distinct()
        )

    def get_candidados_catalogo(self):
        return self.candidatos_catalogo.all()

    def possui_nomenclatura_correta(self):
        palavras_reservadas = PalavrasReservadas.objects.all()
        tokens = self.nome.lower().split()
        for palavra_reservada in palavras_reservadas:
            if any(forma in tokens for forma in palavra_reservada.formas()):
                return False
        return True

    def atualizar_situacao_inconsistencia(self):
        Curso.objects.filter(pk=self.pk).update(situacao_inconsistencia_id=self.inconsistencia_set.calcular_situacao())

    @atomic()
    def reiniciar_inconsistencias(self):
        for inconsistencia in self.inconsistencia_set.all():
            inconsistencia.reiniciar()
        for ciclo in self.ciclo_set.filter(ativo=True):
            ciclo.reiniciar_inconsistencias()
        self.atualizar_situacao_inconsistencia()

    def identificar_candidatos_catalogo(self):
        if not self.candidatos_catalogo.exists():
            qs = CursoCatalogo.objects.none()
            for token in self.nome.split():
                if token.lower() not in ('com', 'sem', 'fic', 'de', 'para', 'em', 'no', 'na', 'do', 'da', 'dos', 'das', 'por', 'técnico', 'tecnico', 'curso', '-', 'e'):
                    qs = qs | CursoCatalogo.objects.filter(tipo=self.tipo, nome__icontains=token)
                    token_sem_acento = ''.join(c for c in unicodedata.normalize('NFD', token) if unicodedata.category(c) != 'Mn')
                    if token_sem_acento !=  token:
                        qs = qs | CursoCatalogo.objects.filter(tipo=self.tipo, nome__icontains=token)
            self.candidatos_catalogo.set(qs)
        return self.candidatos_catalogo.all()

    def has_get_justificativas_permission(self, user):
        return self.justificativa_nome

    def get_matriculas(self):
        return Matricula.objects.filter(ciclo__curso=self)

    def get_tipos_inconsistencias(self):
        return TipoInconsistencia.objects.filter(escopo__in=('Curso', 'Ciclo', 'Matrícula'))


class CicloManager(models.Manager):

    def all(self):
        return self.filter()

    def filter_by_session(self, session):
        papel = session['role']['name'] if 'role' in session else None
        if papel in (Papel.REGISTRO_ACADEMICO, Papel.EXECUCAO_ACADEMICA):
            qs = self.filter(ativo=True, curso__excluido=False, curso__unidade_id=session['role']['scope_id'], curso__situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RA)
        elif papel == Papel.PESQUISADOR_INSTITUCIONAL:
            qs = self.filter(ativo=True, curso__excluido=False, situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RA, curso__unidade__instituicao_id=session['role']['scope_id'], curso__situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_PI)
        elif papel == Papel.REITOR:
            qs = self.filter(ativo=True, curso__excluido=False, situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_PI, curso__unidade__instituicao_id=session['role']['scope_id'], curso__situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RE)
        else:
            qs = self
        if 'unidade' in session:
            qs = qs.filter(curso__unidade_id=session['unidade']['pk'])
        return qs

    def com_justificativas_pendentes(self):
        return self.append('com_justificativa_evasao_zero_pendente', 'com_justificativa_carga_horaria_pendente', 'com_justificativa_duracao_impropria_pendente')

    def com_justificativa_evasao_zero_pendente(self):
        return self.filter(
            justificativa_evasao_zero__isnull=False, justificativa_evasao_zero_aceita__isnull=True
        )

    def com_justificativa_carga_horaria_pendente(self):
        return self.filter(
            justificativa_carga_horaria__isnull=False, justificativa_carga_horaria_aceita__isnull=True
        )

    def com_justificativa_duracao_impropria_pendente(self):
        return self.filter(
            justificativa_duracao_impropria__isnull=False, justificativa_duracao_impropria_aceita__isnull=True
        )


class Ciclo(models.Model):
    curso = models.ForeignKey(Curso, verbose_name='Curso', on_delete=models.CASCADE)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    codigo = models.CharField(verbose_name='Código', max_length=36, db_index=True)
    data_inicio = models.DateField(verbose_name='Data de Início')
    data_fim = models.DateField(verbose_name='Data de Fim')
    vagas = models.IntegerField(verbose_name='Vagas')
    ingressantes = models.IntegerField(verbose_name='Ingressantes')
    inscritos = models.IntegerField(verbose_name='Inscritos')
    evadidos = models.IntegerField(verbose_name='Evadidos')
    tipo_oferta = models.ForeignKey(TipoOferta, verbose_name='Tipo de Oferta', null=True, on_delete=models.CASCADE)
    turnos = models.ManyToManyField(Turno, verbose_name='Turnos', blank=True)
    programa = models.ForeignKey(Programa, verbose_name='Programa', max_length=255, null=True, blank=True, on_delete=models.CASCADE)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now=False)
    excluido = models.BooleanField(verbose_name='Excluído', default=False)
    sg_etec = models.CharField(verbose_name='ETEC', max_length=3)
    carga_horaria = models.IntegerField(verbose_name='Carga Horária', help_text='Em horas')
    situacao_inconsistencia = models.ForeignKey(SituacaoInconsistencia, verbose_name='Situação da Inconsistência', null=True, on_delete=models.CASCADE)
    justificativa_evasao_zero = models.ForeignKey(Justificativa, verbose_name='Justificativa da Evasão 0%', null=True, related_name='s3', on_delete=models.CASCADE)
    justificativa_evasao_zero_aceita = models.BooleanField(verbose_name='Justificativa da Evasão 0% Aceita', null=True)
    justificativa_carga_horaria = models.ForeignKey(Justificativa, verbose_name='Justificativa da Carga-Horária', null=True, related_name='s2', on_delete=models.CASCADE)
    justificativa_carga_horaria_aceita = models.BooleanField(verbose_name='Justificativa da Carga-Horária Aceita', null=True)
    justificativa_duracao_impropria = models.ForeignKey(Justificativa, verbose_name='Justificativa da Duração', null=True, related_name='s4', on_delete=models.CASCADE)
    justificativa_duracao_impropria_aceita = models.BooleanField(verbose_name='Justificativa da Duração Aceita', null=True)
    ativo = models.BooleanField(verbose_name='Ativo', default=False)

    objects = CicloManager()

    class Meta:
        verbose_name = 'Ciclo'
        verbose_name_plural = 'Ciclos'

    def __str__(self):
        return self.nome

    def get_unidade(self):
        return self.curso.unidade

    def get_codigo_curso(self):
        return self.curso.codigo

    def get_curso(self):
        return self.curso

    def get_matriculas(self):
        return self.matricula_set.all()

    def atualizar_situacao_inconsistencia(self):
        Ciclo.objects.filter(pk=self.pk).update(situacao_inconsistencia_id=self.inconsistencia_set.calcular_situacao())

    @atomic()
    def reiniciar_inconsistencias(self):
        for inconsistencia in self.inconsistencia_set.all():
            inconsistencia.reiniciar()
        for matricula in self.matricula_set.filter(atendida=True):
            matricula.reiniciar_inconsistencias()
        self.atualizar_situacao_inconsistencia()

    def has_get_justificativas_permission(self, user):
        return self.justificativa_evasao_zero or self.justificativa_carga_horaria or self.justificativa_duracao_impropria

    def get_justificativas(self):
        return self.value_set(
            ('justificativa_evasao_zero', 'justificativa_evasao_zero_aceita'),
            ('justificativa_carga_horaria', 'justificativa_carga_horaria_aceita'),
            ('justificativa_duracao_impropria', 'justificativa_duracao_impropria_aceita'),
        )

    def get_tipos_inconsistencias(self):
        return TipoInconsistencia.objects.filter(escopo__in=('Ciclo', 'Matrícula'))


class VagasCiclo(models.Model):
    ciclo = models.ForeignKey(Ciclo, verbose_name='Ciclo', on_delete=models.CASCADE)

    vagas_regulares_ac = models.IntegerField(verbose_name='Vagas Ampla Concorrência', null=True)
    vagas_regulares_l1 = models.IntegerField(verbose_name='Vagas L1', null=True)
    vagas_regulares_l2 = models.IntegerField(verbose_name='Vagas L2', null=True)
    vagas_regulares_l5 = models.IntegerField(verbose_name='Vagas L5', null=True)
    vagas_regulares_l6 = models.IntegerField(verbose_name='Vagas L6', null=True)
    vagas_regulares_l9 = models.IntegerField(verbose_name='Vagas L9', null=True)
    vagas_regulares_l10 = models.IntegerField(verbose_name='Vagas L10', null=True)
    vagas_regulares_l13 = models.IntegerField(verbose_name='Vagas L13', null=True)
    vagas_regulares_l14 = models.IntegerField(verbose_name='Vagas L14', null=True)

    vagas_extras_ac = models.IntegerField(verbose_name='Vagas Extras Ampla Concorrência', null=True)
    vagas_extras_l1 = models.IntegerField(verbose_name='Vagas Extras L1', null=True)
    vagas_extras_l2 = models.IntegerField(verbose_name='Vagas Extras L2', null=True)
    vagas_extras_l5 = models.IntegerField(verbose_name='Vagas Extras L5', null=True)
    vagas_extras_l6 = models.IntegerField(verbose_name='Vagas Extras L6', null=True)
    vagas_extras_l9 = models.IntegerField(verbose_name='Vagas Extras L9', null=True)
    vagas_extras_l10 = models.IntegerField(verbose_name='Vagas Extras L10', null=True)
    vagas_extras_l13 = models.IntegerField(verbose_name='Vagas Extras L13', null=True)
    vagas_extras_l14 = models.IntegerField(verbose_name='Vagas Extras L14', null=True)

    class Meta:
        verbose_name = 'Vagas de Ciclo'
        verbose_name_plural = 'Vagas de Ciclo'

    def __str__(self):
        return 'Ocupação de Vagas do ciclo {}'.format(self.ciclo)

    def get_total(self):
        total = 0
        for tipo in ('ac', 'l1', 'l2', 'l5', 'l6', 'l9', 'l10', 'l13', 'l14'):
            total += getattr(self, 'vagas_regulares_{}'.format(tipo)) or 0
            total += getattr(self, 'vagas_extras_{}'.format(tipo)) or 0
        return total


class RacaManager(models.Manager):
    def all(self):
        return self.filter()


class Raca(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)

    objects = RacaManager()

    class Meta:
        verbose_name = 'Raça'
        verbose_name_plural = 'Raças'

    def __str__(self):
        return self.nome


class AlunoManager(models.Manager):
    def all(self):
        return self.filter()


class Aluno(models.Model):

    codigo = models.CharField(verbose_name='Código', max_length=20, db_index=True)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    cpf = models.CharField(verbose_name='CPF', max_length=16, null=True, db_index=True)
    data_nascimento = models.DateField(verbose_name='Data de Nascimento', null=True)
    sexo = models.CharField(verbose_name='Sexo', max_length=1)
    renda_per_capita = models.ForeignKey(FaixaRenda, verbose_name='Renda per Capta', null=True, blank=True, on_delete=models.CASCADE)
    raca = models.ForeignKey(Raca, verbose_name='Raça', null=True, blank=True, on_delete=models.CASCADE)
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now=False)

    objects = AlunoManager()

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'

    def __str__(self):
        return self.nome

    def get_matriculas(self):
        return self.matricula_set.all()


class SituacaoMatricula(models.Model):
    INTEGRALIZADA = 1
    TRANSF_INT = 2
    EM_CURSO = 3
    ABANDONO = 4
    NAO_DECLARADA = 5
    TRANSF_EXT = 6
    DESLIGADA = 7
    SUBSTITUIDO = 8
    EXCLUIDO = 9
    REPROVADA = 10
    CONCLUIDA = 11
    CANCELADA = 12

    SITUACOES_EVASAO = [
        ABANDONO, DESLIGADA, TRANSF_EXT, TRANSF_INT, REPROVADA, CANCELADA
    ]

    nome = models.CharField(verbose_name='Nome', max_length=25)

    class Meta:
        verbose_name = 'Situação de Matrícula'
        verbose_name_plural = 'Situações de Matrícula'

    def __str__(self):
        return self.nome

    def get_catetoria(self):
        if SituacaoMatricula.INTEGRALIZADA == self.id:
            return 'Concluintes'
        elif SituacaoMatricula.TRANSF_INT == self.id:
            return 'Evadidos'
        elif SituacaoMatricula.EM_CURSO == self.id:
            return 'Em Curso'
        elif SituacaoMatricula.ABANDONO == self.id:
            return 'Evadidos'
        elif SituacaoMatricula.TRANSF_EXT == self.id:
            return 'Evadidos'
        elif SituacaoMatricula.DESLIGADA == self.id:
            return 'Evadidos'
        elif SituacaoMatricula.REPROVADA == self.id:
            return 'Evadidos'
        elif SituacaoMatricula.CONCLUIDA == self.id:
            return 'Concluídos'
        elif SituacaoMatricula.CANCELADA == self.id:
            return 'Evadidos'
        return None


class MatriculaManager(models.Manager):
    def all(self):
        return self.filter()

    def filter_by_session(self, session):
        papel = session['role']['name'] if 'role' in session else None
        if papel in (Papel.REGISTRO_ACADEMICO, Papel.EXECUCAO_ACADEMICA):
            qs = self.filter(atendida=True, ciclo__curso__excluido=False, ciclo__curso__unidade_id=session['role']['scope_id'], ciclo__situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RA)
        elif papel == Papel.PESQUISADOR_INSTITUCIONAL:
            qs = self.filter(atendida=True, ciclo__curso__excluido=False, situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RA, ciclo__curso__unidade__instituicao_id=session['role']['scope_id'], ciclo__situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_PI)
        elif papel == Papel.REITOR:
            qs = self.filter(atendida=True, ciclo__curso__excluido=False, situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_PI, ciclo__curso__unidade__instituicao_id=session['role']['scope_id'], ciclo__situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RE)
        else:
            qs = self
        if 'unidade' in session:
            qs = qs.filter(ciclo__curso__unidade_id=session['unidade']['pk'])
        return qs

    def com_justificativas_pendentes(self):
        return self.append('com_justificativa_retencao_pendente')

    def com_justificativa_retencao_pendente(self):
        return self.filter(
            atendida=True, justificativa_retencao__isnull=False, justificativa_retencao_aceita__isnull=True
        )

    def atendidas(self, ano):
        qs = self.filter(ciclo__curso__excluido=False, ciclo__excluido=False
        ).exclude(
            situacao__in=(SituacaoMatricula.EXCLUIDO, SituacaoMatricula.SUBSTITUIDO)
        ).exclude(
            excluido=True
        ).filter(
            data_matricula__lt=date(ano + 1, 1, 1), ciclo__data_inicio__lt=date(ano + 1, 1, 1)
        )
        qs = qs.filter(situacao=SituacaoMatricula.EM_CURSO) | qs.exclude(situacao=SituacaoMatricula.EM_CURSO).filter(data_ocorrencia__gt=date(ano - 1, 12, 31))
        return qs

    def ingressantes(self, ano):
        return self.filter(
            ciclo__curso__excluido=False, ciclo__excluido=False,
            atendida=True, data_matricula__gt=date(ano - 1, 12, 31),
            ciclo__data_inicio__gt=date(ano - 1, 12, 31), ciclo__data_inicio__lt=date(ano + 1, 1, 1)
        )

    def sem_justificativas(self):
        return (
                self.filter(justificativa_retencao__isnull=True)
                .filter(ciclo__curso__justificativa_nome__isnull=True)
                .filter(ciclo__justificativa_evasao_zero__isnull=True)
                .filter(ciclo__justificativa_carga_horaria__isnull=True)
                .filter(ciclo__justificativa_duracao_impropria__isnull=True)
        )

    def com_justificativas_validas(self):
        return (
                self.filter(justificativa_retencao__isnull=False, justificativa_retencao_aceita=True) |
                self.filter(ciclo__curso__justificativa_nome__isnull=False, ciclo__curso__justificativa_nome_aceita=True) |
                self.filter(ciclo__justificativa_evasao_zero__isnull=False, ciclo__justificativa_evasao_zero_aceita=True) |
                self.filter(ciclo__justificativa_carga_horaria__isnull=False, ciclo__justificativa_carga_horaria_aceita=True) |
                self.filter(ciclo__justificativa_duracao_impropria__isnull=False, ciclo__justificativa_duracao_impropria_aceita=True)
        )


class Matricula(models.Model):
    aluno = models.ForeignKey(Aluno, verbose_name='Aluno', on_delete=models.CASCADE)
    ciclo = models.ForeignKey(Ciclo, verbose_name='Ciclo', on_delete=models.CASCADE)
    codigo = models.CharField(verbose_name='Código', max_length=20, db_index=True)
    ingressante = models.BooleanField(verbose_name='Ingressante', default=False)
    atendida = models.BooleanField(verbose_name='Atendida', default=False)
    data_matricula = models.DateField(verbose_name='Data da Matrícula')
    data_ocorrencia = models.DateField(verbose_name='Data da Ocorrência')
    data_cadastro = models.DateTimeField(verbose_name='Data do Cadastro', auto_now_add=True)
    data_atualizacao = models.DateTimeField(verbose_name='Data da Atualização', auto_now=False)
    excluido = models.BooleanField(verbose_name='Excluído', default=False)
    turno = models.ForeignKey(Turno, verbose_name='Turno', null=True, blank=True, on_delete=models.CASCADE)
    situacao = models.ForeignKey(SituacaoMatricula, verbose_name='Situação', on_delete=models.CASCADE)
    situacao_inconsistencia = models.ForeignKey(SituacaoInconsistencia, verbose_name='Situação da Inconsistência', null=True, on_delete=models.CASCADE)
    justificativa_retencao = models.ForeignKey(Justificativa, verbose_name='Justificativa da Retenção', null=True, related_name='s5', on_delete=models.CASCADE)
    justificativa_retencao_aceita = models.BooleanField(verbose_name='Justificativa da Retenção Aceita', null=True)

    objects = MatriculaManager()

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.aluno)

    def get_unidade(self):
        return self.ciclo.curso.unidade

    def get_ciclo(self):
        return '{} - {}'.format(self.ciclo.codigo, self.ciclo)

    def atualizar_situacao_inconsistencia(self):
        Matricula.objects.filter(pk=self.pk).update(situacao_inconsistencia_id=self.inconsistencia_set.calcular_situacao())

    @atomic()
    def reiniciar_inconsistencias(self):
        for inconsistencia in self.inconsistencia_set.all():
            inconsistencia.reiniciar()
        self.atualizar_situacao_inconsistencia()

    def has_get_justificativas_permission(self, user):
        return self.justificativa_retencao

    def get_matriculas(self):
        return Matricula.objects.filter(pk=self.pk)

    def get_tipos_inconsistencias(self):
        return TipoInconsistencia.objects.filter(escopo='Matrícula')


class InconsistenciaManager(models.Manager):

    def all(self):
        return self.order_by('id')

    def aguardando_validacao_ra(self):
        return self.all().filter(data_validacao_ra__isnull=True)

    def aguardando_validacao_pi(self):
        return self.all().filter(data_validacao_ra__isnull=False, data_validacao_pi__isnull=True)

    def aguardando_validacao_re(self):
        return self.all().filter(data_validacao_ra__isnull=False, data_validacao_pi__isnull=False, data_validacao_re__isnull=True)

    def finalizadas(self):
        return self.all().filter(data_validacao_ra__isnull=False, data_validacao_pi__isnull=False, data_validacao_re__isnull=False)

    def ignoradas(self):
        return self.all().filter(ignorada=True)

    def get_queryset_para_monitoramento(self):
        return self.filter(pk__lte=20000).filter(ignorada=False)

    def total_por_situacao_tipo(self):
        return Statistics(self.get_queryset_para_monitoramento()).count('situacao')

    def total_por_situacao_escopo(self):
        return Statistics(self.get_queryset_para_monitoramento()).count('situacao', 'tipo__escopo')

    def total_por_situacao_instituicao(self):
        return Statistics(self.get_queryset_para_monitoramento()).count('situacao', 'unidade__instituicao')

    def total_por_situacao_unidade(self):
        return Statistics(self.get_queryset_para_monitoramento()).count('situacao', 'unidade')

    def get_percentual_validado(self):
        if self.exists():
            return int(self.get_queryset_para_monitoramento().finalizadas().count() * 100.0 / self.count())
        return 0

    def filter_by_session(self, session, local=True):
        if 'role' in session and session['role']['name'] in (Papel.REGISTRO_ACADEMICO, Papel.EXECUCAO_ACADEMICA):
            qs = self.filter(unidade_id=session['role']['scope_id'])
        elif 'role' in session and session['role']['name'] in (Papel.REITOR, Papel.PESQUISADOR_INSTITUCIONAL, Papel.GESTAO_DE_PESSOAS, Papel.RECURSOS_HUMANOS):
            qs = self.filter(unidade__instituicao_id=session['role']['scope_id'])
        else:
            qs = self
        if 'unidade' in session and local:
            qs = qs.filter(unidade_id=session['unidade']['pk'])
        return qs

    def calcular_situacao(self):
        situacoes = self.values_list('situacao_id', flat=True)[0:17]
        if SituacaoInconsistencia.INCONSISTENTE_RA in situacoes:
            pk = SituacaoInconsistencia.INCONSISTENTE_RA
        elif SituacaoInconsistencia.INCONSISTENTE_PI in situacoes:
            pk = SituacaoInconsistencia.INCONSISTENTE_PI
        elif SituacaoInconsistencia.INCONSISTENTE_RE in situacoes:
            pk = SituacaoInconsistencia.INCONSISTENTE_RE
        elif SituacaoInconsistencia.ALTERADO_RA in situacoes:
            pk = SituacaoInconsistencia.ALTERADO_RA
        elif SituacaoInconsistencia.ALTERADO_PI in situacoes:
            pk = SituacaoInconsistencia.ALTERADO_PI
        elif SituacaoInconsistencia.ALTERADO_RE in situacoes:
            pk = SituacaoInconsistencia.ALTERADO_RE
        elif situacoes == {SituacaoInconsistencia.VALIDADO_RA}:
            pk = SituacaoInconsistencia.VALIDADO_RA
        elif situacoes == {SituacaoInconsistencia.VALIDADO_PI}:
            pk = SituacaoInconsistencia.VALIDADO_PI
        elif situacoes == {SituacaoInconsistencia.VALIDADO_RE}:
            pk = SituacaoInconsistencia.VALIDADO_RE
        return pk


class Inconsistencia(models.Model):

    INCONSISTENTE = SituacaoInconsistencia.INCONSISTENTE_RA, SituacaoInconsistencia.INCONSISTENTE_PI, SituacaoInconsistencia.INCONSISTENTE_RE
    ALTERADA = SituacaoInconsistencia.ALTERADO_RA, SituacaoInconsistencia.ALTERADO_PI, SituacaoInconsistencia.ALTERADO_RE
    VALIDADA = SituacaoInconsistencia.VALIDADO_RA, SituacaoInconsistencia.VALIDADO_PI, SituacaoInconsistencia.VALIDADO_RE

    configuracao = models.ForeignKey(Configuracao, verbose_name='Configuração', on_delete=models.CASCADE)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.CASCADE)

    tipo = models.ForeignKey(TipoInconsistencia, verbose_name='Tipo', on_delete=models.CASCADE)

    data_geracao = models.DateTimeField(verbose_name='Data da Geração', auto_now=True)
    situacao = models.ForeignKey(SituacaoInconsistencia, verbose_name='Situação', null=True, on_delete=models.CASCADE)

    responsavel_validacao_ra = models.ForeignKey(Pessoa, verbose_name='Responsável pela Validação RA', null=True, related_name='inconsistencias_ra', on_delete=models.CASCADE)
    responsavel_validacao_pi = models.ForeignKey(Pessoa, verbose_name='Responsável pela Validação PI', null=True, related_name='inconsistencias_pi', on_delete=models.CASCADE)
    responsavel_validacao_re = models.ForeignKey(Pessoa, verbose_name='Responsável pela Validação RE', null=True, related_name='inconsistencias_re', on_delete=models.CASCADE)

    data_validacao_ra = models.DateTimeField(verbose_name='Data da Validação RA', null=True)
    data_validacao_pi = models.DateTimeField(verbose_name='Data da Validação PI', null=True)
    data_validacao_re = models.DateTimeField(verbose_name='Data da Validação RE', null=True)

    curso = models.ForeignKey(Curso, verbose_name='Curso', null=True, on_delete=models.CASCADE)
    ciclo = models.ForeignKey(Ciclo, verbose_name='Ciclo', null=True, on_delete=models.CASCADE)
    matricula = models.ForeignKey(Matricula, verbose_name='Matrícula', null=True, on_delete=models.CASCADE)
    unidadeorganizacional = models.ForeignKey('pnp.UnidadeOrganizacional', verbose_name='Unidade Organizacional', null=True, on_delete=models.CASCADE)
    servidor = models.ForeignKey('pnp.Servidor', verbose_name='Servidor', null=True, on_delete=models.CASCADE)

    ignorada = models.BooleanField(verbose_name='Ignorada', default=False)
    alteracao_anterior = models.BooleanField(verbose_name='Alterado Anteriormente', default=False)

    objects = InconsistenciaManager()


    class Meta:
        verbose_name = 'Inconsistência'
        verbose_name_plural = 'Inconsistências'

    def __str__(self):
        return 'Regra {} - {} (#{})'.format(self.tipo_id, self.tipo, self.pk)

    def get_escopo(self):
        if self.curso_id:
            return 'Curso'
        elif self.ciclo_id:
            return 'Ciclo'
        elif self.matricula_id:
            return 'Matrícula'
        elif self.unidadeorganizacional_id:
            return 'Unidade Organizacional'
        elif self.servidor_id:
            return 'Servidor'

    def get_referencia(self):
        return self.curso or self.ciclo or self.matricula or self.unidadeorganizacional or self.servidor

    def set_referencia(self, referencia):
        if isinstance(referencia, Curso):
            self.curso = referencia
        elif isinstance(referencia, Ciclo):
            self.ciclo = referencia
        elif isinstance(referencia, Matricula):
            self.matricula = referencia

    def get_etapas(self):
        return [
            ('Geração', self.data_geracao),
            ('Validação RA', self.data_validacao_ra),
            ('Validação PI', self.data_validacao_pi),
            ('Validação RE', self.data_validacao_re),
        ]

    def get_status(self):
        if self.situacao_id in (SituacaoInconsistencia.INCONSISTENTE_RA, SituacaoInconsistencia.INCONSISTENTE_PI, SituacaoInconsistencia.INCONSISTENTE_RE):
            return 'danger', self.situacao.nome
        elif self.situacao_id in (SituacaoInconsistencia.ALTERADO_RA, SituacaoInconsistencia.ALTERADO_PI, SituacaoInconsistencia.ALTERADO_RE):
            return 'warning', self.situacao.nome
        elif self.situacao_id in (SituacaoInconsistencia.VALIDADO_RA, SituacaoInconsistencia.VALIDADO_PI, SituacaoInconsistencia.VALIDADO_RE):
            return 'success', self.situacao.nome
        return None

    def has_delete_permission(self, user):
        return False

    def has_get_alteracoes_permission(self, user):
        return True

    def get_alteracoes_atuais(self):
        return self.alteracao_set.all()

    def get_historico_alteracoes(self):
        return self.historicoalteracao_set.all()

    def get_historico_situacao(self):
        return self.historicosituacao_set.all()

    def get_justificativa(self):
        if self.tipo_id == TipoInconsistencia.NOMENCLATURA_CURSO:
            return self.get_referencia().justificativa_nome
        elif self.tipo_id == TipoInconsistencia.EVASAO_ZERO:
            return self.get_referencia().justificativa_evasao_zero
        elif self.tipo_id == TipoInconsistencia.CARGA_HORARIA_INSUFICIENTE:
            return self.get_referencia().justificativa_carga_horaria
        elif self.tipo_id == TipoInconsistencia.DURACAO_CICLO:
            return self.get_referencia().justificativa_duracao_impropria
        elif self.tipo_id == TipoInconsistencia.RETENCAO_CRITICA:
            return self.get_referencia().justificativa_retencao
        elif self.tipo_id == TipoInconsistencia.RETENCAO_FIC:
            return self.get_referencia().justificativa_retencao
        return None

    def pode_ser_modificada(self, papel, scope_id):
        if papel:
            if papel in (Papel.REGISTRO_ACADEMICO, Papel.EXECUCAO_ACADEMICA):
                return self.unidade_id == scope_id
            elif papel in (Papel.GESTAO_DE_PESSOAS, Papel.RECURSOS_HUMANOS):
                if self.unidadeorganizacional_id:
                    codigo = Instituicao.objects.filter(id=scope_id).values_list('codigo', flat=True).first()
                    return self.unidadeorganizacional.codigo.startswith(codigo[0:5])
                elif self.servidor_id:
                    return self.servidor.lotacao.unidade.instituicao_id == scope_id
            else:
                return self.unidade.instituicao_id == scope_id
        return False

    def pode_ser_resolvida(self, request):
        if self.situacao_id not in (SituacaoInconsistencia.INCONSISTENTE_RA, SituacaoInconsistencia.INCONSISTENTE_PI, SituacaoInconsistencia.INCONSISTENTE_RE):
            return False
        if request.user.is_superuser:
            return True
        pode_ser_resolvida = False
        papel = request.session['role']['name'] if 'role' in request.session else None
        if self.situacao_id == SituacaoInconsistencia.INCONSISTENTE_RA:
            if self.unidadeorganizacional_id or self.servidor_id:
                pode_ser_resolvida = papel in (Papel.GESTAO_DE_PESSOAS, Papel.RECURSOS_HUMANOS)
            else:
                pode_ser_resolvida = papel in (Papel.REGISTRO_ACADEMICO, Papel.EXECUCAO_ACADEMICA)
        elif self.situacao_id == SituacaoInconsistencia.INCONSISTENTE_PI:
            pode_ser_resolvida = papel in (Papel.PESQUISADOR_INSTITUCIONAL,)
        elif self.situacao_id == SituacaoInconsistencia.INCONSISTENTE_RE:
            pode_ser_resolvida = papel in (Papel.REITOR,)
        return pode_ser_resolvida and self.pode_ser_modificada(papel, request.session['role']['scope_id'])

    def alterar(self, *alteracoes):
        excluido = self.get_referencia().excluido
        for alteracao in alteracoes:
            alteracao.aplicar()
        if self.situacao_id == SituacaoInconsistencia.INCONSISTENTE_RA:
            self.situacao_id = SituacaoInconsistencia.ALTERADO_RA
        elif self.situacao_id == SituacaoInconsistencia.INCONSISTENTE_PI:
            self.situacao_id = SituacaoInconsistencia.ALTERADO_PI
        elif self.situacao_id == SituacaoInconsistencia.INCONSISTENTE_RE:
            self.situacao_id = SituacaoInconsistencia.ALTERADO_RE
        self.save()
        if self.get_referencia().excluido and not excluido:
            self.ignorar_inconsistencias_relacionadas(True)

    def pode_ser_restaurada(self, request):
        if request.user.is_superuser:
            return True
        pode_ser_resolvida = False
        papel = request.session['role']['name'] if 'role' in request.session else None
        if self.situacao_id == SituacaoInconsistencia.ALTERADO_RA:
            if self.unidadeorganizacional_id or self.servidor_id:
                pode_ser_resolvida = papel in (Papel.GESTAO_DE_PESSOAS,)
            else:
                pode_ser_resolvida = papel in (Papel.REGISTRO_ACADEMICO, Papel.EXECUCAO_ACADEMICA)
        if self.situacao_id == SituacaoInconsistencia.VALIDADO_RA:
            if self.unidadeorganizacional_id or self.servidor_id:
                pode_ser_resolvida = papel in (Papel.REITOR,)
            else:
                pode_ser_resolvida = papel in (Papel.PESQUISADOR_INSTITUCIONAL,)
        if self.situacao_id == SituacaoInconsistencia.ALTERADO_PI:
            pode_ser_resolvida = papel in (Papel.PESQUISADOR_INSTITUCIONAL,)
        if self.situacao_id in (SituacaoInconsistencia.VALIDADO_PI, SituacaoInconsistencia.ALTERADO_RE):
            pode_ser_resolvida = papel in (Papel.REITOR,)
        return pode_ser_resolvida and self.pode_ser_modificada(papel, request.session['role']['scope_id'])

    def restaurar(self, user):
        excluido = self.get_referencia().excluido
        for alteracao in self.alteracao_set.all():
            alteracao.restaurar()
            alteracao.delete()
        if self.situacao_id == SituacaoInconsistencia.ALTERADO_RA:
            self.situacao_id = SituacaoInconsistencia.INCONSISTENTE_RA
        elif self.situacao_id == SituacaoInconsistencia.VALIDADO_RA:
            if self.unidadeorganizacional_id or self.servidor_id:
                self.situacao_id = SituacaoInconsistencia.INCONSISTENTE_RE
            else:
                self.situacao_id = SituacaoInconsistencia.INCONSISTENTE_PI
        elif self.situacao_id == SituacaoInconsistencia.ALTERADO_PI:
            self.situacao_id = SituacaoInconsistencia.INCONSISTENTE_PI

        elif self.situacao_id in (SituacaoInconsistencia.VALIDADO_PI, SituacaoInconsistencia.ALTERADO_RE):
            self.situacao_id = SituacaoInconsistencia.INCONSISTENTE_RE
        self.save()
        if excluido and not type(self.get_referencia()).objects.get(pk=self.get_referencia().pk).excluido:
            self.ignorar_inconsistencias_relacionadas(False)

    def ignorar_inconsistencias_relacionadas(self, ignorada):
        qs = Inconsistencia.objects.exclude(pk=self.pk)
        if self.curso:
            qs.filter(curso=self.curso).update(ignorada=ignorada)
            qs.filter(ciclo__curso=self.curso).update(ignorada=ignorada)
            qs.filter(matricula__ciclo__curso=self.curso).update(ignorada=ignorada)
        if self.ciclo:
            qs.filter(ciclo=self.ciclo).update(ignorada=ignorada)
            qs.filter(matricula__ciclo=self.ciclo).update(ignorada=ignorada)
        if self.matricula:
            qs.filter(matricula=self.matricula).update(ignorada=ignorada)
        if self.unidadeorganizacional:
            qs.filter(unidadeorganizacional=self.unidadeorganizacional).update(ignorada=ignorada)
            qs.filter(servidor__lotacao=self.unidadeorganizacional).update(ignorada=ignorada)
        if self.servidor:
            qs.filter(servidor=self.servidor).update(ignorada=ignorada)

    def pode_ser_reiniciada(self, request):
        return request.user.is_superuser

    def reiniciar(self):
        for alteracao in self.alteracao_set.all():
            alteracao.restaurar()
            alteracao.delete()
        self.situacao_id = SituacaoInconsistencia.ALTERADO_RA if self.alteracao_anterior else SituacaoInconsistencia.INCONSISTENTE_RA
        self.justificativa = None
        self.responsavel_validacao_ra = None
        self.responsavel_validacao_pi = None
        self.responsavel_validacao_re = None
        self.data_validacao_ra = None
        self.data_validacao_pi = None
        self.data_validacao_re = None
        self.save()

    def get_descricao_recibo(self):
        if self.tipo_id == TipoInconsistencia.ASSOCIACAO_CATALOGO:
            info = f'Curso:{self.curso_id}-{self.curso.nome};Catálogo:{self.curso.curso_catalogo_id}'
        if self.tipo_id == TipoInconsistencia.EVASAO_ZERO:
            info = f'Ciclo:{self.ciclo.codigo};Evadidos:{self.ciclo.evadidos};'
            if self.ciclo.evadidos and not self.ciclo.excluido: # Se existem alunos evadidos e o ciclo não foi excluído
                qs = self.ciclo.matricula_set.filter(situacao__in=SituacaoMatricula.SITUACOES_EVASAO)
                alunos_evadidos = ','.join(qs.values_list('codigo', flat=True))
                info = f"{info}Matrículas:{alunos_evadidos};"
            else: # Não existem alunos evadidos, logo ou foi justificado ou excluído
                justificativa = "Ciclo Excluído" if self.ciclo.excluido else self.ciclo.justificativa_evasao_zero
                info = f"{info}Jusitificativa: {justificativa}"
        return f'Regra:{self.tipo_id};Hora:{datetime.now().strftime("%d/%m/%Y %H:%M")};{info}'

class HistoricoAlteracao(models.Model):
    user = models.ForeignKey('auth.User', verbose_name='Usuário', null=True, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(verbose_name='Data/Hora', null=True)
    inconsistencia = models.ForeignKey(Inconsistencia, verbose_name='Inconsistência', on_delete=models.CASCADE)
    descricao = models.CharField(verbose_name='Descrição', max_length=512)

    class Meta:
        verbose_name = 'Histórico de Alteração'
        verbose_name_plural = 'Histórico de Alterações'


class Alteracao(models.Model):
    inconsistencia = models.ForeignKey(Inconsistencia, verbose_name='Inconsistência', on_delete=models.CASCADE)
    objeto = models.GenericField(verbose_name='Objeto', null=True)
    campo = models.CharField(verbose_name='Campo', max_length=255)
    valor_anterior = models.GenericField(verbose_name='Valor Anterior', null=True)
    valor_atual = models.GenericField(verbose_name='Valor Atual', null=True)
    usuario = models.ForeignKey('auth.user', verbose_name='Usuário', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Alteração'
        verbose_name_plural = 'Alterações'

    def get_campo(self):
        objeto = self.objeto._wrapped_obj if self.objeto else self.inconsistencia.get_referencia()
        field = [f for f in type(objeto)._meta.get_fields() if f.name == self.campo][0]
        return field.verbose_name

    def get_objeto(self):
        objeto = self.objeto or self.inconsistencia.get_referencia()
        if type(objeto).__name__ == 'GenericModelWrapper':
            return objeto._wrapped_obj
        return objeto

    def get_valor_atual(self):
        if type(self.valor_atual).__name__ == 'GenericModelWrapper':
            return self.valor_atual._wrapped_obj
        return self.valor_atual

    def aplicar(self):
        valor_atual = self.get_valor_atual()
        if self.campo in [f.name for f in type(self.inconsistencia.get_referencia())._meta.local_many_to_many]:
            getattr(self.inconsistencia.get_referencia(), self.campo).set(Turno.objects.filter(pk__in=valor_atual))
        else:
            objeto = self.get_objeto()
            setattr(objeto, self.campo, valor_atual)
            objeto.save()
        self.gerar_historico()

    def get_turnos(self, valor):
        if isinstance(valor, str):
            valor = json.loads(valor)
        elif str(valor) == 'pnp.Turno.None':
            valor = []
        elif hasattr(valor, 'all'):
            valor = valor.all().values_list('pk', flat=True)
        return '[{}]'.format(','.join([str(x) for x in Turno.objects.filter(pk__in=valor)]))

    def gerar_historico(self, restauracao=False):
        valor_atual = 'nulo' if self.valor_anterior is None else self.valor_anterior
        valor_anterior = 'nulo' if self.valor_atual is None else self.valor_atual
        if self.campo == 'turnos':
            valor_atual = self.get_turnos(valor_atual)
            valor_anterior = self.get_turnos(valor_anterior)
        if restauracao:
            valor_atual, valor_anterior = valor_anterior, valor_atual
        if isinstance(valor_atual, bool):
            valor_atual = 'SIM' if valor_atual else 'NÃO'
        if isinstance(valor_anterior, bool):
            valor_anterior = 'SIM' if valor_anterior else 'NÃO'
        if isinstance(valor_atual, date) or isinstance(valor_atual, datetime):
            valor_atual = valor_atual.strftime('%d/%m/%Y')
        if isinstance(valor_anterior, date) or isinstance(valor_anterior, datetime):
            valor_anterior = valor_anterior.strftime('%d/%m/%Y')
        descricao = 'Alterou o valor do campo "{}" referente a "{}" de "{}" para "{}"'.format(
            self.get_campo(), self.get_objeto(), valor_atual, valor_anterior)
        HistoricoAlteracao.objects.create(user=self.usuario, data_hora=datetime.now(), inconsistencia=self.inconsistencia, descricao=descricao)

    def restaurar(self):
        objeto = self.get_objeto()
        if self.campo in [f.name for f in type(self.inconsistencia.get_referencia())._meta.local_many_to_many]:
            getattr(objeto, self.campo).set({})
        else:
            type(objeto).objects.filter(pk=objeto.pk).update(**{self.campo: self.valor_anterior})
        self.gerar_historico(restauracao=True)

    def save(self, *args, **kwargs):
        objeto = self.get_objeto()
        self.valor_anterior = getattr(objeto, self.campo)
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Alteração {}'.format(self.pk)


class CotaManager(models.Manager):

    def all(self):
        return self.filter()


class Cota(models.Model):
    sigla = models.CharField(verbose_name='Sigla', max_length=255)
    descricao = models.CharField(verbose_name='Descrição', max_length=255)

    objects = CotaManager()

    class Meta:
        verbose_name = 'Cota'
        verbose_name_plural = 'Descrições das Cotas'

    def __str__(self):
        return self.sigla


class RegraAssociacaoProgramaManager(models.Manager):

    def all(self):
        return self.filter()


class RegraAssociacaoPrograma(models.Model):
    modalidade = models.ForeignKey(Modalidade, verbose_name='Modalidade', on_delete=models.CASCADE)
    tipos_curso = models.ManyToManyField(TipoCurso, verbose_name='Tipos de Cursos')
    programas = models.ManyToManyField(Programa, verbose_name='Programas')

    objects = RegraAssociacaoProgramaManager()

    class Meta:
        verbose_name = 'Regra de Associação a Programas'
        verbose_name_plural = 'Regras de Associação a Programas'

    def __str__(self):
        return 'Configuração de Associação de Programa {}'.format(self.pk)


class ArquivoManager(models.Manager):
    def all(self):
        return self.order_by('id')


class Arquivo(models.Model):
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.CASCADE)
    numero_linhas = models.IntegerField(verbose_name='Número de Linhas')
    registros_ativos_identificados = models.BooleanField(verbose_name='Registros Ativos Identificados', default=False)
    configuracao = models.ForeignKey(Configuracao, verbose_name='Configuração', on_delete=models.CASCADE)
    data_processamento = models.DateTimeField(verbose_name='Data do Processamento', null=True)
    total_processado = models.IntegerField(verbose_name='Número de Linhas Processadas com Sucesso', default=0)
    arquivo = models.FileField(null=True)

    objects = ArquivoManager()

    def get_numero_linhas(self):
        n = self.linhaarquivo_set.count()
        return ('success', n) if n else ('warning', 'Aguardando processamento')

    def get_sigla(self):
        return self.unidade.instituicao.sigla

    def __str__(self):
        return f"Arquivo {self.configuracao}"

    def get_linhas(self):
        return self.linhaarquivo_set.all()

    def get_percentual_carregado(self):
        if self.arquivo:
            return self.numero_linhas
        return int(self.linhaarquivo_set.count() * 100 // self.numero_linhas ) if self.numero_linhas else 0

    def get_percentual_processado(self):
        return int(self.total_processado * 100 // self.numero_linhas) if self.numero_linhas else 0

    def atualizar_total_processado(self):
        self.total_processado = self.linhaarquivo_set.processadas_com_sucesso().count()
        if self.total_processado == self.numero_linhas:
            self.data_processamento = datetime.now()
        self.save()


class TipoErroCargaManager(models.Manager):
    def all(self):
        return self.filter()


class TipoErroCarga(models.Model):
    GENERICO = 1
    VIOLACAO_UNICIDADE = 2
    UNIDADE_INEXISTENTE = 4
    TIPO_CURSO = 5
    NUMERO_COLUNAS = 6

    nome = models.CharField('Nome', max_length=255)

    objects = TipoErroCargaManager()

    class Meta:
        verbose_name = 'Tipo de Erro de Carga'
        verbose_name_plural = 'Tipos de Erros de Carga'

    def __str__(self):
        return self.nome


class LinhaArquivoManager(models.Manager):

    def all(self):
        return self.order_by('id')

    def aguardando_processamento(self):
        return self.all().filter(data_processamento__isnull=True)

    def processadas_com_sucesso(self):
        return self.all().filter(data_processamento__isnull=False, erro__isnull=True)

    def processadas_sem_sucesso(self):
        return self.all().filter(data_processamento__isnull=False, erro__isnull=False)

    def get_percentual_processado(self):
        if self.exists():
            return int(self.filter(data_processamento__isnull=False).count()*100/self.count())
        return 0


class LinhaArquivo(models.Model):
    arquivo = models.ForeignKey(Arquivo, verbose_name='Arquivo', on_delete=models.CASCADE)
    numero = models.IntegerField(verbose_name='Número')
    conteudo = models.TextField(verbose_name='Conteúdo')
    data_processamento = models.DateTimeField(verbose_name='Data do Processamento', null=True)
    tipo_erro = models.ForeignKey(TipoErroCarga, verbose_name='Tipo de Erro', null=True, on_delete=models.CASCADE)
    erro = models.TextField(verbose_name='Erro', null=True)

    objects = LinhaArquivoManager()

    class Meta:
        verbose_name = 'Linha do Arquivo'
        verbose_name_plural = 'Linhas do Arquivo'
        ordering = 'pk', 'arquivo'

    def __str__(self):
        return 'Linha {}'.format(self.numero)

    def get_erro(self):
        return self.erro

    def get_conteudo(self):
        from .inconsistencias.carga import COLUMNS
        linha = list()
        tokens = self.conteudo.split(';')
        for idx, column in COLUMNS.items():
            linha.append((idx, column, tokens[idx]))
        return self.id, linha


class PalavrasReservadasManager(models.Manager):
    def all(self):
        return self.filter()


class PalavrasReservadas(models.Model):
    singular = models.CharField(verbose_name='Singular', max_length=255)
    plural = models.CharField(verbose_name="Plural", max_length=255)

    objects = PalavrasReservadasManager()

    class Meta:
        verbose_name = 'Palavras Reservadas'
        verbose_name_plural = 'Palavras Reservadas'

    def __str__(self):
        return self.singular

    def formas(self):
        return (self.singular.lower(), self.plural.lower())


class NivelEnsinoServidor(models.Model):
    nome = models.CharField(verbose_name='Nome', max_length=255)

    class Meta:
        verbose_name = 'Nível de Ensino de Servidor'
        verbose_name_plural = 'Níveis de Ensino dos Servidores'

    def __str__(self):
        return self.nome


class UnidadeOrganizacionalManager(models.Manager):
    def all(self):
        return self.order_by('codigo')

    def filter_by_session(self, session):
        papel = session['role']['name'] if 'role' in session else None
        if papel in (Papel.GESTAO_DE_PESSOAS, Papel.RECURSOS_HUMANOS):
            codigo = Instituicao.objects.filter(id=session['role']['scope_id']).values_list('codigo', flat=True).first()
            qs = self.filter(codigo__startswith=codigo[0:5])
            qs = qs.filter(unidade__isnull=True) | qs.filter(unidade__instituicao__codigo=codigo)
        elif papel == Papel.REITOR:
            qs = self.filter(situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RA, unidade__instituicao_id=session['role']['scope_id'])
        else:
            qs = self
        if 'unidade' in session:
            qs = qs.filter(unidade_id=session['unidade']['pk'])
        return qs


class UnidadeOrganizacional(models.Model):
    codigo = models.CharField(verbose_name='Código', db_index=True, max_length=255)
    instituicao = models.ForeignKey(Instituicao, verbose_name='Instituição', null=True, on_delete=models.CASCADE)
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', null=True, on_delete=models.CASCADE)
    situacao_inconsistencia = models.ForeignKey(SituacaoInconsistencia, verbose_name='Situação da Inconsistência', null=True, on_delete=models.CASCADE)
    excluido = models.BooleanField(verbose_name='Excluído', default=False)
    objects = UnidadeOrganizacionalManager()

    class Meta:
        verbose_name = 'Unidade Organizacional'
        verbose_name_plural = 'Unidades Organizacionais'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.unidade) if self.unidade else self.codigo

    def atualizar_situacao_inconsistencia(self):
        UnidadeOrganizacional.objects.filter(pk=self.pk).update(situacao_inconsistencia_id=self.inconsistencia_set.calcular_situacao())

    @atomic()
    def reiniciar_inconsistencias(self):
        for inconsistencia in self.inconsistencia_set.all():
            inconsistencia.reiniciar()
        self.atualizar_situacao_inconsistencia()


class EscolaridadeManager(models.Manager):
    def all(self):
        return self.order_by('codigo')


class Escolaridade(models.Model):
    codigo = models.CharField(verbose_name='Código', db_index=True, max_length=255)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    nivel_ensino = models.ForeignKey(NivelEnsinoServidor, verbose_name='Nível de Ensino', null=True, on_delete=models.CASCADE)

    objects = EscolaridadeManager()

    class Meta:
        verbose_name = 'Escolaridade'
        verbose_name_plural = 'Escolaridades'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.nome)

    def atualizar_situacao_inconsistencia(self):
        Escolaridade.objects.filter(pk=self.pk).update(situacao_inconsistencia_id=self.inconsistencia_set.calcular_situacao())

    @atomic()
    def reiniciar_inconsistencias(self):
        for inconsistencia in self.inconsistencia_set.all():
            inconsistencia.reiniciar()
        self.atualizar_situacao_inconsistencia()


class TitulacaoManager(models.Manager):
    def all(self):
        return self.order_by('codigo')


class Titulacao(models.Model):
    codigo = models.CharField(verbose_name='Código', db_index=True, max_length=255)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    nivel_ensino = models.ForeignKey(NivelEnsinoServidor, verbose_name='Nível de Ensino', null=True, on_delete=models.CASCADE)

    objects = TitulacaoManager()

    class Meta:
        verbose_name = 'Titulação'
        verbose_name_plural = 'Titulações'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.nome)


class RscManager(models.Manager):
    def all(self):
        return self.order_by('sigla')


class Rsc(models.Model):
    sigla = models.CharField(verbose_name='Nome', db_index=True, max_length=255)

    objects = RscManager()

    class Meta:
        verbose_name = 'RSC'
        verbose_name_plural = 'RSCs'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.nome)


class GrupoCargoEmpregoManager(models.Manager):
    def all(self):
        return self.order_by('codigo')


class GrupoCargoEmprego(models.Model):
    codigo = models.CharField(verbose_name='Código', db_index=True, max_length=255)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    categoria = models.CharField(verbose_name='Categoria', choices=[['T', 'Técnico Administrativo'], ['D', 'Docente']], default='T', null=True, max_length=255)

    objects = GrupoCargoEmpregoManager()

    class Meta:
        verbose_name = 'Grupo do Cargo'
        verbose_name_plural = 'Grupos dos Cargos'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.nome)


class CargoEmpregoManager(models.Manager):
    def all(self):
        return self.order_by('codigo')


class CargoEmprego(models.Model):
    codigo = models.CharField(verbose_name='Código', db_index=True, max_length=255)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    grupo = models.ForeignKey(GrupoCargoEmprego, verbose_name='Grupo', on_delete=models.CASCADE)
    nivel_ensino = models.ForeignKey(NivelEnsinoServidor, verbose_name='Nível de Ensino', null=True, on_delete=models.CASCADE)

    objects = CargoEmpregoManager()

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.nome)


class SituacaoServidorManager(models.Manager):
    def all(self):
        return self.order_by('codigo')


class SituacaoServidor(models.Model):
    codigo = models.CharField(verbose_name='Código', db_index=True, max_length=255)
    nome = models.CharField(verbose_name='Nome', max_length=255)

    objects = SituacaoServidorManager()

    class Meta:
        verbose_name = 'Situação do Servidor'
        verbose_name_plural = 'Situações dos Servidores'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.nome)


class JornadaTrabalhoManager(models.Manager):
    def all(self):
        return self.order_by('codigo')


class JornadaTrabalho(models.Model):
    codigo = models.CharField(verbose_name='Código', db_index=True, max_length=255)
    nome = models.CharField(verbose_name='Nome', max_length=255)

    objects = JornadaTrabalhoManager()

    class Meta:
        verbose_name = 'Jornada de Trabalho'
        verbose_name_plural = 'Jornadas de Trabalho'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.nome)


class ClasseManager(models.Manager):
    def all(self):
        return self.order_by('codigo')


class Classe(models.Model):
    codigo = models.CharField(verbose_name='Código', max_length=255, db_index=True)
    nome = models.CharField(verbose_name='Nome', max_length=255)

    objects = JornadaTrabalhoManager()

    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'

    def __str__(self):
        return '{} - {}'.format(self.codigo, self.nome)


class ServidorManager(models.Manager):
    def all(self):
        return self.order_by('id')

    def filter_by_session(self, session):
        papel = session['role']['name'] if 'role' in session else None
        if papel in (Papel.GESTAO_DE_PESSOAS, Papel.RECURSOS_HUMANOS):
            qs = self.filter(lotacao__unidade__instituicao_id=session['role']['scope_id'])
        elif papel == Papel.REITOR:
            qs = self.filter(situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RA, lotacao__unidade__instituicao_id=session['role']['scope_id'], lotacao__situacao_inconsistencia__gte=SituacaoInconsistencia.VALIDADO_RE)
        else:
            qs = self
        if 'unidade' in session:
            qs = qs.filter(lotacao__unidade_id=session['unidade']['pk'])
        return qs


class Servidor(models.Model):
    matricula = models.CharField(verbose_name='Matrícula', db_index=True, max_length=255)
    nome = models.CharField(verbose_name='Nome', max_length=255)
    sexo = models.CharField(verbose_name='Sexo', max_length=1, choices=[['M', 'M'], ['F', 'F']])
    cpf = models.CharField(verbose_name='CPF', max_length=255)
    situacao = models.ForeignKey(SituacaoServidor, verbose_name='Situação', on_delete=models.CASCADE)
    data_nascimento = models.DateField(verbose_name='Data de Nascimento')
    lotacao = models.ForeignKey(UnidadeOrganizacional, verbose_name='Lotação', on_delete=models.CASCADE)
    jornada = models.ForeignKey(JornadaTrabalho, verbose_name='Jornada de Trabalho', on_delete=models.CASCADE)
    escolaridade = models.ForeignKey(Escolaridade, verbose_name='Escolaridade', null=True, blank=True, on_delete=models.CASCADE)
    titulacao = models.ForeignKey(Titulacao, verbose_name='Titulação', null=True, blank=True, on_delete=models.CASCADE)
    rsc = models.ForeignKey(Rsc, verbose_name='RSC', null=True, blank=True, on_delete=models.CASCADE)
    cargo = models.ForeignKey(CargoEmprego, verbose_name='Cargo', on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, verbose_name='Classe', null=True, on_delete=models.CASCADE)
    excluido = models.BooleanField(verbose_name='Excluído', default=False)
    situacao_inconsistencia = models.ForeignKey(SituacaoInconsistencia, verbose_name='Situação da Inconsistência', null=True, on_delete=models.CASCADE)
    justificativa_lotacao_reitoria = models.ForeignKey(Justificativa, verbose_name='Justificativa Lotação da Reitoria', null=True, related_name='s11', on_delete=models.CASCADE)
    justificativa_lotacao_reitoria_aceita = models.BooleanField(verbose_name='Justificativa Lotação da Reitoria Aceita', null=True)
    justificativa_escolaridade_cargo = models.ForeignKey(Justificativa, verbose_name='Justificativa para Divergência Escolaridade x Cargo', null=True, related_name='s12', on_delete=models.CASCADE)
    justificativa_escolaridade_cargo_aceita = models.BooleanField(verbose_name='Justificativa para Divergência Escolaridade x Cargo Aceita', null=True)
    justificativa_duplicidade_lotacao = models.ForeignKey(Justificativa, verbose_name='Justificativa para Divergência de Duplicidade de Lotação', null=True, related_name='s13', on_delete=models.CASCADE)
    justificativa_duplicidade_lotacao_aceita = models.BooleanField(verbose_name='Justificativa para Divergência de Duplicidade de Lotação Aceita', null=True)
    ativo = models.BooleanField(verbose_name='Ativo', default=True)

    objects = ServidorManager()

    class Meta:
        verbose_name = 'Servidor'
        verbose_name_plural = 'Servidores'

    def __str__(self):
        return '{} ({})'.format(self.nome, self.matricula)

    def atualizar_situacao_inconsistencia(self):
        Servidor.objects.filter(pk=self.pk).update(situacao_inconsistencia_id=self.inconsistencia_set.calcular_situacao())

    @atomic()
    def reiniciar_inconsistencias(self):
        for inconsistencia in self.inconsistencia_set.all():
            inconsistencia.reiniciar()
        self.atualizar_situacao_inconsistencia()


class RelatorioInconsistenciaManager(models.Manager):
    def all(self):
        return self.filter()


class RelatorioInconsistencia(models.Model):
    unidade = models.ForeignKey(Unidade, verbose_name='Unidade', on_delete=models.CASCADE)
    data_hora = models.DateTimeField(verbose_name='Data/Hora', auto_now_add=True)
    campo1 = models.IntegerField('Curso com nomenclatura inválida')
    campo2 = models.IntegerField('Curso não associados ao catálogo')
    campo3 = models.IntegerField('Ciclo com evasão zero não justificada')
    campo4 = models.IntegerField('Ciclo com carga-horária insuficiente')
    campo5 = models.IntegerField('Ciclo sem programa associado')
    campo6 = models.IntegerField('Ciclo com duração imprópria')
    campo7 = models.IntegerField('Ciclo sem detalhamento de vaga')
    campo8 = models.IntegerField('Ciclo com ingressantes maior que inscritos')
    campo9 = models.IntegerField('Ciclo de cursos presenciais sem turno associado')
    campo10 = models.IntegerField('Ciclo de cursos EAD com turnos associados')
    campo11 = models.IntegerField('Matrícula com data anterior a data de início do ciclo')
    campo12 = models.IntegerField('Matrícula com data posterior a data de ocorrência')
    campo13 = models.IntegerField('Matrícula de alunos duplicadas')
    campo14 = models.IntegerField('Matrícula retenção crítica')
    campo15 = models.IntegerField('Matrícula retenção FIC')
    campo16 = models.IntegerField('Matrícula de alunos sem cor/raça definida')
    campo17 = models.IntegerField('Matrícula de alunos sem renda definida')
    campo18 = models.IntegerField('Matrícula sem turno')
    campo19 = models.IntegerField('Matrícula com turno invalido no ciclo')

    objects = RelatorioInconsistenciaManager()

    class Meta:
        verbose_name = 'Relatório de Inconsistência'
        verbose_name_plural = 'Relatórios de Inconsistências'

    def save(self, *args, **kwargs):
        from pnp.reports import RelatorioConsistenciaDados
        relatorio = RelatorioConsistenciaDados(self.unidade)
        for i, item in enumerate(relatorio.gerar()):
            setattr(self, 'campo{}'.format(i+1), item[1].count())
        return super().save(*args, **kwargs)

    def __str__(self):
        return 'Relatório {}'.format(self.pk)


class HistoricoSincronizacaoSistecManager(models.Manager):
    def all(self):
        return self.filter()


class HistoricoSincronizacaoSistec(models.Model):
    data_hora = models.DateTimeField(verbose_name='Data/Hora', auto_now_add=True)
    historico = models.TextField(verbose_name='Histórico')


    objects = HistoricoSincronizacaoSistecManager()

    class Meta:
        verbose_name = 'Histório de Sincroninação SISTEC'
        verbose_name_plural = 'Histório de Sincroninação SISTEC'

    def __str__(self):
        return '{}'.format(self.pk)


class ArquivoExportacaoManager(models.Manager):
    def all(self):
        return self.filter()


class ArquivoExportacao(models.Model):
    descricao = models.CharField(verbose_name='Descrição', max_length=255)
    data = models.DateTimeField(verbose_name='Data', null=True, auto_now_add=True)
    arquivo = models.FileField(null=True, upload_to='arquivos_exportacao')

    objects = ArquivoExportacaoManager()

    class Meta:
        verbose_name = 'Arquivo de Exportação'
        verbose_name_plural = 'Arquivos de Exportação'

    def __str__(self):
        return 'Arquivo #{}'.format(self.pk)

    def get_url(self):
        try:
            return self.arquivo.url
        except Exception:
            return '#'

