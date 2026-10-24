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
  operationResult,
} from "./core.js";
let filter = "",
  kind = "all",
  inventoryKind = "interface";
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
    )}</div></div><div id="device-grid" class="device-list"></div><div id="discovery-section"></div>`;
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
    ? `<div class="panel table-wrap"><table><thead><tr><th>${t("已添加设备", "Saved instruments")}</th><th>${t("接口", "Interface")}</th><th>${t("操作", "Operations")}</th><th></th></tr></thead><tbody>${list.map((d) => `<tr><td><button class="device-name" data-device="${esc(d.id)}">${icon(d.mode === "software" ? "code" : "device")}<span><strong>${esc(d.name || d.id)}</strong><small>${esc(d.id)}</small></span></button></td><td><span class="badge">${esc(d.transport || d.driver)}</span><small>${esc(d.connection?.resource || d.connection?.port || d.connection?.host || mode(d))}</small></td><td>${Object.keys(d.operations).length}</td><td><button class="button small" data-device="${esc(d.id)}">${t("打开", "Open")}${icon("chevron")}</button></td></tr>`).join("")}</tbody></table></div>`
    : `<div class="setup-inline">${icon("device")}<span>${state.devices.length ? t("没有匹配的设备", "No matching instruments") : t("选择下方接口添加仪器，也可以导入仪器说明。", "Add an instrument from the connections below, or import a description.")}</span><button class="button small" id="empty-register">${t("添加设备", "Add instrument")}</button></div>`;
  $$("[data-device]", $("#device-grid")).forEach(
    (n) => (n.onclick = () => inspectDevice(n.dataset.device)),
  );
  $("#empty-register")?.addEventListener("click", () => registerDevice());
}
export function bindDevices() {
  renderGrid();
  renderInventory();
  if (state.inventory?.scanning && !scan.running) scan();
  $("#scan").onclick = (e) => scan(e.currentTarget);
  $("#register-device").onclick = () => registerDevice();
  $("#device-search").oninput = (e) => {
    filter = e.target.value;
    renderGrid();
    renderInventory();
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
  if (scan.running) return;
  scan.running = true;
  try {
    await busy(button, async () => {
      state.inventory = await api("discovery", {});
      if (state.view === "devices") renderInventory();
      while (state.inventory.scanning) {
        await new Promise((resolve) => setTimeout(resolve, 400));
        state.inventory = await api("discovery?cached=true");
        if (state.view === "devices") renderInventory();
      }
      if (state.inventory.error) throw Error(state.inventory.error);
      emit("refresh");
      toast(t("连接列表已更新", "Connections updated"));
    });
  } finally {
    scan.running = false;
  }
}
function renderInventory() {
  const el = $("#discovery-section");
  if (!el || !state.inventory) return;
  const data = state.inventory;
  const all = data.groups || data.connections;
  const category = (c) => (c.transport === "usb" ? "usb" : "interface");
  const list = all.filter(
    (c) =>
      category(c) === inventoryKind &&
      `${c.name} ${c.address} ${c.manufacturer} ${c.serial_number}`
        .toLowerCase()
        .includes(filter.toLowerCase()),
  );
  const counts = (k) => all.filter((c) => category(c) === k).length;
  el.innerHTML = `<div class="section-title"><div class="tabs inventory-tabs">${[
    ["interface", t("可配置接口", "Instrument interfaces")],
    ["usb", t("USB 清单", "USB inventory")],
  ]
    .map(
      ([k, label]) =>
        `<button data-inventory-kind="${k}" class="${inventoryKind === k ? "active" : ""}">${label}<span class="count">${counts(k)}</span></button>`,
    )
    .join(
      "",
    )}</div><small>${data.scanning ? t("正在扫描…", "Scanning…") : t("选择接口，保存仪器说明", "Choose an interface and save its instrument description")}</small></div><div class="panel">${
    list.length
      ? `<div class="table-wrap"><table><thead><tr><th>${t("名称", "Name")}</th><th>${t("接口与地址", "Interface & address")}</th><th>${t("制造商", "Manufacturer")}</th><th></th></tr></thead><tbody>${list
          .map(
            (c, i) =>
              `<tr><td><strong>${esc(c.name || c.id || t("未命名连接", "Unnamed connection"))}</strong>${c.serial_number ? `<small>${esc(c.serial_number)}</small>` : ""}</td><td><span class="badge">${esc(c.transport)}</span><small class="discovery-address">${esc(c.address)}</small>${
                (c.interfaces?.length || 0) > 1
                  ? `<small>${t("另有接口：", "Also available: ")}${esc(
                      c.interfaces
                        .filter((v) => v.transport !== c.transport)
                        .map((v) => v.transport)
                        .join(", "),
                    )}</small>`
                  : ""
              }</td><td>${esc(c.manufacturer || "—")}</td><td>${c.status === "registered" ? `<span class="badge">${t("已添加", "Saved")}</span>` : `<button class="button small" data-register="${i}">${category(c) === "usb" ? t("配置 SDK", "Configure SDK") : t("添加", "Add")}${icon("plus")}</button>`}</td></tr>`,
          )
          .join("")}</tbody></table></div>`
      : `<div class="setup-inline">${icon("search")}<span>${data.scanning ? t("正在读取计算机上的连接", "Reading connections on this computer") : t("没有匹配的连接；网络仪器可直接按地址添加。", "No matching connections. Network instruments can be added by address.")}</span></div>`
  }<div class="provider-list">${(data.providers || []).map((p) => `<span title="${esc(p.detail || "")}"><i class="dot ${p.available ? "online" : ""}"></i>${esc(p.name)}${!p.available ? " · " + t("不可用", "Unavailable") : ""}</span>`).join("")}${data.duration_s != null ? `<span>${t("扫描用时", "Scan time")} ${data.duration_s}s</span>` : ""}</div></div>`;
  $$("[data-inventory-kind]", el).forEach(
    (b) =>
      (b.onclick = () => {
        inventoryKind = b.dataset.inventoryKind;
        renderInventory();
      }),
  );
  $$("[data-register]", el).forEach(
    (b) => (b.onclick = () => registerDevice(list[Number(b.dataset.register)])),
  );
}
export function registerDevice(candidate) {
  const label = [candidate?.name, candidate?.address].filter(Boolean).join("-");
  const stem =
    label
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 60) || "instrument";
  let generatedID = stem;
  for (let i = 2; state.devices.some((d) => d.id === generatedID); i++)
    generatedID = stem + "-" + i;
  const body = modal(
    t("注册仪器或软件", "Register an instrument or software"),
    `<div class="form-stack"><p class="inline-note">${candidate ? esc(candidate.name || candidate.address) + " · " + esc(candidate.address) : t("选择设备使用的接口，或导入已有的说明文件。", "Select the interface used by the device, or import an existing description.")}</p><div class="form-grid">${field(t("设备 ID", "Device ID"), `<input id="reg-id" value="${esc(generatedID)}" maxlength="80" aria-describedby="reg-id-note"><small id="reg-id-note">${t("自动生成，可修改", "Generated automatically; editable")}</small>`)}${field(t("显示名称", "Display name"), `<input id="reg-name" value="${esc(candidate?.name || "")}" placeholder="${t("例如：信号发生器", "e.g. Signal generator")}">`)}${field(t("驱动与接口", "Driver & interface"), `<select id="reg-driver"><option value="scpi-tcp">SCPI · TCP/IP</option><option value="scpi-serial">SCPI · ${t("串口", "Serial")}</option><option value="scpi-visa">SCPI · VISA</option><option value="modbus-tcp">Modbus · TCP/IP</option><option value="modbus-serial">Modbus · RTU</option><option value="http">HTTP API</option><option value="command">${t("命令行程序", "Command-line program")}</option><option value="process">${t("独立 SDK 进程", "SDK worker process")}</option></select>`)}${field(t("导入仪器说明", "Import description"), '<input type="file" id="reg-import" accept=".json">')}</div><div id="reg-fields" class="form-grid"></div><details class="raw"><summary>${icon("code")}${t("完整仪器说明", "Full instrument description")}</summary><textarea id="reg-json" spellcheck="false"></textarea><div style="padding:10px 15px"><button class="button small" id="reg-use-json">${t("使用此说明注册", "Register this description")}</button></div></details></div><div class="form-actions"><button class="button" id="reg-cancel">${t("取消", "Cancel")}</button><button class="button primary" id="reg-save">${t("注册设备", "Register device")}</button></div>`,
    t("仪器说明", "Instrument description"),
  );
  const selected =
    candidate?.transport === "serial"
      ? "scpi-serial"
      : candidate?.transport === "visa"
        ? "scpi-visa"
        : candidate?.transport === "command"
          ? "command"
          : candidate?.transport === "usb"
            ? "process"
            : "scpi-tcp";
  $("#reg-driver").value = selected;
  let imported = false;
  $("#reg-save").insertAdjacentHTML(
    "beforebegin",
    '<p id="reg-error" class="error-text" role="alert"></p>',
  );
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
    if (kind.startsWith("scpi"))
      $("#reg-fields").insertAdjacentHTML(
        "beforeend",
        field(
          t("结束符", "Line ending"),
          '<select id="reg-termination"><option value="lf">LF</option><option value="crlf">CRLF</option><option value="cr">CR</option></select>',
        ),
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
    if ($("#reg-termination"))
      config.termination = { lf: "\n", crlf: "\r\n", cr: "\r" }[
        $("#reg-termination").value
      ];
    if ($("#reg-operations")) config.operations = readJSON("#reg-operations");
    return { id: $("#reg-id").value.trim(), driver, config };
  }
  function updateJSON() {
    try {
      $("#reg-json").value = JSON.stringify(record(), null, 2);
    } catch {}
  }
  async function save(value) {
    const saved = await api("devices", value);
    if (candidate) {
      candidate.status = "registered";
      candidate.id = saved.id;
    }
    closeModal();
    emit("refresh");
    toast(t("设备已保存", "Instrument saved"));
  }
  fields();
  $("#reg-driver").onchange = () => {
    imported = false;
    fields();
  };
  body.addEventListener("input", (e) => {
    if (e.target.id !== "reg-json" && !imported) updateJSON();
  });
  $("#reg-save").onclick = (e) =>
    busy(e.currentTarget, async () => {
      $("#reg-error").textContent = "";
      try {
        await save(imported ? readJSON("#reg-json") : record());
      } catch (error) {
        $("#reg-error").textContent = error.message;
      }
    });
  $("#reg-use-json").onclick = (e) =>
    busy(e.currentTarget, () => save(readJSON("#reg-json")));
  $("#reg-cancel").onclick = closeModal;
  $("#reg-import").onchange = async (e) => {
    try {
      const f = e.target.files[0];
      if (f) {
        imported = true;
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
const operationName = (name) =>
  ({
    identify: t("读取身份", "Read identity"),
    query: t("查询", "Query"),
    write: t("发送命令", "Send command"),
  })[name] || name;
export function inspectDevice(id) {
  const d = state.devices.find((v) => v.id === id);
  if (!d) return;
  const body = modal(
    d.name || d.id,
    `<div class="run-summary"><div><small>ID</small><code>${esc(d.id)}</code></div><div><small>${t("接口", "Interface")}</small>${esc(d.transport || d.driver)}</div><div><small>${t("地址", "Address")}</small>${esc(d.connection?.resource || d.connection?.port || d.connection?.host || "—")}</div></div><div class="form-stack">${field(
      t("仪器操作", "Instrument operation"),
      `<select id="device-operation">${Object.keys(d.operations)
        .map(
          (k) => `<option value="${esc(k)}">${esc(operationName(k))}</option>`,
        )
        .join("")}</select>`,
    )}<p id="operation-description" class="inline-note"></p><div id="operation-parameters" class="form-grid"></div><button class="button primary" id="device-invoke">${icon("play")}${t("执行操作", "Run operation")}</button></div><section id="device-response" class="device-response" aria-live="polite"><h3>${t("返回内容", "Response")}</h3><p class="inline-note">${t("执行后显示仪器返回内容", "The instrument response appears here after execution")}</p></section><div class="actions"><button class="button small" id="device-reconnect">${icon("refresh")}${t("重新连接", "Reconnect")}</button><button class="button small" id="device-export">${icon("download")}${t("导出说明", "Export description")}</button></div>${jsonDetails(d, t("完整仪器说明", "Full instrument description"))}`,
    t("仪器说明", "Instrument description"),
  );
  $("#modal").classList.add("inspector");
  function renderOperation() {
    const op = $("#device-operation").value;
    $("#operation-parameters").innerHTML = parametersHTML(d.operations[op]);
    $("#operation-description").textContent =
      op === "identify" && d.driver === "scpi"
        ? t(
            "发送 *IDN?，读取制造商、型号、序列号与固件版本。",
            "Send *IDN? to read manufacturer, model, serial number and firmware.",
          )
        : d.operations[op].description || "";
  }
  renderOperation();
  $("#device-operation").onchange = renderOperation;
  $("#device-reconnect").onclick = (e) =>
    busy(e.currentTarget, async () => {
      await api("devices/" + encodeURIComponent(id) + "/reconnect", {});
      toast(t("驱动已重新连接", "Driver reconnected"));
      emit("refresh");
    });
  $("#device-export").onclick = (e) =>
    busy(e.currentTarget, async () => {
      const record = await api(
        "devices/" + encodeURIComponent(id) + "/configuration",
      );
      const url = URL.createObjectURL(
        new Blob([JSON.stringify(record, null, 2)], {
          type: "application/json",
        }),
      );
      const a = document.createElement("a");
      a.href = url;
      a.download = id + ".json";
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
  $("#device-invoke").onclick = (e) =>
    busy(e.currentTarget, async () => {
      const op = $("#device-operation").value;
      const args = parameterValues(
        $("#operation-parameters"),
        d.operations[op],
      );
      const run = await api("runs", {
        name: (d.name || d.id) + " · " + operationName(op),
        request_id: uniqueID(),
        steps: [
          { id: "operation", device: id, operation: op, arguments: args },
        ],
      });
      emit("refresh");
      const output = $("#device-response");
      const trace = () => {
        const b = $("[data-device-run]", output);
        if (b) b.onclick = () => emit("run", run.id);
      };
      let cursor = 0;
      while (body.isConnected && $("#modal").open) {
        const page = await api(
          "runs/" + encodeURIComponent(run.id) + "/operations?limit=1",
        );
        if (!body.isConnected) break;
        const operation = page.operations[0];
        output.innerHTML = `<div class="section-title"><h3>${t("返回内容", "Response")}</h3>${badge(operation?.state || "queued")}</div>${operation?.error ? `<p class="error-text">${esc(operation.error)}</p>` : operationResult(operation?.result)}<button class="button small" data-device-run>${t("查看实验记录", "View experiment record")}${icon("arrow")}</button>`;
        trace();
        if (
          operation &&
          ["completed", "failed", "cancelled", "interrupted"].includes(
            operation.state,
          )
        )
          break;
        const events = await api(
          "events?run_id=" +
            encodeURIComponent(run.id) +
            "&after=" +
            cursor +
            "&wait=2",
        );
        cursor = events.cursor;
      }
      emit("refresh");
    });
}
