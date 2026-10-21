/* Offline reader. Every view is built from the embedded, versioned research bundle. */
(() => {
'use strict';
const DATA = JSON.parse(document.getElementById('research-data').textContent);
const lang = document.documentElement.lang === 'zh-CN' ? 'zh' : 'en';
const t = (zh, en) => lang === 'zh' ? zh : en;
const tx = value => typeof value === 'object' && value !== null ? value[lang] || '' : String(value ?? '');
const $ = id => document.getElementById(id);
const all = selector => Array.from(document.querySelectorAll(selector));
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const link = (url, label) => `<a href="${esc(url)}">${esc(label)}</a>`;
const P = DATA.catalogue.projects, L = DATA.landscape, G = DATA.graph;
const index = (items, key = 'id') => new Map(items.map(item => [item[key], item]));
const projects = index(P), profiles = index(L.profiles), actors = index(L.actors), routes = index(L.routes), nodes = index(G.nodes);
const views = ['landscape','relations','approaches','participants','projects','standards','design','sources'];
const state = {view:'landscape', pages:{}, pagination:{}, selected:new Set(), filtered:P, foundation:'', graphFocus:'p:instrmcp', graphEdges:[], sourceQuery:'', decision:0};
const labels = {
 evidence:{experiment:t('论文实机案例','Published experiment'),hardware:t('维护者实机记录','Maintainer hardware record'),adapter:t('接入实现 / 文档','Adapter / documentation'),simulation:t('模拟验证','Simulation-verified'),artifact:t('配套代码 / 资料','Supporting artifact'),proposal:t('构想 / 提案','Concept / proposal')},
 kind:{project:t('工程与研究资料','Project / research artifact'),actor:t('维护者 / 标准主体','Maintainer / standards actor'),standard:t('标准 / 基础生态','Standard / foundation'),foundation:t('设备侧基础接口','Device-side foundation'),route:t('贡献路线','Contribution route'),domain:t('作用领域','Domain')},
 relation:{maintained_by:t('维护归属','Maintained by'),publishes:t('发布 / 维护','Publishes'),uses:t('复用 / 接入','Uses / integrates'),successor:t('后续发展','Successor'),documents:t('配套操作知识','Documents'),related:t('相关发展','Related work'),classified_route:t('贡献路线','Route'),classified_domain:t('作用领域','Domain')}
};
let toastTimer;
function toast(message){$('toast').textContent=message;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),2600);}
function download(name, value, mime='application/json;charset=utf-8') {
 const body = typeof value === 'string' ? value : JSON.stringify(value,null,2)+'\n';
 const url=URL.createObjectURL(new Blob([body],{type:mime}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function paginate(id, elements, matches, size) {
 const total=matches.length,pages=Math.max(1,Math.ceil(total/size));
 state.pages[id]=Math.min(Math.max(1,state.pages[id]||1),pages);
 const page=state.pages[id], visible=new Set(matches.slice((page-1)*size,page*size));
 elements.forEach(el=>{el.hidden=!visible.has(el);});
 const pager=document.querySelector(`[data-pager="${id}"]`);
 pager.querySelector('span').textContent=t(`第 ${page} / ${pages} 页 · ${total} 项`,`Page ${page} / ${pages} · ${total} records`);
 pager.querySelector('[data-page-prev]').disabled=page<=1;pager.querySelector('[data-page-next]').disabled=page>=pages;
 state.pagination[id]={total,pages};
 return total;
}
const projectRows=all('[data-project-row]'), actorRows=all('[data-actor-id]'), componentRows=all('[data-component]'), sourceRows=all('[data-source-index]');
const haystack = value => JSON.stringify(value).toLocaleLowerCase();
const projectSearch = new Map(P.map(p=>[p.id,haystack([p,profiles.get(p.id),actors.get(profiles.get(p.id).actor)])]));
function filterProjects(){
 const query=$('project-search').value.trim().toLocaleLowerCase();
 state.filtered=P.filter(p=>{
  const pf=profiles.get(p.id);
  return (!query||projectSearch.get(p.id).includes(query)) && ($('project-route').value==='all'||pf.route===$('project-route').value) && ($('project-domain').value==='all'||pf.domain===$('project-domain').value) && ($('project-evidence').value==='all'||p.evidence.kind===$('project-evidence').value) && ($('project-license').value==='all'||p.license_class===$('project-license').value) && (!$('project-mcp').checked||p.mcp==='documented') && (!$('project-skills').checked||p.skills==='documented') && (!state.foundation||(L.foundations[p.id]||[]).includes(state.foundation));
 });
 const ids=new Set(state.filtered.map(p=>p.id));paginate('projects',projectRows,projectRows.filter(el=>ids.has(el.dataset.projectRow)),8);
 let caption=t(`${state.filtered.length} / ${P.length} 项工程`,`${state.filtered.length} / ${P.length} projects`);
 if(state.foundation){const n=nodes.get('s:'+state.foundation)||nodes.get('f:'+state.foundation);caption+=' · '+tx(n.label);}
 $('project-count').textContent=caption;$('project-empty').hidden=state.filtered.length>0;
}
function resetProjects(){
 $('project-search').value='';['route','domain','evidence','license'].forEach(k=>$('project-'+k).value='all');['mcp','skills'].forEach(k=>$('project-'+k).checked=false);state.foundation='';state.pages.projects=1;filterProjects();
}
function filterActors(){
 const query=$('actor-search').value.trim().toLocaleLowerCase(),kind=$('actor-kind').value;
 const matches=actorRows.filter(el=>{const a=actors.get(el.dataset.actorId);return (kind==='all'||a.kind===kind)&&(!query||haystack([a,a.projects.map(id=>projects.get(id))]).includes(query));});
 paginate('actors',actorRows,matches,12);$('actor-count').textContent=t(`${matches.length} / ${L.actors.length} 个主体`,`${matches.length} / ${L.actors.length} actors`);
}
function filterComponents(){const parent=$('component-parent').value;const matches=componentRows.filter(el=>parent==='all'||el.dataset.component===parent);paginate('components',componentRows,matches,10);$('component-count').textContent=t(`${matches.length} 个组件`,`${matches.length} components`);}
function filterSources(){const query=$('source-search').value.trim().toLocaleLowerCase();const matches=sourceRows.filter(el=>!query||haystack(DATA.sources[Number(el.dataset.sourceIndex)]).includes(query));paginate('sources',sourceRows,matches,16);$('source-count').textContent=t(`${matches.length} 个来源地址`,`${matches.length} source addresses`);}
function syncCompare(){
 all('[data-compare]').forEach(el=>{el.checked=state.selected.has(el.dataset.compare);});
 $('compare-status').textContent=state.selected.size ? t(`已选 ${state.selected.size} / 3 项：`,`Selected ${state.selected.size} / 3: `)+[...state.selected].map(id=>projects.get(id).name).join(' · ') : t('选择至多 3 项并排比较','Select up to three projects to compare');
 $('compare-open').disabled=state.selected.size===0;$('compare-clear').disabled=state.selected.size===0;
}
function setComparison(id, add){
 if(add && !state.selected.has(id) && state.selected.size>=3){toast(t('最多比较 3 项，请先取消一项。','Compare up to three projects. Remove one first.'));syncCompare();return false;}
 if(add)state.selected.add(id);else state.selected.delete(id);syncCompare();return true;
}
function renderComparison(){
 const ids=[...state.selected],selected=ids.map(id=>projects.get(id));
 if(!ids.length){$('comparison-table').innerHTML=`<p class="empty">${t('请从工程目录中选择项目。','Choose projects from the directory.')}</p>`;return;}
 const sourceHTML=p=>'<div class="source-links">'+p.sources.map((s,i)=>link(s.url,t('来源 ','Source ')+(i+1))).join('')+'</div>';
 const rows=[
  [t('维护主体','Maintainer'),p=>link('#relations/a:'+profiles.get(p.id).actor,tx(actors.get(profiles.get(p.id).actor).name))],
  [t('贡献路线','Contribution route'),p=>esc(tx(routes.get(profiles.get(p.id).route).name))],
  [t('怎样连接','Access path'),p=>'<p class="path-small">'+esc(profiles.get(p.id).path.join(' → '))+'</p>'+esc(tx(p.description))],
  [t('贡献与价值','Contribution and value'),p=>esc(tx(profiles.get(p.id).contribution))],
  [t('差异与条件','Distinctions and conditions'),p=>esc(tx(profiles.get(p.id).difference))],
  [t('可复用部分','Reusable ideas'),p=>esc(tx(profiles.get(p.id).reuse))],
  [t('公开范围与证据','Public scope and evidence'),p=>`<span class="evidence ${p.evidence.kind}">${esc(labels.evidence[p.evidence.kind])}</span><p>${esc(tx(p.evidence))}</p>`],
  [t('接口','Interfaces'),p=>esc(p.interfaces.join(' · '))],
  ['MCP / Skills',p=>'MCP: '+t(p.mcp==='documented'?'已记录':'未见记录',p.mcp==='documented'?'documented':'not documented')+'<br>Skills: '+t(p.skills==='documented'?'已记录':'未见记录',p.skills==='documented'?'documented':'not documented')],
  [t('许可','License'),p=>esc(p.license)],
  [t('原始来源','Primary sources'),sourceHTML]
 ];
 $('comparison-table').innerHTML='<table class="comparison-table"><thead><tr><th>'+t('比较维度','Dimension')+'</th>'+selected.map(p=>'<th>'+link('#projects/'+p.id,p.name)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(([name,cell])=>'<tr><th scope="row">'+esc(name)+'</th>'+selected.map(p=>'<td>'+cell(p)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';
}
function wrapLabel(value, max=23, lines=2){
 const result=[];let current='',width=0;
 for(const char of value){const w=char.charCodeAt(0)>255?1.8:1;if(width+w>max){result.push(current);current='';width=0;}current+=char;width+=w;}
 if(current)result.push(current);if(result.length>lines){result.length=lines;result[lines-1]=result[lines-1].replace(/.$/,'')+'…';}return result;
}
function renderGraph(){
 let current=nodes.get(state.graphFocus);if(!current){state.graphFocus='p:instrmcp';current=nodes.get(state.graphFocus);}
 const include=$('graph-classification').checked;
 const edges=G.edges.filter(e=>(e.source===current.id||e.target===current.id)&&(include||e.basis==='documented'));
 state.graphEdges=edges;
 const incoming=[...new Set(edges.filter(e=>e.target===current.id).map(e=>e.source))];
 const outgoing=[...new Set(edges.filter(e=>e.source===current.id).map(e=>e.target))];
 const left=incoming.slice(0,6),right=outgoing.slice(0,6),max=Math.max(left.length,right.length,1),height=Math.max(300,max*80+60),cy=height/2-33;
 const oneSide=!(left.length&&right.length),currentX=oneSide?(left.length?550:right.length?70:318):318,leftX=oneSide?70:8,rightX=oneSide?550:628;
 const positions=new Map([[current.id,{x:currentX,y:cy,current:true}]]);
 function place(ids,x){const start=(height-ids.length*80+12)/2;ids.forEach((id,i)=>positions.set(id,{x,y:start+i*80}));}place(left,leftX);place(right,rightX);
 let svg=`<svg viewBox="0 0 838 ${height}" role="img" aria-label="${esc(t('当前节点的相邻关系','Relationships adjacent to the current node'))}"><defs><marker id="graph-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7" fill="#9aaf99"/></marker></defs>${left.length?`<text x="${leftX}" y="19" class="graph-column-label">${t('由这些节点关联','Incoming relationships')}</text>`:''}<text x="${currentX}" y="19" class="graph-column-label">${t('当前节点','Current node')}</text>${right.length?`<text x="${rightX}" y="19" class="graph-column-label">${t('关联到这些节点','Outgoing relationships')}</text>`:''}`;
 for(const e of edges){
  if(!positions.has(e.source)||!positions.has(e.target))continue;
  const a=positions.get(e.source),b=positions.get(e.target),x1=a.x+202,x2=b.x,y1=a.y+33,y2=b.y+33,m=(x1+x2)/2;
  svg+=`<path class="graph-line ${e.basis}" d="M${x1},${y1} C${m},${y1} ${m},${y2} ${x2},${y2}" marker-end="url(#graph-arrow)"><title>${esc(labels.relation[e.kind])}</title></path>`;
 }
 for(const [id,pos] of positions){const n=nodes.get(id),ls=wrapLabel(tx(n.label));svg+=`<a href="#relations/${encodeURIComponent(id)}" aria-label="${esc(tx(n.label))}"><g class="graph-node ${pos.current?'current':''}" transform="translate(${pos.x},${pos.y})"><title>${esc(tx(n.label))}</title><rect width="202" height="66" rx="7"/><text x="13" y="18" class="node-kind">${esc(labels.kind[n.kind])}</text>${ls.map((line,i)=>`<text x="13" y="${37+i*16}">${esc(line)}</text>`).join('')}</g></a>`;}
 svg+='</svg>';$('network-graph').innerHTML=svg;
 const shown=positions.size-1,total=new Set([...incoming,...outgoing]).size;
 $('graph-summary').textContent=t(`图中显示 ${shown} / ${total} 个相邻节点；下方列出全部 ${edges.length} 条关系。`,`Showing ${shown} / ${total} neighboring nodes; all ${edges.length} relationships are listed below.`);
 let description='',cta='',sources=current.sources||[];
 if(current.kind==='project'){const p=projects.get(current.reference),pf=profiles.get(p.id);description=tx(pf.contribution);cta=link('#projects/'+p.id,t('阅读工程说明 →','Read project profile →'))+`<p><span class="evidence ${p.evidence.kind}">${esc(labels.evidence[p.evidence.kind])}</span></p>`;}
 if(current.kind==='actor'){const a=actors.get(current.reference);description=tx(a.context);cta=link('#participants',t('参与者目录 →','Participant directory →'));}
 if(current.kind==='standard'){const s=DATA.context.standards.find(s=>s.id===current.reference);description=tx(s.role);cta=link('#standards/'+s.id,t('阅读定义与状态 →','Read definition and status →'));}
 if(current.kind==='foundation'){description=t('查看左侧工程如何接入或复用这一接口，关系来源列在下方。','Inspect how adjacent projects use this interface; relationship sources are listed below.');}
 if(current.kind==='route'){description=tx(routes.get(current.reference).value);cta=link('#approaches/'+current.reference,t('阅读路线分析 →','Read route analysis →'));}
 if(current.kind==='domain'){description=t('按主要应用领域归类；跨领域设计不代表所有仪器已经验证。','Classified by primary application. Cross-domain design does not imply validation on every instrument.');cta=link('#projects?domain='+current.reference,t('查看领域工程 →','View domain projects →'));}
 $('graph-inspector').innerHTML=`<div class="card-kicker">${esc(labels.kind[current.kind])}</div><h2>${esc(tx(current.label))}</h2><p>${esc(description)}</p>${cta}<div class="source-links">${sources.slice(0,4).map((url,i)=>link(url,t('来源 ','Source ')+(i+1))).join('')}</div>`;
 $('edge-list').innerHTML=edges.map(e=>`<article class="edge-row" data-edge="${e.id}"><div>${link('#relations/'+encodeURIComponent(e.source),tx(nodes.get(e.source).label))}</div><div class="relation-label">${esc(labels.relation[e.kind])} →<p>${e.basis==='analysis'?t('分析分类','Analysis'):t('来源记录','Documented')}</p></div><div>${link('#relations/'+encodeURIComponent(e.target),tx(nodes.get(e.target).label))}</div><div class="edge-sources"><div class="source-links">${e.sources.slice(0,2).map((url,i)=>link(url,t('依据 ','Source ')+(i+1))).join('')}</div></div>${e.note?`<p class="edge-note">${esc(tx(e.note))}</p>`:''}</article>`).join('') || `<p class="empty">${t('当前未记录这类关系。可勾选分类关系，或更换节点。','No relationships of this type are recorded. Include classifications or select another node.')}</p>`;
 renderEdges();const option=Array.from($('graph-focus').options).find(o=>o.value===current.id);if(option&&!option.hidden)$('graph-focus').value=current.id;
}
function renderEdges(){const rows=all('[data-edge]');paginate('edges',rows,rows,8);}
function filterGraphOptions(){
 const query=$('graph-search').value.trim().toLocaleLowerCase();let first=null;
 Array.from($('graph-focus').options).forEach(o=>{const n=nodes.get(o.value);o.hidden=!!query&&!haystack([n.id,n.label]).includes(query);if(!o.hidden&&!first)first=o;});
 if(query&&first){$('graph-focus').selectedIndex=-1;}else if(!query){$('graph-focus').value=state.graphFocus;}
 $('graph-focus').disabled=!first;
}
function selectDecision(id){state.decision=Number(id);all('[data-decision-panel]').forEach(el=>el.hidden=Number(el.dataset.decisionPanel)!==state.decision);all('[data-decision]').forEach(el=>{const active=Number(el.dataset.decision)===state.decision;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));});}
function closeMenu() {document.body.classList.remove('menu-open');$('menu-toggle').setAttribute('aria-expanded','false');}
function route(){
 clearTimeout(toastTimer);$('toast').classList.remove('show');
 let raw=location.hash.slice(1);let decoded;
 try{decoded=decodeURIComponent(raw);}catch{decoded='landscape';}
 const [path,query='']=decoded.split('?'),parts=path.split('/'),view=views.includes(parts[0])?parts[0]:'landscape',sub=parts.slice(1).join('/'),params=new URLSearchParams(query);
 state.view=view;all('[data-view]').forEach(el=>el.hidden=el.dataset.view!==view);
 all('[data-nav]').forEach(el=>{const active=el.dataset.nav===view;el.classList.toggle('active',active);if(active)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
 const i=views.indexOf(view),position=String(i+1).padStart(2,'0')+' / 08';$('top-position').textContent=position;$('footer-position').textContent=position;
 $('current-section').textContent=document.querySelector(`[data-nav="${view}"]`).textContent.replace(/^\d+/, '').trim();
 $('language-link').href=`index.${lang==='zh'?'en':'zh-CN'}.html#${raw||'landscape'}`;$('view-prev').disabled=i===0;$('view-next').disabled=i===views.length-1;
 if(view==='relations'){
  if(nodes.has(sub))state.graphFocus=sub;
  if(state.graphFocus.startsWith('r:')||state.graphFocus.startsWith('d:'))$('graph-classification').checked=true;
  $('graph-search').value='';filterGraphOptions();state.pages.edges=1;renderGraph();
 }
 if(view==='approaches'){
  const id=routes.has(sub)?sub:'bridge';all('[data-route-panel]').forEach(el=>el.hidden=el.dataset.routePanel!==id);all('[data-route-choice]').forEach(el=>el.classList.toggle('active',el.dataset.routeChoice===id));
 }
 if(view==='participants')filterActors();
 if(view==='projects'){
  const detail=projects.has(sub),compare=params.has('compare');
  $('project-directory').hidden=detail||compare;$('comparison-panel').hidden=!compare;
  all('[data-dossier]').forEach(el=>el.hidden=!detail||el.dataset.dossier!==sub);
  if(compare){state.selected=new Set((params.get('compare')||'').split(',').filter(id=>projects.has(id)).slice(0,3));syncCompare();renderComparison();}
  else if(!detail){
   if(['route','domain','foundation'].some(k=>params.has(k))){resetProjects();for(const key of ['route','domain'])if(params.has(key))$('project-'+key).value=params.get(key);state.foundation=params.get('foundation')||'';}
   filterProjects();syncCompare();
  }
 }
 if(view==='standards'){
  const components=sub==='components',standard=DATA.context.standards.some(s=>s.id===sub)?sub:'mcp';
  $('component-browser').hidden=!components;$('standard-browser').hidden=components;$('components-tab').classList.toggle('active',components);$('standards-tab').classList.toggle('active',!components);
  all('[data-standard]').forEach(el=>el.hidden=components||el.dataset.standard!==standard);all('.subnav a').forEach(el=>el.classList.toggle('active',el.hash==='#standards/'+standard));if(components)filterComponents();
 }
 if(view==='design'){
  const id=Array.from($('design-chapter-select').options).some(o=>o.value===sub)?sub:'choices';$('design-chapter-select').value=id;all('[data-design]').forEach(el=>el.hidden=el.dataset.design!==id);selectDecision(state.decision);
 }
 if(view==='sources')filterSources();
 closeMenu();window.scrollTo({top:0,behavior:'instant'});
}
all('[data-download]').forEach(button=>button.addEventListener('click',()=>{
 const key=button.dataset.download;let value=key==='all'?DATA:DATA[key];if(key==='sources')value={reviewed:L.updated,sources:DATA.sources};download(key==='all'?'ai4instruments-research.json':key+'.json',value);
}));
all('[data-document]').forEach(button=>button.addEventListener('click',()=>{const name=button.dataset.document;download(name.split('/').pop(),DATA.documents[name],name.endsWith('.json')?'application/json;charset=utf-8':name.endsWith('.csv')?'text/csv;charset=utf-8':'text/markdown;charset=utf-8');}));
$('project-json').addEventListener('click',()=>download('projects-filtered.json',{reviewed:L.updated,projects:state.filtered,profiles:state.filtered.map(p=>profiles.get(p.id))}));
$('project-csv').addEventListener('click',()=>{
 const keys=['id','name','repository','route','domain','license','evidence','access_path','contribution','distinction','reuse','url'];
 const quote=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
 const rows=state.filtered.map(p=>{const pf=profiles.get(p.id);return [p.id,p.name,p.repository,tx(routes.get(pf.route).name),tx(L.domains[pf.domain]),p.license,labels.evidence[p.evidence.kind],pf.path.join(' → '),tx(pf.contribution),tx(pf.difference),tx(pf.reuse),p.url];});
 download('projects-filtered.csv','\ufeff'+[keys,...rows].map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n','text/csv;charset=utf-8');
});
['search','route','domain','evidence','license','mcp','skills'].forEach(key=>$('project-'+key).addEventListener(key==='search'?'input':'change',()=>{state.pages.projects=1;filterProjects();}));
$('project-reset').addEventListener('click',resetProjects);
['search','kind'].forEach(key=>$('actor-'+key).addEventListener(key==='search'?'input':'change',()=>{state.pages.actors=1;filterActors();}));
$('component-parent').addEventListener('change',()=>{state.pages.components=1;filterComponents();});
$('source-search').addEventListener('input',()=>{state.pages.sources=1;filterSources();});
all('[data-compare]').forEach(el=>el.addEventListener('change',()=>setComparison(el.dataset.compare,el.checked)));
all('[data-add-compare]').forEach(el=>el.addEventListener('click',()=>{if(setComparison(el.dataset.addCompare,true))location.hash='projects?compare='+[...state.selected].join(',');}));
$('compare-open').addEventListener('click',()=>{if(state.selected.size)location.hash='projects?compare='+[...state.selected].join(',');});
$('compare-clear').addEventListener('click',()=>{state.selected.clear();syncCompare();});$('compare-close').addEventListener('click',()=>location.hash='projects');
$('graph-focus').addEventListener('change',()=>location.hash='relations/'+encodeURIComponent($('graph-focus').value));
$('graph-search').addEventListener('input',filterGraphOptions);
$('graph-search').addEventListener('keydown',event=>{if(event.key==='Enter'&&!$('graph-focus').disabled){const query=$('graph-search').value.trim().toLocaleLowerCase(),options=Array.from($('graph-focus').options).filter(o=>!o.hidden);const option=options.find(o=>o.value.toLocaleLowerCase().split(':')[1]===query||o.textContent.toLocaleLowerCase()===query)||options[0];if(option)location.hash='relations/'+encodeURIComponent(option.value);}});
$('graph-classification').addEventListener('change',()=>{state.pages.edges=1;renderGraph();});
$('design-chapter-select').addEventListener('change',()=>location.hash='design/'+$('design-chapter-select').value);
all('[data-decision]').forEach(el=>el.addEventListener('click',()=>selectDecision(el.dataset.decision)));
const renderPages={projects:filterProjects,actors:filterActors,components:filterComponents,sources:filterSources,edges:renderEdges};
all('[data-page-prev],[data-page-next]').forEach(button=>button.addEventListener('click',()=>{const id=button.dataset.pagePrev||button.dataset.pageNext;state.pages[id]=(state.pages[id]||1)+(button.dataset.pagePrev?-1:1);renderPages[id]();const start={projects:$('project-list'),actors:document.querySelector('.actor-grid'),components:$('component-browser'),sources:$('source-list'),edges:$('edge-list')}[id];start.scrollIntoView({block:'start',behavior:'instant'});}));
function moveView(delta){const next=views.indexOf(state.view)+delta;if(next>=0&&next<views.length)location.hash=views[next];}
$('view-prev').addEventListener('click',()=>moveView(-1));$('view-next').addEventListener('click',()=>moveView(1));
$('menu-toggle').addEventListener('click',()=>{const open=document.body.classList.toggle('menu-open');$('menu-toggle').setAttribute('aria-expanded',String(open));});
document.addEventListener('click',event=>{if(document.body.classList.contains('menu-open')&&!event.target.closest('.sidebar,#menu-toggle'))closeMenu();});
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeMenu();if(event.altKey||event.ctrlKey||event.metaKey||event.shiftKey||event.target.closest('input,select,textarea,[contenteditable="true"],button,a'))return;if(event.key==='ArrowLeft'){event.preventDefault();moveView(-1);}if(event.key==='ArrowRight'){event.preventDefault();moveView(1);}});
window.addEventListener('hashchange',route);
document.querySelector('.skip-link').addEventListener('click',event=>{event.preventDefault();$('main').focus();});
filterProjects();filterActors();filterComponents();filterSources();syncCompare();route();document.body.classList.add('js');
})();
