#!/usr/bin/env python3
"""Build the bilingual, offline research pages and source indexes. Stdlib only."""
import base64
import csv
import html
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CAT = json.loads((ROOT / 'catalogue.json').read_text())
CTX = json.loads((ROOT / 'context.json').read_text())
PROJECTS = CAT['projects']
BY_ID = {p['id']: p for p in PROJECTS}
assert len(BY_ID) == len(PROJECTS), 'duplicate project id'
assert len({p['repository'].lower() for p in PROJECTS}) == len(PROJECTS), 'duplicate repository'
for p in PROJECTS:
    assert set(p['related']) <= set(BY_ID), (p['id'], 'unknown relation')
    assert p['description']['zh'] and p['description']['en'] and p['sources']
    assert p['evidence']['zh'] and p['evidence']['en']
    assert p['license_class'] != 'open' or p['license'] not in ('Unspecified', 'NOASSERTION')

CATEGORIES = {
 'protocol': ('设备协议', 'Device protocols'), 'runtime': ('执行与编排', 'Execution & orchestration'),
 'measurement': ('测量与台架', 'Measurement & benches'), 'microscopy': ('显微与束线', 'Microscopy & beamlines'),
 'quantum': ('量子实验', 'Quantum experiments'), 'chemistry': ('化学与液体处理', 'Chemistry & liquid handling'),
 'industrial': ('工业与设施', 'Industry & facilities'), 'embedded': ('嵌入式与调试', 'Embedded & debugging'),
 'robotics': ('机器人', 'Robotics'), 'gui': ('GUI 与操作知识', 'GUI & operating knowledge')}
LICENSES = {'open': ('明确开源许可', 'Open-source license'), 'mixed': ('框架与组件许可不同', 'Mixed licensing'),
 'restricted': ('限制性许可', 'Restricted license'), 'unspecified': ('许可证未识别', 'License not identified')}
EVIDENCE = {'experiment': ('论文实机案例', 'Published experiment'), 'hardware': ('维护者实机记录', 'Maintainer hardware record'),
 'adapter': ('接入实现 / 文档', 'Adapter / documentation'), 'simulation': ('模拟验证', 'Simulation-verified'),
 'artifact': ('配套代码 / 资料', 'Supporting code / material'), 'proposal': ('构想 / 提案', 'Concept / proposal')}
ROLES = {'overview': ('项目说明', 'Overview'), 'license': ('许可证', 'License'), 'implementation': ('实现入口', 'Implementation'), 'paper': ('论文', 'Paper')}
REPO = 'https://github.com/Cherish0925/AI4Instruments'

def esc(s): return html.escape(str(s), quote=True)
def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)

def markdown(text):
    out=[]; lines=text.splitlines(); i=0
    while i < len(lines):
        l=lines[i].strip()
        if not l: i+=1; continue
        if l.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i+=1
            out.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+inline(c)+'</th>' for c in rows[0])+'</tr></thead><tbody>')
            for row in rows[2:]:out.append('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in row)+'</tr>')
            out.append('</tbody></table></div>'); continue
        m=re.match(r'^(#{1,4}) (.+)',l)
        if m: out.append(f'<h{len(m[1])}>{inline(m[2])}</h{len(m[1])}>'); i+=1; continue
        block=[l];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|')):block.append(lines[i]);i+=1
        out.append('<p>'+inline(' '.join(block))+'</p>')
    return '\n'.join(out)

source_map={}
def register(url, subject, role):
    entry=source_map.setdefault(url,{'url':url,'subjects':[],'roles':[],'reviewed':CAT['reviewed']})
    if subject not in entry['subjects']:entry['subjects'].append(subject)
    if role not in entry['roles']:entry['roles'].append(role)
for p in PROJECTS:
    for s in p['sources']:register(s['url'],p['id'],s['role'])
for s in CTX['standards']:
    for u in s['sources']:register(u,s['id'],'standard-or-ecosystem')
for c in CTX['components']:register(c['url'],c['parent'],'component')
for x in CTX['boundaries']:register(x['url'],x['name'],'scope-boundary')
for u in CTX['discovery_sources']:register(u,'discovery-index','discovery-only')
SOURCES=list(source_map.values())
(ROOT/'sources.json').write_text(json.dumps({'reviewed':CAT['reviewed'],'sources':SOURCES},ensure_ascii=False,indent=2)+'\n')
DOCUMENTS = {name: (ROOT / name).read_text() for name in (
    'guide.zh-CN.md', 'guide.en.md', 'catalogue.schema.json',
    'examples/measurement-contract.json', 'examples/README.md')}
DATA={'catalogue':CAT,'context':CTX,'sources':SOURCES,'documents':DOCUMENTS}

STANDARD_GROUPS = [
    (('能力描述与 Agent 接口', 'Capability descriptions and agent interfaces'),
     ['mcp', 'sila', 'lads', 'wot']),
    (('执行环境与设备控制', 'Execution environments and device control'),
     ['facility', 'qcodes', 'bluesky', 'liquid', 'ros', 'bench', 'microscopy-access']),
    (('仪器协议提案与研究预览', 'Instrument protocol proposals and research previews'),
     ['aip', 'lap', 'mhs'])]
assert sorted(s['id'] for s in CTX['standards']) == sorted(
    sid for _, ids in STANDARD_GROUPS for sid in ids), 'protocol grouping mismatch'

CSS=r'''
:root{--paper:#f8f6ef;--ink:#182c25;--muted:#59685e;--line:#d8ddd2;--green:#234f3d;--gold:#ac7f38;--pale:#edf0e7;--white:#fffef9;--warm:#f3ead8;color-scheme:light}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:86px}body{margin:0;background:var(--paper);color:var(--ink);font-family:InstrumentSans,"Noto Sans CJK SC",system-ui,sans-serif;font-size:15px;line-height:1.75}a{color:var(--green);text-underline-offset:4px}a:hover{color:#7b5923}button,input,select{font:inherit}button,select{cursor:pointer}button{color:var(--ink)}button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible,a:focus-visible{outline:3px solid #ac7f38;outline-offset:4px}button{border:1px solid var(--line);border-radius:5px;background:var(--white);padding:8px 14px}button:hover{background:var(--pale)}button.primary{background:var(--green);color:white;border-color:var(--green)}[hidden]{display:none!important}.shell{width:min(1260px,calc(100% - 72px));margin:auto}.top{border-bottom:1px solid var(--line);background:var(--paper)}.top-inner{display:flex;align-items:center;justify-content:space-between;min-height:74px;gap:24px}.brand{display:flex;gap:12px;align-items:center;text-decoration:none;font-size:18px;font-weight:700;letter-spacing:-.5px}.flower{width:27px;height:27px;display:inline-block;position:relative;transform:rotate(-12deg)}.flower i{position:absolute;background:var(--gold);border-radius:55% 55% 45% 55%;width:12px;height:13px}.flower i:nth-child(1){left:0;top:0}.flower i:nth-child(2){right:0;top:0}.flower i:nth-child(3){bottom:0;left:0}.flower i:nth-child(4){bottom:0;right:0}.top-links{display:flex;gap:24px;align-items:center;font-size:13px}.lang{border:1px solid var(--line);padding:4px 11px;border-radius:30px;text-decoration:none}.hero{display:grid;grid-template-columns:1.4fr 1fr;gap:60px;padding:68px 0 52px;align-items:start}.eyebrow{color:var(--gold);text-transform:uppercase;font-size:11px;font-weight:700;letter-spacing:2px;margin:0 0 20px}h1{font-size:clamp(38px,4.5vw,64px);line-height:1.2;letter-spacing:-2px;margin:0 0 25px;font-weight:700}.hero .lead{font-size:18px;line-height:1.85;max-width:670px;color:#42584b}.hero-note{padding-top:6px}.hero-note>p{font-size:14px;color:var(--muted)}.fact{border-top:1px solid var(--line);padding:15px 0;display:grid;grid-template-columns:85px 1fr;gap:14px;font-size:13px}.fact b{font-size:17px}.fact span{color:var(--muted)}.stats{display:flex;gap:38px;padding:20px 0 26px;border-bottom:1px solid var(--line)}.stat strong{font-size:35px;line-height:1.1;letter-spacing:-1px}.stat span{display:block;color:var(--muted);font-size:12px;margin-top:5px}.section-nav{position:sticky;top:0;background:rgba(248,246,239,.97);border-bottom:1px solid var(--line);z-index:5}.section-nav .shell{display:flex;gap:27px;overflow-x:auto;white-space:nowrap;padding-top:13px;padding-bottom:13px}.section-nav a{font-size:12px;text-decoration:none}.section-nav a span{color:var(--gold);margin-right:7px}.section{padding:48px 0;border-bottom:1px solid var(--line);scroll-margin-top:60px}.section-title{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:24px}.section-title h2{font-size:28px;letter-spacing:-.8px;margin:0}.section-title p{color:var(--muted);font-size:13px;margin:8px 0 0;max-width:810px}.section-number{font-size:11px;color:var(--gold);letter-spacing:2px;margin-bottom:7px}.pathways{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}.pathway{background:var(--white);padding:23px}.pathway h3{font-size:16px;margin:0 0 8px}.pathway p{font-size:13px;color:var(--muted);margin:0 0 15px}.pathway button{border:0;background:transparent;padding:0;font-size:12px;color:var(--green);text-decoration:underline;text-underline-offset:4px}.filters{background:var(--pale);padding:20px;border:1px solid var(--line);border-radius:7px;margin-bottom:14px}.filter-top{display:flex;gap:12px}.search{flex:1;min-width:100px}.filters input,.filters select{width:100%;border:1px solid #cbd3c5;background:var(--white);padding:10px 12px;color:var(--ink);border-radius:4px}.filters label{display:block;font-size:11px;color:var(--muted);margin-bottom:5px}.filter-bottom{display:grid;grid-template-columns:1.1fr 1.3fr 1.2fr 1fr;gap:12px;margin-top:13px}.result-bar{display:flex;justify-content:space-between;gap:20px;align-items:center;font-size:12px;color:var(--muted);padding:8px 0 17px}.exports{display:flex;gap:8px}.exports button{padding:5px 10px;font-size:11px}.group-title{display:flex;justify-content:space-between;align-items:center;margin:28px 0 8px;padding:8px 0;border-bottom:2px solid var(--green);font-size:14px}.group-title span{font-size:11px;color:var(--muted);font-weight:400}.project{border-bottom:1px solid var(--line);background:var(--white);scroll-margin-top:75px}.project summary{list-style:none;display:grid;grid-template-columns:2.2fr 1.1fr 1.2fr 1.1fr 18px;align-items:center;gap:16px;padding:17px 18px;cursor:pointer}.project summary::-webkit-details-marker{display:none}.project summary:hover{background:#f2f3eb}.project .pname{font-size:14px;font-weight:700}.project .owner{display:block;font-weight:400;color:var(--muted);font-size:10px;overflow-wrap:anywhere}.badge{display:inline-block;font-size:10px;line-height:1.5;padding:4px 7px;border-radius:3px;background:var(--pale);color:#425b4d}.badge.warm{background:var(--warm);color:#785a2b}.small{font-size:11px;color:var(--muted)}.plus{font-size:20px;color:var(--gold);font-weight:400}.project[open] .plus{transform:rotate(45deg)}.project[open] summary{border-bottom:1px dashed var(--line);background:#f0f2e9}.project-body{padding:23px;display:grid;grid-template-columns:1.35fr 1fr;gap:35px}.project-body p{margin:0 0 13px;font-size:13px}.interfaces{font-size:11px;line-height:2;color:var(--green);margin:12px 0}.field-label{font-size:10px;color:var(--gold);text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}.source-links{display:flex;gap:9px;flex-wrap:wrap;font-size:11px;margin:13px 0}.source-links a{word-break:break-word}.related{font-size:11px;color:var(--muted)}.empty{padding:35px;text-align:center;background:var(--white)}.legend{font-size:12px;color:var(--muted);line-height:1.9;margin:14px 0}.legend details{border:1px solid var(--line);padding:10px 14px}.legend summary{cursor:pointer}.legend ul{margin:8px 0}.standards{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.standard{background:var(--white);border:1px solid var(--line);padding:24px}.standard h4{font-size:17px;margin:0 0 7px;letter-spacing:-.2px}.standard .role{font-size:12px;color:var(--green);margin:0 0 13px}.standard p{font-size:13px;color:var(--muted);margin:10px 0}.standard-group{margin-top:30px}.standard-group>h3{font-size:18px;margin:0 0 16px}.prose pre{overflow:auto;max-height:620px;padding:20px;background:var(--pale);font-size:12px;line-height:1.7}.prose pre code{background:none;padding:0;overflow-wrap:normal}.document-actions{margin:18px 0 26px}.table-wrap{overflow:auto;margin:16px 0;border:1px solid var(--line)}table{width:100%;border-collapse:collapse;font-size:12px;text-align:left;background:var(--white)}th{background:var(--pale);font-weight:600;color:var(--green)}th,td{padding:13px 15px;border-bottom:1px solid var(--line);vertical-align:top;min-width:120px}td:first-child{font-weight:600}td a{overflow-wrap:anywhere}tr:last-child td{border-bottom:0}.components-controls{display:flex;gap:8px;flex-wrap:wrap}.components-controls button[aria-pressed=true]{background:var(--green);color:white}.chapter{border-top:1px solid var(--line);padding:0}.chapter>summary{cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;font-size:18px;padding:21px 0;font-weight:600}.chapter>summary::-webkit-details-marker{display:none}.chapter>summary::after{content:'+';color:var(--gold);font-size:25px;font-weight:400;margin-left:20px}.chapter[open]>summary::after{content:'−'}.prose{max-width:940px;margin:0 auto 27px;font-size:14px;line-height:1.95}.prose p{margin:0 0 20px}.prose h3{font-size:19px;margin:28px 0 15px}.prose table{line-height:1.8}.prose strong{font-weight:700}.prose code{font-family:ui-monospace,monospace;font-size:12px;background:var(--pale);padding:2px 4px;border-radius:3px;overflow-wrap:anywhere}.source-list{display:grid;grid-template-columns:repeat(2,1fr);gap:8px 25px;padding-left:23px}.source-list li{font-size:11px;color:var(--muted);padding:6px 0;overflow-wrap:anywhere}.source-list a{display:block}.boundary-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:20px}.boundary{font-size:12px;border-left:2px solid var(--line);padding-left:15px}.boundary p{color:var(--muted);margin:5px 0}.downloads{display:flex;flex-wrap:wrap;gap:12px;font-size:12px}.footer{padding:32px 0 45px;color:var(--muted);font-size:11px;display:flex;justify-content:space-between;gap:25px}.footer a{color:var(--muted)}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}
@media(max-width:900px){.hero{gap:30px;grid-template-columns:1.2fr 1fr}.shell{width:calc(100% - 40px)}.project summary{grid-template-columns:1.7fr 1fr 1.1fr 18px}.project summary>.category{display:none}.pathways{grid-template-columns:repeat(2,1fr)}.standards{gap:10px}.filter-bottom{grid-template-columns:1fr 1fr}}
@media(max-width:600px){body{font-size:14px}.shell{width:calc(100% - 32px)}.top-inner{min-height:64px;gap:10px}.brand{font-size:16px}.top-links{gap:12px}.top-links>.repo{display:none}.hero{display:block;padding:40px 0 25px}.hero-note{margin-top:29px}.hero h1{font-size:39px;letter-spacing:-1.5px}.hero .lead{font-size:16px}.eyebrow{font-size:10px}.stats{gap:23px;padding:15px 0 23px}.stat strong{font-size:30px}.stat span{font-size:10px}.section-nav .shell{gap:20px;padding-top:11px;padding-bottom:11px}.section{padding:32px 0}.section-title{display:block}.section-title h2{font-size:25px}.section-title p{font-size:12px}.pathways{grid-template-columns:1fr}.pathway{padding:19px}.filters{padding:14px}.filter-top{gap:8px}.filter-top button{padding:7px 10px;font-size:12px}.filters input,.filters select{font-size:12px;padding:9px}.filter-bottom{gap:10px}.result-bar{align-items:start;font-size:11px}.project summary{grid-template-columns:1fr auto 18px;gap:10px;padding:15px 12px}.project summary>.license-summary{display:none}.project .pname{font-size:13px}.project .owner{font-size:9px}.project summary .badge{font-size:9px;max-width:100px}.project-body{display:block;padding:17px}.project-body>div+div{margin-top:22px}.standards{grid-template-columns:1fr}.standard{padding:19px}.source-list,.boundary-grid{grid-template-columns:1fr}.chapter>summary{font-size:16px;padding:18px 0}.prose{font-size:13px}.prose table{min-width:660px}.footer{display:block}.footer>div{margin:8px 0}.group-title{font-size:12px}.group-title span{font-size:10px}.table-wrap table{min-width:650px}.fact{grid-template-columns:75px 1fr}.downloads{gap:12px}}
@media print{.top-links,.section-nav,.filters,.exports,.components-controls,button{display:none!important}.shell{width:100%}.hero{padding:20px 0;gap:25px}h1{font-size:35px}.section{padding:20px 0}.project-body{display:block}.project summary{display:block}.project summary span{margin-right:10px}.project,.standard{break-inside:avoid}.standard{padding:14px}.prose{max-width:none}.table-wrap{overflow:visible}.table-wrap table{min-width:0!important}.source-list{display:block}.chapter{break-inside:auto}a{color:inherit}.footer{font-size:9px}}
'''

JS=r'''
const DATA=JSON.parse(document.getElementById('research-data').textContent);
const projects=DATA.catalogue.projects, all=[...document.querySelectorAll('.project')];
const query=document.getElementById('search'), category=document.getElementById('category'), license=document.getElementById('license'), evidence=document.getElementById('evidence'), access=document.getElementById('access');
const byId=new Map(projects.map(p=>[p.id,p]));
const texts=new Map(projects.map(p=>[p.id,JSON.stringify(p).toLowerCase()]));
const zh=document.documentElement.lang==='zh-CN';
function visible(){return all.filter(el=>!el.hidden).map(el=>byId.get(el.dataset.id))}
function apply(){const terms=query.value.toLowerCase().trim().split(/\s+/).filter(Boolean);for(const el of all){const p=byId.get(el.dataset.id);el.hidden=!(terms.every(t=>texts.get(p.id).includes(t))&&(category.value==='all'||p.category===category.value)&&(license.value==='all'||p.license_class===license.value)&&(evidence.value==='all'||p.evidence.kind===evidence.value)&&(access.value==='all'||(access.value==='mcp'&&p.mcp==='documented')||(access.value==='skills'&&p.skills==='documented')||(access.value==='reference'&&p.scope==='reference')))}const n=visible().length;document.getElementById('count').textContent=zh?`${n} / ${projects.length} 项记录`:`${n} / ${projects.length} records`;document.getElementById('empty').hidden=n!==0;for(const group of document.querySelectorAll('.project-group')){group.hidden=![...group.querySelectorAll('.project')].some(el=>!el.hidden)}}
function reset(){query.value='';for(const el of [category,license,evidence,access])el.value='all';apply()}
for(const el of [query,category,license,evidence,access])el.addEventListener(el===query?'input':'change',apply);
document.getElementById('reset').addEventListener('click',reset);
for(const el of document.querySelectorAll('[data-route]'))el.addEventListener('click',()=>{reset();category.value=el.dataset.route;apply();document.getElementById('catalogue').scrollIntoView();query.focus({preventScroll:true})});
function download(content,name,type){const a=document.createElement('a');const url=URL.createObjectURL(new Blob([content],{type}));a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000)}
document.getElementById('export-json').addEventListener('click',()=>download(JSON.stringify({schema_version:'1.0',reviewed:DATA.catalogue.reviewed,projects:visible()},null,2),'agent-instruments-filtered.json','application/json'));
document.getElementById('export-all').addEventListener('click',()=>download(JSON.stringify(DATA,null,2),'agent-instruments-research.json','application/json'));
for(const el of document.querySelectorAll('[data-document]'))el.addEventListener('click',()=>{const name=el.dataset.document;download(DATA.documents[name],name.split('/').pop(),name.endsWith('.json')?'application/json':'text/plain;charset=utf-8')});
for(const el of document.querySelectorAll('[data-dataset]'))el.addEventListener('click',()=>{const key=el.dataset.dataset;const value=key==='sources'?{reviewed:DATA.catalogue.reviewed,sources:DATA.sources}:DATA[key];download(JSON.stringify(value,null,2),key+'.json','application/json')});
document.getElementById('export-csv').addEventListener('click',()=>{const q=v=>'"'+String(v??'').replaceAll('"','""')+'"';const cols=['id','name','repository','category','license','license_class','evidence','interfaces','mcp','skills','description','evidence_note','url'];const rows=visible().map(p=>[p.id,p.name,p.repository,p.category,p.license,p.license_class,p.evidence.kind,p.interfaces.join('; '),p.mcp,p.skills,p.description[zh?'zh':'en'],p.evidence[zh?'zh':'en'],p.url]);download('\ufeff'+[cols,...rows].map(r=>r.map(q).join(',')).join('\r\n'),'agent-instruments-filtered.csv','text/csv;charset=utf-8')});
for(const b of document.querySelectorAll('[data-components]'))b.addEventListener('click',()=>{for(const x of document.querySelectorAll('[data-components]'))x.setAttribute('aria-pressed',String(x===b));for(const row of document.querySelectorAll('tr[data-parent]'))row.hidden=b.dataset.components!=='all'&&row.dataset.parent!==b.dataset.components});
document.getElementById('source-search').addEventListener('input',e=>{const q=e.target.value.toLowerCase();for(const el of document.querySelectorAll('.source-list li'))el.hidden=!el.textContent.toLowerCase().includes(q)});
function followHash(){let el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(!el)return;if(el.classList.contains('project')){reset();el.open=true}else if(el.classList.contains('chapter'))el.open=true;requestAnimationFrame(()=>el.scrollIntoView())}
addEventListener('hashchange',followHash);apply();if(location.hash)followHash();
let printState=[];addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(el=>[el,el.open]);for(const [el]of printState)el.open=true});addEventListener('afterprint',()=>{for(const [el,state]of printState)el.open=state});
'''

def build(lang):
    idx=0 if lang=='zh' else 1
    def t(z,e):return z if idx==0 else e
    def label(d,k):return d[k][idx]
    def options(d):return ''.join(f'<option value="{k}">{esc(v[idx])}</option>' for k,v in d.items())
    def a(url,text):return f'<a href="{esc(url)}">{esc(text)}</a>'
    guide=(ROOT/f'guide.{"zh-CN" if idx==0 else "en"}.md').read_text()
    chapters=[]
    for n,section in enumerate(re.split(r'^## ',guide,flags=re.M)[1:],1):
        title,_,body=section.partition('\n');chapters.append(f'<details class="chapter" id="chapter-{n}"><summary>{inline(title)}</summary><div class="prose">{markdown(body)}</div></details>')
    groups=[]
    for group in LICENSES:
        ps=[p for p in PROJECTS if p['license_class']==group]
        ps.sort(key=lambda p:(list(CATEGORIES).index(p['category']),p['name'].lower()))
        cards=[]
        for p in ps:
            role_numbers={}
            source_links=''
            for s in p['sources']:
                role_numbers[s['role']]=role_numbers.get(s['role'],0)+1
                suffix=f' {role_numbers[s["role"]]}' if sum(x['role']==s['role'] for x in p['sources'])>1 else ''
                source_links+=a(s['url'],label(ROLES,s['role'])+suffix)
            relations=' · '.join(a('#project-'+r,BY_ID[r]['name']) for r in p['related'])
            mcp=t('已记录','Documented') if p['mcp']=='documented' else t('未在本次资料中确认','Not documented in reviewed material')
            skills=t('已记录','Documented') if p['skills']=='documented' else t('未在本次资料中确认','Not documented in reviewed material')
            cards.append(f'''<details class="project" id="project-{p['id']}" data-id="{p['id']}"><summary><span class="pname">{esc(p['name'])}<span class="owner">{esc(p['repository'])}</span></span><span class="small category">{esc(label(CATEGORIES,p['category']))}</span><span><span class="badge {'warm' if p['evidence']['kind'] in ('simulation','proposal','artifact') else ''}">{esc(label(EVIDENCE,p['evidence']['kind']))}</span></span><span class="small license-summary">{esc(p['license'])}</span><span class="plus" aria-hidden="true">+</span></summary><div class="project-body"><div><div class="field-label">{t('作用与接入路径','Purpose & access path')}</div><p>{esc(p['description'][lang])}</p><div class="interfaces">{' · '.join(esc(x) for x in p['interfaces'])}</div><p class="small">MCP: {mcp}<br>Skills: {skills}</p><div class="source-links">{a(p['url'],t('上游仓库 ↗','Repository ↗'))}{source_links}</div></div><div><div class="field-label">{t('证据与复用范围','Evidence & reuse scope')}</div><p>{esc(p['evidence'][lang])}</p><p class="small">{esc(p['license'])} · {esc(label(LICENSES,p['license_class']))}<br>{t('记录类型','Record type')}: {t('实现工程','Implementation') if p['scope']=='implementation' else t('配套资料 / 设计参考','Supporting material / design reference')}</p>{'<div class="related">'+t('相关工程：','Related: ')+relations+'</div>' if relations else ''}</div></div></details>''')
        groups.append(f'<div class="project-group" data-license="{group}"><h3 class="group-title">{label(LICENSES,group)}<span>{len(ps)} {t("项记录","records")}</span></h3>'+''.join(cards)+'</div>')
    standard_cards={}
    for s in CTX['standards']:
        links=''.join(a(u,t('来源','Source')+f' {i+1}') for i,u in enumerate(s['sources']))
        standard_cards[s['id']]=f'<article class="standard" id="standard-{s["id"]}"><h4>{esc(s["name"])}</h4><p class="role">{esc(s["role"][lang])}</p><p>{esc(s["status"][lang])}</p><p>{esc(s["detail"][lang])}</p><div class="source-links">{links}</div></article>'
    standards=''.join('<div class="standard-group"><h3>'+esc(t(*names))+'</h3><div class="standards">'+''.join(standard_cards[sid] for sid in ids)+'</div></div>' for names,ids in STANDARD_GROUPS)
    rows=[]
    for c in CTX['components']:
        status={'simulated':t('模拟验证','Simulated'),'twin-tested':t('孪生验证','Twin-tested'),'template':t('人工操作模板','Manual template')}[c['status']]
        kind=t('设备 / 协议路径','Device / protocol path') if c['device_path'] else t('资料 / 人工路径','Data / manual path')
        rows.append(f'<tr data-parent="{c["parent"]}"><td>{a(c["url"],c["name"])}</td><td>{esc(BY_ID[c["parent"]]["name"])}</td><td>{esc(c["protocol"])}</td><td>{kind}</td><td>{status}</td><td>{c["tool_count"] if c["tool_count"] is not None else "—"}</td></tr>')
    sources=''.join('<li>'+a(s['url'],s['url'])+'<span>'+esc(' · '.join(s['subjects']))+'</span></li>' for s in SOURCES)
    boundaries=''.join('<div class="boundary">'+a(x['url'],x['name'])+'<p>'+esc(x['reason'][lang])+'</p></div>' for x in CTX['boundaries'])
    route_data=[('protocol',t('设计设备协议','Design a device contract'),t('比较设备能力、单位、状态、任务和数据的共同约定。','Compare shared definitions of capabilities, units, state, jobs and data.')),('runtime',t('接入已有实验室','Connect an existing laboratory'),t('从 QCoDeS、设施控制和工作流执行层出发。','Start with QCoDeS, facility controls and workflow runtimes.')),('measurement',t('连接台架仪器','Connect a measurement bench'),t('查找示波器、电源、DAQ 和 LabVIEW 接口。','Find oscilloscope, supply, DAQ and LabVIEW interfaces.')),('microscopy',t('建立图像反馈','Build an imaging feedback loop'),t('查看显微镜、光机部件、束线和视觉实验。','Explore microscopes, optomechanics, beamlines and visual experiments.')),('chemistry',t('编排液体与样品','Coordinate liquids and samples'),t('检查机器人 API、移液协议与实际执行范围。','Inspect robot APIs, liquid-handling protocols and execution scope.')),('embedded',t('开发仪器底层','Develop instrument hardware'),t('让固件、总线和调试探针进入实验反馈。','Bring firmware, buses and debug probes into the feedback loop.'))]
    pathways=''.join(f'<article class="pathway"><h3>{esc(title)}</h3><p>{esc(desc)}</p><button data-route="{cat}">{t("查看相关工程 →","Explore projects →")}</button></article>' for cat,title,desc in route_data)
    title=t('让智能体<br>操作真实仪器','Agents operating<br>physical instruments')
    lead=t('理解设备如何接入、实验如何执行、物理结果如何反馈。结合开源工程、协议分工与实验案例，形成选型、接口设计和生态建设的依据。','Understand device access, experiment execution and physical feedback. Connect open projects, protocol roles and experimental cases to decisions about integration, interface design and ecosystem development.')
    def section_title(num,title,desc):return f'<div class="section-title"><div><div class="section-number">{num}</div><h2>{title}</h2><p>{desc}</p></div></div>'
    nav=[('start',t('选择入口','Start here')),('catalogue',t('项目目录','Projects')),('standards',t('协议与生态','Protocols')),('components',t('设备组件','Components')),('guide',t('分析与设计','Analysis')),('sources',t('资料来源','Sources'))]
    font=ROOT/'assets/InstrumentSans.woff'
    fontcss="@font-face{font-family:InstrumentSans;src:url(data:font/woff;base64,"+base64.b64encode(font.read_bytes()).decode()+") format('woff');font-display:swap;font-weight:400;}" if font.exists() else ''
    payload=json.dumps(DATA,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    source_placeholder=t('搜索网址、项目或协议名称','Search URL, project or protocol')
    return f'''<!doctype html><html lang="{t('zh-CN','en')}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(lead)}"><meta name="color-scheme" content="light"><title>{t('智能体与真实仪器','Agents and physical instruments')} · AI4Instruments</title><style>{fontcss}{CSS}</style></head><body>
<a class="sr-only" href="#catalogue">{t('跳至项目目录','Skip to projects')}</a><header class="top"><div class="shell top-inner"><a class="brand" href="{REPO}"><span class="flower" aria-hidden="true"><i></i><i></i><i></i><i></i></span>AI4Instruments</a><div class="top-links"><a class="repo" href="{REPO}/tree/main/docs/agent-instruments">GitHub ↗</a><a class="lang" href="{t('index.en.html','index.zh-CN.html')}">{t('English','中文')}</a></div></div></header>
<main><div class="shell"><div class="hero"><div><p class="eyebrow">INSTRUMENTS · INTERFACES · EXPERIMENTS</p><h1>{title}</h1><p class="lead">{lead}</p></div><aside class="hero-note"><p>{t('资料核查','Source review')} / {esc(CAT['reviewed'])}</p><div class="fact"><b>{t('设备接入','Access')}</b><span>{t('发现设备、理解能力，将工具调用连接到实际驱动。','Discover devices, describe capabilities and connect tool calls to device drivers.')}</span></div><div class="fact"><b>{t('实验执行','Execution')}</b><span>{t('组合操作、协调资源，让测量过程持续运行并留下记录。','Compose operations, coordinate resources and keep experiments running with traceable records.')}</span></div><div class="fact"><b>{t('物理反馈','Feedback')}</b><span>{t('关联动作与观测，用数据评价结果、改进过程与仪器。','Link actions to observations, assess results and improve procedures and instruments.')}</span></div></aside></div><div class="stats"><div class="stat"><strong>{len(PROJECTS):02}</strong><span>{t('项目与资料记录','Project & material records')}</span></div><div class="stat"><strong>{len(CTX['standards']):02}</strong><span>{t('协议与基础生态','Protocols & foundations')}</span></div><div class="stat"><strong>{len(CTX['components']):02}</strong><span>{t('单列设备组件','Separate components')}</span></div></div></div>
<nav class="section-nav" aria-label="{t('目录','Contents')}"><div class="shell">{''.join(f'<a href="#{anchor}"><span>{i:02}</span>{text}</a>' for i,(anchor,text) in enumerate(nav,1))}</div></nav>
<div class="shell"><section class="section" id="start">{section_title('01',t('从你已有的设备出发','Start with the equipment you have'),t('先找到接入路径，再比较契约与执行方式。','Find the access path, then compare contracts and execution.'))}<div class="pathways">{pathways}</div></section>
<section class="section" id="catalogue">{section_title('02',t('项目目录','Project directory'),t('开源许可、实现范围与实机证据分别记录。展开任一项目，查看接口、依赖和原始来源。','Licensing, implementation scope and hardware evidence are recorded separately. Expand a project for interfaces, dependencies and primary sources.'))}
<div class="filters"><div class="filter-top"><div class="search"><label for="search">{t('检索项目、仪器、接口或关键词','Search projects, instruments, interfaces or keywords')}</label><input id="search" type="search" placeholder="{t('例如：Nanonis、SCPI、显微镜、QCoDeS','e.g. Nanonis, SCPI, microscope, QCoDeS')}" autocomplete="off"></div><button id="reset">{t('重置','Reset')}</button></div><div class="filter-bottom"><div><label for="category">{t('领域与角色','Domain & role')}</label><select id="category"><option value="all">{t('全部领域','All domains')}</option>{options(CATEGORIES)}</select></div><div><label for="license">{t('许可','License')}</label><select id="license"><option value="all">{t('全部许可状态','All license statuses')}</option>{options(LICENSES)}</select></div><div><label for="evidence">{t('实验与实现证据','Experiment & implementation evidence')}</label><select id="evidence"><option value="all">{t('全部证据类型','All evidence types')}</option>{options(EVIDENCE)}</select></div><div><label for="access">{t('接入与资料','Access & material')}</label><select id="access"><option value="all">{t('全部记录','All records')}</option><option value="mcp">MCP {t('已记录','documented')}</option><option value="skills">Skills {t('已记录','documented')}</option><option value="reference">{t('配套资料 / 参考','Supporting / reference')}</option></select></div></div></div>
<div class="result-bar"><span id="count" aria-live="polite">{len(PROJECTS)} {t('项记录','records')}</span><div class="exports"><button id="export-json">JSON ↓</button><button id="export-csv">CSV ↓</button></div></div><div id="empty" class="empty" hidden>{t('没有匹配项。请减少筛选条件。','No matches. Try fewer filters.')}</div>{''.join(groups)}
<div class="legend"><details><summary>{t('如何阅读这些状态','How to read the status labels')}</summary><p>{t('“接入实现 / 文档”表示已有具体连接路径，不表示已完成实机验证；“模拟验证”指项目明确报告的模拟或孪生测试；“论文实机案例”和“维护者实机记录”分别标明来源性质。未确认 MCP 或 Skills 不等于确定不存在。','“Adapter / documentation” identifies a concrete integration route, not completed hardware validation. “Simulation-verified” denotes reported simulator or twin testing. Published and maintainer hardware records distinguish evidence sources. An undocumented MCP or skill interface is not a claim that none exists.')}</p></details></div></section>
<section class="section" id="standards">{section_title('03',t('协议与基础生态','Protocols and foundations'),t('设备契约、Agent 接口、执行系统与底层总线处于不同层。这里把它们放回各自的位置。','Device contracts, agent interfaces, runtimes and buses occupy different layers. Each entry is placed in its role.'))}{standards}</section>
<section class="section" id="components">{section_title('04',t('设备组件索引','Device component index'),t('LabMCP 的 32 个组件与 OpenMHP 的 8 个设备包单独列出；它们不增加独立项目计数。','LabMCP’s 32 components and OpenMHP’s eight device packages are listed separately, without inflating project counts.'))}<div class="components-controls"><button data-components="all" aria-pressed="true">{t('全部','All')}</button><button data-components="labmcp" aria-pressed="false">LabMCP · 32</button><button data-components="openmhp" aria-pressed="false">OpenMHP · 8</button></div><div class="table-wrap"><table><thead><tr>{''.join('<th>'+x+'</th>' for x in [t('组件','Component'),t('所属工程','Project'),t('设备侧接口','Device-side interface'),t('用途','Path'),t('验证状态','Status'),t('工具数','Tools')])}</tr></thead><tbody>{''.join(rows)}</tbody></table></div><p class="small">{t('设备路径表示适配目标；此表的模拟状态不代表实机通过。手动离心机模板需要操作者执行，质谱数据和工作单组件不直接驱动仪器。','Device path describes the adapter target, not verified hardware execution. The manual centrifuge template requires an operator; MS data and worklist components do not directly drive instruments.')}</p></section>
<section class="section" id="guide">{section_title('05',t('理解接口，设计生态','Understand interfaces, design an ecosystem'),t('贯通系统分工、工程选择、接口契约与生态协作，结合光学对准、长扫描和液体处理说明设计取舍。','Connect system responsibilities, project selection, interface contracts and ecosystem development through optical alignment, long scans and liquid handling.'))}{''.join(chapters)}<details class="chapter" id="contract-example"><summary>{t('09 · 从接口设计到一份测量记录','09 · From interface design to a measurement record')}</summary><div class="prose"><p>{t('这份设计示例用合成数据串起设备能力、采集请求、任务受理、观测和结束记录。请求返回 queued，采集结束才返回 completed；功率来自设备读数，波长设定来自状态追踪，分别标记 reported 与 tracked。','This design example uses synthetic data to connect device capabilities, an acquisition request, job acceptance, an observation and completion. The request returns queued; completion is recorded after acquisition. Power is reported by the device interface, while the wavelength setting is tracked.')}</p><p>{t('校准信息和不确定度保留各自的可用状态；采集完成与实验目标是否达成分别记录。将这些语义落到已有驱动和执行服务，才形成可运行的接口。','Calibration and uncertainty retain their availability status. Acquisition completion and assessment of the experimental objective are recorded separately. Implementing these meanings in a driver and execution service creates a working interface.')}</p><pre><code>{esc(DOCUMENTS['examples/measurement-contract.json'])}</code></pre><button data-document="examples/measurement-contract.json">{t('下载契约示例 JSON ↓','Download contract example ↓')}</button></div></details><div class="downloads document-actions"><button data-document="guide.{t('zh-CN','en')}.md">{t('下载完整分析 Markdown ↓','Download full analysis Markdown ↓')}</button><button data-document="catalogue.schema.json">{t('下载目录字段规范 ↓','Download catalogue schema ↓')}</button></div></section>
<section class="section" id="sources">{section_title('06',t('来源与可复用资料','Sources and reusable material'),t('每项记录保留原始地址。网页内嵌数据，下载后可离线检索；外部文档由原站提供。','Every record retains source addresses. Embedded data remains searchable offline; external documents stay with their original publishers.'))}<div class="downloads"><button class="primary" id="export-all">{t('下载完整研究数据 JSON ↓','Download complete research data ↓')}</button><button data-dataset="catalogue">catalogue.json ↓</button><button data-dataset="context">context.json ↓</button><button data-dataset="sources">sources.json ↓</button>{a(REPO+'/tree/main/docs/agent-instruments',t('维护与重建 ↗','Maintenance & build ↗'))}</div><div class="legend"><p>{esc(CTX['method'][lang])}</p></div><details class="chapter"><summary>{t('范围边界与名称消歧','Scope boundaries and naming distinctions')}</summary><div class="boundary-grid">{boundaries}</div></details><details class="chapter"><summary>{t('完整来源索引','Complete source index')} · {len(SOURCES)}</summary><label for="source-search" class="sr-only">{source_placeholder}</label><input id="source-search" type="search" placeholder="{source_placeholder}" style="width:100%;padding:12px;border:1px solid var(--line);background:var(--white);color:var(--ink)"><ol class="source-list">{sources}</ol></details></section></div></main>
<footer class="shell footer"><div>AI4Instruments · {t('真实仪器的开放知识与开发','Open knowledge and development for physical instruments')}</div><div>{a(REPO+'/blob/main/LICENSE-docs.md','CC BY 4.0')} · {a(REPO+'/blob/main/LICENSE',t('代码 MIT','Code MIT'))} · {a('#',t('返回顶部 ↑','Back to top ↑'))}</div></footer><script id="research-data" type="application/json">{payload}</script><script>{JS}</script></body></html>'''

for lang in ('zh','en'):
    suffix='zh-CN' if lang=='zh' else 'en'
    (ROOT/f'index.{suffix}.html').write_text(build(lang))
    idx=0 if lang=='zh' else 1
    lines=[f'# {"项目目录" if idx==0 else "Project catalogue"}', '', '[中文 HTML](index.zh-CN.html) · [English HTML](index.en.html) · [JSON](catalogue.json)', '']
    for p in PROJECTS:
        lines += [f'## {p["name"]}', '', f'[{p["repository"]}]({p["url"]}) · {CATEGORIES[p["category"]][idx]} · {p["license"]} · {EVIDENCE[p["evidence"]["kind"]][idx]}', '', p['description'][lang], '', p['evidence'][lang], '', ' / '.join(p['interfaces']), '', ' · '.join(f'[{ROLES[s["role"]][idx]}]({s["url"]})' for s in p['sources']), '']
    (ROOT/f'catalogue.{suffix}.md').write_text('\n'.join(lines)+'\n')
output=io.StringIO(newline='')
writer=csv.writer(output)
writer.writerow(['id','name','repository','category','scope','license','license_class','evidence','mcp','skills','interfaces','description_zh','description_en','evidence_zh','evidence_en','url','reviewed'])
for p in PROJECTS:writer.writerow([p['id'],p['name'],p['repository'],p['category'],p['scope'],p['license'],p['license_class'],p['evidence']['kind'],p['mcp'],p['skills'],'; '.join(p['interfaces']),p['description']['zh'],p['description']['en'],p['evidence']['zh'],p['evidence']['en'],p['url'],p['reviewed']])
(ROOT/'catalogue.csv').write_text(output.getvalue(),encoding='utf-8-sig')
print(f'Built 2 languages · {len(PROJECTS)} project records · {len(CTX["components"])} components · {len(SOURCES)} source URLs')
