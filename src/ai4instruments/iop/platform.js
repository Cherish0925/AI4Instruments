(() => {
  let revision = 0;
  const element = (tag, text) => {const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node};
  const action = (label, fn) => {const b=element('button',label);b.onclick=async()=>{try{await fn()}catch(e){message(e.message)}};return b};
  const show = value => {$('#platform-result').hidden=false;$('#platform-result').textContent=JSON.stringify(value,null,2)};
  const edit = (definition, rev=0) => {revision=rev;$('#platform-definition').value=JSON.stringify(definition,null,2);$('#platform-revision').textContent=rev?'配置版本 '+rev:'新平台'};
  function graph(definition) {
    const ns='http://www.w3.org/2000/svg'; const nodes=definition.devices; const cols=Math.min(3,nodes.length||1);
    const svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 900 ${Math.max(130,Math.ceil(nodes.length/cols)*130)}`);svg.setAttribute('role','img');svg.setAttribute('aria-label','设备与物理连接');
    const points=new Map(nodes.map((id,i)=>[id,{x:40+(i%cols)*300,y:35+Math.floor(i/cols)*130}]));
    const make=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text)n.textContent=text;svg.append(n);return n};
    for(const link of definition.connections||[]) {const a=points.get(link.from.device),b=points.get(link.to.device);if(!a||!b)continue;make('path',{d:`M ${a.x+110} ${a.y+48} L ${b.x+110} ${b.y+48}`});const title=document.createElementNS(ns,'title');title.textContent=`${link.from.device}:${link.from.port} → ${link.to.device}:${link.to.port} (${link.kind})`;svg.lastChild.append(title)}
    for(const [id,p] of points){make('rect',{x:p.x,y:p.y,width:220,height:48,rx:5});make('text',{x:p.x+110,y:p.y+29,'text-anchor':'middle'},id)}
    return svg;
  }
  window.refreshPlatforms=async()=>{
    const platforms=await api('platforms');const cards=$('#platform-cards');cards.replaceChildren();const select=$('#experiment-platform'),selected=select.value;select.replaceChildren(new Option('直接选择已登记设备',''));
    if(!platforms.length)cards.append(element('p','尚未配置平台。设备登记后，可在下方创建或导入配置。'));
    for(const record of platforms){const d=record.definition;select.add(new Option(d.name||d.id,d.id));const card=element('article');card.className='platform-card';card.append(element('h3',d.name||d.id),element('small',`${d.id} · 配置 ${record.revision} · ${d.devices.length} 台设备 · ${record.active_runs.length} 个活动实验`),graph(d));
      if(d.connections.length){const list=element('ul');for(const c of d.connections)list.append(element('li',`${c.from.device}:${c.from.port} → ${c.to.device}:${c.to.port} · ${c.kind}`));card.append(list)}
      if(d.resources.length)card.append(element('p','共享资源：'+d.resources.map(r=>`${r.id} (${r.devices.join(', ')})`).join('；')));
      if(record.missing_devices.length)card.append(element('p','待连接：'+record.missing_devices.join(', ')));
      const buttons=element('div');buttons.className='tools';buttons.append(action('编辑配置',()=>edit(d,record.revision)));
      for(const name of Object.keys(d.procedures))buttons.append(action(name==='initialize'?'执行初始化':'执行 '+name,async()=>{const run=await api(`platforms/${encodeURIComponent(d.id)}/procedures/${encodeURIComponent(name)}`,{request_id:crypto.randomUUID()});message('已提交：'+run.id);await refresh()}));
      card.append(buttons);cards.append(card);
    }
    select.value=selected;
  };
  $('#platform-draft').onclick=()=>{edit({schema_version:1,id:$('#platform-id').value.trim(),devices:$('#platform-devices').value.split(',').map(s=>s.trim()).filter(Boolean),resources:[],connections:[],procedures:{}})};
  $('#platform-file').onchange=async()=>{try{const file=$('#platform-file').files[0];if(file)edit(JSON.parse(await file.text()))}catch(e){message(e.message)}};
  $('#platform-preview').onclick=async()=>{try{show(await api('platforms/preview',{definition:JSON.parse($('#platform-definition').value)}))}catch(e){message(e.message)}};
  $('#platform-apply').onclick=async()=>{try{const p=await api('platforms',{definition:JSON.parse($('#platform-definition').value),expected_revision:revision});edit(p.definition,p.revision);message('已保存配置：'+p.id+' · '+p.revision);await refresh()}catch(e){message(e.message)}};
  $('#platform-export').onclick=()=>{try{const d=JSON.parse($('#platform-definition').value),url=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)+'\n'],{type:'application/json'})),a=element('a');a.href=url;a.download=d.id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}catch(e){message(e.message)}};
  if(token)window.refreshPlatforms().catch(e=>message(e.message));
})();
