"""IOP presentation: a curated reading hierarchy over the research catalogue."""
import html


def pair(zh, en):
    return {'zh': zh, 'en': en}


GROUPS = [
    {'id': 'understand', 'name': pair('仪器知识与能力描述', 'Instrument knowledge and capabilities'),
     'short': pair('理解仪器', 'Understand'), 'color': '#a6803a',
     'question': pair('仪器能做什么，这些能力意味着什么？', 'What can an instrument do, and what does each capability mean?'),
     'routes': ['knowledge', 'contract']},
    {'id': 'execute', 'name': pair('设备接入与操作执行', 'Device access and operation execution'),
     'short': pair('执行操作', 'Execute'), 'color': '#39796e',
     'question': pair('怎样让操作在真实设备上完成，并获得读回？', 'How does an operation run on real equipment and return observations?'),
     'routes': ['bridge', 'runtime', 'development', 'gui']},
    {'id': 'experiment', 'name': pair('实验方法与闭环组织', 'Experimental methods and feedback'),
     'short': pair('组织实验', 'Experiment'), 'color': '#74719b',
     'question': pair('怎样组合操作，并根据观测决定下一步？', 'How are operations composed, and how do observations guide the next step?'),
     'routes': ['workflow', 'experiment']},
]

# Titles make the argument; notes provide the detail for a speaker or a reader.
SLIDES = [
    ('purpose', pair('IOP：让仪器知识与操作相互对应', 'IOP connects instrument knowledge with operation'),
     pair('Instrument Operations Protocol · 仪器操作协议', 'Instrument Operations Protocol'),
     pair('从一台仪器开始：知道它为什么这样工作、哪些变量可控可测、怎样执行一个方法，以及怎样解释观测。人和 Agent 使用同一套定义，通过各自适合的入口访问。', 'Begin with an instrument: its physical principles, controllable and observable variables, executable methods and interpretation of observations. People and agents use the same definitions through appropriate interfaces.')),
    ('scope', pair('73 条工程记录，与标准材料分别收录', 'Projects and standards use separate inventories'),
     pair('MHS 和 AIP 在标准与设计材料中，均未计入 73 条工程记录', 'MHS and AIP are in the standards and design collection, outside the 73 project records'),
     pair('73 是本资料库工程与研究条目的数量，不是全网协议总数。14 组标准与基础生态中包含 MHS 和 AIP。维护主体、关系和来源是不同维度，不能与项目数量相加。', 'The 73 entries are projects and research artifacts in this collection, not a worldwide protocol count. The 14 standards and foundation groups include MHS and AIP. Actors, relationships and sources count different things and cannot be added to projects.')),
    ('islands', pair('具体工作，归入八条路线与三个部分', 'Specific work, eight approaches, three responsibilities'),
     pair('一级：具体工作　　二级：方法路线　　三级：系统分工', 'Level 1: individual work   Level 2: approaches   Level 3: system responsibilities'),
     pair('这是按主要贡献建立的人工分类，用于理解与讲解。一个工程可以跨越多个部分。主归属使计数不重复，具体接入关系仍在来源图谱中。三个部分共同构成 IOP 的建设范围，不代表三种协议或成熟度等级。点击路线可以展开全部项目。', 'This is an editorial classification by primary contribution. A project may span several responsibilities. A primary assignment avoids double counting; the sourced graph separately records actual integrations. The three responsibilities organize IOP development, not three protocols or maturity levels. Select an approach to inspect every assigned project.')),
    ('knowledge', pair('知识解释能力，契约明确操作含义', 'Knowledge explains capabilities; contracts define operations'),
     pair('第一部分：仪器知识与能力描述', 'Responsibility A: instrument knowledge and capabilities'),
     pair('知识材料提供原理、使用条件、方法与经验。能力契约把其中需要执行的部分写成明确的参数、物理量、前置条件和结果定义。人读说明，程序读结构，二者引用相同的操作身份和版本。OpenMHP 是公开契约样本，device-skills 是配套知识样本。', 'Knowledge resources explain principles, conditions, methods and experience. Capability contracts make parameters, quantities, preconditions and result meanings explicit. Human documentation and programmatic descriptions refer to the same operation identity and version. OpenMHP illustrates public contracts; device-skills illustrates supporting knowledge.')),
    ('execution', pair('接入、执行与设备开发各有职责', 'Access, execution and device development have distinct roles'),
     pair('第二部分：设备接入与操作执行', 'Responsibility B: device access and operation execution'),
     pair('桥接把已有接口暴露给调用者。常驻运行环境持有设备连接和执行状态。仪器开发涉及固件、调试与可编程能力的形成。GUI 路线用于已有软件缺少可用接口的情况。四者互补，不能用工具数来比较整体能力。', 'Bridges expose existing interfaces. Persistent runtimes own connections and execution state. Instrument development creates or changes programmable capabilities through firmware and debugging. GUI access serves software without a usable programmatic interface. These roles are complementary; tool counts do not measure their overall capability.')),
    ('methods', pair('方法组织执行，实验决策使用反馈', 'Methods organize execution; decisions use feedback'),
     pair('第三部分：实验方法与闭环组织', 'Responsibility C: experimental methods and feedback'),
     pair('过程编排解决设备、样品、资源与步骤之间的关系。实验决策根据结果提出或选择下一步。Uni-Lab-OS 是多设备编排样本，AILA 是真实 AFM 实验样本。IOP 应使过程与观测可表达、可复用，研究目标和决策策略由研究系统持有。', 'Workflow orchestration handles devices, samples, resources and dependencies. Experimental decision systems use observations to choose or propose the next step. Uni-Lab-OS illustrates multi-device workflows; AILA illustrates physical AFM experiments. IOP should make procedures and observations reusable while research systems retain objectives and decision policies.')),
    ('mhs', pair('MHS、AIP 与 OpenMHP 提供不同的参照', 'MHS, AIP and OpenMHP serve different reference roles'),
     pair('分别比较产业协作、设计思想和公开实现', 'Compare ecosystem participation, design ideas and public implementation separately'),
     pair('MHS 是 Anthropic 与 HHMI Janelia 发起的研究预览，公开材料列出科学机构与设备厂商的试用和集成计划，因此值得重点跟踪生态发展。它的发布主体不能单独证明技术覆盖或规模第一。AIP 是用户提供的设计材料。OpenMHP 是独立的公开规范与实现，当前设备包主要以孪生测试为证据。', 'MHS is a research preview initiated by Anthropic and HHMI Janelia. Public materials describe trials and integration plans across research groups and vendors, making it important to track for ecosystem development. Sponsorship alone does not establish technical or deployment leadership. AIP is a supplied design document. OpenMHP is an independent public specification and implementation with primarily twin-tested device packages.')),
    ('representatives', pair('汇报围绕五个问题选择代表工作', 'Five questions organize the representative work'),
     pair('选择依据是对 IOP 的建设作用', 'Selection follows the decisions needed to build IOP'),
     pair('这五项不是全球排名。MHS 帮助观察跨机构生态，OpenMHP 提供可检查的契约样本，Osprey 展示既有设施的语义接入，Uni-Lab-OS 展示多设备流程，AILA 展示实机实验中的判断与反馈。其余条目按设备和实现需要查询。', 'These five entries are not a global ranking. MHS informs ecosystem analysis, OpenMHP provides an inspectable contract, Osprey demonstrates semantic access to existing facilities, Uni-Lab-OS illustrates multi-device procedures, and AILA grounds decisions and feedback in physical experiments. Other records remain available for device selection and implementation.')),
    ('architecture', pair('IOP 用共同定义连接知识、执行与实验', 'IOP connects knowledge, execution and experiments through shared definitions'),
     pair('拟议架构：保留现有设备接口，统一操作与结果的含义', 'Proposed architecture: retain device interfaces and share operation and result meanings'),
     pair('共同定义至少连接设备身份、能力、物理量、操作、任务、观测与数据。知识材料解释这些对象，运行服务执行它们，方法库组合它们。API、CLI、MCP 和人工界面可以使用相同定义。驱动与适配层映射到现有控制系统。图示为设计方向，兼容性需要具体映射与实机验证。', 'Shared definitions connect device identity, capabilities, quantities, operations, jobs, observations and data. Knowledge explains them, services execute them and method libraries compose them. APIs, CLIs, MCP and human interfaces can share those definitions. Adapters map to existing control systems. This is a proposed design; compatibility requires concrete mappings and physical validation.')),
    ('composition', pair('操作可以从基本能力组合成实验工作流', 'Operations compose from basic capabilities into experimental workflows'),
     pair('Basic Operations · Standard Operations · Workflow Operations', 'Basic Operations · Standard Operations · Workflow Operations'),
     pair('这三种操作角色与三级阅读分类是两件事。基础操作表达控制或观测，标准操作表达有实验意义的可复用方法，工作流操作组织仪器、样品与决策。每一类操作都需要明确含义、可执行实现和结果记录。这里的 Standard 表示文档化的可复用方法，不是行业认证。', 'These operation roles differ from the three reading levels. Basic Operations express controls or observations. Standard Operations express reusable experimental methods. Workflow Operations organize instruments, samples and decisions. Every role needs meaning, execution and records. Standard denotes a documented reusable method, not industry certification.')),
    ('example', pair('一个偏振扫描，贯通整个结构', 'One polarization scan connects the whole design'),
     pair('设计示例：线偏振入射、半波片、固定检偏器与功率计', 'Design example: linear input, a half-wave plate, a fixed analyzer and a power meter'),
     pair('明确工作波长、波片轴零点、转台角度与读回、探测器校准和等待条件。方法逐点设角、等待稳定、读取实际角度和功率，并记录时间与采集条件。工作流可增加复测或比较不同条件。这个示例说明接口设计，不声称本仓库已完成这套实机实验。', 'Specify wavelength, wave-plate axis zero, stage angle and readback, detector calibration and settling conditions. The method sets each angle, waits, reads actual angle and power, and records time and acquisition conditions. A workflow may repeat measurements or compare conditions. This illustrates interface design, not an already completed hardware experiment in this repository.')),
    ('build', pair('从现有操作模型走向跨设备复用', 'From operations to reuse across devices'),
     pair('每一步交付一个可以使用的能力', 'Each step delivers a usable capability'),
     pair('当前仓库已经有操作模型与模拟参考实现。下一阶段先给具体仪器建立共同定义和人工可读说明，再连接真实设备，最后让同一方法跨设备实现运行。协议映射应记录已支持的能力和差异。生态建设来自真实设备包、可复用方法和共同维护，不以增加术语或仓库数量衡量。', 'The repository already contains an operation model and a simulated reference implementation. Next, define concrete instruments with readable documentation, connect real devices and run the same method through different implementations. Protocol mappings record supported capabilities and differences. Ecosystem development comes from usable device packages, methods and shared maintenance.')),
    ('reading', pair('演示讲清判断，资料库支持深入使用', 'The presentation explains decisions; the catalogue supports deeper work'),
     pair('按问题进入项目、标准、关系和来源', 'Explore projects, standards, relationships and sources by question'),
     pair('对公司讲清接入与复用成本，对课题组讲清可执行的方法，对科学家讲清物理含义与实验依据，对工程师讲清接口边界与适配方式。全部条目和来源保留在后续栏目中，演示不要求逐项朗读。', 'For a company, explain integration and reuse. For a research group, explain executable methods. For scientists, explain physical meaning and experimental evidence. For engineers, explain interfaces and mappings. The full catalogue remains available without requiring a presentation of every record.')),
]

PROTOCOL_GROUPS = [
    {'id': 'capabilities', 'name': pair('共同能力与设备驱动', 'Shared capabilities and drivers'),
     'question': pair('不同设备怎样用共同语言表达和调用？', 'How can different devices describe and expose capabilities consistently?'),
     'members': ['s:mhs', 'p:open-mhs-abenor', 'p:open-mhs-tong', 'p:open-mhs-scut', 'p:mhp-cuntinum']},
    {'id': 'jobs', 'name': pair('操作、任务与测量契约', 'Operations, jobs and measurement contracts'),
     'question': pair('一次真实操作怎样执行、跟踪并解释结果？', 'How is a physical operation executed, tracked and interpreted?'),
     'members': ['s:aip', 's:lap', 'p:openmhp']},
    {'id': 'access', 'name': pair('设备发现与资源访问', 'Device discovery and resource access'),
     'question': pair('怎样找到、取得和释放分布式设备资源？', 'How are distributed devices discovered, acquired and released?'),
     'members': ['p:oahl']},
]
PROTOCOL_PENDING = ['p:agent2device']
EXTRA_SLIDES = [
    ('protocols', pair('直接比较的十项接口与契约方案', 'Ten approaches to instrument interfaces'),
     pair('当前资料库中的比较集合，按主要设计重心分组', 'A comparison set from this collection, grouped by primary design emphasis'),
     pair('集合由 7 条工程记录与 3 条标准/设计材料组成：MHS、AIP、LAP、OpenMHP、三个独立 Open-MHS 工程、Cuntinum MHP、OAHL、Agent2Device。它不是十个同等成熟的标准。edge-mhs 属于相邻的边缘网关工程，MCP 属于通用 Agent 接口，均单独放回其职责位置。', 'The set combines seven project records and three standards/design references: MHS, AIP, LAP, OpenMHP, three independent Open-MHS projects, Cuntinum MHP, OAHL and Agent2Device. Their maturity differs. edge-mhs is an adjacent gateway project; MCP is a general agent interface. Both retain their separate roles.')),
    ('protocol-islands', pair('三个机制岛屿，形成 IOP 的共同结构', 'Three mechanism groups inform a shared IOP structure'),
     pair('一级是具体方案，二级是机制归纳，三级是我们的设计综合', 'Level 1: approaches   Level 2: mechanism groups   Level 3: our design synthesis'),
     pair('第一岛统一能力与驱动，第二岛统一操作、任务与结果，第三岛组织设备发现与资源访问。这是按公开设计进行的人工归纳，不是自动聚类或已存在的协议继承关系。OpenMHP 同时涉及资源发现，MHS 的公开范围也跨越执行与流程。Agent2Device 目前公开细节不足，保留为概念提案而不强行归类。三个岛帮助提出共同模型，还需要通过设备实现检验组合是否合理。', 'One group emphasizes capabilities and drivers, another operations, jobs and results, and a third discovery and resource access. This is an editorial synthesis of public designs, not automated clustering or a protocol inheritance tree. OpenMHP also addresses discovery, and MHS spans execution and workflows. Agent2Device remains a concept with insufficient public detail for mechanism assignment. The grouping guides a shared model whose composition must be exercised through device implementations.')),
    ('foundations', pair('已有规范为 IOP 提供可复用基础', 'Existing specifications provide reusable foundations'),
     pair('把已有设备语义、交互模型与 Agent 入口接起来', 'Connect existing device semantics, interaction models and agent interfaces'),
     pair('SiLA 2 提供 Feature、Command、Property 与可观测执行。OPC UA/LADS 提供设备信息模型、状态与程序管理。W3C WoT 分离设备交互描述和协议绑定。这些规范早于或独立于 LLM Agent，仍是关键基础。MCP 提供通用工具与资源入口。具体适配必须保留各自的物理含义和执行差异。', 'SiLA 2 provides features, commands, properties and observable execution. OPC UA/LADS supplies device information models, states and program management. W3C WoT separates interaction descriptions from protocol bindings. These specifications precede or are independent of LLM agents. MCP supplies general tool and resource access. Concrete mappings must preserve physical meaning and execution differences.')),
]
SLIDES[2:2] = EXTRA_SLIDES


def metadata(data):
    profiles = data['landscape']['profiles']
    routes = {r['id'] for r in data['landscape']['routes']}
    grouped = [r for g in GROUPS for r in g['routes']]
    assert set(grouped) == routes and len(grouped) == len(routes)
    groups = [{**g, 'projects': [p['id'] for p in profiles if p['route'] in g['routes']]} for g in GROUPS]
    assert sum(len(g['projects']) for g in groups) == len(data['catalogue']['projects'])
    return {'schema_version': '1.0', 'updated': '2026-10-21', 'name': 'Instrument Operations Protocol',
            'abbreviation': 'IOP', 'basis': 'editorial-classification', 'groups': groups,
            'levels': {'1': 'individual work', '2': 'contribution route', '3': 'system responsibility'},
            'context_placement': [
                {'id': 'mhs', 'record': 'context.standards', 'roles': ['understand', 'execute', 'experiment'], 'basis': 'announced-scope'},
                {'id': 'aip', 'record': 'context.standards', 'roles': ['understand', 'execute'], 'basis': 'supplied-design'}],
            'protocol_comparison': {'basis': 'editorial-classification', 'groups': PROTOCOL_GROUPS,
                'unassigned_concepts': PROTOCOL_PENDING,
                'selection': 'Seven instrument-contract projects plus MHS, AIP and LAP; adjacent gateways and general agent protocols are separate.'},
            'slides': [{'id': s[0], 'title': s[1], 'subtitle': s[2], 'notes': s[3]} for s in SLIDES]}


def render(data, lang):
    e = lambda x: html.escape(str(x), quote=True)
    t = lambda zh, en: zh if lang == 'zh' else en
    tx = lambda x: e(x[lang])
    D = data['presentation']; groups = D['groups']; profiles = data['landscape']['profiles']
    projects = {p['id']: p for p in data['catalogue']['projects']}
    routes = {r['id']: r for r in data['landscape']['routes']}
    a = lambda target, text: f'<a href="{e(target)}">{e(text)}</a>'
    p = lambda id: a('#projects/' + id, projects[id]['name'])
    s = lambda id, label: a('#standards/' + id, label)
    def card(title, body, tail='', cls=''):
        return f'<section class="deck-card {cls}"><h3>{title}</h3><p>{body}</p>{"<div class=deck-card-tail>"+tail+"</div>" if tail else ""}</section>'
    def conclusion(zh, en):
        return '<p class="deck-conclusion">'+e(t(zh,en))+'</p>'
    def table(headers, rows):
        return '<table class="deck-table"><thead><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+x+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
    bodies=[]
    bodies.append('<div class="deck-opening"><div class="iop-word">IOP</div><div class="deck-opening-copy"><p>'+t('人能够理解和学习<br>程序能够调用和组合<br>实验能够留下可解释的结果','People understand and learn<br>Programs invoke and compose<br>Experiments return interpretable results')+'</p></div></div><div class="deck-three">'+''.join(card(tx(g['short']),tx(g['question']),cls='island-'+g['id']) for g in groups)+'</div>')
    bodies.append('<div class="deck-two">'+card(t('工程与研究资料','Projects and research'),t('73 条记录，包含桥接、契约、运行环境、工作流及实验研究。','73 records: bridges, contracts, runtimes, workflows and research.'),a('#projects',t('打开工程目录','Open project directory')))+card(t('标准与基础生态','Standards and foundations'),t('14 组材料。MHS 是研究预览，AIP 是用户提供的设计材料。','14 groups, including MHS (preview) and AIP (supplied design).'),s('mhs','MHS')+' '+s('aip','AIP'))+'</div>'+table([t('另行统计','Separate counts'),t('含义','Meaning')],[['70',t('维护者与标准主体，包括个人账号和组织','Maintainers and standards actors, including accounts and organizations')],['323',t('关系：177 条来源记录，146 条分析分类','Relationships: 177 documented and 146 analytical classifications')],['316',t('来源地址，同一工程可有多个来源','Source addresses; one project can have several sources')]])+conclusion('数量描述资料规模；贡献与可复用能力决定阅读顺序。','Counts describe the collection. Contributions and reusable capabilities guide reading.'))
    island_slide = next(i+1 for i,slide in enumerate(D['slides']) if slide['id']=='islands')
    svg=['<svg class="islands-svg" viewBox="0 0 1140 360" role="img" aria-labelledby="islands-title"><title id="islands-title">'+t('73 项工作、8 条路线、3 个系统部分','73 records, eight approaches, three responsibilities')+'</title>']
    for gi,g in enumerate(groups):
        x=gi*382; svg.append(f'<g style="--island:{g["color"]}"><rect x="{x+2}" y="3" width="371" height="350" rx="18" class="island-background"/><text x="{x+22}" y="35" class="island-heading">{tx(g["short"])}</text><text x="{x+349}" y="35" text-anchor="end" class="island-total">{len(g["projects"])}</text>')
        y=68
        for rid in g['routes']:
            ids=[pf['id'] for pf in profiles if pf['route']==rid]
            svg.append(f'<a href="#presentation/{island_slide}?route={rid}" aria-label="{tx(routes[rid]["name"])}"><rect x="{x+16}" y="{y-18}" width="339" height="26" rx="4" class="island-route-hit"/><text x="{x+25}" y="{y}" class="island-route">{tx(routes[rid]["name"])} · {len(ids)}</text><text x="{x+338}" y="{y}">+</text></a>')
            for j,pid in enumerate(ids):
                cx=x+31+(j%12)*27; cy=y+24+(j//12)*25
                svg.append(f'<a href="#projects/{pid}" aria-label="{e(projects[pid]["name"])}"><title>{e(projects[pid]["name"])}</title><circle cx="{cx}" cy="{cy}" r="8" class="island-project"/></a>')
            y+=48+((len(ids)-1)//12)*25
        svg.append('</g>')
    svg.append('</svg>')
    bodies.append(''.join(svg)+'<div class="deck-legend"><span>'+t('每个圆点是一项工作，点击查看详情','Each dot opens one project')+'</span><span>'+t('点击路线名称，展开该岛中的项目','Select an approach to expand its projects')+'</span></div>'+conclusion('按主要贡献归类，项目可以跨岛；三个部分通过 IOP 相互连接。','Primary contributions determine the grouping. Projects can span islands; IOP connects the responsibilities.'))
    bodies.append('<div class="deck-two">'+card(t('知识与资料 · 4 项','Knowledge resources · 4'),t('原理、适用条件、操作经验与预期观测，让能力可以理解和学习。','Principles, applicability, operating experience and expected observations make capabilities understandable.'),p('device-skills'))+card(t('仪器契约 · 7 项','Instrument contracts · 7'),t('能力、物理量、参数、状态和结果定义，让操作可以被程序准确调用。','Capabilities, quantities, parameters, state and result definitions make operations callable.'),p('openmhp')+' '+p('oahl'))+'</div><div class="shared-definition"><span>'+t('人读：原理与方法','Human view: principles and methods')+'</span><b>'+t('同一操作身份与版本','One operation identity and version')+'</b><span>'+t('程序读：结构与接口','Program view: structure and interface')+'</span></div>'+conclusion('IOP 的知识与接口应引用彼此，让说明、参数和实际行为保持对应。','Knowledge and interfaces should reference each other so descriptions, parameters and behavior stay aligned.'))
    bodies.append('<div class="deck-grid-four">'+card(t('设备桥接 · 26 项','Device bridges · 26'),t('把现有驱动或控制接口变成可调用能力。','Expose capabilities through existing drivers or control interfaces.'),p('scpi-mcp')+' '+p('epics-mcp'))+card(t('常驻执行 · 10 项','Persistent execution · 10'),t('持有连接、任务和状态，支持持续运行与结果读回。','Own connections, jobs and state across sustained execution.'),p('instrmcp')+' '+p('osprey'))+card(t('仪器开发 · 4 项','Instrument development · 4'),t('读写固件、观察总线、调试设备，形成新的控制能力。','Develop firmware and inspect buses to create new control capabilities.'),p('embedded-debugger')+' '+p('saleae'))+card(t('界面操作 · 1 项','GUI operation · 1'),t('通过已有仪器软件的界面完成操作。','Operate through the interface of existing instrument software.'),p('device-use'))+'</div>'+conclusion('IOP 需要明确操作与读回的关系，并复用这些已有接入路径。','IOP should relate operations to observations while reusing existing access paths.'))
    bodies.append('<div class="deck-two">'+card(t('过程编排 · 8 项','Workflow orchestration · 8'),t('描述步骤依赖、资源使用、样品流转和跨设备过程。','Express dependencies, resource use, sample transfers and multi-device procedures.'),p('unilabos')+' '+p('ivoryos'))+card(t('实验决策 · 13 项','Experimental decisions · 13'),t('依据目标和观测选择方法、调整参数或提出下一次实验。','Choose methods, adjust parameters or propose experiments using objectives and observations.'),p('aila')+' '+p('k-agents'))+'</div><div class="feedback-cycle"><div>'+t('方法与条件','Method and conditions')+'</div><span>→</span><div>'+t('仪器执行','Instrument execution')+'</div><span>→</span><div>'+t('观测与判断','Observations and judgment')+'</div><p>'+t('反馈回到下一次方法选择','Feedback informs the next method choice')+'</p></div>'+conclusion('接口提供可解释的实验能力，研究系统决定用它研究什么。','Interfaces expose interpretable experimental capabilities; research systems choose how to use them.'))
    bodies.append('<div class="deck-three reference-cards">'+card('MHS',t('Anthropic / HHMI Janelia<br><strong>研究预览</strong><br>共同驱动、能力说明与多种入口。公开材料列出跨机构试用和厂商集成计划。','Anthropic / HHMI Janelia<br><strong>Research preview</strong><br>Shared drivers, capability descriptions and multiple interfaces. Public materials describe institutional trials and vendor plans.'),s('mhs',t('生态发展参照','Ecosystem reference')))+card('AIP',t('用户提供的 PRD v1.1<br><strong>设计材料</strong><br>类型化物理量、持久执行、状态来源及控制与数据分离。','Supplied PRD v1.1<br><strong>Design reference</strong><br>Typed quantities, persistent execution, state provenance and separate control/data paths.'),s('aip',t('执行架构参照','Execution design reference')))+card('OpenMHP',t('独立社区工程<br><strong>公开规范与实现</strong><br>描述、操作、任务、租约与结果。当前设备包主要为孪生测试。','Independent community project<br><strong>Public specification and code</strong><br>Descriptors, operations, jobs, leases and results. Current device packages are primarily twin-tested.'),p('openmhp'))+'</div>'+conclusion('MHS 值得重点跟踪；技术价值仍要看能力覆盖、实现、采用和实验成果。','MHS warrants close attention. Technical value still depends on coverage, implementation, adoption and experimental results.'))
    bodies.append(table([t('代表','Example'),t('抓住的问题','Question'),t('对 IOP 的作用','Relevance to IOP')],[
        [s('mhs','MHS'),t('跨机构与厂商如何协作？','How can institutions and vendors collaborate?'),t('共同接入与生态组织','Shared access and ecosystem participation')],
        [p('openmhp'),t('一个设备任务如何完整表达？','How is a device job represented?'),t('可检查的操作与执行契约','Inspectable operation and execution contracts')],
        [p('osprey'),t('怎样使用已有大型设施？','How can existing facilities be used?'),t('设施知识与真实通道的对应','Mapping facility knowledge to control channels')],
        [p('unilabos'),t('多台设备怎样组成实验？','How do devices form an experiment?'),t('资源与过程的组合','Resource and procedure composition')],
        [p('aila'),t('观测怎样影响下一步？','How do observations inform the next step?'),t('实机实验与反馈判断','Physical experiments and feedback')],
    ])+conclusion('详细讲贡献不同的代表；相似实现按具体设备需求查询。','Explain representatives with distinct contributions; consult similar implementations for specific device needs.'))
    bodies.append('<div class="architecture"><div class="architecture-users"><span>'+t('人：界面 / 文档 / 脚本','People: interface / docs / scripts')+'</span><span>'+t('Agent：API / MCP / CLI','Agents: API / MCP / CLI')+'</span></div><div class="architecture-core"><b>'+t('IOP 共同定义','IOP shared definitions')+'</b><span>'+t('设备与能力　物理量与操作　任务与观测　结果与数据','Devices and capabilities · Quantities and operations · Jobs and observations · Results and data')+'</span></div><div class="architecture-roles">'+''.join('<div style="--island:'+g['color']+'"><b>'+tx(g['short'])+'</b><span>'+t(*v)+'</span></div>' for g,v in zip(groups,[('原理、描述、知识','Principles, descriptions, knowledge'),('运行、状态、读回','Execution, state, readback'),('方法、过程、反馈','Methods, procedures, feedback')]))+'</div><div class="architecture-adapters">'+t('适配器与协议绑定：SCPI / VISA、EPICS、TANGO、ROS、厂商 SDK','Adapters and bindings: SCPI / VISA, EPICS, TANGO, ROS, vendor SDKs')+'</div><div class="architecture-physical">'+t('真实仪器、样品与物理环境','Physical instruments, samples and environment')+'</div></div>'+conclusion('对应关系要落实到物理意义、状态和结果，而不只转换函数名。','Mappings must preserve physical meaning, state and results, beyond translating function names.'))
    bodies.append(table([t('操作角色','Operation role'),t('含义','Meaning'),t('光学示例','Optical example')],[
        ['Basic Operations',t('一个明确的控制或观测','An explicit control or observation'),t('设置转台角度；读取功率','Set stage angle; read optical power')],
        ['Standard Operations',t('可复用、有适用条件的方法','A reusable method with stated applicability'),t('完成一次偏振扫描，返回校准条件与测量记录','Run a polarization scan and return acquisition and calibration records')],
        ['Workflow Operations',t('组织方法、仪器和实验决策','Organize methods, instruments and decisions'),t('改变实验条件，复测并选择下一组参数','Change conditions, repeat measurements and select the next parameters')],
    ])+'<div class="composition-grid">'+''.join('<span>'+tx(g['short'])+'</span>' for g in groups)+'</div>'+conclusion('每种操作都需要含义、执行与结果。阅读层级与操作组合角色分别表达。','Every operation needs meaning, execution and results. Reading levels and operation roles describe different dimensions.'))
    bodies.append('<div class="optical-bench"><span>'+t('线偏振入射','Linear input')+'</span><i>→</i><span>'+t('可旋转半波片','Rotating half-wave plate')+'</span><i>→</i><span>'+t('固定检偏器','Fixed analyzer')+'</span><i>→</i><span>'+t('功率计','Power meter')+'</span></div><div class="deck-three">'+card(t('理解','Understand'),t('工作波长<br>轴零点与角度定义<br>探测器校准与量程','Wavelength<br>Axis zero and angle definition<br>Detector calibration and range'))+card(t('执行','Execute'),t('设置目标角度<br>等待并读取实际位置<br>采集功率和时间','Set target angle<br>Settle and read actual position<br>Acquire power and time'))+card(t('组织实验','Experiment'),t('遍历扫描点<br>记录条件与观测<br>复测或调整下一轮','Traverse scan points<br>Record conditions and observations<br>Repeat or adjust the next run'))+'</div>'+conclusion('人工界面与 Agent 工具调用引用同一方法定义，生成相同结构的实验记录。','Human interfaces and agent tools refer to one method definition and produce the same record structure.'))
    bodies.append('<div class="build-status">'+t('现有基础：操作模型与模拟参考实现','Existing foundation: operation model and simulated reference implementation')+'</div>'+table([t('建设步骤','Step'),t('可交付内容','Deliverable')],[
        ['01 '+t('描述具体仪器','Describe an instrument'),t('能力与操作定义，关联原理、校准和人工可读说明','Capability and operation definitions linked to principles, calibration and readable documentation')],
        ['02 '+t('接入真实设备','Connect physical equipment'),t('驱动适配与持久执行，真实读回和结果记录','Driver adapters, persistent execution, physical readback and results')],
        ['03 '+t('复用实验方法','Reuse experimental methods'),t('同一方法在不同设备实现上运行，保留特有能力','One method running through different device implementations, retaining device-specific capabilities')],
        ['04 '+t('扩展共同生态','Extend the shared ecosystem'),t('设备包、方法库、映射说明与可重复的互操作示例','Device packages, method libraries, mapping specifications and repeatable interoperability examples')],
    ])+conclusion('以真实设备和可复用方法检验设计，再扩展规范覆盖。','Exercise the design through real devices and reusable methods, then extend its coverage.'))
    bodies.append('<div class="deck-grid-four">'+card(t('比较具体工程','Compare projects'),t('贡献、差异、连接路径与实验记录','Contributions, distinctions, access paths and experiment records'),a('#projects',t('工程与比较','Projects and comparison')))+card(t('理解已有规范','Understand existing specifications'),t('MHS、AIP、SiLA、OPC UA 等的角色与状态','Roles and status of MHS, AIP, SiLA, OPC UA and other foundations'),a('#standards',t('标准与组件','Standards and components')))+card(t('追踪实际关系','Trace actual relationships'),t('维护、复用、接入与后续发展','Maintenance, reuse, integration and successors'),a('#relations',t('关系图谱','Relationship graph')))+card(t('阅读和复用原始资料','Read and reuse the evidence'),t('来源链接、结构化数据与中英文正文','Source links, structured data and bilingual text'),a('#sources',t('来源与数据','Sources and data')))+'</div>'+conclusion('IOP 的目标：让人和 Agent 理解仪器、执行方法，并使用有物理意义的实验结果。','IOP aims to help people and agents understand instruments, execute methods and use physically meaningful results.'))
    names={'s:mhs':'MHS','s:aip':'AIP','s:lap':'LAP','p:open-mhs-abenor':'Open-MHS · Abenor','p:open-mhs-tong':'Open MHS · tongriyaotxt','p:open-mhs-scut':'Open MHS · SCUT-ESA','p:mhp-cuntinum':'MHP · Cuntinum','p:openmhp':'OpenMHP','p:oahl':'OAHL','p:agent2device':'Agent2Device'}
    status={'s:mhs':t('研究预览','Preview'),'s:aip':t('设计材料','Design'),'s:lap':t('设计论文','Design paper'),'p:openmhp':t('规范与代码','Spec + code'),'p:agent2device':t('概念提案','Concept')}
    def ref(key):
        kind,id=key.split(':',1)
        return a(('#standards/' if kind=='s' else '#projects/')+id,names[key])
    protocol_cards=[]
    for g in PROTOCOL_GROUPS:
        items=''.join('<li>'+ref(key)+'<span>'+status.get(key,t('公开工程','Public code'))+'</span></li>' for key in g['members'])
        protocol_cards.append('<section class="deck-card protocol-list"><h3>'+tx(g['name'])+'</h3><ul>'+items+'</ul></section>')
    inventory='<div class="deck-three">'+''.join(protocol_cards)+'</div><p class="protocol-pending">'+ref('p:agent2device')+' · '+t('概念提案，公开细节尚不足以归入具体机制','Concept proposal; public details do not yet support a mechanism assignment')+'</p>'+conclusion('三项 Open-MHS 是不同维护者的独立工程，不是官方 MHS 的三个版本。','The three Open-MHS entries are independently maintained projects, not three versions of official MHS.')
    mechanisms='<div class="deck-three">'+''.join(card(tx(g['name']),tx(g['question']),t('代表：','Examples: ')+', '.join(ref(key) for key in (g['members'][:1] if g['id']!='jobs' else g['members']))) for g in PROTOCOL_GROUPS)+'</div><div class="synthesis-core"><b>'+t('IOP 的共同模型','Shared IOP model')+'</b><p>'+t('仪器与能力　操作与任务　资源与状态　观测与结果','Instruments and capabilities · Operations and jobs · Resources and state · Observations and results')+'</p></div>'+conclusion('机制可以跨岛组合。共同模型的价值取决于实际映射和跨设备方法复用。','Mechanisms can span groups. The shared model earns its value through actual mappings and reusable methods.')
    foundations='<div class="deck-three">'+card('SiLA 2',t('实验室服务与功能<br>命令、属性与可观测执行','Laboratory services and features<br>Commands, properties and observable execution'),s('sila',t('复用服务与执行语义','Reuse service and execution semantics')))+card('OPC UA / LADS',t('设备信息模型<br>功能单元、状态与程序管理','Device information models<br>Functional units, states and program management'),s('lads',t('复用设备与程序模型','Reuse device and program models')))+card('W3C WoT',t('设备交互描述<br>属性、动作、事件与协议绑定','Interaction descriptions<br>Properties, actions, events and protocol bindings'),s('wot',t('复用描述与绑定分离','Reuse description/binding separation')))+'</div><div class="shared-definition"><b>MCP / API / CLI</b><span>'+t('面向 Agent 与程序的调用入口','Invocation interfaces for agents and programs')+'</span></div>'+conclusion('IOP 的建设先识别能直接采用的已有语义，再补充需要共同约定的部分。','IOP development starts by identifying reusable semantics, then defines the additional shared requirements.')
    bodies[2:2]=[inventory,mechanisms,foundations]
    refs={6:[('projects/device-skills','device-skills'),('projects/openmhp','OpenMHP')],7:[('projects/instrmcp','instrMCP'),('projects/osprey','Osprey')],8:[('projects/unilabos','Uni-Lab-OS'),('projects/aila','AILA')],9:[('standards/mhs','MHS'),('standards/aip','AIP'),('projects/openmhp','OpenMHP')],10:[('standards/mhs','MHS'),('projects/openmhp','OpenMHP'),('projects/osprey','Osprey'),('projects/unilabos','Uni-Lab-OS'),('projects/aila','AILA')]}
    slides=[]
    for i,(info,body) in enumerate(zip(D['slides'],bodies)):
        sources=' '.join(a('#'+path,label) for path,label in refs.get(i,[]))
        slides.append(f'<article class="deck-slide" data-slide="{i+1}" aria-label="{i+1}. {tx(info["title"])}"><header><p class="deck-subtitle">{tx(info["subtitle"])}</p><h2>{tx(info["title"])}</h2></header><div class="deck-body">{body}</div><footer><span>AI4Instruments · IOP</span><span class="deck-refs">{sources}</span><span>{i+1:02} / {len(D["slides"]):02}</span></footer></article>')
    options=''.join(f'<option value="{i+1}">{i+1:02}　{tx(info["title"])}</option>' for i,info in enumerate(D['slides']))
    return f'''<section class="view" id="view-presentation" data-view="presentation"><div class="deck-shell" id="deck-shell"><div class="deck-controls"><label for="deck-select">{t('IOP 演示','IOP presentation')}</label><select id="deck-select">{options}</select><button id="deck-focus">{t('演示模式','Present')}</button><button id="deck-fullscreen">{t('全屏','Fullscreen')}</button><button id="deck-exit" hidden>{t('退出演示','Exit')}</button></div><div class="deck-stage" id="deck-stage">{''.join(slides)}</div><div class="deck-pagination"><button id="deck-prev">← {t('上一页','Previous')}</button><span id="deck-position" aria-live="polite"></span><button id="deck-notes-toggle" aria-expanded="false">{t('讲解备注','Speaker notes')}</button><button id="deck-next">{t('下一页','Next')} →</button></div><aside id="deck-notes" hidden></aside></div><dialog id="island-detail"><div class="section-line"><h2 id="island-detail-title"></h2><button id="island-close">{t('关闭','Close')}</button></div><p id="island-detail-question"></p><div id="island-detail-projects"></div></dialog></section>'''
