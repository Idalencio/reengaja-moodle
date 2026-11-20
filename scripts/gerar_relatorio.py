"""Gera o relatório a partir dos registros efetivamente produzidos."""
from datetime import datetime
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
evidencia = json.loads((ROOT/'evidencias/integracao.json').read_text())
real = json.loads((ROOT/'evidencias/moodle_real_fluxo.json').read_text())
cobertura = json.loads((ROOT/'test-results/coverage.json').read_text())['totals']
suite = ET.parse(ROOT/'test-results/junit.xml').getroot().find('testsuite')
ci_path = ROOT/'evidencias/ci_github.json'
ci = json.loads(ci_path.read_text()) if ci_path.exists() else None
docker_aprovado = bool(ci and ci.get('conclusion') == 'success')
revisao = '20/11/2026'
data_testes = datetime.fromisoformat(suite.attrib['timestamp']).strftime('%d/%m/%Y')
assert int(suite.attrib['failures']) == int(suite.attrib['errors']) == evidencia['failed'] == real['failed'] == 0
testes = int(suite.attrib['tests'])
data = datetime.fromisoformat(evidencia['executed_at']).astimezone(ZoneInfo('America/Sao_Paulo'))
percentual = f"{cobertura['percent_covered']:.1f}".replace('.',',')
nomes = 'Lucas Gallesio, Pedro Idalencio, Artur Thomé e Vitor Hugo'
fontes = Path('/usr/share/fonts/truetype/dejavu')
for nome, arquivo in [('Texto','DejaVuSerif.ttf'),('TextoB','DejaVuSerif-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(nome,str(fontes/arquivo)))
pdfmetrics.registerFontFamily('Texto',normal='Texto',bold='TextoB',italic='Texto',boldItalic='TextoB')
estilos = {
 'titulo':ParagraphStyle('titulo',fontName='TextoB',fontSize=18,leading=24,spaceAfter=11),
 'sub':ParagraphStyle('sub',fontName='Texto',fontSize=10.2,leading=15,spaceAfter=11),
 'corpo':ParagraphStyle('corpo',fontName='Texto',fontSize=10.3,leading=15.2,spaceAfter=8),
 'secao':ParagraphStyle('secao',fontName='TextoB',fontSize=12,leading=17,spaceBefore=9,spaceAfter=7),
 'pequeno':ParagraphStyle('pequeno',fontName='Texto',fontSize=8.7,leading=12.4,spaceAfter=7),
 'celula':ParagraphStyle('celula',fontName='Texto',fontSize=9,leading=12.7),
 'codigo':ParagraphStyle('codigo',fontName='Mono',fontSize=8.4,leading=13.3,spaceAfter=10),
}
conteudo=[]
largura=A4[0]-44*mm

def texto(valor,estilo='corpo'):
    conteudo.append(Paragraph(valor,estilos[estilo]))

def secao(valor):
    texto(valor,'secao')

def pagina(valor):
    conteudo.append(PageBreak())
    texto(valor,'titulo')

def tabela(cabecalho,linhas,proporcoes):
    celulas=[[Paragraph('<b>'+escape(v)+'</b>',estilos['celula']) for v in cabecalho]]
    celulas += [[v if isinstance(v,Paragraph) else Paragraph(escape(str(v)),estilos['celula']) for v in linha] for linha in linhas]
    t=Table(celulas,colWidths=[largura*p for p in proporcoes],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf0')),
      ('LINEABOVE',(0,0),(-1,0),.6,colors.HexColor('#203b4b')),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#203b4b')),
      ('LINEBELOW',(0,-1),(-1,-1),.4,colors.HexColor('#8a969e')),
      ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
      ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    conteudo.extend([t,Spacer(1,8)])

def codigo(valor):
    texto('<br/>'.join(escape(l).replace(' ','&#160;') for l in valor.splitlines()),'codigo')

texto('Serviço de reengajamento de estudantes','titulo')
texto(f'Engenharia de Software II - 2026/2<br/>Revisão de {revisao} para a entrega de 20/11/2026','sub')
texto('<b>Integrantes:</b> '+nomes,'sub')
secao('1. Proposta e escopo')
texto('O projeto envia um lembrete ao estudante que ainda não entregou uma tarefa do Moodle e tem até 24 horas para concluí-la. O e-mail informa a atividade, o prazo e o link de acesso. A intenção é apoiar o acompanhamento das pendências e reduzir contatos manuais.')
texto('A solução acompanha uma disciplina, com tarefas individuais visíveis para toda a turma e prazo único. Entregas em grupo, prorrogações individuais, interface própria e outros canais de contato ficam fora do escopo do enunciado.')
secao('2. Organização do sistema')
tabela(['Componente','Responsabilidade'],[
 ['Acompanhamento','Consulta tarefas, matrículas e entregas pela API REST. Seleciona pendências e publica as solicitações.'],
 ['RabbitMQ','Mantém a comunicação assíncrona e as filas principal, de nova tentativa e de falhas.'],
 ['Notificações','Consome a fila, prepara o e-mail, envia por SMTP e registra o resultado.'],
 ['SQLite e Mailpit','O banco preserva o histórico. O Mailpit captura os e-mails dos testes com contas fictícias.'],
],[.27,.73])
texto('Os dois microsserviços têm processos e Dockerfiles próprios. A consulta acontece ao iniciar e se repete a cada hora. O intervalo é configurável para a demonstração.')
secao('3. Situação da revisão')
texto(f'Em {data_testes}, passaram novamente {testes} testes de unidade/componentes. O registro de {data.strftime("%d/%m/%Y")} preserva nove cenários locais de integração. O ensaio histórico de 06/11 acrescenta cinco cenários no Moodle real da demonstração oficial.')
if docker_aprovado:
    texto('O GitHub Actions também aprovou a execução com Docker: dois microsserviços prontos, lembretes para Ana e Carla, bloqueio de repetição e histórico preservado após reiniciar o consumidor. A suíte de testes e a integração passaram em contêineres.')
else:
    texto('A configuração Docker está válida. O workflow publicado executa os serviços e a suíte; o resultado precisa ser conferido na aba Actions.','pequeno')
texto('Código e materiais: <link href="https://github.com/Idalencio/reengaja-moodle">github.com/Idalencio/reengaja-moodle</link>. O código, os relatos e os registros dos testes acompanham os materiais da equipe.','pequeno')

pagina('Regras e integração')
secao('4. Seleção das pendências')
texto('A tarefa deve estar visível, aceitar entrega individual e vencer nas próximas 24 horas. A janela inclui o limite de 24 horas e exclui o instante do vencimento. Tarefas sem prazo, vencidas, em grupo, ocultas ou com restrições ficam fora da seleção.')
codigo('0 < prazo - agora <= 86400')
texto('A tentativa mais recente com status submitted dispensa o lembrete. Um rascunho permanece pendente. Se a consulta de entregas falhar, o acompanhamento interrompe o ciclo antes de publicar uma lista parcial. O link do e-mail usa o cmid, identificador do módulo do curso.')
secao('5. API do Moodle')
texto('As consultas usam POST nos webservices REST. O token segue no corpo da requisição. As três funções previstas no enunciado recebem uma consulta complementar de visibilidade:')
tabela(['Função','Informação consultada'],[
 ['mod_assign_get_assignments','Tarefas e prazos'],
 ['core_enrol_get_enrolled_users','Estudantes ativos, nomes e e-mails'],
 ['mod_assign_get_submissions','Situação das entregas'],
 ['core_course_get_contents','Visibilidade e restrições dos módulos'],
],[.60,.40])
texto('A instalação precisa disponibilizar essas funções e permitir a leitura dos dados. O guia docs/moodle_real.md explica a configuração. O ensaio público de 06/11 registra o uso na demonstração oficial; outra instalação precisa de configuração própria.')
secao('6. Repetição e falhas')
texto('A chave curso:tarefa:aluno identifica o lembrete. Se o envio já estiver registrado como concluído no SQLite, o consumidor ignora a repetição. O histórico permanece após reiniciar, desde que o banco e o volume sejam preservados.')
texto('Uma falha temporária fica no histórico e encaminha a solicitação para a fila de espera. Após o TTL, ela volta à fila principal. O limite é de três tentativas. Falhas definitivas e mensagens inválidas ficam em uma fila separada. O ACK ocorre depois do processamento ou da publicação confirmada do encaminhamento.')
texto('Limite: SMTP e SQLite não compartilham uma transação. Uma queda entre a aceitação do e-mail e o commit pode gerar duplicata. O critério comprovado é o bloqueio de solicitações já registradas como concluídas.','pequeno')

pagina('Critérios de aceite e evidências')
secao('7. Resultados reproduzidos')
texto(f'A suíte executada em {data_testes} aprovou {testes} testes de unidade/componentes, sem falhas. A cobertura foi de {percentual}% das instruções medidas. O percentual exclui pontos de entrada, simulador e scripts. Os dois pontos de entrada também foram conferidos em processos separados.')
texto('Os nove cenários I01 a I09 usam Moodle simulado, RabbitMQ real e Mailpit real. Eles produziram três e-mails: dois envios iniciais e um após recuperação da falha. O reinício do consumidor manteve o total e bloqueou duas repetições.')
tabela(['Critério do professor','Verificação e resultado'],[
 ['1. Lembrete na janela','I01/I02: Ana e Carla recebem. M01: a pendência real chega ao Mailpit. Passou.'],
 ['2. Sem envio para entregue ou fora da janela','I01/I07 e testes de limites. M03/M04: prazo acima de 24 horas e entrega final dispensam o envio. Passou.'],
 ['3. Sem novo envio ao reprocessar concluída','I03/I04, reinício do consumidor e M02. O histórico bloqueia outro e-mail. Passou.'],
 ['4. Registro de falha e nova tentativa','I05/I06 e M05: erro SMTP registrado e sucesso na tentativa 2. I09 limita a três tentativas. Passou.'],
],[.36,.64])
secao('8. Ensaio histórico com Moodle real')
texto('Em 06/11, o projeto foi integrado ao Moodle 5.3 da demonstração oficial, com contas fictícias e duas atividades de teste. Cinco cenários passaram e dois e-mails chegaram ao Mailpit. Os registros M01 a M05 identificam a execução histórica na demonstração oficial.')
secao('Registros incluídos')
tabela(['Pasta ou arquivo','O que comprova'],[
 ['evidencias/unitarios_19_11.xml e .txt','104 testes locais aprovados em 19/11 e cobertura de 94%'],
 ['evidencias/integracao.json e .log','Nove cenários locais e histórico de processamento'],
 ['evidencias/ambiente.json e worker-*.log','Serviços separados, prontidão e reinício'],
 ['evidencias/moodle_real_fluxo.json, .log e EML','Ensaio de 06/11 e e-mails capturados'],
 ['GitHub Actions e evidencias/ci_github.json','Execução Docker e suíte em contêineres' if docker_aprovado else 'Workflow de verificação publicado'],
],[.48,.52])

pagina('Instalação e fechamento da entrega')
secao('9. Executar a demonstração')
texto('Com Docker Desktop iniciado e configurado para contêineres Linux, abra a pasta do projeto e execute INICIAR_DEMO.bat. Os comandos equivalentes são:')
codigo('docker compose up -d --build --wait\ndocker compose run --build --rm testes')
texto('Abra http://localhost:8025. Na demonstração nova, Ana e Carla recebem e Bruno não recebe. Para repetir a consulta sem reenviar as mensagens concluídas:')
codigo('docker compose exec acompanhamento python -m acompanhamento --once')
texto('A verificação dos contêineres usa python scripts/verificar_containers.py após a inicialização. O workflow do GitHub repete esse roteiro, reinicia o consumidor e preserva os registros. Para encerrar conservando o histórico, use docker compose down.')
secao('10. Material da entrega')
pendencias = [
 ['Vídeo da apresentação',Paragraph('<link href="https://youtu.be/aXw6Iu1j9lQ">https://youtu.be/aXw6Iu1j9lQ</link>',estilos['celula'])],
 ['Relatórios individuais','Quatro textos em preparacao_extensao/, um por integrante'],
]
if not docker_aprovado:
    pendencias.insert(0, ['Conferir a execução Docker','Resultado do workflow e test-results/execucao_containers.json'])
tabela(['Item','Localização e uso'],pendencias,[.35,.65])
if docker_aprovado:
    texto('Execução aprovada: <link href="'+escape(ci['html_url'])+'">abrir resultado no GitHub Actions</link>. O artefato registros-de-testes contém os logs, as evidências de integração e a verificação dos contêineres.','pequeno')
texto('A entrega reúne os oito slides, o roteiro da apresentação e os quatro relatos individuais. Cada integrante confere seu texto antes do envio. O projeto tem como objetivo apoiar o acompanhamento das tarefas; seu efeito na participação dos estudantes ainda não foi medido.')
texto('Os requisitos e os arquivos correspondentes estão em docs/conferencia_final.md.','pequeno')
secao('Referências')
for ref in ['Enunciado: projeto_2026_2.pdf, Engenharia de Software II, 2026/2.',
 'Moodle: https://docs.moodle.org/en/Using_web_services',
 'RabbitMQ: https://www.rabbitmq.com/docs/confirms',
 'Mailpit: https://mailpit.axllent.org/docs/']:
    texto(escape(ref),'pequeno')

def rodape(canvas,doc):
    canvas.setFont('Texto',8)
    canvas.setFillColor(colors.HexColor('#53616a'))
    canvas.drawString(22*mm,14*mm,'Engenharia de Software II - Revisão de '+revisao)
    canvas.drawRightString(A4[0]-22*mm,14*mm,str(doc.page))

destino=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'entrega/Relatorio_Tecnico_Reengaja_Moodle.pdf'
destino.parent.mkdir(parents=True,exist_ok=True)
SimpleDocTemplate(str(destino),pagesize=A4,leftMargin=22*mm,rightMargin=22*mm,topMargin=20*mm,bottomMargin=23*mm,
 title='Serviço de reengajamento de estudantes - Relatório técnico',author=nomes).build(conteudo,onFirstPage=rodape,onLaterPages=rodape)
print(destino)
