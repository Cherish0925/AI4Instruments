#!/usr/bin/env python3
"""Build the bilingual instrument landscape and portable data. Python stdlib only."""
import csv
import io
import json
from pathlib import Path
from reader import render, CATEGORIES, EVIDENCE, ROLES

ROOT=Path(__file__).resolve().parent
read=lambda name:json.loads((ROOT/name).read_text())
CAT=read('catalogue.json');CTX=read('context.json');LAND=read('landscape.json')
PROJECTS=CAT['projects'];BY_ID={p['id']:p for p in PROJECTS}
PROFILES={p['id']:p for p in LAND['profiles']};ACTORS={a['id']:a for a in LAND['actors']}
ROUTES={r['id']:r for r in LAND['routes']}
assert len(BY_ID)==len(PROJECTS)==len(PROFILES)
assert set(BY_ID)==set(PROFILES)
assert len({p['repository'].lower() for p in PROJECTS})==len(PROJECTS)
for p in PROJECTS:
    assert set(p['related'])<=set(BY_ID)
    assert p['sources'] and p['description']['zh'] and p['description']['en']
    assert p['license_class']!='open' or p['license'] not in ('Unspecified','NOASSERTION')
    profile=PROFILES[p['id']]
    assert profile['actor'] in ACTORS and profile['route'] in ROUTES
    for field in ['contribution','difference','reuse']:
        assert all(profile[field].get(lang) for lang in ['zh','en'])
    assert profile['path'] and profile['sources']

DOMAINS=LAND['domains']
nodes=[];edges=[];edge_keys=set()
def node(id,kind,label,**fields):
    nodes.append({'id':id,'kind':kind,'label':label,**fields})
def edge(source,target,kind,basis,sources=None,note=None):
    key=(source,target,kind)
    if key in edge_keys:return
    edge_keys.add(key)
    edges.append({'id':'e'+str(len(edges)+1),'source':source,'target':target,'kind':kind,'basis':basis,'sources':sources or [],'note':note})
for r in LAND['routes']:node('r:'+r['id'],'route',r['name'],reference=r['id'])
for key,label in DOMAINS.items():node('d:'+key,'domain',label,reference=key)
for a in LAND['actors']:
    node('a:'+a['id'],'actor',a['name'],reference=a['id'],sources=a['sources'])
    for sid in a.get('standards',[]):edge('a:'+a['id'],'s:'+sid,'publishes','documented',a['sources'])
for s in CTX['standards']:node('s:'+s['id'],'standard',{'zh':s['name'],'en':s['name']},reference=s['id'],sources=s['sources'])
for sid,name in LAND['extra_foundations'].items():node('f:'+sid,'foundation',{'zh':name,'en':name},reference=sid)
standard_ids={s['id'] for s in CTX['standards']}
for p in PROJECTS:
    pf=PROFILES[p['id']];pid='p:'+p['id']
    node(pid,'project',{'zh':p['name'],'en':p['name']},reference=p['id'],sources=pf['sources'])
    edge(pid,'a:'+pf['actor'],'maintained_by','documented',[p['url']])
    edge(pid,'r:'+pf['route'],'classified_route','analysis',pf['sources'])
    edge(pid,'d:'+pf['domain'],'classified_domain','analysis',pf['sources'])
    for sid in LAND['foundations'].get(p['id'],[]):
        target=('s:' if sid in standard_ids else 'f:')+sid
        note=None
        if sid in {'lads','facility','microscopy-access','liquid','bench'}:
            path=' → '.join(pf['path'])
            note={
                'zh':'该节点合并展示同类基础生态；此工程的具体路径：'+path+'。',
                'en':'This node groups related foundations; this project’s specific path is '+path+'.'}
        if sid=='lads':
            note={'zh':'此关系指向 OPC UA 接口；所引工程未建立 LADS 信息模型实现。',
                  'en':'This relationship concerns OPC UA access; the cited project does not establish an implementation of the LADS information model.'}
        edge(pid,target,'uses','documented',pf['sources'],note)
for r in LAND['relations']:edge('p:'+r['source'],'p:'+r['target'],r['kind'],'documented',r['sources'],r['note'])
node_ids={n['id'] for n in nodes}
assert len(node_ids)==len(nodes)
assert all(e['source'] in node_ids and e['target'] in node_ids for e in edges)
assert all(e['sources'] for e in edges if e['basis']=='documented')
GRAPH={'schema_version':'1.0','updated':LAND['updated'],'nodes':nodes,'edges':edges}
(ROOT/'graph.json').write_text(json.dumps(GRAPH,ensure_ascii=False,indent=2)+'\n')
source_map={}
def register(url,subject,role,reviewed):
    item=source_map.setdefault(url,{'url':url,'subjects':[],'roles':[],'reviewed':reviewed})
    if subject not in item['subjects']:item['subjects'].append(subject)
    if role not in item['roles']:item['roles'].append(role)
    item['reviewed']=max(item['reviewed'],reviewed)
for p in PROJECTS:
    for s in p['sources']:register(s['url'],p['id'],s['role'],p['reviewed'])
for s in CTX['standards']:
    for url in s['sources']:register(url,s['id'],'standard-or-ecosystem',CTX['reviewed'])
for c in CTX['components']:register(c['url'],c['parent'],'component',CAT['reviewed'])
for x in CTX['boundaries']:register(x['url'],x['name'],'scope-boundary',CAT['reviewed'])
for url in CTX['discovery_sources']:register(url,'discovery-index','discovery-only',CAT['reviewed'])
for a in LAND['actors']:
    for url in a['sources']:register(url,a['id'],'maintainer-context',a['reviewed'])
SOURCES=list(source_map.values())
(ROOT/'sources.json').write_text(json.dumps({'reviewed':LAND['updated'],'sources':SOURCES},ensure_ascii=False,indent=2)+'\n')
for lang in ['zh','en']:
    suffix='zh-CN' if lang=='zh' else 'en';idx=0 if lang=='zh' else 1
    lines=['# '+('工程说明与比较' if lang=='zh' else 'Project profiles and comparisons'),'']
    catalog=['# '+('项目目录' if lang=='zh' else 'Project catalogue'),'','[中文 HTML](index.zh-CN.html) · [English HTML](index.en.html) · [JSON](catalogue.json)','']
    for p in PROJECTS:
        pf=PROFILES[p['id']]
        head=[f'## {p["name"]}','',f'[{p["repository"]}]({p["url"]}) · {ROUTES[pf["route"]]["name"][lang]} · {p["license"]} · {EVIDENCE[p["evidence"]["kind"]][idx]}','',p['description'][lang],'']
        catalog+=head+[p['evidence'][lang],'',' / '.join(p['interfaces']),'',' · '.join(f'[{ROLES[s["role"]][idx]}]({s["url"]})' for s in p['sources']),'']
        lines+=head+[('维护主体：' if lang=='zh' else 'Maintainer: ')+ACTORS[pf['actor']]['name'][lang],'',('接入关系：' if lang=='zh' else 'Access path: ')+' → '.join(pf['path']),'']
        for field,labels in [('contribution',('贡献与价值','Contribution and value')),('difference',('差异与适用条件','Distinctions and conditions')),('reuse',('可复用部分','Reusable ideas'))]:lines+=['### '+labels[idx],'',pf[field][lang],'']
        lines+=['### '+('公开范围与实验记录' if lang=='zh' else 'Public scope and experiment record'),'',p['evidence'][lang],'',' · '.join(f'[{ROLES[s["role"]][idx]}]({s["url"]})' for s in p['sources']),'']
    (ROOT/f'profiles.{suffix}.md').write_text('\n'.join(lines)+'\n')
    (ROOT/f'catalogue.{suffix}.md').write_text('\n'.join(catalog)+'\n')
output=io.StringIO(newline='');writer=csv.writer(output)
writer.writerow(['id','name','repository','category','scope','license','license_class','evidence','mcp','skills','interfaces','description_zh','description_en','evidence_zh','evidence_en','url','reviewed'])
for p in PROJECTS:writer.writerow([p['id'],p['name'],p['repository'],p['category'],p['scope'],p['license'],p['license_class'],p['evidence']['kind'],p['mcp'],p['skills'],'; '.join(p['interfaces']),p['description']['zh'],p['description']['en'],p['evidence']['zh'],p['evidence']['en'],p['url'],p['reviewed']])
(ROOT/'catalogue.csv').write_text(output.getvalue(),encoding='utf-8-sig')
DOCUMENTS={name:(ROOT/name).read_bytes().decode('utf-8') for name in ['guide.zh-CN.md','guide.en.md','profiles.zh-CN.md','profiles.en.md','catalogue.schema.json','landscape.schema.json','graph.schema.json','data-model.md','catalogue.csv','examples/measurement-contract.json','examples/README.md']}
DATA={'catalogue':CAT,'context':CTX,'landscape':LAND,'graph':GRAPH,'sources':SOURCES,'documents':DOCUMENTS}
for lang in ['zh','en']:(ROOT/f'index.{"zh-CN" if lang=="zh" else "en"}.html').write_text(render(ROOT,DATA,lang))
print(f'Built 2 editions · {len(PROJECTS)} profiles · {len(ACTORS)} actors · {len(nodes)} nodes · {len(edges)} edges · {len(SOURCES)} sources')
