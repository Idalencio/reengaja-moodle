"""Gera o roteiro e a conferência de entrega da equipe."""
from pathlib import Path
import sys
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

root = Path(__file__).resolve().parents[1]
font_root = Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('Guia',str(font_root/'DejaVuSerif.ttf')))
pdfmetrics.registerFont(TTFont('GuiaB',str(font_root/'DejaVuSerif-Bold.ttf')))
pdfmetrics.registerFontFamily('Guia', normal='Guia', bold='GuiaB', italic='Guia', boldItalic='GuiaB')
styles = {
 'body':ParagraphStyle('body',fontName='Guia',fontSize=10,leading=14.8,spaceAfter=8),
 'title':ParagraphStyle('title',fontName='GuiaB',fontSize=18,leading=23,spaceAfter=12),
 'head':ParagraphStyle('head',fontName='GuiaB',fontSize=11.4,leading=16,spaceBefore=9,spaceAfter=7),
 'small':ParagraphStyle('small',fontName='Guia',fontSize=8.5,leading=12,spaceAfter=7),
 'cell':ParagraphStyle('cell',fontName='Guia',fontSize=8.6,leading=12.2),
 'cellhead':ParagraphStyle('cellhead',fontName='GuiaB',fontSize=8.6,leading=12.2),
}
w,h=A4
cw=w-44*mm
story=[]


def text(value,style='body'):
 story.append(Paragraph(value,styles[style]))


def table(headers,rows,widths):
 values=[[Paragraph(escape(v),styles['cellhead']) for v in headers]]
 values += [[Paragraph(escape(v),styles['cell']) for v in row] for row in rows]
 obj=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT')
 obj.setStyle(TableStyle([
  ('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),
  ('LINEABOVE',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,0),(-1,0),.6,colors.black),
  ('LINEBELOW',(0,-1),(-1,-1),.4,colors.grey),('TOPPADDING',(0,0),(-1,-1),6),
  ('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
 ]))
 story.append(obj)
 story.append(Spacer(1,8))


text('Roteiro da equipe','title')
text('Projeto de reengajamento de estudantes - Engenharia de Software II, 2026/2','small')
text('Divisão sugerida para quatro participantes. Cada parte leva cerca de 40 a 60 segundos.','small')
source=(root/'docs/roteiro_4_integrantes.md').read_text()
for section in source.split('\n## ')[1:5]:
 lines=section.strip().splitlines()
 text(escape(lines[0]),'head')
 for paragraph in '\n'.join(lines[1:]).strip().split('\n\n'):
  if paragraph.strip():text(escape(paragraph.strip()))

story.append(PageBreak())
text('Conferência antes da entrega','title')
text('O que já está pronto','head')
text('Código dos dois serviços, regras de seleção, RabbitMQ, SMTP, histórico de envios e tratamento de falhas. O pacote inclui guia de execução, registros dos testes, relatório técnico e slides.')
text('O que precisa ser fechado','head')
table(['Item','Conferência'],[
 ['Moodle','Seguir o guia de configuração ao conectar outra instalação.'],
 ['Publicação','Publicar o vídeo no YouTube e registrar seu link. O código já está no GitHub.'],
 ['Equipe','Conferir os quatro nomes em EQUIPE.md.'],
 ['Extensão','Cada integrante conferir e enviar seu relatório individual.'],
],[.24*cw,.76*cw])
text('Preparação de cada integrante','head')
table(['Parte','Arquivos para revisar'],[
 ['1. API e contexto','acompanhamento/moodle.py e docs/moodle_real.md'],
 ['2. Seleção e mensagens','acompanhamento/service.py e infra/events.py'],
 ['3. Envio e falhas','notificacoes/, infra/broker.py e os e-mails EML'],
 ['4. Testes e execução','tests/, compose.yaml e evidencias/'],
],[.32*cw,.68*cw])
text('Equipe: Lucas Gallesio, Pedro Idalencio, Artur Thomé e Vitor Hugo. A divisão organiza as falas e as revisões; cada integrante deve registrar as contribuições que realizou.','small')
text('Os quatro textos individuais estão listados em docs/extensao_individual.md.','small')


def footer(canvas,doc):
 canvas.saveState();canvas.setFont('Guia',8);canvas.setFillColor(colors.grey)
 canvas.drawString(22*mm,15*mm,'Engenharia de Software II - Material da equipe')
 canvas.drawRightString(w-22*mm,15*mm,str(doc.page));canvas.restoreState()


destination=Path(sys.argv[1]) if len(sys.argv)>1 else root/'entrega/Guia_Equipe_4_Integrantes.pdf'
destination.parent.mkdir(parents=True,exist_ok=True)
doc=BaseDocTemplate(str(destination),pagesize=A4,title='Roteiro para quatro integrantes e conferência da entrega',author='')
frame=Frame(22*mm,24*mm,cw,h-44*mm,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
doc.addPageTemplates(PageTemplate(id='guia',frames=[frame],onPage=footer))
doc.build(story)
print(destination)
