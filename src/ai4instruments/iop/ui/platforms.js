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
  emit,
  download,
  readJSON,
  uniqueID,
} from "./core.js";
export function topology(definition) {
  const nodes = definition.devices || [];
  if (!nodes.length) return "";
  const cols = Math.min(3, nodes.length),
    width = cols * 260 + 40,
    height = Math.ceil(nodes.length / cols) * 120 + 30;
  const points = new Map(
    nodes.map((id, i) => [
      id,
      { x: 30 + (i % cols) * 260, y: 25 + Math.floor(i / cols) * 120 },
    ]),
  );
  const marker = "arrow-" + definition.id;
  return `<div class="topology"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${t("设备与物理连接", "Devices and physical connections")}"><defs><marker id="${esc(marker)}" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 7 3.5 0 7" fill="none" stroke="var(--accent)"/></marker></defs>${(
    definition.connections || []
  )
    .map((c) => {
      const a = points.get(c.from.device),
        b = points.get(c.to.device);
      if (!a || !b) return "";
      const right = b.x > a.x,
        down = b.y > a.y;
      const x1 = a.x + (right ? 210 : down ? 105 : 0),
        y1 = a.y + (right ? 28 : down ? 56 : 28),
        x2 = b.x + (right ? 0 : down ? 105 : 210),
        y2 = b.y + (right ? 28 : down ? 0 : 28);
      return `<path class="edge" marker-end="url(#${esc(marker)})" d="M${x1} ${y1} C${(x1 + x2) / 2} ${y1} ${(x1 + x2) / 2} ${y2} ${x2} ${y2}"><title>${esc(c.from.device + ":" + c.from.port + " → " + c.to.device + ":" + c.to.port + " · " + c.kind)}</title></path>`;
    })
    .join("")}${nodes
    .map((id) => {
      const p = points.get(id),
        d = state.devices.find((v) => v.id === id),
        label = d?.name || id;
      return `<g><title>${esc(label + " · " + id)}</title><rect class="node" x="${p.x}" y="${p.y}" width="210" height="56" rx="9"/><circle cx="${p.x + 18}" cy="${p.y + 23}" r="3" fill="var(--accent)"/><text x="${p.x + 31}" y="${p.y + 27}">${esc(label.length > 23 ? label.slice(0, 22) + "…" : label)}</text><text class="port-text" x="${p.x + 31}" y="${p.y + 43}">${esc(d?.driver || t("待注册", "Not registered"))}</text></g>`;
    })
    .join("")}</svg></div>`;
}
export function platformCard(record, compact = false) {
  const d = record.definition;
  return `<article class="platform-card"><div class="platform-heading"><div><h3>${esc(d.name || d.id)}</h3><small>${d.devices.length} ${t("台设备", "devices")} · ${t("配置", "Revision")} ${record.revision}${record.active_runs.length ? " · " + record.active_runs.length + " " + t("个实验运行中", "active experiments") : ""}</small></div><button class="button small" data-platform-edit="${esc(d.id)}">${t("配置", "Configure")}${icon("chevron")}</button></div>${topology(d)}${!compact && d.connections.length ? `<details class="raw" style="margin:15px 20px"><summary>${icon("network")}${d.connections.length} ${t("条物理连接", "physical connections")}</summary><div class="table-wrap"><table><tbody>${d.connections.map((c) => `<tr><td>${esc(c.from.device)}<small>${esc(c.from.port)}</small></td><td>${icon("arrow")}</td><td>${esc(c.to.device)}<small>${esc(c.to.port)}</small></td><td>${esc(c.kind)}</td></tr>`).join("")}</tbody></table></div></details>` : ""}<div class="platform-bottom"><span class="muted">${esc(d.description || d.id)}</span>${Object.keys(
    d.procedures || {},
  )
    .map(
      (name) =>
        `<button class="button small" data-procedure="${esc(name)}" data-platform="${esc(d.id)}">${icon("play")}${name === "initialize" ? t("初始化", "Initialize") : esc(name)}</button>`,
    )
    .join("")}</div></article>`;
}
export function bindCards(root = document) {
  $$("[data-platform-edit]", root).forEach(
    (b) =>
      (b.onclick = () =>
        editPlatform(
          state.platforms.find((p) => p.id === b.dataset.platformEdit),
        )),
  );
  $$("[data-procedure]", root).forEach(
    (b) =>
      (b.onclick = () =>
        busy(b, async () => {
          const run = await api(
            "platforms/" +
              encodeURIComponent(b.dataset.platform) +
              "/procedures/" +
              encodeURIComponent(b.dataset.procedure),
            { request_id: uniqueID() },
          );
          emit("run", run.id);
          emit("refresh");
        })),
  );
}
export function renderPlatforms() {
  return `<div class="page-heading"><div><span class="eyebrow">EXPERIMENTAL PLATFORMS</span><h1>${t("实验平台", "Platforms")}</h1><p>${t("将仪器、物理连接和初始化方法组织为可重复使用的实验系统。", "Organize instruments, physical connections and initialization into reusable experimental systems.")}</p></div><div class="actions"><label class="button">${icon("upload")}${t("导入配置", "Import")}<input id="platform-import" type="file" accept=".json" hidden></label><button class="button primary" id="platform-new">${icon("plus")}${t("新建平台", "New platform")}</button></div></div>${state.platforms.length ? state.platforms.map((p) => platformCard(p)).join("") : `<div class="panel">${empty("network", t("建立你的实验平台", "Create your experimental platform"), t("选取已经注册的仪器，填写它们之间的连接，并保存平台配置。", "Choose registered instruments, describe their connections and save the platform."), `<button class="button" id="platform-empty-new">${icon("plus")}${t("新建平台", "New platform")}</button>`)}</div>`}`;
}
export function bindPlatforms() {
  bindCards();
  $("#platform-new").onclick = () => editPlatform();
  $("#platform-empty-new")?.addEventListener("click", () => editPlatform());
  $("#platform-import").onchange = async (e) => {
    try {
      const f = e.target.files[0];
      if (f)
        editPlatform({ definition: JSON.parse(await f.text()), revision: 0 });
    } catch (error) {
      toast(error.message, true);
    }
  };
}
export function editPlatform(record) {
  const d = record?.definition || {
    schema_version: 1,
    id: "",
    name: "",
    devices: [],
    connections: [],
    resources: [],
    procedures: {},
  };
  let links = structuredClone(d.connections || []),
    revision = record?.revision || 0;
  const body = modal(
    record
      ? t("配置实验平台", "Configure platform")
      : t("新建实验平台", "New platform"),
    `<div class="form-stack"><div class="form-grid">${field(t("平台名称", "Platform name"), `<input id="platform-name" value="${esc(d.name || "")}" placeholder="${t("例如：材料表征平台", "e.g. Materials characterization")}">`)}${field(t("平台 ID", "Platform ID"), `<input id="platform-id" value="${esc(d.id)}" ${revision ? "readonly" : ""} placeholder="materials-bench">`)}<div class="full">${field(t("平台用途", "Description"), `<input id="platform-description" value="${esc(d.description || "")}" placeholder="${t("此平台用于哪些实验", "What experiments is this platform used for?")}">`)}</div></div><div><h3 style="margin-bottom:12px">${t("平台仪器", "Instruments")}</h3><div class="selection-list">${state.devices.map((v) => `<label class="selection-item"><input type="checkbox" name="platform-device" value="${esc(v.id)}" ${d.devices.includes(v.id) ? "checked" : ""}>${esc(v.name || v.id)}<small>${esc(v.id)}</small></label>`).join("") || `<p class="inline-note">${t("请先在“仪器与软件”中注册设备。", "Register devices in Instruments & software first.")}</p>`}</div></div><div><div class="section-title" style="margin:0 0 10px"><h3>${t("物理连接", "Physical connections")}</h3><button class="button small" id="connection-add">${icon("plus")}${t("添加连接", "Add connection")}</button></div><p class="inline-note">${t("记录信号线、触发线、光路或流体管路；实验的执行顺序在任务中设置。", "Describe signal, trigger, optical or fluid connections. Execution order is defined by the experiment.")}</p><div id="connection-rows"></div></div><details class="raw"><summary>${icon("code")}${t("完整配置 · 共享资源与初始化方法", "Full configuration · shared resources and initialization")}</summary><textarea id="platform-json" spellcheck="false">${esc(JSON.stringify(d, null, 2))}</textarea><div style="padding:12px 15px" class="actions"><button class="button small" id="platform-sync-json">${t("从表单生成", "Update from form")}</button><button class="button small" id="platform-save-json">${t("保存此配置", "Save this configuration")}</button></div></details></div><div class="form-actions"><button class="button" id="platform-export">${icon("download")}${t("导出配置", "Export")}</button><button class="button primary" id="platform-save">${t("保存平台", "Save platform")}</button></div>`,
    "PLATFORM",
  );
  $("#modal").classList.add("wide");
  function members() {
    return $$('[name="platform-device"]', body)
      .filter((n) => n.checked)
      .map((n) => n.value);
  }
  function capture() {
    links = $$(".connection-row", body).map((row) => ({
      from: {
        device: $('[data-side="from"]', row).value,
        port: $('[data-port="from"]', row).value.trim(),
      },
      to: {
        device: $('[data-side="to"]', row).value,
        port: $('[data-port="to"]', row).value.trim(),
      },
      kind: $("[data-kind]", row).value.trim(),
    }));
  }
  function connections() {
    const ids = members();
    $("#connection-rows").innerHTML = links
      .map(
        (c, i) =>
          `<div class="connection-row"><select data-side="from" aria-label="${t("起点设备", "Source device")}">${ids.map((id) => `<option value="${esc(id)}" ${c.from.device === id ? "selected" : ""}>${esc(id)}</option>`).join("")}</select><input data-port="from" value="${esc(c.from.port)}" placeholder="${t("输出端口", "Output port")}" aria-label="${t("输出端口", "Output port")}">${icon("arrow")}<select data-side="to" aria-label="${t("终点设备", "Target device")}">${ids.map((id) => `<option value="${esc(id)}" ${c.to.device === id ? "selected" : ""}>${esc(id)}</option>`).join("")}</select><input data-port="to" value="${esc(c.to.port)}" placeholder="${t("输入端口", "Input port")}" aria-label="${t("输入端口", "Input port")}"><input data-kind value="${esc(c.kind)}" placeholder="${t("类型，如 trigger", "Kind, e.g. trigger")}" aria-label="${t("连接类型", "Connection kind")}"><button class="icon-button" data-remove="${i}" aria-label="${t("移除连接", "Remove connection")}">${icon("close")}</button></div>`,
      )
      .join("");
    $$("[data-remove]", body).forEach(
      (b) =>
        (b.onclick = () => {
          capture();
          links.splice(Number(b.dataset.remove), 1);
          connections();
        }),
    );
  }
  function definition() {
    capture();
    return {
      ...d,
      id: $("#platform-id").value.trim(),
      name: $("#platform-name").value.trim() || $("#platform-id").value.trim(),
      description: $("#platform-description").value.trim(),
      devices: members(),
      connections: links,
    };
  }
  async function save(value) {
    await api("platforms", { definition: value, expected_revision: revision });
    closeModal();
    emit("refresh");
    toast(t("平台配置已保存", "Platform saved"));
  }
  connections();
  $$('[name="platform-device"]', body).forEach(
    (n) =>
      (n.onchange = () => {
        capture();
        connections();
      }),
  );
  $("#connection-add").onclick = () => {
    capture();
    const ids = members();
    if (ids.length < 2)
      return toast(
        t("先选择至少两台仪器", "Choose at least two instruments first"),
        true,
      );
    links.push({
      from: { device: ids[0], port: "" },
      to: { device: ids[1], port: "" },
      kind: "",
    });
    connections();
  };
  $("#platform-sync-json").onclick = () =>
    ($("#platform-json").value = JSON.stringify(definition(), null, 2));
  $("#platform-save-json").onclick = (e) =>
    busy(e.currentTarget, () => save(readJSON("#platform-json")));
  $("#platform-save").onclick = (e) =>
    busy(e.currentTarget, () => save(definition()));
  $("#platform-export").onclick = () => {
    const value = definition();
    download((value.id || "platform") + ".json", value);
  };
}
