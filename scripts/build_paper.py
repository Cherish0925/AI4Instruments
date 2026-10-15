#!/usr/bin/env python3
"""Build the standalone HTML and typeset PDF from one Markdown manuscript.

Only the PDF build needs reportlab. No network access or browser is used.
"""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'paper'
INK = '#172b3a'
TEAL = '#126b71'
PALE = '#eef6f5'


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', text)
    return text


def blocks(text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith('<!--'):
            continue
        if line.startswith('#'):
            marks, title = line.split(' ', 1)
            yield ('heading', (len(marks), title))
        elif line.startswith('!['):
            match = re.fullmatch(r'!\[(.*)\]\((.*)\)', line)
            if not match:
                raise ValueError(f'Invalid figure: {line}')
            yield ('figure', match.groups())
        elif line.startswith('|'):
            rows = [line]
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(lines[i].strip())
                i += 1
            yield ('table', [[s.strip() for s in r.strip('|').split('|')]
                            for r in rows if not re.fullmatch(r'[| :\-]+', r)])
        else:
            paragraph = [line]
            while i < len(lines) and lines[i].strip():
                paragraph.append(lines[i].strip())
                i += 1
            yield ('paragraph', ' '.join(paragraph))


def figure_spec(kind):
    if kind == 'operation-hierarchy':
        return 490, 248, [
            (18, 14, 250, 44, 'Research question', 'Objectives and evaluation'),
            (18, 76, 250, 44, 'Workflow Operations', 'Devices, samples and analysis'),
            (18, 138, 250, 44, 'Standard Operations', 'Reusable experimental procedures'),
            (18, 200, 250, 38, 'Basic Operations', 'Elementary control and observation'),
            (308, 76, 162, 62, 'Instrument development', 'Mechanics / circuits / firmware'),
            (308, 174, 162, 64, 'Physical apparatus', 'Actuators / sensors / samples')
        ], [(143,58,143,76),(143,120,143,138),(143,182,143,200),
             (268,219,308,219),(389,174,389,138),(308,107,268,107)]
    return 490, 300, [
        (148, 8, 194, 42, 'Select target positions', 'Research objective and search'),
        (18, 82, 194, 44, 'x.position', 'Set target and observe convergence'),
        (278, 82, 194, 44, 'y.position', 'Set target and observe convergence'),
        (148, 160, 194, 46, 'detector.capture', 'Configure / read back / acquire'),
        (148, 242, 194, 46, 'Evaluate observation', 'Record evidence and update search')
    ], [(200,50,115,82),(290,50,375,82),(115,126,200,160),
         (375,126,290,160),(245,206,245,242),(342,265,482,265),
         (482,265,482,29),(482,29,342,29)]


def svg_figure(kind):
    w,h,boxes,arrows = figure_spec(kind)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{kind.replace("-", " ")}">',
             '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#126b71"/></marker></defs>']
    for x,y,bw,bh,title,sub in boxes:
        parts += [f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="6" fill="{PALE}" stroke="#b9d4d3"/>',
                  f'<text x="{x+bw/2}" y="{y+19}" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="{INK}">{html.escape(title)}</text>',
                  f'<text x="{x+bw/2}" y="{y+34}" text-anchor="middle" font-family="sans-serif" font-size="8" fill="#47606c">{html.escape(sub)}</text>']
    for x1,y1,x2,y2 in arrows:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{TEAL}" stroke-width="1.4" marker-end="url(#arrow)"/>')
    parts.append('</svg>')
    return ''.join(parts)


def references():
    return json.loads((PAPER / 'references.json').read_text(encoding='utf-8'))


def reference_text(ref, pdf=False):
    text = f'[{ref["number"]}] {ref["authors"]} ({ref["year"]}). {ref["title"]}. {ref["venue"]}.'
    link = f'<a href="{html.escape(ref["url"], quote=True)}" color="{TEAL}">Source</a>'
    if ref.get('doi'):
        link += f' · DOI: {html.escape(ref["doi"])}'
    if ref.get('accessed'):
        link += f' · Accessed {ref["accessed"]}'
    if ref.get('correction_url'):
        link += f' · <a href="{html.escape(ref["correction_url"], quote=True)}" color="{TEAL}">Author correction</a>'
    return inline(text) + ' ' + link


CSS = '''
:root{--ink:#172b3a;--teal:#126b71;--paper:#fff;--muted:#536875}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#edf1f2;color:var(--ink);font:18px/1.75 Georgia,'Times New Roman',serif}
main{max-width:1040px;margin:40px auto;background:var(--paper);padding:64px 88px;box-shadow:0 8px 35px #2339470d}
header{border-top:5px solid var(--teal);padding-top:30px;margin-bottom:32px}header .eyebrow{font:12px/1.5 Arial,sans-serif;letter-spacing:.15em;text-transform:uppercase;color:var(--teal)}
h1{font-size:54px;line-height:1.1;letter-spacing:-.04em;margin:18px 0}header h2{font:26px/1.35 Georgia,serif;font-weight:normal;margin:0 0 22px}header .author{font:17px/1.5 Arial,sans-serif;margin:18px 0}
a{color:var(--teal);text-decoration-thickness:1px;text-underline-offset:3px}.downloads{font:13px/1.6 Arial,sans-serif}nav{border:1px solid #dae5e6;padding:20px 26px;background:#f6f9f9;margin-bottom:36px;font:14px/1.6 Arial,sans-serif}nav ol{margin:8px 0 0;padding-left:22px;columns:2;column-gap:35px}nav li{padding:3px 0;break-inside:avoid}
h2{font:700 27px/1.3 Georgia,serif;margin:42px 0 18px;scroll-margin-top:20px}h3{font:700 20px/1.4 Georgia,serif;margin:28px 0 14px}p{margin:0 0 17px}figure{margin:30px 0;padding:18px 15px 12px;background:#fafcfc;border:1px solid #e2eaea}svg{display:block;width:100%;height:auto}figcaption{font:13px/1.55 Arial,sans-serif;color:var(--muted);margin:14px 8px 0}table{border-collapse:collapse;width:100%;font:14px/1.5 Arial,sans-serif;margin:24px 0}th,td{border-bottom:1px solid #d5e0e3;padding:12px 14px;text-align:left;vertical-align:top}th{background:var(--ink);color:white}td:first-child{width:32%;font-weight:600}tr:nth-child(even){background:#f2f7f7}.references{font:14px/1.6 Arial,sans-serif}.references p{margin-bottom:16px;overflow-wrap:anywhere}footer{border-top:1px solid #d5e0e3;margin-top:42px;padding-top:18px;font:12px/1.6 Arial,sans-serif;color:var(--muted)}
@media(max-width:750px){body{font-size:17px}main{margin:0;padding:30px 22px;box-shadow:none}h1{font-size:40px}header h2{font-size:23px}nav ol{columns:1}th,td{padding:9px 7px}}
@media print{body{background:white;font-size:11pt}main{max-width:none;margin:0;padding:0;box-shadow:none}nav,.downloads{display:none}h2,h3{break-after:avoid}figure,table{break-inside:avoid}a{color:inherit}}
'''


def build_html(items, refs):
    title = items[0][1][1]
    subtitle = items[1][1][1]
    toc = [(f'section-{i}', data[1]) for i,(kind,data) in enumerate(items)
           if kind == 'heading' and data[0] == 2 and i > 1]
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
           f'<title>{title}: {subtitle} — Shuxing Yang</title>',
           '<meta name="author" content="Shuxing Yang">',
           '<meta name="description" content="A design framework for AI participation in instrument engineering and experimental science.">',
           f'<style>{CSS}</style></head><body><main><header><div class="eyebrow">Perspective · October 2026</div>',
           f'<h1>{title}</h1><h2>{subtitle}</h2><p class="author">Shuxing Yang</p>',
           '<div class="downloads"><a href="https://github.com/Cherish0925/AI4Instruments">Project repository</a> &nbsp; / &nbsp; <a href="https://github.com/Cherish0925/AI4Instruments/raw/refs/heads/main/paper/AI4Instruments.pdf">Download PDF</a></div></header>',
           '<nav aria-label="Contents"><b>Contents</b><ol>']
    out += [f'<li><a href="#{anchor}">{html.escape(title)}</a></li>' for anchor,title in toc]
    out.append('</ol></nav>')
    for i,(kind,data) in enumerate(items[3:],3):
        if kind == 'heading':
            level,title = data
            out.append(f'<h{level} id="section-{i}">{inline(title)}</h{level}>')
        elif kind == 'paragraph':
            out.append(f'<p>{inline(data)}</p>')
        elif kind == 'table':
            out.append('<table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in data[0]) + '</tr></thead><tbody>')
            out += ['<tr>'+''.join(f'<td>{inline(c)}</td>' for c in row)+'</tr>' for row in data[1:]]
            out.append('</tbody></table>')
        elif kind == 'figure':
            caption,path = data
            out.append('<figure>' + svg_figure(Path(path).stem) + f'<figcaption>{inline(caption)}</figcaption></figure>')
    out.append('<div class="references">')
    out += [f'<p id="ref-{r["number"]}">{reference_text(r)}</p>' for r in refs]
    out.append('</div><footer>© 2026 Shuxing Yang. Text and original figures: CC BY 4.0. Version 0.1.0.</footer></main></body></html>')
    (PAPER/'AI4Instruments.html').write_text('\n'.join(out),encoding='utf-8')
    for kind in ['operation-hierarchy','experimental-loop']:
        (ROOT/'assets'/f'{kind}.svg').write_text(svg_figure(kind),encoding='utf-8')


def build_pdf(items, refs):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
    fontdir = Path('/usr/share/fonts/truetype/dejavu')
    if (fontdir/'DejaVuSerif.ttf').exists():
        for name,file in [('Body','DejaVuSerif.ttf'),('BodyBold','DejaVuSerif-Bold.ttf')]:
            pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
        pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
    else:
        pdfmetrics.registerFontFamily('Body',normal='Times-Roman',bold='Times-Bold',italic='Times-Italic',boldItalic='Times-BoldItalic')
        # Use the built-in family when the optional system fonts are unavailable.
        pdfmetrics.registerFont(pdfmetrics.Font('Body','Times-Roman','WinAnsiEncoding'))
        pdfmetrics.registerFont(pdfmetrics.Font('BodyBold','Times-Bold','WinAnsiEncoding'))
    c = colors.HexColor
    styles = {
        'body':ParagraphStyle('body',fontName='Body',fontSize=10.2,leading=15.6,textColor=c(INK),spaceAfter=9,alignment=TA_LEFT),
        'h2':ParagraphStyle('h2',fontName='BodyBold',fontSize=15,leading=19.8,textColor=c(INK),spaceBefore=21,spaceAfter=10,keepWithNext=True),
        'h3':ParagraphStyle('h3',fontName='BodyBold',fontSize=11.5,leading=16,textColor=c(TEAL),spaceBefore=13,spaceAfter=7,keepWithNext=True),
        'caption':ParagraphStyle('caption',fontName='Helvetica',fontSize=8.2,leading=11.8,textColor=c('#47606c'),spaceAfter=15),
        'table':ParagraphStyle('table',fontName='Helvetica',fontSize=8.6,leading=12,textColor=c(INK)),
        'thead':ParagraphStyle('thead',fontName='Helvetica-Bold',fontSize=8.6,leading=12,textColor=colors.white),
        'ref':ParagraphStyle('ref',fontName='Helvetica',fontSize=8.3,leading=12,spaceAfter=8,textColor=c(INK)),
    }
    width = 483.28
    def diagram(kind):
        w,h,boxes,arrows = figure_spec(kind)
        d = Drawing(w,h)
        for x,y,bw,bh,title,sub in boxes:
            d.add(Rect(x,h-y-bh,bw,bh,rx=6,ry=6,fillColor=c(PALE),strokeColor=c('#b9d4d3'),strokeWidth=.7))
            d.add(String(x+bw/2,h-y-19,title,fontName='Helvetica-Bold',fontSize=11,fillColor=c(INK),textAnchor='middle'))
            d.add(String(x+bw/2,h-y-34,sub,fontName='Helvetica',fontSize=7.9,fillColor=c('#47606c'),textAnchor='middle'))
        import math
        for x1,y1,x2,y2 in arrows:
            y1,y2=h-y1,h-y2
            d.add(Line(x1,y1,x2,y2,strokeColor=c(TEAL),strokeWidth=1.2))
            theta=math.atan2(y2-y1,x2-x1)
            p=[x2,y2,x2-5*math.cos(theta)+2.3*math.sin(theta),y2-5*math.sin(theta)-2.3*math.cos(theta),x2-5*math.cos(theta)-2.3*math.sin(theta),y2-5*math.sin(theta)+2.3*math.cos(theta)]
            d.add(Polygon(p,fillColor=c(TEAL),strokeColor=c(TEAL)))
        scale=width/w
        d.scale(scale,scale)
        d.width=width;d.height=h*scale
        return d
    story=[]
    story += [Paragraph('PERSPECTIVE  /  OCTOBER 2026',ParagraphStyle('label',fontName='Helvetica-Bold',fontSize=8.6,leading=12,textColor=c(TEAL))),Spacer(1,15),
              Paragraph(items[0][1][1],ParagraphStyle('title',fontName='BodyBold',fontSize=32,leading=39,textColor=c(INK))),Spacer(1,8),
              Paragraph(items[1][1][1],ParagraphStyle('subtitle',fontName='Body',fontSize=17.5,leading=23,textColor=c(INK))),Spacer(1,15),
              Paragraph('Shuxing Yang',ParagraphStyle('author',fontName='Helvetica',fontSize=11,leading=16)),Spacer(1,14)]
    for kind,data in items[3:]:
        if kind == 'heading':
            level,title=data
            story.append(Paragraph(inline(title),styles['h2' if level==2 else 'h3']))
        elif kind=='paragraph':
            story.append(Paragraph(inline(data),styles['body']))
        elif kind=='figure':
            caption,path=data
            story.append(KeepTogether([Spacer(1,8),diagram(Path(path).stem),Spacer(1,8),Paragraph(inline(caption),styles['caption'])]))
        elif kind=='table':
            rows=[[Paragraph(inline(cell),styles['thead' if r==0 else 'table']) for cell in row] for r,row in enumerate(data)]
            table=Table(rows,colWidths=[width*.32,width*.68],repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),c(INK)),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,c(PALE)]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,-1),.3,c('#c8d7db'))]))
            story += [Spacer(1,7),table,Spacer(1,12)]
    story += [Paragraph(reference_text(r,True),styles['ref']) for r in refs]
    def furniture(canvas,doc):
        canvas.saveState()
        canvas.setStrokeColor(c('#c8d7db'));canvas.setLineWidth(.5)
        canvas.line(56,45,539.28,45)
        canvas.setFont('Helvetica',7.6);canvas.setFillColor(c('#536875'))
        canvas.drawString(56,32,'AI4Instruments  |  Shuxing Yang')
        canvas.drawRightString(539.28,32,str(doc.page))
        if doc.page>1:
            canvas.drawString(56,812,'INSTRUMENTS AS PROGRAMMABLE PARTNERS IN SCIENTIFIC DISCOVERY')
        canvas.restoreState()
    doc=SimpleDocTemplate(str(PAPER/'AI4Instruments.pdf'),pagesize=(595.28,841.89),leftMargin=56,rightMargin=56,topMargin=50,bottomMargin=62,title='AI4Instruments: Instruments as programmable partners in scientific discovery',author='Shuxing Yang',subject='Instrument design, experimental operations and autonomous scientific research')
    doc.build(story,onFirstPage=furniture,onLaterPages=furniture)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html-only',action='store_true')
    args=parser.parse_args()
    refs=references()
    manuscript=(PAPER/'manuscript.md').read_text(encoding='utf-8').partition('## References')[0].rstrip()+'\n\n## References\n'
    items=list(blocks(manuscript))
    bibliography=[]
    for r in refs:
        entry=f'[{r["number"]}] {r["authors"]} ({r["year"]}). [{r["title"]}]({r["url"]}). {r["venue"]}.'
        if r.get('correction_url'):
            entry+=f' [Author correction]({r["correction_url"]}).'
        if r.get('accessed'):
            entry+=f' Accessed {r["accessed"]}.'
        bibliography.append(entry)
    (PAPER/'manuscript.md').write_text(manuscript+'\n'+'\n\n'.join(bibliography)+'\n',encoding='utf-8')
    build_html(items,refs)
    if not args.html_only:
        build_pdf(items,refs)
    print('Built paper/AI4Instruments.html' + ('' if args.html_only else ' and paper/AI4Instruments.pdf'))

if __name__=='__main__':
    main()
