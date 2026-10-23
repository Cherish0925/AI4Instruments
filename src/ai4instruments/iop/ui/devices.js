import {
  $,
  $$,
  state,
  t,
  esc,
  icon,
  api,
  busy,
  toast,
  modal,
  closeModal,
  field,
  empty,
  badge,
  jsonDetails,
  emit,
  go,
  readJSON,
  uniqueID,
} from "./core.js";
let filter = "",
  kind = "all";
const mode = (d) =>
  d.mode === "simulation"
    ? t("模拟设备", "Simulation")
    : d.mode === "software"
      ? t("软件", "Software")
      : t("实体仪器", "Instrument");
export function parametersHTML(spec = {}, prefix = "arg") {
  return (
    Object.entries(spec.parameters || {})
      .map(([name, p]) => {
        const id = prefix + "-" + name,
          value = p.default ?? "",
          optional = p.required === false || p.default !== undefined;
        let input = p.enum
          ? `<select id="${esc(id)}" data-parameter="${esc(name)}"><option value="">${t("选择", "Choose")}</option>${p.enum.map((v) => `<option value="${esc(JSON.stringify(v))}" ${v === value ? "selected" : ""}>${esc(v)}</option>`).join("")}</select>`
          : p.type === "boolean"
            ? `<select id="${esc(id)}" data-parameter="${esc(name)}"><option value="">${t("选择", "Choose")}</option><option value="true" ${value === true ? "selected" : ""}>true</option><option value="false" ${value === false ? "selected" : ""}>false</option></select>`
            : ["object", "array"].includes(p.type)
              ? `<textarea id="${esc(id)}" data-parameter="${esc(name)}" rows="2" style="min-height:75px" placeholder="${p.type === "array" ? "[]" : "{}"}">${esc(value === "" ? "" : JSON.stringify(value))}</textarea>`
              : `<input id="${esc(id)}" data-parameter="${esc(name)}" type="${["integer", "number"].includes(p.type) ? "number" : "text"}" ${p.type === "integer" ? 'step="1"' : 'step="any"'} ${p.minimum !== undefined ? `min="${esc(p.minimum)}"` : ""} ${p.maximum !== undefined ? `max="${esc(p.maximum)}"` : ""} value="${esc(value)}" placeholder="${optional ? t("可选", "Optional") : t("必填", "Required")}">`;
        return field(
          esc(name) + (p.unit ? " <small>" + esc(p.unit) + "</small>" : ""),
          input,
          esc(p.description || ""),
        );
      })
      .join("") ||
    `<p class="inline-note">${t("此操作无需参数。", "This operation takes no parameters.")}</p>`
  );
}
export function parameterValues(container, spec) {
  const result = {};
  for (const input of $$("[data-parameter]", container)) {
    const name = input.dataset.parameter,
      p = spec.parameters[name],
      v = input.value;
    if (v === "") {
      if (p.required === false || p.default !== undefined) continue;
      throw Error(t("请填写参数：", "Enter parameter: ") + name);
    }
    if (!input.checkValidity())
      throw Error(
        t("参数值不符合范围：", "Parameter value is outside its range: ") +
          name,
      );
    result[name] =
      p.enum || ["array", "object", "boolean"].includes(p.type)
        ? JSON.parse(v)
        : ["integer", "number"].includes(p.type)
          ? Number(v)
          : v;
  }
  return result;
}
export function renderDevices() {
  return `<div class="page-heading"><div><span class="eyebrow">INSTRUMENTS & SOFTWARE</span><h1>${t("仪器与软件", "Instruments & software")}</h1><p>${t("查看设备说明、可用操作和计算机上的连接。", "Inspect registered instruments, available operations and connections on this computer.")}</p></div><div class="actions"><button class="button" id="scan">${icon("refresh")}${t("发现设备", "Discover")}</button><button class="button primary" id="register-device">${icon("plus")}${t("注册设备", "Register device")}</button></div></div><div class="toolbar"><label class="search-field">${icon("search")}<input id="device-search" value="${esc(filter)}" placeholder="${t("搜索名称、驱动或设备 ID", "Search name, driver or device ID")}"></label><div class="segmented">${[
    ["all", t("全部", "All")],
    ["hardware", t("实体仪器", "Instruments")],
    ["software", t("软件", "Software")],
    ["simulation", t("模拟", "Simulation")],
  ]
    .map(
      ([k, v]) =>
        `<button data-kind="${k}" class="${kind === k ? "active" : ""}">${v}</button>`,
    )
    .join(
      "",
    )}</div></div><div id="device-grid" class="card-grid"></div><div id="discovery-section"></div>`;
}
function renderGrid() {
  const list = state.devices.filter(
    (d) =>
      (kind === "all" || (d.mode || "hardware") === kind) &&
      `${d.id} ${d.name} ${d.driver}`
        .toLowerCase()
        .includes(filter.toLowerCase()),
  );
  $("#device-grid").innerHTML = list.length
    ? list
        .map(
          (d) =>
            `<button class="device-card" data-device="${esc(d.id)}"><div class="card-top"><span class="device-icon">${icon(d.mode === "software" ? "code" : "device")}</span><span class="badge">${mode(d)}</span></div><h3>${esc(d.name || d.id)}</h3><div class="mono">${esc(d.id)}</div><div class="card-bottom"><span>${Object.keys(d.operations).length} ${t("个操作", "operations")} · ${esc(d.transport || d.driver)}</span>${icon("arrow")}</div></button>`,
        )
        .join("")
    : empty(
        "device",
        state.devices.length
          ? t("没有匹配的设备", "No matching devices")
          : t("还没有注册设备", "No registered devices"),
        state.devices.length
          ? t("尝试其他名称或类型。", "Try another name or category.")
          : t(
              "发现连接后，选择驱动并注册。也可以导入已有的仪器说明。",
              "Discover a connection and register it with a driver, or import an existing instrument description.",
            ),
        `<button class="button" id="empty-register">${icon("plus")}${t("注册设备", "Register device")}</button>`,
      );
  $$("[data-device]", $("#device-grid")).forEach(
    (n) => (n.onclick = () => inspectDevice(n.dataset.device)),
  );
  $("#empty-register")?.addEventListener("click", () => registerDevice());
}
export function bindDevices() {
  renderGrid();
  renderInventory();
  $("#scan").onclick = (e) => scan(e.currentTarget);
  $("#register-device").onclick = () => registerDevice();
  $("#device-search").oninput = (e) => {
    filter = e.target.value;
    renderGrid();
  };
  $$("[data-kind]").forEach(
    (b) =>
      (b.onclick = () => {
        kind = b.dataset.kind;
        $$("[data-kind]").forEach((n) => n.classList.toggle("active", n === b));
        renderGrid();
      }),
  );
}
export async function scan(button) {
  await busy(button, async () => {
    toast(t("正在读取连接列表…", "Reading available connections…"));
    state.inventory = await api("discovery", undefined, { timeout: 90000 });
    emit("refresh");
    if (state.view === "devices") renderInventory();
    toast(
      t(
        `发现 ${state.inventory.connections.length} 个连接`,
        `Found ${state.inventory.connections.length} connections`,
      ),
    );
  });
}
function renderInventory() {
  const el = $("#discovery-section");
  if (!el || !state.inventory) return;
  const data = state.inventory;
  el.innerHTML = `<div class="section-title"><h2>${t("发现的连接", "Discovered connections")}<span class="count">${data.connections.length}</span></h2><small>${t("选择连接，补充仪器说明后注册", "Select a connection and its instrument driver")}</small></div><div class="panel">${data.connections.length ? `<div class="table-wrap"><table><thead><tr><th>${t("名称", "Name")}</th><th>${t("接口与地址", "Interface & address")}</th><th>${t("制造商", "Manufacturer")}</th><th></th></tr></thead><tbody>${data.connections.map((c, i) => `<tr><td><strong>${esc(c.name || c.id || t("未命名连接", "Unnamed connection"))}</strong>${c.serial_number ? `<small>${esc(c.serial_number)}</small>` : ""}</td><td><span class="badge">${esc(c.transport)}</span><small class="discovery-address">${esc(c.address)}</small></td><td>${esc(c.manufacturer || "—")}</td><td>${c.status === "registered" ? `<span class="badge">${t("已注册", "Registered")}</span>` : `<button class="button small" data-register="${i}">${t("注册", "Register")}${icon("plus")}</button>`}</td></tr>`).join("")}</tbody></table></div>` : empty("search", t("没有发现新的连接", "No connections found"), t("检查连接线和系统驱动；网络设备可直接按地址注册。", "Check the connection and system driver. Network devices can be registered by address."))}<div class="provider-list">${(data.providers || []).map((p) => `<span title="${esc(p.detail || "")}"><i class="dot ${p.available ? "online" : ""}"></i>${esc(p.name)}${!p.available ? " · " + t("不可用", "Unavailable") : ""}</span>`).join("")}</div></div>`;
  $$("[data-register]", el).forEach(
    (b) =>
      (b.onclick = () =>
        registerDevice(data.connections[Number(b.dataset.register)])),
  );
}
export function registerDevice(candidate) {
  const body = modal(
    t("注册仪器或软件", "Register an instrument or software"),
    `<div class="form-stack"><p class="inline-note">${candidate ? esc(candidate.name || candidate.address) + " · " + esc(candidate.address) : t("选择设备使用的接口，或导入已有的说明文件。", "Select the interface used by the device, or import an existing description.")}</p><div class="form-grid">${field(t("设备 ID", "Device ID"), '<input id="reg-id" placeholder="instrument-01" maxlength="80">')}${field(t("显示名称", "Display name"), `<input id="reg-name" value="${esc(candidate?.name || "")}" placeholder="${t("例如：信号发生器", "e.g. Signal generator")}">`)}${field(t("驱动与接口", "Driver & interface"), `<select id="reg-driver"><option value="scpi-tcp">SCPI · TCP/IP</option><option value="scpi-serial">SCPI · ${t("串口", "Serial")}</option><option value="scpi-visa">SCPI · VISA</option><option value="modbus-tcp">Modbus · TCP/IP</option><option value="modbus-serial">Modbus · RTU</option><option value="http">HTTP API</option><option value="command">${t("命令行程序", "Command-line program")}</option><option value="process">${t("独立 SDK 进程", "SDK worker process")}</option></select>`)}${field(t("导入仪器说明", "Import description"), '<input type="file" id="reg-import" accept=".json">')}</div><div id="reg-fields" class="form-grid"></div><details class="raw"><summary>${icon("code")}${t("完整仪器说明", "Full instrument description")}</summary><textarea id="reg-json" spellcheck="false"></textarea><div style="padding:10px 15px"><button class="button small" id="reg-use-json">${t("使用此说明注册", "Register this description")}</button></div></details></div><div class="form-actions"><button class="button" id="reg-cancel">${t("取消", "Cancel")}</button><button class="button primary" id="reg-save">${t("注册设备", "Register device")}</button></div>`,
    "INSTRUMENT",
  );
  const selected =
    candidate?.transport === "serial"
      ? "scpi-serial"
      : candidate?.transport === "visa"
        ? "scpi-visa"
        : candidate?.transport === "command"
          ? "command"
          : "scpi-tcp";
  $("#reg-driver").value = selected;
  function fields() {
    const kind = $("#reg-driver").value;
    $("#reg-fields").innerHTML = kind.endsWith("-tcp")
      ? field(
          t("主机地址", "Host"),
          '<input id="reg-host" placeholder="192.168.1.20">',
        ) +
        field(
          t("端口", "Port"),
          `<input id="reg-port" type="number" min="1" max="65535" value="${kind.startsWith("modbus") ? 502 : 5025}">`,
        )
      : kind.endsWith("-serial")
        ? field(
            t("串口地址", "Serial port"),
            `<input id="reg-port" value="${esc(candidate?.address || "")}" placeholder="COM7 / /dev/ttyUSB0">`,
          ) +
          field(
            t("波特率", "Baud rate"),
            '<input id="reg-baud" type="number" value="9600">',
          )
        : kind === "scpi-visa"
          ? field(
              t("VISA 地址", "VISA resource"),
              `<input id="reg-resource" value="${esc(candidate?.address || "")}" placeholder="USB0::...::INSTR">`,
            )
          : kind === "http"
            ? field(
                t("服务地址", "Service URL"),
                '<input id="reg-url" placeholder="http://192.168.1.20:8000">',
              )
            : field(
                t("程序命令（JSON 数组）", "Program command (JSON array)"),
                `<textarea id="reg-command" style="min-height:80px">${esc(JSON.stringify(candidate?.transport === "command" ? [candidate.address] : ["{python}", "/path/to/worker.py"]))}</textarea>`,
              );
    if (["http", "command"].includes(kind))
      $("#reg-fields").insertAdjacentHTML(
        "beforeend",
        `<div class="full">${field(t("操作说明", "Operations"), '<textarea id="reg-operations" placeholder="{}">{}</textarea>', t("填写程序或 API 提供的操作、参数和结果。", "Describe the operations and parameters supported by this program or API."))}</div>`,
      );
    updateJSON();
  }
  function record() {
    const kind = $("#reg-driver").value;
    const driver = kind.startsWith("scpi")
      ? "scpi"
      : kind.startsWith("modbus")
        ? "modbus"
        : kind;
    let config = {
      name: $("#reg-name").value.trim() || $("#reg-id").value.trim(),
    };
    if (kind.endsWith("-tcp"))
      Object.assign(config, {
        transport: "tcp",
        host: $("#reg-host").value.trim(),
        port: Number($("#reg-port").value),
      });
    else if (kind.endsWith("-serial"))
      Object.assign(config, {
        transport: "serial",
        port: $("#reg-port").value.trim(),
        baudrate: Number($("#reg-baud").value),
      });
    else if (kind === "scpi-visa")
      Object.assign(config, {
        transport: "visa",
        resource: $("#reg-resource").value.trim(),
      });
    else if (kind === "http") config.base_url = $("#reg-url").value.trim();
    else config.command = readJSON("#reg-command");
    if ($("#reg-operations")) config.operations = readJSON("#reg-operations");
    return { id: $("#reg-id").value.trim(), driver, config };
  }
  function updateJSON() {
    try {
      $("#reg-json").value = JSON.stringify(record(), null, 2);
    } catch {}
  }
  async function save(value) {
    await api("devices", value);
    if (candidate) {
      candidate.status = "registered";
      candidate.id = value.id;
    }
    closeModal();
    emit("refresh");
    toast(t("设备已注册", "Device registered"));
  }
  fields();
  $("#reg-driver").onchange = fields;
  body.addEventListener("input", (e) => {
    if (e.target.id !== "reg-json") updateJSON();
  });
  $("#reg-save").onclick = (e) => busy(e.currentTarget, () => save(record()));
  $("#reg-use-json").onclick = (e) =>
    busy(e.currentTarget, () => save(readJSON("#reg-json")));
  $("#reg-cancel").onclick = closeModal;
  $("#reg-import").onchange = async (e) => {
    try {
      const f = e.target.files[0];
      if (f) {
        $("#reg-json").value = JSON.stringify(
          JSON.parse(await f.text()),
          null,
          2,
        );
        $("#reg-json").closest("details").open = true;
      }
    } catch (error) {
      toast(error.message, true);
    }
  };
}
export function inspectDevice(id) {
  const d = state.devices.find((v) => v.id === id);
  if (!d) return;
  const body = modal(
    d.name || d.id,
    `<div class="run-summary"><div><small>ID</small><code>${esc(d.id)}</code></div><div><small>${t("驱动", "Driver")}</small>${esc(d.driver)}</div><div><small>${t("类型", "Type")}</small>${mode(d)}</div><button class="button small" id="device-reconnect">${icon("refresh")}${t("重新连接", "Reconnect")}</button></div><div class="form-stack">${field(
      t("可用操作", "Available operation"),
      `<select id="device-operation">${Object.keys(d.operations)
        .map((k) => `<option value="${esc(k)}">${esc(k)}</option>`)
        .join("")}</select>`,
    )}<div id="operation-parameters" class="form-grid"></div></div>${jsonDetails(d, t("完整仪器说明", "Full instrument description"))}<div class="form-actions"><small>${t("操作通过运行服务执行并保留记录", "Operations run through the service and remain in experiment history")}</small><button class="button primary" id="device-invoke">${icon("play")}${t("执行操作", "Run operation")}</button></div>`,
    t("仪器说明", "INSTRUMENT"),
  );
  const render = () =>
    ($("#operation-parameters").innerHTML = parametersHTML(
      d.operations[$("#device-operation").value],
    ));
  render();
  $("#device-operation").onchange = render;
  $("#device-reconnect").onclick = (e) =>
    busy(e.currentTarget, async () => {
      await api("devices/" + encodeURIComponent(id) + "/reconnect", {});
      toast(t("驱动已重新连接", "Driver reconnected"));
      emit("refresh");
    });
  $("#device-invoke").onclick = (e) =>
    busy(e.currentTarget, async () => {
      const op = $("#device-operation").value;
      const args = parameterValues(
        $("#operation-parameters"),
        d.operations[op],
      );
      const run = await api("runs", {
        name: (d.name || d.id) + " · " + op,
        request_id: uniqueID(),
        steps: [
          { id: "operation", device: id, operation: op, arguments: args },
        ],
      });
      emit("run", run.id);
      emit("refresh");
    });
}
