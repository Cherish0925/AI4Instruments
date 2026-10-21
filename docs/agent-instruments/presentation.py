"""Bilingual IOP argument: existing designs → mechanisms → a shared operation model."""
import html


def pair(zh, en):
    return {'zh': zh, 'en': en}


CHAPTERS = [
    {'id': 'question', 'name': pair('问题与全图', 'The problem'), 'start': 1},
    {'id': 'designs', 'name': pair('一级 · 具体方案', 'I · Existing designs'), 'start': 3},
    {'id': 'mechanisms', 'name': pair('二级 · 机制归纳', 'II · Mechanisms'), 'start': 10},
    {'id': 'iop', 'name': pair('三级 · IOP', 'III · IOP'), 'start': 13},
]
SOURCES = {
    'mhs': ('MHS · Anthropic', 'https://www.anthropic.com/news/model-hardware-standard-research-preview'),
    'mhs-site': ('MHS · Research preview', 'https://modelhardwarestandard.com/'),
    'aip': ('AIP PRD v1.1 · 2026-10-18', '#standards/aip'),
    'openmhp': ('OpenMHP · SPEC', 'https://github.com/kushalsinha/openmhp/blob/main/SPEC.md'),
    'openmhp-devices': ('OpenMHP · Devices', 'https://github.com/kushalsinha/openmhp/blob/main/supported-devices/README.md'),
    'lap': ('LAP · §3–5', 'https://arxiv.org/html/2606.03755v1'),
    'oahl': ('OAHL · Architecture', 'https://github.com/fredabila/oahl'),
    'abenor': ('Abenor Labs', 'https://github.com/Abenor-Labs/Open-MHS'),
    'tong': ('tongriyaotxt', 'https://github.com/tongriyaotxt/open-mhs'),
    'scut': ('SCUT-ESA', 'https://github.com/SCUT-ESA/open-mhs'),
    'cuntinum': ('Cuntinum · MHP', 'https://github.com/Cuntinum/model-hardware-protocol'),
    'sila': ('SiLA 2', 'https://sila-standard.com/standards/'),
    'lads': ('OPC UA · LADS', 'https://reference.opcfoundation.org/specs/OPC-30500-1/4.1.2.2'),
    'wot': ('W3C · WoT TD 1.1', 'https://www.w3.org/TR/wot-thing-description11/'),
    'operations': ('AI4Instruments · Operations', 'https://github.com/Cherish0925/AI4Instruments/blob/main/docs/operations.md'),
}
ISLANDS = [
    {'id':'capability', 'name':pair('设备能力模型','Device capability models'),
     'mechanism':pair('把型号接口翻译成可发现、可理解、可调用的能力。','Translate model-specific interfaces into discoverable, interpretable capabilities.'),
     'members':['s:mhs','p:open-mhs-abenor','p:open-mhs-tong','p:open-mhs-scut','p:mhp-cuntinum'],
     'iop_objects':['instrument','capability','operation','binding']},
    {'id':'execution', 'name':pair('操作执行与结果契约','Execution and result contracts'),
     'mechanism':pair('把一次调用延伸为有身份、状态、资源与结果的物理过程。','Give a physical process identity, state, resources and results beyond a single call.'),
     'members':['s:aip','p:openmhp','s:lap'],
     'iop_objects':['operation','run','observation','method']},
    {'id':'access', 'name':pair('设备发现与资源协作','Discovery and resource coordination'),
     'mechanism':pair('找到能力所在的位置，并安排调用者对设备的使用。','Locate capabilities and coordinate callers’ use of equipment.'),
     'members':['p:oahl'], 'iop_objects':['instrument','resource','binding']},
]


def content(lang):
    z = lang == 'zh'
    t = lambda a,b: a if z else b
    E = lambda s: html.escape(str(s), quote=True)
    pages = []
    def add(id, chapter, title, short, body, refs=(), status=''):
        pages.append(dict(id=id,chapter=chapter,title=title,short=short,body=body,sources=list(refs),status=status))
    def insight(text): return '<p class="thesis">'+text+'</p>'
    def note(title, text): return '<div class="explanation"><h3>'+title+'</h3><p>'+text+'</p></div>'
    def flow(items):
        return '<div class="process">'+''.join('<div><b>'+a+'</b><span>'+b+'</span></div>' for a,b in items)+'</div>'
    def table(head,rows,cls=''):
        return '<div class="argument-table '+cls+'"><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
    def entity(name, detail, cls=''): return '<div class="entity '+cls+'"><b>'+name+'</b><span>'+detail+'</span></div>'
    def link(target,label): return '<a href="'+target+'">'+label+'</a>'

    # 01: the entire argument, before the catalogue.
    rows=[
        ('I',t('具体方案','Existing designs'), 'MHS · AIP · OpenMHP · LAP · OAHL',t('各家用什么对象和机制连接仪器','How each design represents and operates instruments'),'#presentation/3'),
        ('II',t('共同机制','Shared mechanisms'),t('能力模型 · 执行契约 · 资源协作','Capabilities · Execution · Resources'),t('把相似实现归到同一问题，把互补机制接起来','Group similar solutions; connect complementary mechanisms'),'#presentation/10'),
        ('III','IOP',t('一套操作定义，连接知识、执行与结果','One operation model linking knowledge, execution and results'),t('人和 Agent 使用同一个方法，驱动适配不同设备','People and agents share methods; adapters connect devices'),'#presentation/13'),
    ]
    body='<p class="opening-definition">'+t('仪器操作协议，定义一件实验操作的<b>物理含义、执行方式与结果依据</b>，使它能被人理解、被程序执行，并在不同设备之间复用。','IOP defines an operation’s <b>physical meaning, execution and evidence</b>. People and software share the definition; adapters make methods reusable across devices.')+'</p>'
    body+='<div class="argument-map">'+''.join('<a href="'+href+'"><span class="roman">'+num+'</span><div><h3>'+title+'</h3><b>'+line+'</b><p>'+desc+'</p></div><span class="map-arrow">↗</span></a>' for num,title,line,desc,href in rows)+'</div>'
    add('argument','question',t('IOP · 仪器操作协议','IOP · Instrument Operations Protocol'),t('三级关系','The three levels'),body,status=t('AI4Instruments · 设计研究','AI4Instruments · Design study'))

    # 02: one physical experiment, with a genuinely useful technical diagram.
    labels=[t('线偏振光','Linear input'),t('半波片','Half-wave plate'),t('固定检偏器','Fixed analyzer'),t('功率计','Power meter')]
    svg='<svg class="bench-diagram" viewBox="0 0 1000 200" role="img" aria-label="'+t('线偏振光经过旋转半波片和固定检偏器到达功率计','Linear light passes a rotating half-wave plate and a fixed analyzer to a power meter')+'"><path d="M70 92H905" class="beam"/><path d="M900 87l12 5-12 5" class="beam-fill"/><rect x="90" y="62" width="70" height="60" rx="4"/><path d="M115 75v34m10-34v34m10-34v34" class="fine"/><circle cx="360" cy="92" r="37"/><path d="M335 118l50-52" class="axis"/><path d="M397 46a58 58 0 0 1 20 47" class="fine"/><text x="424" y="70">θ</text><rect x="570" y="50" width="32" height="84" rx="3"/><path d="M580 62v59m11-59v59" class="fine"/><path d="M820 58h70v68h-70z"/><circle cx="855" cy="92" r="21" class="fine"/>'
    svg+=''.join('<text class="bench-label" x="'+str(x)+'" y="173" text-anchor="middle">'+v+'</text>' for x,v in zip([125,360,586,855],labels))+'</svg>'
    body=svg+'<div class="split equal"><div><div class="formula">P(θ) = P₀ cos²(2θ − φ)</div><p class="figure-caption">'+t('理想半波片、固定检偏器；φ 包含入射偏振与轴零点。实际测量还受波长、损耗与探测器响应影响。','Ideal half-wave plate and fixed analyzer; φ includes input polarization and axis zero. Wavelength, loss and detector response affect the physical measurement.')+'</p></div><div>'+note(t('任务','Task'),t('改变波片角度，测量透射功率，得到角度—功率曲线。','Vary the plate angle, measure transmitted power and obtain an angle–power curve.'))+'</div></div>'
    body+=flow([(t('定义','Define'),t('θ 的零点、单位与范围','Angle origin, units and range')),(t('执行','Execute'),t('转动 → 到位 → 采集','Move → settle → acquire')),(t('解释','Interpret'),t('实际角度、功率与校准条件','Actual angle, power and calibration'))])
    add('physical-problem','question',t('一次偏振扫描，需要比“调用成功”更多的信息','A polarization scan needs more than a successful call'),t('从真实操作出发','Start with a physical operation'),body,status=t('贯穿案例 · 物理模型与接口设计','Running example · Physical model and interface design'))

    # 03: compact, exact inventory. Each substantive design has an explanation next.
    rows=[
        [link('#presentation/4','MHS'),t('共享驱动与设备能力描述','Shared drivers and capability descriptions'),t('Anthropic + HHMI Janelia','Anthropic + HHMI Janelia'),t('研究预览','Research preview')],
        [link('#presentation/5','Open-MHS × 3 · MHP'),t('把共同设备接口实现为代码','Implement common device interfaces'),t('四个独立维护项目','Four independent projects'),t('公开代码','Public code')],
        [link('#presentation/6','AIP'),t('持久运行的仪器操作服务','Persistent instrument-operation service'),t('本项目所用 PRD','Supplied PRD'),t('设计材料','Design document')],
        [link('#presentation/7','OpenMHP'),t('设备包、动作、任务和运行记录','Device packages, actions, jobs and run records'),'kushalsinha/openmhp',t('公开草案与实现','Public draft and code')],
        [link('#presentation/8','LAP'),t('带资源占用与测量语义的任务','Tasks with reservations and measurement semantics'),'Shiyanjia Lab',t('v0.1 设计论文','v0.1 design paper')],
        [link('#presentation/9','OAHL'),t('节点、设备发现与会话占用','Nodes, discovery and exclusive sessions'),'fredabila/oahl',t('公开代码','Public code')],
    ]
    body=table([t('方案','Design'),t('统一的核心对象','Core abstraction'),t('维护者 / 来源','Maintainer / source'),t('材料形态','Artifact')],rows,'inventory')
    body+='<p class="small-note">'+t('三个 Open-MHS 分别由 Abenor Labs、tongriyaotxt、SCUT-ESA 维护；MHP 指 Cuntinum 的项目。另有 Agent2Device 概念提案，现有内容为 README。','The three Open-MHS projects are maintained by Abenor Labs, tongriyaotxt and SCUT-ESA. MHP refers to Cuntinum’s project. Agent2Device is an additional concept proposal documented in a README.')+'</p>'
    add('designs','designs',t('现有方案，首先在“统一什么”上不同','Existing designs differ first in what they unify'),t('方案全表','Design inventory'),body,('mhs','aip','openmhp','lap','oahl'))

    # 04: MHS anatomy, not sponsor praise.
    body='<div class="split"><div class="system-drawing">'+entity(t('人 / Agent / 自动化程序','People / agents / automation'),'MCP · CLI · API','top')+'<div class="connector">↓</div>'+entity(t('共同设备接口','Shared device interface'),t('发现设备 · 读状态 · 写控制量','Discover devices · Read state · Write controls'),'core')+'<div class="driver-grid">'+entity(t('激光器驱动','Laser driver'),t('功率、开关','Power, enable'))+entity(t('转台驱动','Stage driver'),t('角度、位置','Angle, position'))+entity(t('相机驱动','Camera driver'),t('曝光、图像','Exposure, image'))+'</div><div class="device-strip">'+t('物理设备与各自的编程接口','Physical devices and their programming interfaces')+'</div></div><div>'+note(t('定义','Definition'),t('MHS（Model Hardware Standard）把设备包装为共同驱动接口；物理说明标签描述设备能力及操作条件。','MHS wraps equipment in a shared driver interface. Physical-description tags explain capabilities and operating conditions.'))+note(t('改变了什么','What changes'),t('上层程序按能力发现和操作仪器，型号差异由驱动承担。同一套设备能力可从不同入口访问。','Callers operate named capabilities. Drivers translate them for each device; MCP, CLI and API expose the same interface.'))+note(t('在扫描中','In the scan'),t('找到能旋转波片的轴和能读取光功率的通道，再通过共同接口操作。','Find an axis that rotates the plate and a channel that measures optical power, then operate both through a common interface.'))+'</div></div>'
    body+=insight(t('可继承的机制：让设备“自我描述”，让上层程序脱离厂商函数名。','Self-describing capabilities let callers work independently of vendor function names.'))
    add('mhs','designs',t('MHS：把不同设备接到共同能力接口','MHS: a shared capability interface for heterogeneous devices'),'MHS',body,('mhs','mhs-site'),t('Anthropic × HHMI Janelia · 研究预览','Anthropic × HHMI Janelia · Research preview'))

    # 05: the four implementations have different engineering choices.
    body=table([t('独立项目','Independent project'),t('实现的组织方式','Implementation structure'),t('具体区别','Concrete distinction')],[
        [link('#projects/open-mhs-abenor','Open-MHS · Abenor Labs'),t('能力标签 → 设备基类 → 传输驱动','Capability tags → device base class → transport'),t('标签随设备提供；读写检查集中在运行层；支持生成设备说明。','Device-owned tags; centralized read/write checks; generated device documentation.')],
        [link('#projects/open-mhs-tong','Open MHS · tongriyaotxt'),t('设备注册 → 命令分派 → 运动技能','Registry → command dispatch → motion skills'),t('在读写之上增加机器人技能，把连续动作交给本地控制。','Robot skills add local continuous control above individual reads and writes.')],
        [link('#projects/open-mhs-scut','Open MHS · SCUT-ESA'),t('共同接口 → 显式后端 → VISA 仪器','Common interface → explicit backend → VISA instrument'),t('分别管理实机、实验性与模拟后端；维护者列出两款 UNI-T 仪器的实机记录。','Separates hardware, experimental and simulated backends; reports hardware work with two UNI-T models.')],
        [link('#projects/mhp-cuntinum','MHP · Cuntinum'),t('discover / read / write / execute<br>+ State Bus','discover / read / write / execute<br>+ State Bus'),t('以四类原语组织 SDK 和驱动，用共享状态组织设备协作；包名 khp。','Four primitive families organize SDKs and drivers; a shared state bus supports coordination. Package: khp.')],
    ])
    body+=insight(t('共同点是“能力—驱动”映射；差异在状态共享、动作组织和设备后端。选择依据应落实到所需设备与操作。','The common mechanism is capability-to-driver mapping. State sharing, action composition and device backends distinguish the implementations.'))
    add('implementations','designs',t('同样叫设备接口，实现重心仍然不同','Device interfaces differ in their implementation choices'),t('Open-MHS 与 MHP','Open-MHS and MHP'),body,('abenor','tong','scut','cuntinum'),t('三个 Open-MHS 独立维护；Cuntinum MHP 为另一项目','Three independently maintained Open-MHS projects; Cuntinum MHP is a separate project'))

    # 06: persistent state, resource declarations, observation provenance.
    body='<div class="split"><div class="system-drawing">'+entity(t('客户端请求','Client request'),'read · write · ramp · act','top')+'<div class="connector">↓</div><div class="runtime-box"><h3>'+t('常驻仪器服务','Persistent instrument service')+'</h3><div>'+entity(t('量 / 动作 / 活动','Quantity / action / activity'),t('单位、参数、进度、完成条件','Units, parameters, progress, completion'))+entity(t('资源与状态','Resources and state'),'touches · occupies · events')+'</div></div><div class="connector">↓ ↑</div>'+entity(t('型号驱动 + 通信 channel','Model driver + communication channel'),t('下发操作；读取实际状态','Issue operations; read actual state'))+'</div><div>'+note(t('定义','Definition'),t('AIP（Agent–Instrument Protocol）把仪器连接、长活动与执行记录放进持续运行的服务；客户端提交工作并查询结果。','AIP places device connections, long-running activities and execution records in a persistent service. Clients submit work and retrieve results.'))+note(t('关键区别','Key distinction'),t('“动作已受理”与“物理目标已达成”分别记录。资源声明描述操作会影响什么；读数区分仪器报告、驱动记账与推断。','Acceptance and physical achievement are recorded separately. Resource declarations describe effects; readings distinguish device reports, tracked values and inference.'))+note(t('在扫描中','In the scan'),t('转台移动期间，服务持续跟踪到位条件；调用者离开后，活动和观测仍有明确身份。','The service tracks arrival while the stage moves. Activities and observations retain identities beyond the initiating call.'))+'</div></div>'
    body+=insight(t('可继承的机制：由运行服务持有操作生命周期，供不同调用者持续查询和使用。','Mechanism to carry forward: the runtime owns the physical operation’s lifecycle across individual tool calls.'))
    add('aip','designs',t('AIP：把一次调用变成持续可追踪的操作','AIP: track physical operations beyond a single call'),'AIP',body,('aip',),t('Agent–Instrument Protocol · 用户提供的 PRD v1.1','Agent–Instrument Protocol · Supplied PRD v1.1'))

    # 07: the public specification's actual object and method names.
    body='<div class="split"><div class="package-diagram"><div><b>DEVICE.md</b><span>'+t('身份、摘要、操作说明','Identity, summary and instructions')+'</span></div><div><b>descriptor.yaml</b><span>signals · settings · actions</span></div><div><b>driver.py</b><span>'+t('读写与动作的设备实现','Device implementation of reads, writes and actions')+'</span></div><div><b>references / scripts / methods</b><span>'+t('知识材料、过程脚本与方法参数','References, procedures and method parameters')+'</span></div></div><div>'+note(t('定义','Definition'),t('OpenMHP 用设备包把操作说明、机器可读描述与驱动放在一起，再以统一请求操作设备。','OpenMHP packages instructions, machine-readable descriptions and drivers, then exposes devices through common requests.'))+note(t('执行路径','Execution path'),'<code>device/describe</code> → '+t('选择能力','select capabilities')+' → '+t('读取 / 写入 / 调用动作','read / write / invoke')+' → '+t('查询任务和运行文件','inspect jobs and run files'))+note(t('关键区别','Key distinction'),t('描述按需加载；长动作交给任务；过程脚本与产出的文件关联到 run。参考设备包主要经过孪生测试。','Descriptions load on demand; jobs handle long actions; runs associate scripts with output files. Reference device packages are primarily twin-tested.'))+'</div></div>'
    body+=insight(t('可继承的机制：一个可分发的设备包，把“怎么理解、怎么运行、产出在哪里”连在一起。','Mechanism to carry forward: a distributable device package connecting understanding, execution and outputs.'))
    add('openmhp','designs',t('OpenMHP：让设备说明、驱动与运行记录相互关联','OpenMHP: connect descriptions, drivers and run records'),'OpenMHP',body,('openmhp','openmhp-devices'),t('公开规范草案与 Python 实现','Public draft specification and Python implementation'))

    # 08: four physical-world primitives, named accurately and concisely.
    body='<div class="lap-contract">'+entity('InstrumentCard',t('能力、设备身份与物理限制','Capabilities, identity and physical limits'))+'<span>↓</span>'+entity(t('Reservation + task','Reservation + task'),t('设备 / 样品占用，任务状态与参数绑定的执行确认','Device/sample reservation, task state and task-bound confirmation'),'core')+'<span>↓</span>'+entity('MeasurementResult',t('数值、单位、校准、不确定度与来源','Values, units, calibration, uncertainty and provenance'))+'</div>'
    body+='<div class="split equal">'+note(t('定义','Definition'),t('LAP（Lab Agent Protocol）沿用 Agent 之间发现和任务协作的结构，把仪器作为有物理状态和测量结果的参与者。','LAP retains agent discovery and task collaboration while treating instruments as participants with physical state and measurement results.'))+note(t('在扫描中','In the scan'),t('取得转台与探测器的使用权；提交扫描任务；返回带角度单位、探测器校准信息及测量来源的结果。','Reserve the stage and detector, submit a scan task, and return results with angle units, detector calibration and measurement provenance.'))+'</div>'
    body+=insight(t('可继承的机制：让“结果是什么、在什么条件下产生”成为任务契约的一部分。','Mechanism to carry forward: make the meaning and conditions of a measurement part of the task contract.'))
    add('lap','designs',t('LAP：把资源占用和测量含义写进任务契约','LAP: include reservations and measurement meaning in task contracts'),'LAP',body,('lap',),t('Shiyanjia Lab · LAP v0.1 设计论文','Shiyanjia Lab · LAP v0.1 design paper'))

    # 09: a topology rather than a capabilities buzzword list.
    body='<div class="split"><div class="system-drawing">'+entity(t('调用者','Caller'),'JavaScript / Python SDK','top')+'<div class="connector">↓</div>'+entity(t('本地节点 / 可选注册与中继','Local node / optional registry and relay'),t('发现能力与节点地址','Find capabilities and node addresses'),'core')+'<div class="connector">↓</div>'+entity(t('会话管理 → 设备适配器 → 传输','Session → adapter → transport'),'Serial · ADB · MQTT · TCP')+'<div class="device-strip">'+t('节点所在位置的真实设备','Physical equipment attached to the node')+'</div></div><div>'+note(t('定义','Definition'),t('OAHL（Open Agent Hardware Layer）把设备暴露为节点中的能力，调用者通过会话取得使用权，再由适配器和传输插件执行。','OAHL exposes capabilities through hardware nodes. Callers reserve sessions; adapters and transport plugins perform the operation.'))+note(t('它重点解决什么','Primary problem'),t('设备在哪里、通过哪个节点访问、当前由谁使用。README 展示了通过 ADB 操作手机的路径。','Where equipment is, which node exposes it and who is using it. The README demonstrates an Android device through ADB.'))+'</div></div>'
    body+=flow([('discover',t('找到设备','Find equipment')),('reserve',t('取得会话','Acquire a session')),('execute',t('执行能力','Run a capability')),('release',t('释放占用','Release the resource'))])
    add('oahl','designs',t('OAHL：把分散的设备组织成可访问的资源','OAHL: make distributed devices accessible resources'),'OAHL',body,('oahl',),t('MIT · 节点、SDK 与传输插件','MIT · Nodes, SDKs and transport plugins'))

    # 10: one hierarchy, one criterion. No second taxonomy of the 73 records.
    families=[
        ('A',t('设备能力模型','Device capability models'),'MHS · Open-MHS × 3 · MHP',t('设备能做什么？','What can the device do?'),t('共同描述 + 驱动映射','Shared description + driver mapping'),t('设备、能力、操作定义','Instrument, capability, operation'),'#presentation/4'),
        ('B',t('操作执行与结果契约','Execution and result contracts'),'AIP · OpenMHP · LAP',t('怎样完成，又怎样证明？','How does it finish, and what is the evidence?'),t('任务状态 + 资源 + 观测','Task state + resources + observations'),t('执行实例、观测、方法','Run, observation, method'),'#presentation/6'),
        ('C',t('设备发现与资源协作','Discovery and resource coordination'),'OAHL',t('设备在哪里，由谁使用？','Where is it, and who can use it now?'),t('发现 + 会话 + 访问路径','Discovery + sessions + access paths'),t('身份、占用、绑定','Identity, reservation, binding'),'#presentation/9'),
    ]
    body='<div class="island-headings"><span>'+t('一级 · 具体方案','I · Existing designs')+'</span><span>'+t('二级 · 共同机制','II · Shared mechanisms')+'</span><span>'+t('三级 · IOP 对象','III · IOP objects')+'</span></div><div class="island-map">'
    for id,name,examples,question,mechanism,objects,href in families:
        body+='<div class="island-row tone-'+id+'"><a class="island-origin" href="'+href+'">'+examples+'</a><div class="island-mechanism"><span class="island-letter">'+id+'</span><h3>'+name+'</h3><p>'+question+'</p><b>'+mechanism+'</b></div><div class="island-output">'+objects+'</div></div>'
    body+='</div><p class="figure-caption">'+t('按主要设计重心归纳。OpenMHP 和 LAP 也包含发现与资源机制；分组表达贡献重心，这些机制在同一次操作中协作。','Grouped by primary design emphasis. OpenMHP and LAP also include discovery and resources; these overlapping mechanisms work together in a physical operation.')+'</p>'
    add('islands','mechanisms',t('九项有具体机制的方案，归纳为三个机制岛屿','Nine substantive designs reveal three mechanism families'),t('三级关系全图','The complete hierarchy'),body,('mhs','aip','openmhp','lap','oahl'),t('由具体设计归纳','Synthesis of the reviewed designs'))

    # 11: interaction among islands, keeping the same physical example.
    body='<div class="mechanism-trace"><div class="trace-row"><span class="island-letter">C</span><div><h3>'+t('取得可用设备','Acquire available equipment')+'</h3><p>'+t('按旋转轴与功率测量能力找到设备，建立会话，确认资源占用。','Find rotational and power-measurement capabilities, establish a session and reserve resources.')+'</p></div><code>'+t('设备身份 + 可访问端点','identity + endpoint')+'</code></div><div class="trace-row"><span class="island-letter">A</span><div><h3>'+t('建立操作的共同含义','Establish shared operation meanings')+'</h3><p>'+t('把转台位置定义为半波片角度 θ；把探测器通道定义为光功率 P。','Define the stage position as plate angle θ and the detector channel as optical power P.')+'</p></div><code>'+t('能力 + 单位 + 轴零点','capability + unit + origin')+'</code></div><div class="trace-row"><span class="island-letter">B</span><div><h3>'+t('执行并保存物理结果','Execute and retain physical results')+'</h3><p>'+t('每点设角、确认到位、采集功率；将实际读数与同一次 run 关联。','Set each angle, confirm arrival and acquire power; associate actual readings with the same run.')+'</p></div><code>run → observations</code></div></div>'
    body+=insight(t('IOP 的连接点是共同的操作身份：设备描述、执行请求、实际观测和方法知识，始终指向同一件事。','IOP joins these mechanisms through shared operation identities: descriptions, requests, observations and methods refer to the same operation.'))
    add('mechanism-composition','mechanisms',t('三个岛屿，分别承担同一次操作的不同责任','Three mechanism families serve the same physical operation'),t('机制怎样协作','How mechanisms connect'),body,status=t('偏振扫描 · 机制组合','Polarization scan · Mechanism composition'))

    # 12: standards are not just logos. Separate information model from binding.
    body=table([t('既有基础','Existing foundation'),t('它已经提供的对象','Objects it already provides'),t('IOP 可映射的部分','What IOP can map')],[
        ['SiLA 2','Feature · Command · Property',t('能力集合、属性读取、命令与可观测执行。把仪器类语义映射到这些交互。','Capability sets, property access, commands and observable execution. Map instrument-class semantics onto these interactions.')],
        ['OPC UA / LADS','Device · FunctionalUnit · ProgramManager',t('仪器与功能单元、程序及结果管理。复用设备信息模型与状态。','Devices, functional units, program and result management. Reuse information models and device state.')],
        ['W3C WoT','Thing Description · Property · Action · Event',t('把能力描述与具体通信绑定分开。IOP 操作可对应 Action，观测可对应 Property / Event。','Separate capability descriptions from transport bindings. Map operations to Actions and observations to Properties or Events.')],
    ])
    body+='<div class="interface-ribbon"><b>'+t('调用入口','Client entry points')+'</b><span>MCP · API · CLI · '+t('人工界面','Human UI')+'</span><p>'+t('共享操作模型；入口选择由使用场景决定。','Share the operation model; choose an interface for the use case.')+'</p></div>'
    add('foundations','mechanisms',t('共同语义可以复用已有设备标准','Shared semantics can build on existing device standards'),t('既有标准的位置','Where existing standards fit'),body,('sila','lads','wot'),t('接口映射设计','Interface mapping design'))

    # 13: this is the actual thesis, with object relations and cardinality meanings.
    body='<div class="object-model"><div class="object-row">'+entity(t('仪器 Instrument','Instrument'),t('物理身份、能力与资源','Physical identity, capabilities and resources'))+'<span class="relation-word">'+t('提供','provides')+'</span>'+entity(t('操作 Operation','Operation'),t('输入、作用、完成条件、输出','Inputs, effects, completion and outputs'),'core')+'<span class="relation-word">'+t('被组合为','composes into')+'</span>'+entity(t('方法 Method','Method'),t('适用条件、步骤与分析','Applicability, procedure and analysis'))+'</div><div class="object-connectors"><span>'+t('驱动绑定 ↓','Driver binding ↓')+'</span><span>'+t('每次调用实例化 ↓','Each invocation creates ↓')+'</span><span>'+t('方法规定观测 ↓','Specifies acquisition ↓')+'</span></div><div class="object-row">'+entity(t('设备实现 Binding','Binding'),t('厂商命令、现有控制系统','Vendor commands and control systems'))+'<span class="relation-word">'+t('执行','executes')+'</span>'+entity(t('执行实例 Run','Run'),t('参数、占用、状态与事件','Parameters, reservations, state and events'),'core')+'<span class="relation-word">'+t('产出','produces')+'</span>'+entity(t('观测 Observation','Observation'),t('读回、单位、时间与条件','Readback, units, time and conditions'))+'</div></div>'
    body+='<div class="model-definition"><b>'+t('IOP 的核心约束','The central IOP contract')+'</b><p>'+t('一次操作必须能从“它的物理含义”追到“这次如何执行”，再追到“结果由哪些观测支持”。原理与经验通过操作身份关联；方法复用这些操作；驱动实现它们。','An operation must connect its physical meaning to a particular execution and the observations supporting its result. Principles and practical knowledge link to operation identities; methods compose operations; drivers implement them.')+'</p></div>'
    add('iop-model','iop',t('IOP：以操作为中心，把知识、执行和观测连成整体','IOP: connect knowledge, execution and observations around operations'),t('IOP 的核心模型','The IOP model'),body,('operations',),t('AI4Instruments · IOP 设计','AI4Instruments · IOP design'))

    # 14: human and machine are views of the SAME definition.
    code='''id: optics.polarization_scan
version: 0.1
requires:
  angle: {unit: deg, origin: plate_axis_zero}
  power: {unit: W}
context: [wavelength, calibration_ref]
inputs: {angles: {type: array, unit: deg}}
procedure:
  for_each: {angle_target: angles}
  steps:
    - move_to: angle_target
    - wait_for: stage_settled
    - read: [angle_actual, power, time]
result: {columns: [angle_actual, power, time]}'''
    body='<div class="split equal definition-pair"><div><span class="margin-label">'+t('人看到的操作定义','Human-readable operation')+'</span><h3>'+t('偏振扫描','Polarization scan')+'</h3><p>'+t('沿给定角度序列旋转半波片，每点确认转台到位后采集透射功率。','Rotate the half-wave plate through the requested angles. At each point, confirm stage settling before acquiring transmitted power.')+'</p><dl><dt>'+t('角度','Angle')+'</dt><dd>'+t('单位为度；零点对应波片轴的标定位置。','Degrees relative to the calibrated plate-axis origin.')+'</dd><dt>'+t('功率','Power')+'</dt><dd>'+t('单位为瓦；记录工作波长与探测器校准引用。','Watts, with wavelength and a detector calibration reference.')+'</dd><dt>'+t('输出','Output')+'</dt><dd>'+t('保存实际角度、功率与采集时间，形成同一份扫描记录。','Actual angle, power and acquisition time in one scan record.')+'</dd></dl></div><div><span class="margin-label">'+t('程序读取的同一份定义','The same definition for software')+'</span><pre class="contract-code"><code>'+E(code)+'</code></pre></div></div>'
    body+=insight(t('原理、说明、参数与程序共享同一个 id 和版本；修改方法时，同时更新它们的对应关系。','Principles, instructions, parameters and execution share one id and version. Method changes update their relationships together.'))
    add('shared-definition','iop',t('一个操作定义，供人理解，也供程序执行','One operation definition for people and software'),t('共同定义的具体形态','A concrete operation definition'),body,status=t('IOP 定义示意 · YAML','Illustrative IOP definition · YAML'))

    # 15: physical and software states are different, shown in parallel lanes.
    body='<div class="execution-timeline"><div class="timeline-heading"><span>'+t('过程','Process')+'</span><b>01</b><b>02</b><b>03</b><b>04</b></div><div class="timeline-row"><b>'+t('软件记录','Software')+'</b>'+''.join('<div>'+x+'</div>' for x in [t('请求受理<br><small>固定参数与方法版本</small>','Accepted<br><small>Parameters and method version fixed</small>'),t('操作执行<br><small>下发移动，跟踪活动</small>','Running<br><small>Move issued, activity tracked</small>'),t('条件成立<br><small>到位读回满足约定</small>','Condition met<br><small>Arrival readback meets criteria</small>'),t('结果形成<br><small>观测写入 run</small>','Result recorded<br><small>Observations linked to run</small>')])+'</div><div class="timeline-row physical"><b>'+t('物理过程','Physical')+'</b>'+''.join('<div>'+x+'</div>' for x in [t('转台仍在原位置','Stage at its initial position'),t('波片转动','Plate moving'),t('实际位置稳定','Actual position settled'),t('探测器完成采集','Detector acquisition complete')])+'</div></div>'
    body+='<div class="split equal">'+note(t('完成条件来自仪器行为','Completion follows device behavior'),t('驱动给出到位状态或读回判据；方法定义需要满足的条件，然后才采集功率。','The driver supplies a settled state or readback criterion. The method specifies the required condition before power acquisition.'))+note(t('中断后根据读回恢复认知','Reconcile from readback after interruption'),t('连接中断时保留 run。重连后先检查位置与活动状态，再决定继续、结束或保留未完成记录。','Retain the run across disconnection. Read position and activity state on reconnection before continuing, ending or retaining a partial record.'))+'</div>'
    body+=insight(t('执行记录回答“发出了什么”；观测记录回答“物理上发生了什么”。IOP 用同一个 run 将两者关联。','Execution records state what was issued; observations state what physically occurred. A shared run links both.'))
    add('execution','iop',t('一次执行，必须走到实际状态和测量读回','Follow execution through to physical state and readback'),t('执行与观测','Execution and observation'),body,status=t('IOP 执行语义设计','IOP execution semantics design'))

    # 16: concrete compatibility boundaries, not a promise of universal support.
    body='<div class="reuse-banner"><b>optics.polarization_scan</b><span>'+t('同一个方法与结果格式','One method and result format')+'</span></div>'+table([t('IOP 要求','IOP requirement'),t('设备实现 A','Device implementation A'),t('设备实现 B','Device implementation B')],[
        [t('角度设定，单位 deg','Set angle in deg'),t('厂商 SDK：将角度转换为原生位置单位','Vendor SDK: convert angle to native position units'),t('EPICS：映射设定值通道和单位','EPICS: map setpoint channel and units')],
        [t('实际位置与到位条件','Actual position and settling'),t('读取编码器与运动状态','Read encoder and motion state'),t('映射读回及到位状态通道','Map readback and done-state channels')],
        [t('光功率，单位 W','Optical power in W'),t('SCPI / VISA：读取并统一单位','SCPI / VISA: query and normalize units'),t('已有采集服务：读取功率与时间','Acquisition service: read power and time')],
        [t('方法所需条件','Method requirements'),t('波长、轴零点、量程与校准引用','Wavelength, origin, range and calibration'),t('提供相同含义；缺失能力显式返回','Expose the same meanings; report missing capabilities')],
    ])
    body+=insight(t('兼容性落实到能力：输入含义相同、完成判据相同、结果可解释。传输方式与内部实现可以不同。','Compatibility is capability-specific: equivalent input meaning, completion criteria and interpretable results across different transports and implementations.'))
    add('compatibility','iop',t('跨设备复用，靠明确的语义映射','Reuse across devices requires explicit semantic mappings'),t('怎样兼容现有系统','Compatibility with existing systems'),body,status=t('两种设备组合的适配设计','Adapter design for two equipment configurations'))

    # 17: the ecosystem has tangible, linked artifacts.
    body='<div class="instrument-package"><div class="package-spine"><span>IOP</span><h3>'+t('仪器包','Instrument package')+'</h3><p>'+t('共同身份<br>明确版本','Shared identity<br>Explicit version')+'</p></div><div class="package-sections">'
    for title,what,use in [
        (t('原理与知识','Principles and knowledge'),t('物理量、作用机制、适用条件与实践经验','Quantities, physical mechanisms, applicability and practice'),t('解释操作的含义与选择依据','Explain meaning and method choices')),
        (t('能力与操作定义','Capability and operation definitions'),t('参数、单位、状态、作用与结果结构','Parameters, units, state, effects and result structure'),t('供界面、脚本与 Agent 共同读取','Shared by interfaces, scripts and agents')),
        (t('驱动与方法实现','Drivers and methods'),t('设备适配、步骤组合、分析与复测','Adapters, procedure composition, analysis and repetition'),t('把定义落实到真实设备','Execute definitions on real devices')),
        (t('测量与一致性记录','Measurement and conformance records'),t('校准引用、实机读回、测试条件与数据','Calibration references, readbacks, test conditions and data'),t('支持复用、比较与持续维护','Support reuse, comparison and maintenance')),
    ]:body+='<div><h3>'+title+'</h3><p>'+what+'</p><span>'+use+'</span></div>'
    body+='</div></div>'
    body+=insight(t('生态的基本单位是可使用、可理解、可验证的仪器包；共享词汇和一致性测试，使不同作者的仪器包能够协作。','The ecosystem grows through usable, understandable and testable instrument packages, joined by shared vocabulary and conformance tests.'))
    add('ecosystem','iop',t('知识、方法、代码与数据，围绕同一台仪器组织','Organize knowledge, methods, code and data around the instrument'),t('生态由什么组成','What the ecosystem contains'),body,status=t('IOP 仪器包设计','IOP instrument-package design'))

    # 18: an experimentally assessable end state; no meta-discussion of the medium.
    body='<div class="validation-map"><div class="common-method"><span>'+t('同一份操作定义与方法','One operation definition and method')+'</span><b>optics.polarization_scan</b></div><div class="parallel-setups"><div><b>'+t('设备组合 A','Equipment configuration A')+'</b><span>'+t('SDK 转台 + VISA 功率计','SDK stage + VISA power meter')+'</span></div><div><b>'+t('设备组合 B','Equipment configuration B')+'</b><span>'+t('控制系统转台 + 采集服务','Control-system stage + acquisition service')+'</span></div></div><div class="comparison-output"><b>'+t('可解释、可对照的扫描记录','Interpretable, comparable scan records')+'</b><span>angle_actual · power · time · calibration_ref · method_version</span></div></div>'
    body+='<div class="validation-criteria">'+note(t('语义一致','Consistent meaning'),t('同一角度定义、单位与方法条件。','Same angle definition, units and method conditions.'))+note(t('执行成立','Valid execution'),t('到位判据由实机读回满足。','Physical readback satisfies arrival criteria.'))+note(t('结果可解释','Interpretable results'),t('差异能追溯到设备、校准与实验条件。','Differences trace to devices, calibration and conditions.'))+'</div>'
    body+=insight(t('IOP 的价值：保留仪器的物理真实性，同时减少人和程序在理解、接入与复用方法时的重复工作。','IOP preserves physical meaning while making instrument knowledge, connections and methods reusable.'))
    add('validation','iop',t('IOP 的成立条件：同一方法，跨设备保持同一含义','The IOP test: preserve method meaning across devices'),t('如何判断 IOP 做成了','What demonstrates that IOP works'),body,('operations',),t('建设目标 · 仓库现有基础：操作模型与模拟参考实现','Development target · Current foundation: operation model and simulated reference implementation'))
    return pages


def metadata(data):
    zh,en=content('zh'),content('en')
    assert [x['id'] for x in zh]==[x['id'] for x in en]
    slides=[]
    for a,b in zip(zh,en):
        slides.append({'id':a['id'],'chapter':a['chapter'],'title':pair(a['title'],b['title']),
            'short':pair(a['short'],b['short']),'status':pair(a['status'],b['status']),
            'body':pair(a['body'],b['body']),'sources':a['sources']})
    return {'schema_version':'2.0','updated':'2026-10-21','edition':'IOP-02',
        'name':'Instrument Operations Protocol','abbreviation':'IOP',
        'levels':{'1':'existing designs','2':'mechanism families','3':'IOP operation model'},
        'chapters':CHAPTERS,'mechanism_families':ISLANDS,
        'classification_basis':'primary design emphasis; mechanisms may overlap',
        'additional_concepts':['p:agent2device'],
        'sources':{k:{'label':v[0],'url':v[1]} for k,v in SOURCES.items()},'slides':slides}


def render(data,lang):
    E=lambda x:html.escape(str(x),quote=True)
    t=lambda a,b:a if lang=='zh' else b
    d=data['presentation']; slides=[]
    chapter_names={c['id']:c['name'][lang] for c in CHAPTERS}
    for i,s in enumerate(d['slides'],1):
        refs=''.join('<a href="'+E(SOURCES[r][1])+'">'+E(SOURCES[r][0])+' ↗</a>' for r in s['sources'])
        slides.append(f'<article class="deck-slide" data-slide="{i}" data-chapter="{s["chapter"]}" aria-label="{i}. {E(s["title"][lang])}"><header><div class="slide-meta"><span>{E(chapter_names[s["chapter"]])}</span><span>{i:02} / {len(d["slides"]):02}</span></div><h2>{s["title"][lang]}</h2></header><div class="deck-body">{s["body"][lang]}</div><footer><span>{E(s["status"][lang]) or "AI4Instruments · IOP"}</span><div class="deck-refs">{refs}</div></footer></article>')
    tabs=''.join('<a data-chapter-nav="'+c['id']+'" href="#presentation/'+str(c['start'])+'">'+E(c['name'][lang])+'</a>' for c in CHAPTERS)
    options=''.join('<option value="'+str(i)+'">'+f'{i:02}　'+E(s['short'][lang])+'</option>' for i,s in enumerate(d['slides'],1))
    outline=''.join('<a data-page-nav="'+str(i)+'" data-page-chapter="'+s['chapter']+'" href="#presentation/'+str(i)+'"><span>'+f'{i:02}'+'</span>'+E(s['short'][lang])+'</a>' for i,s in enumerate(d['slides'],1))
    return f'''<section class="view" id="view-presentation" data-view="presentation"><div class="deck-shell" id="deck-shell"><nav class="chapter-tabs" aria-label="{t('论述结构','Argument structure')}">{tabs}</nav><div class="deck-workspace"><nav class="chapter-outline" aria-label="{t('本章内容','Chapter contents')}">{outline}</nav><div class="deck-reading"><div class="deck-stage" id="deck-stage">{''.join(slides)}</div><div class="deck-controls"><button id="deck-prev" aria-label="{t('上一页','Previous page')}">←</button><label class="sr-only" for="deck-select">{t('选择页面','Select a page')}</label><select id="deck-select">{options}</select><button id="deck-next" aria-label="{t('下一页','Next page')}">→</button><span id="deck-position" aria-live="polite"></span><button id="deck-focus">{t('展开','Expand')}</button><button id="deck-fullscreen">{t('全屏','Fullscreen')}</button><button id="deck-exit" hidden>{t('还原','Restore')}</button></div></div></div></div><dialog id="island-detail"><div class="section-line"><h2 id="island-detail-title"></h2><button id="island-close">{t('关闭','Close')}</button></div><p id="island-detail-question"></p><div id="island-detail-projects"></div></dialog></section>'''
