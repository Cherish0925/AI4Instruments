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
AUTHOR = 'Shuxing Yang'
VERSION = '0.2.1'


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
    """Native-vector figures share geometry between the HTML and PDF editions.

    Coordinates use the SVG convention (origin at the upper left). An arrow is
    a sequence of points; only its last segment carries an arrowhead.
    """
    if kind == 'design-transition':
        return 490, 307, [
            (12, 30, 142, 57, 'Existing instruments', 'Inherited hardware\nand software interfaces'),
            (174, 30, 142, 57, 'Integration', 'Drivers, documentation\nand tool interfaces'),
            (336, 30, 142, 57, 'AI use', 'Experiments within\nexposed capabilities'),
            (18, 136, 204, 57, 'Research questions', 'What should become possible?'),
            (268, 136, 204, 57, 'Instrument design', 'Mechanics / circuits / firmware'),
            (268, 236, 204, 57, 'Experimental use', 'Program / act / observe / infer'),
            (18, 236, 204, 57, 'Evidence', 'Results / trajectories / limitations'),
        ], [
            [(154, 58), (174, 58)], [(316, 58), (336, 58)],
            [(222, 164), (268, 164)], [(370, 193), (370, 236)],
            [(268, 264), (222, 264)], [(120, 236), (120, 193)],
            [(222, 248), (268, 181)],
        ], [
            (12, 14, 'Instruments4AI: adaptation after design'),
            (18, 119, 'AI4Instruments: design and use evolve together'),
        ]
    if kind == 'operation-hierarchy':
        return 490, 349, [
            (18, 12, 256, 48, 'Research objective', 'Question, evidence and evaluation'),
            (18, 92, 256, 48, 'Workflow Operations', 'Composition across resources and time'),
            (18, 171, 256, 48, 'Standard Operations', 'Reusable experimental procedures'),
            (18, 250, 256, 48, 'Basic Operations', 'Elementary control and observation'),
            (321, 92, 151, 69, 'Development', 'Change procedures,\ncontrollers and apparatus'),
            (321, 250, 151, 69, 'Physical apparatus', 'Actuation, sensing\nand material processes'),
        ], [
            [(135, 60), (135, 92)],
            [(135, 140), (135, 171)], [(157, 171), (157, 140)],
            [(135, 219), (135, 250)], [(157, 250), (157, 219)],
            [(18, 116), (4, 116), (4, 274), (18, 274)],
            [(274, 265), (321, 265)], [(321, 291), (274, 291)],
            [(274, 116), (321, 116)],
            [(397, 161), (397, 250)],
            [(472, 284), (486, 284), (486, 36), (274, 36)],
        ], [
            (18, 339, 'Any level may be inspected and recomposed'),
        ]
    if kind == 'experimental-learning':
        return 490, 306, [
            (18, 15, 202, 58, 'Experimental capability', 'What can be controlled,\nmeasured and constructed'),
            (270, 15, 202, 58, 'Experiments', 'Questions, actions\nand physical observations'),
            (270, 121, 202, 58, 'Linked evidence', 'Conditions, trajectories,\nresults and uncertainty'),
            (18, 121, 202, 58, 'Scientific knowledge', 'Findings, explanations\nand new research questions'),
            (270, 229, 202, 58, 'Model learning', 'Training and evaluation\non new experiments'),
            (18, 229, 202, 58, 'Instrument development', 'New access, performance\nand observable degrees of freedom'),
        ], [
            [(220, 44), (270, 44)], [(371, 73), (371, 121)],
            [(270, 150), (220, 150)], [(270, 166), (220, 244)],
            [(371, 179), (371, 229)],
            [(18, 258), (4, 258), (4, 44), (18, 44)],
            [(472, 258), (486, 258), (486, 44), (472, 44)],
        ], []
    if kind != 'experimental-loop':
        raise ValueError(f'Unknown figure: {kind}')
    return 490, 300, [
        (148, 8, 194, 42, 'Select target positions', 'Research objective and search'),
        (18, 82, 194, 44, 'x.position', 'Set target and observe convergence'),
        (278, 82, 194, 44, 'y.position', 'Set target and observe convergence'),
        (148, 160, 194, 46, 'detector.capture', 'Configure / read back / acquire'),
        (148, 242, 194, 46, 'Evaluate observation', 'Record evidence and update search')
    ], [[(200,50),(115,82)],[(290,50),(375,82)],[(115,126),(200,160)],
         [(375,126),(290,160)],[(245,206),(245,242)],
         [(342,265),(482,265),(482,29),(342,29)]], []


def svg_figure(kind):
    w,h,boxes,arrows,labels = figure_spec(kind)
    marker_id = f'{kind}-arrow'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{kind.replace("-", " ")}">',
             f'<defs><marker id="{marker_id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#126b71"/></marker></defs>']
    for x,y,bw,bh,title,sub in boxes:
        parts += [f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="6" fill="{PALE}" stroke="#b9d4d3"/>',
                  f'<text x="{x+bw/2}" y="{y+19}" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="600" fill="{INK}">{html.escape(title)}</text>']
        for line_no,line in enumerate(sub.splitlines()):
            parts.append(f'<text x="{x+bw/2}" y="{y+34+line_no*11}" text-anchor="middle" font-family="sans-serif" font-size="8.2" fill="#47606c">{html.escape(line)}</text>')
    for points in arrows:
        coordinates = ' '.join(f'{x},{y}' for x,y in points)
        parts.append(f'<polyline points="{coordinates}" fill="none" stroke="{TEAL}" stroke-width="1.3" marker-end="url(#{marker_id})"/>')
    for x,y,label in labels:
        parts.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="9" font-weight="600" fill="{TEAL}">{html.escape(label)}</text>')
    parts.append('</svg>')
    return ''.join(parts)


def document_parts(items):
    """Separate the sole title and author from the manuscript body."""
    if not items or items[0][0] != 'heading' or items[0][1][0] != 1:
        raise ValueError('The manuscript must begin with one level-one title.')
    title = items[0][1][1]
    body_start = 1
    if len(items) > 1 and items[1] == ('paragraph', f'**{AUTHOR}**'):
        body_start = 2
    body = items[body_start:]
    if any(kind == 'heading' and data[0] == 1 for kind,data in body):
        raise ValueError('Only one level-one title is permitted.')
    return title,body


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
:root{--ink:#20242a;--teal:#126b71;--muted:#50565b}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;color:var(--ink);font:17px/1.65 Georgia,'Times New Roman',serif}
main{max-width:880px;margin:0 auto;padding:64px 48px 40px}
header{text-align:center;margin:0 0 36px}h1{font-size:32px;line-height:1.25;font-weight:700;margin:0 0 22px}header .author{font-size:18px;margin:0;text-align:center}
a{color:var(--teal);text-decoration-thickness:1px;text-underline-offset:3px}p{margin:0 0 15px;text-align:justify;hyphens:auto}
.abstract{margin:0 28px 26px;font-size:15.5px;line-height:1.6}.abstract h2{font-size:17px;text-align:center;margin:0 0 12px}
details.contents{font-size:14px;line-height:1.5;margin:0 0 32px;color:var(--muted)}details.contents summary{cursor:pointer;width:max-content;margin:auto}nav ol{list-style:none;padding:0;margin:14px 0;columns:2;column-gap:28px}nav li{margin-bottom:6px;break-inside:avoid}
h2{font-size:21px;line-height:1.35;margin:32px 0 14px;scroll-margin-top:20px}h3{font-size:18px;line-height:1.4;margin:25px 0 12px}figure{margin:25px 0 28px}svg{display:block;width:100%;height:auto}figcaption,.table-caption{font-size:14px;line-height:1.5;text-align:left;margin:12px 0 0}p.table-caption{margin:22px 0 8px}
table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.5;margin:0 0 22px;border-top:1.3px solid #333;border-bottom:1.3px solid #333}th,td{padding:9px 10px;text-align:left;vertical-align:top}th{font-weight:700;border-bottom:.8px solid #555}td{border-bottom:.4px solid #ddd}td:first-child{width:32%}table.three-columns td:first-child{width:24%}table.three-columns td:nth-child(2){width:33%}table.three-columns td:nth-child(3){width:43%}
.references{font-size:14px;line-height:1.55}.references p{margin:0 0 12px 25px;text-indent:-25px;text-align:left;overflow-wrap:anywhere}footer{border-top:1px solid #ddd;margin-top:35px;padding-top:16px;font-size:12px;line-height:1.65;color:var(--muted);text-align:center}footer a{margin:0 6px}
@media(max-width:650px){body{font-size:16px}main{padding:36px 22px 28px}h1{font-size:clamp(24px,5.8vw,32px)}header{margin-bottom:28px}.abstract{margin-left:5px;margin-right:5px;font-size:14.5px}p{text-align:left}nav ol{columns:1}h2{font-size:20px}h3{font-size:17px}th,td{padding:8px 6px}table{font-size:12px}figcaption,.table-caption{font-size:13px}}
@media print{@page{size:A4;margin:20mm}body{font-size:10.5pt;line-height:1.4}main{max-width:none;margin:0;padding:0}header{margin-bottom:20pt}h1{font-size:22pt}.abstract{font-size:9.5pt}.abstract h2{font-size:10.5pt}h2{font-size:12.5pt}h3{font-size:11pt}details.contents,footer{display:none}h2,h3,.table-caption{break-after:avoid}figure,table{break-inside:avoid}a{color:inherit;text-decoration:none}figcaption,.table-caption,table,.references{font-size:9pt}}
'''


def build_html(items, refs):
    title,body = document_parts(items)
    title_display = html.escape(title).replace(' to AI4Instruments', '<br>to AI4Instruments')
    toc = [(f'section-{i}', data[1]) for i,(kind,data) in enumerate(body)
           if kind == 'heading' and data[0] == 2]
    out = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
           f'<title>{html.escape(title)}</title>',
           f'<meta name="author" content="{AUTHOR}">',
           '<meta name="description" content="A perspective on AI participation in instrument design, experimental use and the development of new physical capabilities.">',
           f'<style>{CSS}</style></head><body><main><header>',
           f'<h1>{title_display}</h1><p class="author">{AUTHOR}</p>',
           '</header>']
    in_abstract = False
    for i,(kind,data) in enumerate(body):
        if kind == 'heading':
            level,title = data
            if in_abstract:
                out.append('</section><details class="contents"><summary>Contents</summary><nav aria-label="Contents"><ol>')
                out += [f'<li><a href="#{anchor}">{html.escape(entry)}</a></li>' for anchor,entry in toc if entry != 'Abstract']
                out.append('</ol></nav></details>')
                in_abstract = False
            if title == 'Abstract':
                out.append('<section class="abstract" aria-label="Abstract">')
                in_abstract = True
            out.append(f'<h{level} id="section-{i}">{inline(title)}</h{level}>')
        elif kind == 'paragraph':
            css_class = ' class="table-caption"' if data.startswith('**Table ') else ''
            out.append(f'<p{css_class}>{inline(data)}</p>')
        elif kind == 'table':
            css_class = ' class="three-columns"' if len(data[0]) == 3 else ''
            out.append(f'<table{css_class}><thead><tr>' + ''.join(f'<th scope="col">{inline(c)}</th>' for c in data[0]) + '</tr></thead><tbody>')
            out += ['<tr>'+''.join(f'<td>{inline(c)}</td>' for c in row)+'</tr>' for row in data[1:]]
            out.append('</tbody></table>')
        elif kind == 'figure':
            caption,path = data
            out.append('<figure>' + svg_figure(Path(path).stem) + f'<figcaption>{inline(caption)}</figcaption></figure>')
    out.append('<div class="references">')
    out += [f'<p id="ref-{r["number"]}">{reference_text(r)}</p>' for r in refs]
    out.append(f'</div><footer><a href="https://github.com/Cherish0925/AI4Instruments">Repository</a> · <a href="https://github.com/Cherish0925/AI4Instruments/raw/refs/heads/main/paper/AI4Instruments.pdf">PDF</a><br>© 2026 {AUTHOR}. Text and original figures: CC BY 4.0. Version {VERSION}.</footer></main></body></html>')
    (PAPER/'AI4Instruments.html').write_text('\n'.join(out),encoding='utf-8')
    for kind in ['design-transition','operation-hierarchy','experimental-learning','experimental-loop']:
        (ROOT/'assets'/f'{kind}.svg').write_text(svg_figure(kind),encoding='utf-8')


def build_pdf(items, refs):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
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
        'body':ParagraphStyle('body',fontName='Body',fontSize=10.5,leading=14.7,textColor=c('#20242a'),spaceAfter=8,alignment=TA_JUSTIFY,allowWidows=0,allowOrphans=0),
        'abstract':ParagraphStyle('abstract',fontName='Body',fontSize=9.5,leading=13.5,leftIndent=20,rightIndent=20,textColor=c('#20242a'),spaceAfter=12,alignment=TA_JUSTIFY),
        'abstract_heading':ParagraphStyle('abstract_heading',fontName='BodyBold',fontSize=10.5,leading=14,alignment=TA_CENTER,spaceBefore=6,spaceAfter=8,keepWithNext=True),
        'h2':ParagraphStyle('h2',fontName='BodyBold',fontSize=12.5,leading=17,textColor=c('#20242a'),spaceBefore=17,spaceAfter=9,keepWithNext=True),
        'h3':ParagraphStyle('h3',fontName='BodyBold',fontSize=11,leading=15,textColor=c('#20242a'),spaceBefore=13,spaceAfter=7,keepWithNext=True),
        'caption':ParagraphStyle('caption',fontName='Body',fontSize=8.8,leading=12,textColor=c('#20242a'),spaceAfter=13),
        'table_caption':ParagraphStyle('table_caption',fontName='Body',fontSize=8.8,leading=12,textColor=c('#20242a'),spaceBefore=9,spaceAfter=7,keepWithNext=True),
        'table':ParagraphStyle('table',fontName='Body',fontSize=8.7,leading=12,textColor=c('#20242a')),
        'thead':ParagraphStyle('thead',fontName='BodyBold',fontSize=8.7,leading=12,textColor=c('#20242a')),
        'ref':ParagraphStyle('ref',fontName='Body',fontSize=8.6,leading=12.2,leftIndent=20,firstLineIndent=-20,spaceAfter=8,textColor=c('#20242a')),
    }
    # ReportLab's content frame has a six-point inset on both sides.
    width = 467.28
    def diagram(kind):
        w,h,boxes,arrows,labels = figure_spec(kind)
        d = Drawing(w,h)
        for x,y,bw,bh,title,sub in boxes:
            d.add(Rect(x,h-y-bh,bw,bh,rx=6,ry=6,fillColor=c(PALE),strokeColor=c('#b9d4d3'),strokeWidth=.7))
            d.add(String(x+bw/2,h-y-19,title,fontName='Helvetica-Bold',fontSize=11,fillColor=c(INK),textAnchor='middle'))
            for line_no,line in enumerate(sub.splitlines()):
                d.add(String(x+bw/2,h-y-34-line_no*11,line,fontName='Helvetica',fontSize=8.2,fillColor=c('#47606c'),textAnchor='middle'))
        import math
        for points in arrows:
            for (x1,y1),(x2,y2) in zip(points,points[1:]):
                d.add(Line(x1,h-y1,x2,h-y2,strokeColor=c(TEAL),strokeWidth=1.2))
            (x1,y1),(x2,y2)=points[-2:]
            y1,y2=h-y1,h-y2
            theta=math.atan2(y2-y1,x2-x1)
            p=[x2,y2,x2-5*math.cos(theta)+2.3*math.sin(theta),y2-5*math.sin(theta)-2.3*math.cos(theta),x2-5*math.cos(theta)-2.3*math.sin(theta),y2-5*math.sin(theta)+2.3*math.cos(theta)]
            d.add(Polygon(p,fillColor=c(TEAL),strokeColor=c(TEAL)))
        for x,y,label in labels:
            d.add(String(x,h-y,label,fontName='Helvetica-Bold',fontSize=9,fillColor=c(TEAL)))
        scale=width/w
        d.scale(scale,scale)
        d.width=width;d.height=h*scale
        return d
    document_title,body = document_parts(items)
    title_display = inline(document_title).replace(' to AI4Instruments', '<br/>to AI4Instruments')
    story=[]
    story += [Paragraph(title_display,ParagraphStyle('title',fontName='BodyBold',fontSize=22,leading=28,textColor=c('#20242a'),alignment=TA_CENTER)),Spacer(1,16),
              Paragraph(AUTHOR,ParagraphStyle('author',fontName='Body',fontSize=11.5,leading=16,alignment=TA_CENTER)),Spacer(1,22)]
    in_abstract = False
    for kind,data in body:
        if kind == 'heading':
            level,title=data
            in_abstract = title == 'Abstract'
            style_name = 'abstract_heading' if in_abstract else ('h2' if level==2 else 'h3')
            story.append(Paragraph(inline(title),styles[style_name]))
        elif kind=='paragraph':
            style_name = 'table_caption' if data.startswith('**Table ') else ('abstract' if in_abstract else 'body')
            story.append(Paragraph(inline(data),styles[style_name]))
        elif kind=='figure':
            caption,path=data
            story.append(KeepTogether([Spacer(1,8),diagram(Path(path).stem),Spacer(1,8),Paragraph(inline(caption),styles['caption'])]))
        elif kind=='table':
            rows=[[Paragraph(inline(cell),styles['thead' if r==0 else 'table']) for cell in row] for r,row in enumerate(data)]
            columns=len(data[0])
            if columns == 2:
                column_widths = [width*.32,width*.68]
            elif columns == 3:
                column_widths = [width*.24,width*.33,width*.43]
            else:
                column_widths = [width/columns]*columns
            if any(len(row)!=columns for row in data):
                raise ValueError('Every row of a table must have the same column count.')
            table=Table(rows,colWidths=column_widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEABOVE',(0,0),(-1,0),.9,c('#333333')),('LINEBELOW',(0,0),(-1,0),.6,c('#333333')),('LINEBELOW',(0,-1),(-1,-1),.9,c('#333333'))]))
            # Keep the caption and complete table on one page.
            caption = story.pop() if story and isinstance(story[-1],Paragraph) and story[-1].style.name == 'table_caption' else None
            story.append(KeepTogether(([caption] if caption else []) + [table,Spacer(1,12)]))
    story += [Paragraph(reference_text(r,True),styles['ref']) for r in refs]
    def furniture(canvas,doc):
        canvas.saveState()
        canvas.setFont('Body',9);canvas.setFillColor(c('#50565b'))
        canvas.drawCentredString(595.28/2,30,str(doc.page))
        canvas.restoreState()
    doc=SimpleDocTemplate(str(PAPER/'AI4Instruments.pdf'),pagesize=(595.28,841.89),leftMargin=58,rightMargin=58,topMargin=57,bottomMargin=55,title=document_title,author=AUTHOR,subject='AI participation in instrument design, experimental use and the development of physical capabilities')
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
