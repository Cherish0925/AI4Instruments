"""Bilingual IOP argument: existing designs → mechanisms → a shared operation model."""
import html


def pair(zh, en):
    return {'zh': zh, 'en': en}


CHAPTERS = [
    {'id': 'question', 'name': pair('问题与全图', 'Overview'), 'start': 1},
    {'id': 'designs', 'name': pair('一级 · 已有方案', 'I · Existing designs'), 'start': 3},
    {'id': 'mechanisms', 'name': pair('二级 · 共同机制', 'II · Shared mechanisms'), 'start': 10},
    {'id': 'iop', 'name': pair('三级 · 我们的 IOP', 'III · Our IOP'), 'start': 13},
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
    {'id':'execution', 'name':pair('操作执行与结果定义','Execution and result definitions'),
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
        ('I',t('具体方案','Existing designs'), 'MHS · AIP · OpenMHP · LAP · OAHL',t('各方案怎样描述、连接和操作真实仪器','How each design describes, connects and operates instruments'),'#presentation/3'),
        ('II',t('共同机制','Shared mechanisms'),t('能力模型 · 执行规则 · 资源协作','Capabilities · Execution · Resources'),t('把相似实现归到同一问题，把互补机制接起来','Group similar solutions; connect complementary mechanisms'),'#presentation/10'),
        ('III','IOP',t('仪器说明、常驻服务、实验程序、实验记录','Descriptions, service, programs and records'),t('人和 Agent 提交实验程序，平台常驻服务统一执行与留档','People and agents submit programs; a persistent service executes and records them'),'#presentation/13'),
    ]
    body='<p class="opening-definition">'+t('IOP 组织<b>仪器说明、常驻服务、实验程序与实验记录</b>。人和 Agent 使用同一套操作定义，由平台服务协调真实设备，完成实验并保存过程与结果。','IOP organizes <b>instrument descriptions, a persistent service, experiment programs and records</b> so people and agents can operate equipment through shared definitions.')+'</p>'
    body+='<div class="argument-map">'+''.join('<a href="'+href+'"><span class="roman">'+num+'</span><div><h3>'+title+'</h3><b>'+line+'</b><p>'+desc+'</p></div><span class="map-arrow">↗</span></a>' for num,title,line,desc,href in rows)+'</div>'
    add('argument','question',t('IOP · 仪器操作协议','IOP · Instrument Operation Protocol'),t('三级关系','The three levels'),body,status=t('AI4Instruments · 设计研究','AI4Instruments · Design study'))

    # 02: one physical experiment, with a genuinely useful technical diagram.
    labels=[t('线偏振光','Linear input'),t('半波片','Half-wave plate'),t('固定检偏器','Fixed analyzer'),t('功率计','Power meter')]
    svg='<svg class="bench-diagram" viewBox="0 0 1000 200" role="img" aria-label="'+t('线偏振光经过旋转半波片和固定检偏器到达功率计','Linear light passes a rotating half-wave plate and a fixed analyzer to a power meter')+'"><path d="M70 92H905" class="beam"/><path d="M900 87l12 5-12 5" class="beam-fill"/><rect x="90" y="62" width="70" height="60" rx="4"/><path d="M115 75v34m10-34v34m10-34v34" class="fine"/><circle cx="360" cy="92" r="37"/><path d="M335 118l50-52" class="axis"/><path d="M397 46a58 58 0 0 1 20 47" class="fine"/><text x="424" y="70">θ</text><rect x="570" y="50" width="32" height="84" rx="3"/><path d="M580 62v59m11-59v59" class="fine"/><path d="M820 58h70v68h-70z"/><circle cx="855" cy="92" r="21" class="fine"/>'
    svg+=''.join('<text class="bench-label" x="'+str(x)+'" y="173" text-anchor="middle">'+v+'</text>' for x,v in zip([125,360,586,855],labels))+'</svg>'
    body=svg+'<div class="split equal"><div><div class="formula">P(θ) = P₀ cos²(2θ − φ)</div><p class="figure-caption">'+t('理想半波片、固定检偏器。φ 由入射偏振、检偏器方向及轴零点确定。实际测量还受波长、损耗与探测器响应影响。','Ideal half-wave plate and fixed analyzer; φ depends on input polarization, analyzer orientation and axis zero. Wavelength, loss and detector response affect the physical measurement.')+'</p></div><div>'+note(t('任务','Task'),t('改变波片角度，测量透射功率，得到角度—功率曲线。','Vary the plate angle, measure transmitted power and obtain an angle–power curve.'))+'</div></div>'
    body+=flow([(t('定义','Define'),t('θ 的零点、单位与范围','Angle origin, units and range')),(t('执行','Execute'),t('转动 → 到位 → 采集','Move → settle → acquire')),(t('解释','Interpret'),t('实际角度、功率与校准条件','Actual angle, power and calibration'))])
    add('physical-problem','question',t('贯穿案例：半波片偏振扫描','Running example: a polarization scan'),t('从真实操作出发','Start with a physical operation'),body,status=t('贯穿案例 · 物理模型与接口设计','Running example · Physical model and interface design'))

    # 03: compact, exact inventory. Each substantive design has an explanation next.
    rows=[
        [link('#presentation/4','MHS'),t('共享驱动与设备能力描述','Shared drivers and capability descriptions'),t('Anthropic + HHMI Janelia','Anthropic + HHMI Janelia'),t('研究预览','Research preview')],
        [link('#presentation/5','Open-MHS × 3 · MHP'),t('把共同设备接口实现为代码','Implement common device interfaces'),t('四个独立维护项目','Four independent projects'),t('公开代码','Public code')],
        [link('#presentation/6','AIP'),t('持久运行的仪器操作服务','Persistent instrument-operation service'),t('所提供的架构文档','Supplied PRD'),t('设计材料','Design document')],
        [link('#presentation/7','OpenMHP'),t('设备包、动作、任务和运行记录','Device packages, actions, jobs and run records'),'kushalsinha/openmhp',t('公开草案与实现','Public draft and code')],
        [link('#presentation/8','LAP'),t('带资源占用与测量语义的任务','Tasks with reservations and measurement semantics'),'Shiyanjia Lab',t('v0.1 设计论文','v0.1 design paper')],
        [link('#presentation/9','OAHL'),t('节点、设备发现与会话占用','Nodes, discovery and exclusive sessions'),'fredabila/oahl',t('公开代码','Public code')],
    ]
    body=table([t('方案','Design'),t('主要解决的问题','Primary contribution'),t('维护者 / 来源','Maintainer / source'),t('材料形态','Artifact')],rows,'inventory')
    body+='<p class="small-note">'+t('这里选取九项设备接口与操作方案。完整目录另收录驱动、实验框架和研究系统，共 73 项工程资料。三个 Open-MHS 各自维护，MHP 指 Cuntinum 项目。','These nine designs focus on device interfaces and operation. The full catalogue contains 73 projects, including drivers, experiment frameworks and research systems. The three Open-MHS projects have separate maintainers. MHP here means Cuntinum’s project.')+'</p>'
    add('designs','designs',t('九项代表方案及各自解决的问题','Nine designs and the problems they address'),t('方案全表','Design inventory'),body,('mhs','aip','openmhp','lap','oahl'))

    # 04: MHS anatomy, not sponsor praise.
    body='<div class="split"><div class="system-drawing">'+entity(t('人 / Agent / 自动化程序','People / agents / automation'),'MCP · CLI · API','top')+'<div class="connector">↓</div>'+entity(t('共同设备接口','Shared device interface'),t('发现设备 · 读状态 · 写控制量','Discover devices · Read state · Write controls'),'core')+'<div class="driver-grid">'+entity(t('激光器驱动','Laser driver'),t('功率、开关','Power, enable'))+entity(t('转台驱动','Stage driver'),t('角度、位置','Angle, position'))+entity(t('相机驱动','Camera driver'),t('曝光、图像','Exposure, image'))+'</div><div class="device-strip">'+t('物理设备与各自的编程接口','Physical devices and their programming interfaces')+'</div></div><div>'+note(t('定义','Definition'),t('MHS（Model Hardware Standard）用共同驱动接口描述和操作设备。说明标签补充物理特性、使用知识及操作条件。','MHS (Model Hardware Standard) exposes devices through shared drivers. Description tags add physical characteristics, operating knowledge and conditions.'))+note(t('改变了什么','What changes'),t('驱动处理厂商接口差异。Agent 可从 MCP、命令行或 API 调用设备，也可将多仪器动作写成持续执行的程序。','Drivers translate vendor interfaces. Agents use MCP, CLI or APIs, and can compose commands into programs that coordinate multiple instruments.'))+note(t('在扫描中','In the scan'),t('找到能旋转波片的轴和能读取光功率的通道，再通过共同接口操作。','Find an axis that rotates the plate and a channel that measures optical power, then operate both through a common interface.'))+'</div></div>'
    body+=insight(t('IOP 可沿用能力描述与驱动映射，让同一实验方法使用不同型号的仪器。','IOP can reuse capability descriptions and driver mappings so one method can work with different instrument models.'))
    add('mhs','designs',t('MHS：把不同设备接到共同能力接口','MHS: a shared capability interface for heterogeneous devices'),'MHS',body,('mhs','mhs-site'),t('Anthropic × HHMI Janelia · 研究预览','Anthropic × HHMI Janelia · Research preview'))

    # 05: the four implementations have different engineering choices.
    body=table([t('独立项目','Independent project'),t('实现的组织方式','Implementation structure'),t('具体区别','Concrete distinction')],[
        [link('#projects/open-mhs-abenor','Open-MHS · Abenor Labs'),t('能力标签 → 设备基类 → 传输驱动','Capability tags → device base class → transport'),t('标签随设备提供。读写检查集中在运行层。支持生成设备说明。','Device-owned tags; centralized read/write checks; generated device documentation.')],
        [link('#projects/open-mhs-tong','Open MHS · tongriyaotxt'),t('设备注册 → 命令分派 → 运动技能','Registry → command dispatch → motion skills'),t('在读写之上增加机器人技能，把连续动作交给本地控制。','Robot skills add local continuous control above individual reads and writes.')],
        [link('#projects/open-mhs-scut','Open MHS · SCUT-ESA'),t('共同接口 → 显式后端 → VISA 仪器','Common interface → explicit backend → VISA instrument'),t('分别管理实机、实验性与模拟后端。维护者列出两款 UNI-T 仪器的实机记录。','Separates hardware, experimental and simulated backends; reports hardware work with two UNI-T models.')],
        [link('#projects/mhp-cuntinum','MHP · Cuntinum'),t('discover / read / write / execute<br>+ State Bus','discover / read / write / execute<br>+ State Bus'),t('以四类原语组织 SDK 和驱动，用共享状态组织设备协作。包名 khp。','Four primitive families organize SDKs and drivers; a shared state bus supports coordination. Package: khp.')],
    ])
    body+=insight(t('共同点是“能力—驱动”映射。差异在状态共享、动作组织和设备后端。选择依据应落实到所需设备与操作。','The common mechanism is capability-to-driver mapping. State sharing, action composition and device backends distinguish the implementations.'))
    add('implementations','designs',t('Open-MHS 与 MHP：四个项目的实现差异','Open-MHS and MHP: four implementation choices'),t('Open-MHS 与 MHP','Open-MHS and MHP'),body,('abenor','tong','scut','cuntinum'),t('三个 Open-MHS 独立维护。Cuntinum MHP 为另一项目','Three independently maintained Open-MHS projects; Cuntinum MHP is a separate project'))

    # 06: persistent state, resource declarations, observation provenance.
    body='<div class="split"><div class="system-drawing">'+entity(t('客户端请求','Client request'),'read · write · ramp · act','top')+'<div class="connector">↓</div><div class="runtime-box"><h3>'+t('常驻仪器服务','Persistent instrument service')+'</h3><div>'+entity(t('物理量 / 操作 / 持续活动','Quantity / action / activity'),t('单位、参数、进度、完成条件','Units, parameters, progress, completion'))+entity(t('资源与状态','Resources and state'),t('操作影响什么 · 活动占用什么','Operation effects · Activity resources'))+'</div></div><div class="connector">↓ ↑</div>'+entity(t('型号驱动与通信连接','Model driver + communication channel'),t('下发操作。读取实际状态','Issue operations; read actual state'))+'</div><div>'+note(t('定义','Definition'),t('AIP（Agent–Instrument Protocol）把仪器连接、长活动与执行记录放进持续运行的服务。客户端提交工作并查询结果。','AIP places device connections, long-running activities and execution records in a persistent service. Clients submit work and retrieve results.'))+note(t('关键区别','Key distinction'),t('分别记录请求受理和实际完成。每项操作说明会影响哪些资源。读数注明来自仪器、驱动保存的状态，还是计算推得。','Acceptance and physical completion have separate records. Operations declare affected resources. Readings identify device reports, driver-maintained state or calculated values.'))+note(t('在扫描中','In the scan'),t('转台移动期间，服务持续跟踪到位条件。调用者离开后，活动和观测仍有明确身份。','The service tracks arrival while the stage moves. Activities and observations retain identities beyond the initiating call.'))+'</div></div>'
    body+=insight(t('IOP 可沿用常驻服务、资源声明与操作事件，让实验在多次调用之间持续运行。','IOP can reuse persistent execution, resource declarations and operation events so experiments continue across client calls.'))
    add('aip','designs',t('AIP：常驻服务与持续操作','AIP: persistent services and ongoing operations'),'AIP',body,('aip',),t('Agent–Instrument Protocol · 用户提供的 PRD v1.1','Agent–Instrument Protocol · Supplied PRD v1.1'))

    # 07: the public specification's actual object and method names.
    body='<div class="split"><div class="package-diagram"><div><b>DEVICE.md</b><span>'+t('身份、摘要、操作说明','Identity, summary and instructions')+'</span></div><div><b>descriptor.yaml</b><span>signals · settings · actions</span></div><div><b>driver.py</b><span>'+t('读写与动作的设备实现','Device implementation of reads, writes and actions')+'</span></div><div><b>references / scripts / methods</b><span>'+t('知识材料、过程脚本与方法参数','References, procedures and method parameters')+'</span></div></div><div>'+note(t('定义','Definition'),t('OpenMHP 用设备包把操作说明、机器可读描述与驱动放在一起，再以统一请求操作设备。','OpenMHP packages instructions, machine-readable descriptions and drivers, then exposes devices through common requests.'))+note(t('执行路径','Execution path'),'<code>device/describe</code> → '+t('选择能力','select capabilities')+' → '+t('读取 / 写入 / 调用动作','read / write / invoke')+' → '+t('查询任务和运行文件','inspect jobs and run files'))+note(t('关键区别','Key distinction'),t('每个服务管理一个逻辑设备，长动作作为任务执行。实验脚本可后台运行，并将数据文件关联到 run。设备描述按需读取。','A server owns one logical device and runs long actions as jobs. Experiment scripts can run in the background and link files to a run. Descriptions load on demand.'))+'</div></div>'
    body+=insight(t('IOP 可沿用设备包的组织方式，将操作说明、驱动、方法与运行数据相互关联。','IOP can reuse the device-package structure to connect instructions, drivers, methods and run data.'))
    add('openmhp','designs',t('OpenMHP：让设备说明、驱动与运行记录相互关联','OpenMHP: connect descriptions, drivers and run records'),'OpenMHP',body,('openmhp','openmhp-devices'),t('规范草案与 Python 实现 · 参考设备主要在数字孪生环境运行','Draft specification and Python code · Reference devices primarily run in digital twins'))

    # 08: four physical-world primitives, named accurately and concisely.
    body='<div class="lap-contract">'+entity('InstrumentCard',t('能力、设备身份与物理限制','Capabilities, identity and physical limits'))+'<span>↓</span>'+entity(t('Reservation + task','Reservation + task'),t('设备 / 样品占用，任务状态与参数绑定的执行确认','Device/sample reservation, task state and task-bound confirmation'),'core')+'<span>↓</span>'+entity('MeasurementResult',t('数值、单位、校准、不确定度与来源','Values, units, calibration, uncertainty and provenance'))+'</div>'
    body+='<div class="split equal">'+note(t('定义','Definition'),t('LAP（Lab Agent Protocol）沿用 A2A 的设备发现与任务结构，增加仪器说明、资源预约、操作确认和测量结果。','LAP (Lab Agent Protocol) extends A2A discovery and tasks with instrument descriptions, reservations, operation confirmation and measurement results.'))+note(t('在扫描中','In the scan'),t('取得转台与探测器的使用权。提交扫描任务。返回带角度单位、探测器校准信息及测量来源的结果。','Reserve the stage and detector, submit a scan task, and return results with angle units, detector calibration and measurement provenance.'))+'</div>'
    body+=insight(t('IOP 可沿用任务与结果的关联：测量值同时说明单位、校准、不确定度及产生条件。','IOP can link each task to results that carry units, calibration, uncertainty and acquisition conditions.'))
    add('lap','designs',t('LAP：资源预约、任务与测量结果','LAP: reservations, tasks and measurement results'),'LAP',body,('lap',),t('Shiyanjia Lab · LAP v0.1 设计论文','Shiyanjia Lab · LAP v0.1 design paper'))

    # 09: a topology rather than a capabilities buzzword list.
    body='<div class="split"><div class="system-drawing">'+entity(t('调用者','Caller'),'JavaScript / Python SDK','top')+'<div class="connector">↓</div>'+entity(t('本地节点 / 可选注册与中继','Local node / optional registry and relay'),t('发现能力与节点地址','Find capabilities and node addresses'),'core')+'<div class="connector">↓</div>'+entity(t('会话管理 → 设备适配器 → 传输','Session → adapter → transport'),'Serial · ADB · MQTT · TCP')+'<div class="device-strip">'+t('节点所在位置的真实设备','Physical equipment attached to the node')+'</div></div><div>'+note(t('定义','Definition'),t('OAHL（Open Agent Hardware Layer）把设备暴露为节点中的能力，调用者通过会话取得使用权，再由适配器和传输插件执行。','OAHL exposes capabilities through hardware nodes. Callers reserve sessions; adapters and transport plugins perform the operation.'))+note(t('它重点解决什么','Primary problem'),t('节点提供设备地址与能力，会话安排设备使用权。README 展示了通过 ADB 操作手机。IOP 可借鉴节点发现和会话管理。','Nodes expose device locations and capabilities. Sessions allocate access. The README demonstrates ADB control of a phone. IOP can reuse node discovery and session management.'))+'</div></div>'
    body+=flow([('discover',t('找到设备','Find equipment')),('reserve',t('取得会话','Acquire a session')),('execute',t('执行能力','Run a capability')),('release',t('释放占用','Release the resource'))])
    add('oahl','designs',t('OAHL：设备节点与使用会话','OAHL: hardware nodes and access sessions'),'OAHL',body,('oahl',),t('MIT · 节点、SDK 与传输插件','MIT · Nodes, SDKs and transport plugins'))

    # 10: one hierarchy, one criterion. No second taxonomy of the 73 records.
    families=[
        ('A',t('设备能力模型','Device capability models'),'MHS · Open-MHS × 3 · MHP',t('设备能做什么？','What can the device do?'),t('共同描述 + 驱动映射','Shared description + driver mapping'),t('仪器说明：知识、能力与操作','Descriptions: knowledge, capabilities and operations'),'#presentation/4'),
        ('B',t('操作执行与结果定义','Execution and result definitions'),'AIP · OpenMHP · LAP',t('怎样执行，怎样取得结果？','How does it execute and return results?'),t('任务状态 + 资源 + 观测','Task state + resources + observations'),t('常驻服务、实验程序与记录','Runtime, experiment programs and records'),'#presentation/6'),
        ('C',t('设备发现与资源协作','Discovery and resource coordination'),'OAHL',t('设备在哪里，由谁使用？','Where is it, and who can use it now?'),t('发现 + 会话 + 访问路径','Discovery + sessions + access paths'),t('常驻服务：注册、占用与连接','Runtime: registration, reservations and connections'),'#presentation/9'),
    ]
    body='<div class="island-headings"><span>'+t('一级 · 具体方案','I · Existing designs')+'</span><span>'+t('二级 · 共同机制','II · Shared mechanisms')+'</span><span>'+t('对 IOP 的贡献','Contribution to IOP')+'</span></div><div class="island-map">'
    for id,name,examples,question,mechanism,objects,href in families:
        body+='<div class="island-row tone-'+id+'"><a class="island-origin" href="'+href+'">'+examples+'</a><div class="island-mechanism"><span class="island-letter">'+id+'</span><h3>'+name+'</h3><p>'+question+'</p><b>'+mechanism+'</b></div><div class="island-output">'+objects+'</div></div>'
    body+='</div><p class="figure-caption">'+t('按主要贡献归为三个岛屿，同一方案可以包含多类机制。它们共同用于组织 IOP 的四个部分：仪器说明、常驻服务、实验程序、实验记录。','These families group primary contributions and can overlap within a design. Together they inform four IOP components: instrument descriptions, a persistent service, experiment programs and records.')+'</p>'
    add('islands','mechanisms',t('已有方案的三类共同机制','Three shared mechanisms across existing designs'),t('三级关系全图','The complete hierarchy'),body,('mhs','aip','openmhp','lap','oahl'),t('由具体设计归纳','Synthesis of the reviewed designs'))

    # 11: interaction among islands, keeping the same physical example.
    body='<div class="mechanism-trace"><div class="trace-row"><span class="island-letter">C</span><div><h3>'+t('取得可用设备','Acquire available equipment')+'</h3><p>'+t('按旋转轴与功率测量能力找到设备，建立会话，确认资源占用。','Find rotational and power-measurement capabilities, establish a session and reserve resources.')+'</p></div><code>'+t('设备身份 + 可访问端点','identity + endpoint')+'</code></div><div class="trace-row"><span class="island-letter">A</span><div><h3>'+t('建立操作的共同含义','Establish shared operation meanings')+'</h3><p>'+t('把转台位置定义为半波片角度 θ。把探测器通道定义为光功率 P。','Define the stage position as plate angle θ and the detector channel as optical power P.')+'</p></div><code>'+t('能力 + 单位 + 轴零点','capability + unit + origin')+'</code></div><div class="trace-row"><span class="island-letter">B</span><div><h3>'+t('执行并保存物理结果','Execute and retain physical results')+'</h3><p>'+t('每点设角、确认到位、采集功率。将实际读数与同一次 run 关联。','Set each angle, confirm arrival and acquire power; associate actual readings with the same run.')+'</p></div><code>run → observations</code></div></div>'
    body+=insight(t('三类机制在一次实验中共同工作。能力说明供程序选择设备，服务安排使用与执行，测量记录保存实际结果。','All three mechanisms contribute to an experiment. Descriptions guide device selection, services arrange access and execution, and measurement records retain the results.'))
    add('mechanism-composition','mechanisms',t('同一次扫描中的三类机制','Three mechanisms in one polarization scan'),t('机制怎样协作','How mechanisms connect'),body,status=t('偏振扫描 · 机制组合','Polarization scan · Mechanism composition'))

    # 12: standards are not just logos. Separate information model from binding.
    body=table([t('既有基础','Existing foundation'),t('它已经提供的对象','Objects it already provides'),t('IOP 可映射的部分','What IOP can map')],[
        ['SiLA 2','Feature · Command · Property',t('能力集合、属性读取、命令与可观测执行。把仪器类语义映射到这些交互。','Capability sets, property access, commands and observable execution. Map instrument-class semantics onto these interactions.')],
        ['OPC UA / LADS','Device · FunctionalUnit · ProgramManager',t('仪器与功能单元、程序及结果管理。复用设备信息模型与状态。','Devices, functional units, program and result management. Reuse information models and device state.')],
        ['W3C WoT','Thing Description · Property · Action · Event',t('把能力描述与具体通信绑定分开。IOP 操作可对应 Action，观测可对应 Property / Event。','Separate capability descriptions from transport bindings. Map operations to Actions and observations to Properties or Events.')],
    ])
    body+='<div class="interface-ribbon"><b>'+t('调用入口','Client entry points')+'</b><span>MCP · API · CLI · '+t('人工界面','Human UI')+'</span><p>'+t('共享操作模型。入口选择由使用场景决定。','Share the operation model; choose an interface for the use case.')+'</p></div>'
    add('foundations','mechanisms',t('共同语义可以复用已有设备标准','Shared semantics can build on existing device standards'),t('既有标准的位置','Where existing standards fit'),body,('sila','lads','wot'),t('接口映射设计','Interface mapping design'))

    # IOP system design: four components connected by one platform service.
    body='<div class="iop-system-four"><div class="iop-program"><span class="component-index">03</span><h3>'+t('实验程序','Experiment programs')+'</h3><p>'+t('人 / Agent 提交方法、步骤依赖与参数。服务接管执行','People and agents submit methods, dependencies and parameters; the service executes them')+'</p></div><div class="iop-contract"><span class="component-index">01</span><h3>'+t('仪器说明','Instrument descriptions')+'</h3><p>'+t('原理与使用知识<br>能力、单位与操作<br>资源、影响与完成条件','Principles and operating knowledge<br>Capabilities, units and operations<br>Resources, effects and completion')+'</p></div><div class="iop-runtime"><span class="component-index">02</span><h3>'+t('常驻服务','Persistent service')+'</h3><p>'+t('设备注册与连接<br>依赖和资源调度<br>执行、状态与事件','Device registration and connections<br>Dependency and resource scheduling<br>Execution, state and events')+'</p></div><div class="iop-records"><span class="component-index">04</span><h3>'+t('实验记录','Experiment records')+'</h3><p>'+t('研究、实验与运行身份<br>操作、观测和原始数据<br>版本、条件与来源','Project, experiment and run identity<br>Operations, observations and raw data<br>Versions, conditions and provenance')+'</p></div><div class="iop-hardware">'+t('平台上的真实设备：转台 · 功率计 · 相机 · 激光器 · 其他已注册仪器','Physical platform: stages · power meters · cameras · lasers · other registered instruments')+'</div></div>'
    body+=insight(t('仪器说明回答怎么用，实验程序决定做什么，常驻服务组织执行，实验记录保存发生了什么。','Descriptions explain how to use equipment. Programs specify the experiment. The persistent service executes it. Records preserve what happened.'))
    add('system','iop',t('IOP 的四个组成部分','The four components of IOP'),t('IOP 四部分','Four IOP components'),body,status=t('IOP 总体架构设计','IOP system architecture design'))

    body='<div class="split daemon-layout"><div class="system-drawing">'+entity(t('人 / Agent 的实验程序','Experiment programs from people and agents'),t('提交实验 · 调用操作 · 订阅状态 · 查询结果','Submit experiments · Invoke operations · Watch state · Retrieve results'),'top')+'<div class="connector">↓ ↑</div><div class="daemon-core"><h3>'+t('平台常驻服务','Persistent platform service')+'</h3><p>'+t('统一的设备所有权与执行入口','One authority for device access and execution')+'</p><div class="daemon-functions"><span>'+t('设备与能力注册表','Device and capability registry')+'</span><span>'+t('依赖 / 资源调度器','Dependency / resource scheduler')+'</span><span>'+t('活动状态与事件记录','Activity state and event records')+'</span></div></div><div class="connector">↓ ↑</div><div class="driver-grid">'+entity(t('转台驱动','Stage driver'),t('位置与运动','Position and motion'))+entity(t('功率计驱动','Meter driver'),t('配置与采集','Settings and acquisition'))+entity(t('相机驱动','Camera driver'),t('曝光与图像','Exposure and images'))+'</div></div><div>'+note(t('注册与连接','Registration and connections'),t('单台或多台仪器都可注册到平台服务，提供设备身份、驱动、说明和连接地址。驱动管理各自设备的连接与读写。','One device or many can register with a platform service, supplying an identity, driver, description and endpoint. Drivers handle connections and device commands.'))+note(t('常驻与执行','Persistent execution'),t('服务持续运行并管理实验工作进程。每次运行有 run_id。调用者断开后实验继续，重新连接可查询进度和结果。','The service stays active and manages experiment workers. Each run has a run_id. Experiments continue after a caller disconnects and remain available on reconnection.'))+note(t('多平台协作','Multiple platforms'),t('服务内部可使用多个进程。多个平台各有自己的服务，通过服务间通信协调实验，每台设备由所属平台管理。','A service may use several processes. Each platform has its own service, and services coordinate experiments while retaining local device management.'))+'</div></div>'
    body+=insight(t('Runtime 指实验运行系统。常驻服务由持续运行的守护进程承载，可管理一台仪器或整个平台。','The runtime executes experiments. Persistent daemon processes host its service and manage device access.'))
    add('daemon','iop',t('常驻服务：从单台仪器到实验平台','Persistent service: one device or a whole platform'),t('常驻服务与设备','Service and devices'),body,status=t('IOP 平台服务设计','IOP platform service design'))

    # A real dependency join, rather than an unqualified promise of concurrency.
    nodes=[(25,115,145,65,t('扫描点 θ','Scan point θ'),t('建立操作实例','Create operations')),
           (235,25,255,80,t('A · 转动波片并确认到位','A · Move and confirm arrival'),t('占用转轴与光路','Own axis and optical path')),
           (235,190,255,80,t('B · 设置探测器参数','B · Configure detector'),t('占用探测器配置资源','Own detector configuration')),
           (560,110,230,80,t('C · 采集透射功率','C · Acquire optical power'),t('等待 A、B 完成','Wait for A and B')),
           (855,110,125,80,t('观测入档','Record'),t('进入下一点','Next point'))]
    svg='<svg class="schedule-diagram" viewBox="0 0 1000 295" role="img" aria-label="'+t('转台移动和探测器配置可以并行。两者完成后才采集功率并记录结果','Stage movement and detector setup run in parallel. Acquisition follows both, then observations are recorded.')+'"><defs><marker id="schedule-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z"/></marker></defs><path class="schedule-edge" d="M170 147H200V65H235M200 147V230H235M490 65H525V150H560M490 230H525V150M790 150H855"/>'
    for i,(x,y,w,h,title,desc) in enumerate(nodes):
        svg+='<g class="schedule-node '+('join' if i==3 else '')+'"><rect x="'+str(x)+'" y="'+str(y)+'" width="'+str(w)+'" height="'+str(h)+'"/><text class="schedule-title" x="'+str(x+w/2)+'" y="'+str(y+31)+'" text-anchor="middle">'+title+'</text><text x="'+str(x+w/2)+'" y="'+str(y+58)+'" text-anchor="middle">'+desc+'</text></g>'
    svg+='</svg>'
    body='<div class="schedule-scroll">'+svg+'</div><div class="dispatch-rule">'+t('启动条件 = 前置步骤已完成 ＋ 所需物理资源与通信资源可用','Start when dependencies are complete and required physical and communication resources are available')+'</div><div class="scheduling-rules">'+note(t('独立操作并行','Independent work overlaps'),t('A 与 B 的资源兼容，可同时推进。C 依赖二者，按实际完成事件开始。','A and B use compatible resources and can overlap. C starts after both completion events.'))+note(t('冲突资源串行','Conflicting access is ordered'),t('同一转轴、共享光路或独占连接按资源规则排序。运动期间，其他可用设备继续工作。','Resource rules order access to a shared axis, optical path or exclusive connection. Other available devices continue while motion proceeds.'))+'</div>'
    body+='<p class="figure-caption">'+t('扫描点持续保留转轴、光路与探测器，直到采集完成。通信连接按实际通信区间占用。精确同步由设备时钟和硬件触发执行。','Reserve the axis, optical path and detector for the whole scan point. Hold connections during exchanges. Device clocks and hardware triggers perform precision synchronization.')+'</p>'
    add('scheduling','iop',t('依赖决定先后，资源决定能否并行','Dependencies set order; resources determine concurrency'),t('并行与串行调度','Parallel and sequential execution'),body,status=t('偏振扫描 · 操作依赖与资源声明','Polarization scan · Declared dependencies and resources'))

    code='''platform = IOP.connect("optics-bench-01")
run = platform.submit(
    project="polarization-study",
    package="polarization-scan@0.1",
    parameters={"angles_deg": [0, 15, 30, 45]}
)

for event in platform.watch(run.id):
    print(event)

result = platform.result(run.id)'''
    body='<div class="split equal"><div><span class="margin-label">'+t('调用者的程序','Caller program')+'</span><pre class="contract-code runtime-example"><code>'+E(code)+'</code></pre><div class="package-files"><b>'+t('实验包','Experiment package')+'</b><span>experiment.py · method.yaml · dependencies.lock</span></div></div><div>'+note(t('程序组织实验方法','The program expresses the method'),t('实验包声明能力需求、步骤依赖、循环和条件。服务选择已注册设备，安排工作进程执行程序。','Packages declare capabilities, dependencies, loops and conditions. The service selects registered devices and runs the program in managed workers.'))+note(t('服务组织实际执行','The service organizes execution'),t('所有设备操作经服务安排，驱动负责下发命令。数据拟合与分析可在客户端或工作进程中完成。','The service schedules device operations and drivers issue commands. Fitting and analysis may run in a client or an experiment worker.'))+note(t('调用者按需参与','Callers participate as needed'),t('人或 Agent 随时查询、分析、提交下一轮或请求停止。当前实验按已提交的方法持续运行。','People or agents inspect, analyze, submit another run or request a stop. The current experiment continues under its submitted method.'))+'</div></div>'
    body+=insight(t('实验包组织操作与分析。平台服务持续管理设备执行，Agent 根据结果安排下一轮实验。','Packages organize operations and analysis. The platform service manages device execution. Agents use the results to plan subsequent experiments.'))
    add('program','iop',t('实验程序与常驻服务的分工','Experiment programs and the platform service'),t('实验程序与服务接口','Programs and service interface'),body,status=t('IOP 客户端接口设计示例','Illustrative IOP client interface design'))

    body='<div class="provenance-chain"><div><span>project_id</span><b>'+t('研究项目','Research project')+'</b><p>'+t('研究目标与上下文','Research goal and context')+'</p></div><div><span>experiment_id</span><b>'+t('实验定义','Experiment definition')+'</b><p>'+t('方法、样品与变量','Method, sample and variables')+'</p></div><div><span>run_id</span><b>'+t('一次实际运行','A concrete run')+'</b><p>'+t('包版本、参数与设备','Package version, parameters, devices')+'</p></div></div><div class="record-branches"><div><b>operation_id</b><span>'+t('操作请求 → 下发 → 活动 → 结束事件','Request → dispatch → activity → terminal event')+'</span></div><div><b>observation / artifact</b><span>'+t('实际读回、时间、单位、校准与数据文件','Actual readback, time, units, calibration and data files')+'</span></div></div>'
    body+=table([t('何时记录','When'),t('自动关联的内容','Automatically linked information')],[
        [t('任务受理','At acceptance'),t('建立实验与运行记录，固定程序包、参数、驱动和说明版本。关联研究项目与调用者。','Create experiment/run records; fix package, parameters, driver and description versions; link the project and caller.')],
        [t('操作与观测','During operations'),t('先登记请求，再下发操作。进度、读数与文件关联到 operation_id 和 run_id。程序将分析结果与其输入数据一并提交。','Record requests before dispatch. Link progress, readings and files to operation_id and run_id. Programs submit analysis results with their input-data references.')],
        [t('结束与再连接','At completion or reconnection'),t('完成、失败、停止和部分结果都保留。服务重启后依据持久记录与设备读回核对未完成操作。','Retain completion, failure, stop and partial results. After a service restart, reconcile unfinished operations using durable records and device readback.')],
    ],'record-table')
    body+=insight(t('实验程序使用同一执行入口，服务就能持续建立“研究—实验—运行—操作—数据”的关联。','A shared execution entry point lets the service continuously link research, experiments, runs, operations and data.'))
    add('records','iop',t('实验过程与数据的自动记录','Automatic experiment and data records'),t('自动登记与全程留档','Registration and persistent records'),body,status=t('IOP 实验记录与恢复设计','IOP experiment records and recovery design'))

    # Definitions are reusable; run and operation identifiers name actual executions.
    body='<div class="reuse-banner"><b>method_id + version</b><span>'+t('同一方法可反复运行，每次运行包含多项操作','One method can run repeatedly. Each run contains individual operations.')+'</span></div>'
    body+=table([t('对象','Object'),t('保存什么','What it describes'),t('偏振扫描中的例子','Polarization-scan example')],[
        [t('仪器与操作说明','Instrument and operation descriptions'),t('设备身份、操作含义、参数、单位、完成条件与说明版本。','Device identity, operation meaning, parameters, units, completion conditions and version.'),t('转台 move_to 接受角度，完成时提供实际位置。','Stage move_to accepts an angle and reports the actual position at completion.')],
        [t('方法 method_id','Method: method_id'),t('可复用的实验步骤，引用所需操作定义和版本。','Reusable experimental steps that refer to operation definitions and versions.'),'optics.polarization_scan @ 0.1'],
        [t('实验运行 run_id','Experiment run: run_id'),t('一次提交，记录实验包、参数、样品与所用设备。','One submission, with its package, parameters, sample and equipment.'),t('今天对样品 S1 扫描 0°、15°、30°、45°。','Scan sample S1 at 0°, 15°, 30° and 45°.')],
        [t('操作实例 operation_id','Operation instance: operation_id'),t('本次运行中的一次实际操作，关联状态、事件与观测。','One actual operation within a run, linked to state, events and observations.'),t('第二点转到 15°，记录实际角度、时间与结束状态。','At point two, move to 15° and record position, time and completion.')],
    ],'identity-table')
    body+=insight(t('方法版本说明“按什么做”，run_id 标识“哪次实验”，operation_id 标识“哪次操作”。测量与数据文件沿这些关系保存。','The method version identifies the procedure, run_id the experiment execution, and operation_id an individual operation. Measurements and files retain those links.'))
    add('iop-model','iop',t('方法、实验运行与操作实例','Methods, experiment runs and operation instances'),t('定义与每次执行','Definitions and executions'),body,('operations',),t('IOP 对象与记录设计','IOP objects and records'))

    # 14: human and machine are views of the SAME definition.
    code="""method_id: optics.polarization_scan
version: 0.1
requires: {stage: rotation, meter: optical_power}
inputs: {angles_deg: [0, 15, 30, 45]}
context: [plate_axis_zero, wavelength, calibration_ref]
for_each: {angle: angles_deg}
point:
  reserve: [stage.axis, optical_path, meter]
  until: acquire.completed
  steps:
    - {id: move, use: stage.move_to, angle_deg: $angle}
    - {id: setup, use: meter.configure}
    - id: acquire
      after: [move, setup]
      use: meter.measure
  record: [move.angle_actual, acquire.power, acquire.time]"""

    body='<div class="split equal definition-pair"><div><span class="margin-label">'+t('人阅读的方法说明','Method instructions for people')+'</span><h3>'+t('偏振扫描','Polarization scan')+'</h3><p>'+t('每个角度先保留转轴、光路与探测器。转台移动与探测器配置可以同时进行，两者完成后采集功率。','Reserve the axis, optical path and meter at each angle. Move the stage while configuring the meter, then acquire power after both complete.')+'</p><dl><dt>'+t('角度','Angle')+'</dt><dd>'+t('单位为度。零点对应波片轴的标定位置。','Degrees relative to the calibrated plate-axis origin.')+'</dd><dt>'+t('功率','Power')+'</dt><dd>'+t('单位为瓦。记录工作波长与探测器校准引用。','Watts, with wavelength and a detector calibration reference.')+'</dd><dt>'+t('输出','Output')+'</dt><dd>'+t('保存实际角度、功率与采集时间，形成同一份扫描记录。','Actual angle, power and acquisition time in one scan record.')+'</dd></dl></div><div><span class="margin-label">'+t('程序读取的同一份定义','The same definition for software')+'</span><pre class="contract-code"><code>'+E(code)+'</code></pre></div></div>'
    body+=insight(t('文字与程序引用同一方法版本。转台“完成”的具体条件由操作说明给出，常驻服务等待设备返回到位状态。','Text and code refer to the same method version. The operation description defines settling, and the service waits for the device to report it.'))
    add('shared-definition','iop',t('同一实验方法的文字与程序表达','One experimental method for people and software'),t('方法说明与程序','Method description and program'),body,status=t('IOP 定义示意 · YAML','Illustrative IOP definition · YAML'))

    # 16: concrete compatibility boundaries, not a promise of universal support.
    body='<div class="reuse-banner"><b>optics.polarization_scan</b><span>'+t('同一个方法与结果格式','One method and result format')+'</span></div>'+table([t('IOP 要求','IOP requirement'),t('注册驱动 A','Registered driver A'),t('注册驱动 B','Registered driver B')],[
        [t('角度设定，单位 deg','Set angle in deg'),t('厂商 SDK：将角度转换为原生位置单位','Vendor SDK: convert angle to native position units'),t('EPICS：映射设定值通道和单位','EPICS: map setpoint channel and units')],
        [t('实际位置与到位条件','Actual position and settling'),t('读取编码器与运动状态','Read encoder and motion state'),t('映射读回及到位状态通道','Map readback and done-state channels')],
        [t('光功率，单位 W','Optical power in W'),t('SCPI / VISA：读取并统一单位','SCPI / VISA: query and normalize units'),t('已有采集服务：读取功率与时间','Acquisition service: read power and time')],
        [t('方法所需条件','Method requirements'),t('波长、轴零点、量程与校准引用','Wavelength, origin, range and calibration'),t('提供相同含义。缺失能力显式返回','Expose the same meanings; report missing capabilities')],
    ])
    body+=insight(t('兼容性落实到能力：输入含义相同、完成条件相同、结果可解释。传输方式与内部实现可以不同。','Compatibility is capability-specific: equivalent input meaning, completion criteria and interpretable results across different transports and implementations.'))
    add('compatibility','iop',t('已有设备接口如何接入 IOP','Connecting existing device interfaces to IOP'),t('怎样兼容现有系统','Compatibility with existing systems'),body,status=t('两种设备组合的适配设计','Adapter design for two equipment configurations'))

    # 18: an experimentally assessable end state; no meta-discussion of the medium.
    body='<div class="validation-map"><div class="common-method"><span>'+t('同一份操作定义与方法','One operation definition and method')+'</span><b>optics.polarization_scan</b></div><div class="parallel-setups"><div><b>'+t('平台常驻服务 A','Platform service A')+'</b><span>'+t('SDK 转台 + VISA 功率计','SDK stage + VISA power meter')+'</span></div><div><b>'+t('平台常驻服务 B','Platform service B')+'</b><span>'+t('控制系统转台 + 采集服务','Control-system stage + acquisition service')+'</span></div></div><div class="comparison-output"><b>'+t('可解释、可对照的扫描记录','Interpretable, comparable scan records')+'</b><span>angle_actual · power · time · calibration_ref · method_version</span></div></div>'
    body+='<div class="validation-criteria">'+note(t('语义一致','Consistent meaning'),t('同一角度定义、单位与方法条件。','Same angle definition, units and method conditions.'))+note(t('操作完成','Operation completion'),t('实际位置和运动状态确认转台到位。','Position and motion readback confirm that the stage has settled.'))+note(t('结果可解释','Interpretable results'),t('差异能追溯到设备、校准与实验条件。','Differences trace to devices, calibration and conditions.'))+'</div>'
    body+=insight(t('人和 Agent 使用同一实验入口。常驻服务统一执行与留档，同一方法可在不同设备组合上复用。','People and agents share an experiment interface. Persistent services execute and record reusable methods across equipment configurations.'))
    add('validation','iop',t('建设目标：同一方法在两个平台运行','Development goal: one method on two platforms'),t('跨平台的完整实验','A complete cross-platform experiment'),body,('operations',),t('建设目标 · 仓库现有基础：操作模型与模拟参考实现','Development target · Current foundation: operation model and simulated reference implementation'))
    return pages


def metadata(data):
    zh,en=content('zh'),content('en')
    assert [x['id'] for x in zh]==[x['id'] for x in en]
    slides=[]
    for a,b in zip(zh,en):
        slides.append({'id':a['id'],'chapter':a['chapter'],'title':pair(a['title'],b['title']),
            'short':pair(a['short'],b['short']),'status':pair(a['status'],b['status']),
            'body':pair(a['body'],b['body']),'sources':a['sources']})
    return {'schema_version':'2.2','updated':'2026-10-21','edition':'IOP-04',
        'name':'Instrument Operation Protocol','abbreviation':'IOP',
        'levels':{'1':'existing designs','2':'mechanism families','3':'IOP system design'},
        'chapters':CHAPTERS,'mechanism_families':ISLANDS,
        'system_components':[
            {'id':'instrument-descriptions','name':pair('仪器说明','Instrument descriptions')},
            {'id':'runtime','name':pair('常驻服务','Persistent service')},
            {'id':'programs','name':pair('实验程序','Experiment programs')},
            {'id':'records','name':pair('实验记录','Experiment records')}],
        'runtime_design':{'meaning':'experiment execution system hosted by persistent service processes',
            'scope':'one authority per experimental platform',
            'dispatch':'declared dependencies complete and compatible physical/communication resources available',
            'ownership':'service-managed device connections and experiment workers',
            'records':['project_id','experiment_id','run_id','operation_id','observation','artifact']},
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
        slides.append(f'<article class="deck-slide" data-slide="{i}" data-slide-id="{s["id"]}" data-chapter="{s["chapter"]}" aria-label="{i}. {E(s["title"][lang])}"><header><div class="slide-meta"><span>{E(chapter_names[s["chapter"]])}</span><span>{i:02} / {len(d["slides"]):02}</span></div><h2>{s["title"][lang]}</h2></header><div class="deck-body">{s["body"][lang]}</div><footer><span>{E(s["status"][lang]) or "AI4Instruments · IOP"}</span><div class="deck-refs">{refs}</div></footer></article>')
    tabs=''.join('<a data-chapter-nav="'+c['id']+'" href="#presentation/'+str(c['start'])+'">'+E(c['name'][lang])+'</a>' for c in CHAPTERS)
    options=''.join('<option value="'+str(i)+'">'+f'{i:02}　'+E(s['short'][lang])+'</option>' for i,s in enumerate(d['slides'],1))
    outline=''.join('<a data-page-nav="'+str(i)+'" data-page-chapter="'+s['chapter']+'" href="#presentation/'+str(i)+'"><span>'+f'{i:02}'+'</span>'+E(s['short'][lang])+'</a>' for i,s in enumerate(d['slides'],1))
    return f'''<section class="view" id="view-presentation" data-view="presentation"><div class="deck-shell" id="deck-shell"><nav class="chapter-tabs" aria-label="{t('论述结构','Argument structure')}">{tabs}</nav><div class="deck-workspace"><nav class="chapter-outline" aria-label="{t('本章内容','Chapter contents')}">{outline}</nav><div class="deck-reading"><div class="deck-stage" id="deck-stage">{''.join(slides)}</div><div class="deck-controls"><button id="deck-prev" aria-label="{t('上一页','Previous page')}">←</button><label class="sr-only" for="deck-select">{t('选择页面','Select a page')}</label><select id="deck-select">{options}</select><button id="deck-next" aria-label="{t('下一页','Next page')}">→</button><span id="deck-position" aria-live="polite"></span><button id="deck-focus">{t('展开','Expand')}</button><button id="deck-fullscreen">{t('全屏','Fullscreen')}</button><button id="deck-exit" hidden>{t('还原','Restore')}</button></div></div></div></div><dialog id="island-detail"><div class="section-line"><h2 id="island-detail-title"></h2><button id="island-close">{t('关闭','Close')}</button></div><p id="island-detail-question"></p><div id="island-detail-projects"></div></dialog></section>'''
