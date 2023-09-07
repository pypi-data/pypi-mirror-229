from api.tests import ApiTestCase
from django.contrib.auth.models import User
from .models import TipoInstituicao, Instituicao, Pessoa, Administrador
from api.models import Scope
from django.conf import settings

from api.test import SeleniumTestCase

class TesteIntegracao(SeleniumTestCase):

    def importar_pessoas(self):
        self.search_menu('Pessoas')
        self.click('Importar Pessoas')
        self.enter('Arquivo', 'pnp/fixtures/teste/pessoas.csv')
        self.submit_form()

    def cadastrar_pessoa(self, nome, cpf, email, capacitacao=True, ativo=True):
        self.click('Cadastrar')
        self.enter('Nome', nome)
        self.enter('CPF', cpf)
        self.enter('Email', email)
        self.choose('Capacitação Concluída', 'Sim' if capacitacao else 'Não')
        self.choose('Cadastro Ativo', 'Sim' if ativo else 'Não')
        self.submit_form()
        self.see_message('Ação realizada com sucesso')

    def cadastrar_administrador(self):
        self.search_menu('Pessoas')
        self.cadastrar_pessoa('MEC', '11111111111', 'mec@gmail.com')
        self.search_menu('Administradores')
        self.click('Cadastrar')
        self.choose('Pessoa Física', 'MEC')
        self.submit_form()
        self.see_message('Ação realizada com sucesso')
 
    def cadastrar_pessoas(self):
        dados = [
            ('22222222222', 'RA1'),
            ('33333333333', 'PI1'),
            ('44444444444', 'RE1'),
            ('88888888888', 'GP1'),
            ('99999999999', 'RH1'),
        ]
        self.search_menu('Pessoas')
        for cpf, nome in dados:
            email = f'{nome.lower()}@mail.com'
            self.cadastrar_pessoa(nome, cpf, email)

    def cadastrar_municipios(self):
        data = [
            {
               "codigo": "2408102",
                "nome": "Natal",
            },
            {
               "codigo": "2406106",
                "nome": "Jucurutu",
            },
            {
               "codigo": "2503209",
                "nome": "Cabedelo",
            }
        ]
        self.search_menu('Municípios')
        for item in data:
            self.click('Cadastrar')
            self.enter('Código', item['codigo'])
            self.enter('Nome', item['nome'])
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

    def cadastrar_tipos_instituicoes(self):
        data = [
            {
                "codigo": '001', 
                "nome": 'Instituto Federal'
            },
        ]
        self.search_menu('Tipos Instituição')
        for item in data:
            self.click('Cadastrar')
            self.enter('Código',item[ "codigo"])
            self.enter('Nome', item['nome'])
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

        
    def cadastrar_instituicoes(self):
        data = [
            {
                'nome': "Instituto Federal do Rio Grande do Norte",
                'tipo': 'Instituto Federal',
                'uf': 'RN',
                'sigla': "IFRN",
                'codigo': "26435",
                'reitor': 'RE1',
                'pesquisadores': ['PI1'],
                'gestao_pessoas': ['GP1'],
                'recursos_humanos': ['RH1']
            },
            {
                "nome": "Instituto Federal da Paraíba",
                'tipo': 'Instituto Federal',
                "sigla": "IFPB",
                "uf": "PB",
                "codigo": "26417",
                'reitor': None,
                'pesquisadores': [],
                'gestao_pessoas': [],
                'recursos_humanos': []
            }
        ]
        self.search_menu('Instituições')
        for item in data:
            self.click('Cadastrar')
            self.enter('Código',item[ "codigo"])
            self.enter('Nome', item['nome'])
            self.enter('Sigla', item[ "sigla"])
            self.choose('Tipo', item['tipo'])
            self.enter('Uf', item['uf'])
            if item[ 'reitor']:
                self.choose('Reitor', item[ 'reitor'])
            
            for pesquisador in item['pesquisadores']:
                self.choose('Pesquisadores Institucionais', pesquisador)

            for gp in item['gestao_pessoas']:
                self.choose('Gestão Pessoas', gp)

            for rh in item['recursos_humanos']:
                self.choose('Recursos Humanos', rh)

            self.submit_form()
            self.see_message('Ação realizada com sucesso')

    def cadastrar_tipos_cursos(self):
        data = [
             {
                "codigo": "1",
                "nome": "Qualificação Profissional (FIC)",
                "fator": "1.00",
                "nivel_verticalizacao": "1",
                "duracao_minima": 3,
                "duracao_maxima": 365
            },

            {
                "codigo": "3",
                "nome": "Técnico",
                "fator": "1.00",
                "nivel_verticalizacao": "2",
                "duracao_minima": 365,
                "duracao_maxima": 1460
            },
            {
                "codigo": "4",
                "nome": "Tecnologia",
                "fator": "1.00",
                "nivel_verticalizacao": "3",
                "duracao_minima": 730,
                "duracao_maxima": 1460
            },
            { 
                "codigo": "5",
                "nome": "Bacharelado",
                "fator": "1.00",
                "nivel_verticalizacao": "3",
                "duracao_minima": 1460,
                "duracao_maxima": 1825
            },
            { 
               "codigo": "6",
                "nome": "Licenciatura",
                "fator": "1.11",
                "nivel_verticalizacao": "3",
                "duracao_minima": 365,
                "duracao_maxima": 1460
            },
            {
              "codigo": "7",
                "nome": "Especialização (Lato Sensu)",
                "fator": "1.67",
                "nivel_verticalizacao": "4",
                "duracao_minima": 180,
                "duracao_maxima": 730
            },
            {
                "codigo": "11",
                "nome": "Mestrado Profissional",
                "fator": "2.50",
                "nivel_verticalizacao": "4",
                "duracao_minima": 365,
                "duracao_maxima": 730
            },
            {
                "codigo": "12",
                "nome": "Ensino Fundamental I",
                "fator": "1.67",
                "nivel_verticalizacao": "0",
                "duracao_minima": 365,
                "duracao_maxima": 1825
            },
            {
                "codigo": "13",
                "nome": "Doutorado",
                "fator": "1.67",
                "nivel_verticalizacao": "0",
                "duracao_minima": 365,
                "duracao_maxima": 730
            }
        ]
        self.search_menu('Tipos de Curso')
        for item in data:
            self.click('Cadastrar')
            self.enter('Código',item[ "codigo"])
            self.enter('Nome', item['nome'])
            self.enter('Fator', item['fator'])
            self.enter('Nível de Verticalização', item['nivel_verticalizacao'])
            self.enter('Duração Mínima', item['duracao_minima'])
            self.enter('Duração Máxima', item['duracao_maxima'])
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

        


    def cadastrar_programas(self):
        programas = [
            'UAB (Universidade Aberta do Brasil)',
            'E-TEC',
            'Bolsa Formação',
            'Aprenda Mais',
            'Outros MOOC',
            'MedioTec',
            'Sem Programa Associado'
        ]
        self.search_menu('Programas')
        for programa in programas:
            self.click('Cadastrar')
            self.enter('Nome', programa)
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

    def cadastrar_regras_associacao_programas(self):
        data = [
            (
                "Educação a Distância", 
                ["Bacharelado", "Licenciatura", "Especialização (Lato Sensu)"], 
                ["Sem Programa Associado"]
            ),
            (
                "Educação a Distância", 
                ["Tecnologia"], 
                ["UAB (Universidade Aberta do Brasil)", "E-TEC", "Sem Programa Associado"]
            ),
            (
                "Educação a Distância", 
                ["Qualificação Profissional (FIC)"],
                [ "Bolsa Formação", "Aprenda Mais", "Outros MOOC", "Sem Programa Associado"]
            ),
            (
                "Educação a Distância", 
                ["Técnico"], 
                ["E-TEC", "MedioTec", "Sem Programa Associado"]
            ),
            (
                "Educação a Distância", ["Mestrado Profissional"], ["Sem Programa Associado"]
            ),
            (
                "Educação Presencial", ["Técnico"], ["Bolsa Formação", "MedioTec", "Sem Programa Associado"]
            ),
            (
                "Educação Presencial", 
                [
                    "Tecnologia", "Bacharelado", "Doutorado"
                ],
                ["Sem Programa Associado"]
            ),
            ("Educação Presencial", ["Qualificação Profissional (FIC)"], ["Bolsa Formação", "Sem Programa Associado"])
        ]
        self.search_menu('Regras de Associação a Programa')
        for (modalidade, tipo_cursos, programas) in data:
            self.click('Cadastrar')
            self.choose('Modalidade', modalidade)
            #
            for tipo_curso in tipo_cursos:
                self.choose('Tipos de Curso', tipo_curso)
            #
            for programa in programas:
                self.choose('Programas', programa)
            #
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

    def cadastrar_tipos_unidades(self):
        data = [
            {
                "codigo": "1",
                "nome": "Campus",
            },
            {
                "codigo": "2",
                "nome": "Campus Avançado",
            },
        ]
        self.search_menu('Tipos de Unidade')
        for item in data:
            self.click('Cadastrar')
            self.enter('Código', item['codigo'])
            self.enter('Nome', item['nome'])
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

    def cadastrar_tipos_inconsistencias(self):
        data = [
            {
                "nome": "Associação ao Catálogo",
                "escopo": "Curso"
            },
            {
                "nome": "Nome do Curso",
                "escopo": "Curso"
            },
            {
                "nome": "Evasão 0%",
                "escopo": "Ciclo"
            },
            {
                "nome": "Carga Horária Insuficiente",
                "escopo": "Ciclo"
            },
            {
                "nome": "Programas Associados",
                "escopo": "Ciclo"
            },
            {
                "nome": "Duração do Ciclo",
                "escopo": "Ciclo"
            },
            {
                "nome": "Número de vagas",
                "escopo": "Ciclo"
            },
            {
                "nome": "Ingressantes > Inscritos",
                "escopo": "Ciclo"
            },
            {
                "nome": "Turno de Oferta do Ciclo",
                "escopo": "Ciclo"
            },
            {
                "nome": "Matrícula Anterior",
                "escopo": "Matrícula"
            },
            {
                "nome": "Matrícula Posterior",
                "escopo": "Matrícula"
            },
            {
                "nome": "Aluno Duplicado",
                "escopo": "Matrícula"
            },
            {
                "nome": "Retenção Crítica",
                "escopo": "Matrícula"
            },
            {
                "nome": "Retenção FIC",
                "escopo": "Matrícula"
            },
            {
                "nome": "Cor/Raça",
                "escopo": "Matrícula"
            },
            {
                "nome": "Renda",
                "escopo": "Matrícula"
            },
            {
                "nome": "Turno do Aluno",
                "escopo": "Matrícula"
            },
            {
                "nome": "Docente Lotado em Reitoria",
                "escopo": "Unidade Organizacional"
            },
            {
                "nome": "Divergência entre Escolaridade e Titulação",
                "escopo": "Servidor"
            },
            {
                "nome": "Divergência entre Escolaridade e Cargo",
                "escopo": "Servidor"
            },
            {
                "nome": "Titulação não Informada",
                "escopo": "Servidor"
            },
            {
                "nome": "Escolaridade não Informada",
                "escopo": "Servidor"
            },
            {
                "nome": "Cargo sem Descrição",
                "escopo": "Servidor"
            },
            {
                "nome": "Duplicidade de Lotação",
                "escopo": "Servidor"
            },
            {
                "nome": "UORG não Vinculada",
                "escopo": "Servidor"
            },
        ] 
        self.search_menu('Tipos de Inconsistência')
        for item in data:
            self.click('Cadastrar')
            self.enter('Nome', item['nome'])
            self.choose('Escopo', item['escopo'])
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

       
    
    def cadastrar_unidades(self):
        data = [
            {
                'instituicao': 'Instituto Federal do Rio Grande do Norte',
                "codigo": "338",
                "nome": "Campus Natal Central",
                "tipo": 'Campus',
                "municipio": "Natal",
                "caracteristica": "Acadêmica",
                "periodo_criacao": "Preexistente a Expansão",
                "codigo_inep": "24059110",
                "codigo_simec": "391823",
                "codigo_sistec": "2959",
            },
            {
                'instituicao': 'Instituto Federal do Rio Grande do Norte',
                'codigo': '911',
                'nome': 'Campus Avançado Jucurutu',
                'tipo': 'Campus Avançado',
                'municipio': 'Jucurutu',
                'caracteristica': 'Acadêmica',
                'periodo_criacao': 'Expansão 2017-2018',
                'codigo_sistec': '49145',
                "codigo_simec": "862604",
                "codigo_inep": "42828",
            },
            {
               "instituicao": 'Instituto Federal da Paraíba',
                "codigo": "129",
                "nome": "Campus Cabedelo",
                "tipo": 'Campus',
                "municipio": 'Cabedelo',
                "caracteristica": "Acadêmica",
                "periodo_criacao": "Expansão 2011-2014",
                "codigo_inep": "25282921",
                "codigo_simec": "389272",
                "codigo_sistec": "3562",
            }
        ]
        self.search_menu('Unidades')
        for item in data:
            self.click('Cadastrar')
            self.enter('Nome', item['nome'])
            self.choose('Tipo', item['tipo'])
            self.choose('Instituição', item['instituicao'])
            self.enter('Código', item['codigo'])
            self.enter("Período de Criação", item['periodo_criacao'])
            self.enter("Característica", item['caracteristica'])
            self.choose('Município', item['municipio'])
            self.enter("Código SISTEC", item['codigo_sistec'])
            self.enter("Código INEP", item['codigo_inep'])
            self.enter("Código SIMEC", item['codigo_simec'])
            #
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

    def cadastrar_cursos_catalogos(self):
        data = [ 
            {
                "codigo": "1001",
                "nome": "Qualificação Profissional - Ambiente e Saúde",
                "tipo": "Qualificação Profissional (FIC)",
                "fator": "1.0",
                "duracao_minima": 0,
                "carga_horaria_minima": 160,
                "observacao": "Genérico 1",
                "capacitacao": False,
                "area_cnpq": 'Controle Ambiental',
                "nivel_ensino": 'Qualificação Profissional (FIC)',
                "eixo": "Ambiente e Saúde",
                "sub_eixo": "AMBIENTE E SAÚDE",
                "curso": "NEUROEDUCAÇÃO EM FOCO"
            },
            {
                "codigo": "176",
                "nome": "Técnico em Computação Gráfica",
                "tipo": 'Técnico',
                "fator": "1.25",
                "duracao_minima": '100',
                "carga_horaria_minima": '1000',
                "observacao": "",
                "capacitacao": False,
                "area_cnpq": 'Processamento Gráfico (Graphics)',
                "nivel_ensino": 'Técnico',
                "eixo": 'Informação e Comunicação',
                "sub_eixo": 'Automação',
            },
  
        ]
        self.search_menu('Cursos do Catálogo')
        for item in data:
            self.click('Cadastrar')
            self.enter('Nome', item['nome'])
            self.choose('Tipo', item['tipo'])
            self.enter('Código', item['codigo'])
            self.enter('Fator', item['fator'])
            self.enter('Duração Mínima', item['duracao_minima'])
            self.enter('Carga Horária Mínima', item['carga_horaria_minima'])
            self.enter('Observação', item['observacao'])
            if item['capacitacao']:
                self.choose('Curso de Capacitação', 'Sim' if item['capacitacao'] else 'Não')
                self.click('Curso de Capacitação', item['capacitacao'])
            #
            self.choose('Área', item['area_cnpq'])
            self.choose('Nível de Ensino', item['nivel_ensino'])
            self.choose('Eixo', item['eixo'])
            self.choose('Sub-Eixo', item['sub_eixo'])
            self.submit_form()
            self.see_message('Ação realizada com sucesso')
            
    def cadastrar_justificativas(self):
        data_justificativas = [
            ('Nome do Curso', 'Curso preparatório - curso de formação inicial e continuada com o objetivo de preparar para a realização de exames, concursos, olimpíadas de conhecimento etc.'),
            ('Nome do Curso', 'Curso para formação de treinadores e instrutores - curso de formação profissional de instrutores/treinadores (exemplo Treinadores de cães-guia).'),
            ('Nome do Curso', 'Curso para formação profissional - curso para formação profissional com emissão de certificado de qualificação profissional.'),
            ('Evasão 0%', 'Ciclo encerrado sem ocorrência de abandono, transferência ou desligamento.'),
            ('Evasão 0%', 'Ciclo em andamento sem ocorrência de abandono, transferência ou desligamento.'),
            ('Carga Horária Insuficiente', 'Curso com carga horária inferior a 20h, conforme Projeto Pedagógico do Curso (curso será desconsiderado para fins estatísticos).'),
            ('Duração do Ciclo', 'Ciclo exclusivamente  noturno com duração estendida.'),
            ('Duração do Ciclo', 'Ciclo ofertado na modalidade PROEJA'),
            ('Duração do Ciclo', 'Ciclo com duração de acordo com o PPC aprovado, está duração não é o prazo máximo para integralização do curso.'),
            ('Retenção Crítica', 'Aluno matriculado e com registro de frequência no ano base (inclui alunos que efetuaram trancamento no referido ano base).'),
            ('Retenção Crítica', 'Aluno matriculado, mas sem registro de frequência no ano base (inclui alunos que efetuaram trancamento em anos anteriores ao referido ano base).'),
            ('Retenção FIC', 'Curso ainda em andamento devido a ocorrências fortuitas (exemplo: greve, ocupação, incidentes climáticos e outros).'),
            ('Retenção FIC', 'Aluno matriculado em curso FIC com oferta regular, com registro de frequência no ano base (inclui alunos que efetuaram trancamento no referido ano base).'),
            ('Retenção FIC', 'Aluno matriculado em curso FIC com oferta regular, sem registro de frequência no ano base (inclui alunos que efetuaram trancamento em anos anteriores).'),
            ('Docente Lotado em Reitoria', 'Decisão Judicial.'),
            ('Docente Lotado em Reitoria', 'Decisão Administrativa por questões de saúde.'),
            ('Duplicidade de Lotação', 'Acúmulo de cargos.'),
            ('Duplicidade de Lotação', 'Erro no SIAPE.')
        ]
        self.search_menu('Justificativas')
        for (tipo_inconsistencia, justificativa) in data_justificativas:
            self.click('Cadastrar')
            self.choose('Tipo de Inconsistência', tipo_inconsistencia)
            self.enter('Justificativa', justificativa)
            self.submit_form()
            self.see_message('Ação realizada com sucesso')

    def test(self):
        self.loaddata(settings.BASE_DIR.joinpath('pnp/fixtures/initial_data.json'))

        if self.step('001'):
            self.create_superuser('admin', '123')
            self.login('admin', '123')
            self.cadastrar_administrador()
            self.logout()

        if self.step('002'):
            # Acessando como Administrador
            self.login('admin', '123')
            self.cadastrar_pessoas()
            self.cadastrar_municipios()
            self.cadastrar_tipos_instituicoes()
            self.cadastrar_instituicoes()
            self.cadastrar_tipos_cursos()
            self.cadastrar_tipos_unidades()
            self.cadastrar_tipos_inconsistencias()
        if self.step('003'):
            self.login('admin', '123')
            self.cadastrar_programas()
            self.cadastrar_regras_associacao_programas()
            self.cadastrar_unidades()
            self.importar_pessoas()
            self.cadastrar_justificativas()
        if self.step('005'):
            self.login('admin', '123')
            self.search_menu('Configurações')
            self.click('Cadastrar')
            self.enter('Ano', '2023')
            self.enter('Data de Início', '01/01/2023')
            self.enter('Data de Fim', '31/12/2023')
            self.enter('Data de Envio', '31/01/2024')
            self.submit_form()
            self.wait(4)
        if self.step('006'):
            self.login('admin', '123')
            self.search_menu('Configurações')
            self.click('Visualizar')
            self.choose('Unidade', 'Jucurutu')
            self.click('Filtrar')
            self.click('Realizar Carga')
            self.submit_form()
            self.wait(3)
            self.click('Processar Carga')
            self.submit_form()
            self.wait(10)
            self.click('Identificar Registros')
            self.choose('Unidade', 'Jucurutu')
            self.submit_form()
            self.wait(2)
            self.click('Gerar Inconsistências')
            self.choose('Unidade', 'Jucurutu')
            self.submit_form()
            self.wait(5)
        if self.step('007'):
            self.login('admin', '123')
            self.search_menu('Inconsistências')
            self.enter('Palavras-chave', '1')
            self.click('Filtrar')
            self.click('Alterar Inconsistencia')
            breakpoint()
        # self.logout()


class PnpTestCase(ApiTestCase):

    def test(self):
        self.loaddata(settings.BASE_DIR.joinpath('pnp/fixtures/initial_data.json'))
        self.loaddata(settings.BASE_DIR.joinpath('pnp/fixtures/cadastros_primarios.json.gz'))
        self.create_superuser('admin', '123')
        self.login('admin', '123')
        self.get('/user/')
        self.get('/tipos_instituicao/')
        programa = self.post('/programas/', dict(nome='XXX'))
        self.delete('/programas/{}/'.format(programa['id']))


class ApiTestCase(ApiTestCase):

    def _test(self):
        from api.viewsets import apply_lookups
        print('--------- PNP ---------')
        admin = User.objects.create_superuser('admin', password='123')
        tipo = TipoInstituicao.objects.create(codigo='1', nome='Instituto Federal')
        ifrn = Instituicao.objects.create(codigo='1', nome='IFRN', sigla='IFRN', uf='RN', tipo=tipo)
        ifpb = Instituicao.objects.create(codigo='1', nome='IFPB', sigla='IFPB', uf='PB', tipo=tipo)
        p0 = Pessoa.objects.create(nome='p0', cpf='00000000000', email='p0.mail.com')
        print('Cadastrando administrador')
        a = Administrador.objects.create(pessoa_fisica=p0)
        self.debug()
        print('Excluindo administrador')
        # a.delete()
        self.debug()
        p1 = Pessoa.objects.create(nome='p1', cpf='11111111111', email='p1.mail.com')
        p2 = Pessoa.objects.create(nome='p2', cpf='22222222222', email='p2.mail.com')
        p3 = Pessoa.objects.create(nome='p3', cpf='33333333333', email='p3.mail.com')
        print('Definindo p1 como reitor do IFRN')
        ifrn.reitor = p1
        ifrn.save()
        self.debug()
        print('Definindo p2 como pi do IFRN')
        ifrn.pesquisadores_institucionais.add(p2)
        ifrn.save()
        self.debug()
        print('Removendo p2 como PI do IFRN')
        ifrn.pesquisadores_institucionais.remove(p2)
        self.debug()

        print('Definindo p1 como reitor do IFPB')
        ifpb.reitor = p1
        ifpb.save()
        lookups = {None: {'pesquisadores_institucionais__cpf': 'username', 'reitor__cpf': 'username'}, 'Administrador': {}}
        lookups = {'Reitor': {'pk': 'instituicao'}, 'Administrador': {}}
        qs = apply_lookups(Instituicao.objects.all(), lookups, User.objects.get(username=p1.cpf))
        print(qs)
        return
        self.debug()
        print('Removendo p1 como reitor do IFRN')
        ifrn.reitor = None
        ifrn.save()
        self.debug()
        print('Removendo p2 reitor do IFPB')
        ifpb.reitor = None
        ifpb.save()
        self.debug()

    def debug(self):
        print('\nUSERS')
        for o in User.objects.all():
            print(o, [g.name for g in o.groups.all()])
        print('SCOPES')
        for o in Scope.objects.all():
            print(o)
        print('\n')