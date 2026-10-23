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
  readJSON,
} from "./core.js";
export function renderResources() {
  const rows = state.resources.allocation || [];
  return `<div class="page-heading"><div><span class="eyebrow">RESOURCES</span><h1>${t("运行资源", "Resources")}</h1><p>${t("查看仪器、共享对象与计算容量的使用情况。", "See how instruments, shared resources and compute capacity are being used.")}</p></div><button class="button primary" id="resources-edit">${icon("settings")}${t("配置可用数量", "Configure capacity")}</button></div><div class="resource-grid">${rows.map((r) => `<article class="resource-card"><div class="resource-card-top"><h3>${esc(r.resource.replace(/^(pool|device|shared):/, ""))}</h3><span>${r.resource.startsWith("device:") ? t("仪器", "Device") : r.resource.startsWith("pool:") ? t("计算与许可", "Capacity") : t("共享对象", "Shared")}</span></div><div class="resource-quantity">${r.used} <small>/ ${r.capacity}</small></div><small>${t("使用中 / 可用总量", "In use / total capacity")}</small><div class="progress-track" role="meter" aria-label="${esc(r.resource)}" aria-valuenow="${r.used}" aria-valuemin="0" aria-valuemax="${r.capacity}"><i style="width:${Math.min(100, (r.used / r.capacity) * 100)}%"></i></div></article>`).join("") || `<div class="panel full">${empty("layers", t("配置实验使用的资源", "Configure experiment resources"), t("设备注册后会自动出现在这里，也可以添加 CPU、GPU 或软件许可的可用数量。", "Registered devices appear here automatically. You can also define CPU, GPU and software license capacities."))}</div>`}</div><div class="section-title"><h2>${t("已安装适配器", "Installed adapters")}</h2></div><div class="panel" id="adapter-panel"></div>`;
}
export async function bindResources() {
  $("#resources-edit").onclick = editResources;
  try {
    const adapters = await api("adapters");
    const root = $("#adapter-panel");
    if (!root) return;
    root.innerHTML = `<div class="table-wrap"><table><thead><tr><th>${t("适配器", "Adapter")}</th><th>${t("用途", "Purpose")}</th><th>${t("来源", "Source")}</th></tr></thead><tbody>${adapters.map((a) => `<tr><td><strong>${esc(a.name)}</strong></td><td>${esc(a.description || a.entry_point || "")}</td><td><span class="badge">${esc(a.package || t("内置", "Built in"))}${a.version ? " " + esc(a.version) : ""}</span></td></tr>`).join("")}</tbody></table></div>`;
  } catch (e) {
    toast(e.message, true);
  }
}
export function editResources() {
  const body = modal(
    t("配置可用数量", "Configure capacity"),
    `<p class="inline-note" style="margin-bottom:20px">${t("实验声明所需数量，服务统一分配。设备并发数量由对应驱动说明。", "Experiments request quantities and the service allocates them. Device concurrency is declared by each driver.")}</p><div id="resource-edit-rows" class="form-stack"></div><button class="button small" id="resource-add" style="margin-top:18px">${icon("plus")}${t("添加资源", "Add resource")}</button><div class="form-actions"><button class="button" id="resource-cancel">${t("取消", "Cancel")}</button><button class="button primary" id="resource-save">${t("保存数量", "Save capacities")}</button></div>`,
    "RESOURCES",
  );
  function add(name = "", count = 1) {
    const row = document.createElement("div");
    row.className = "form-grid";
    row.dataset.resourceRow = "";
    row.innerHTML =
      field(
        t("资源名称", "Resource name"),
        `<input data-resource-name value="${esc(name)}" placeholder="cpu / gpu / solver">`,
      ) +
      `<div class="actions" style="align-items:end">${field(t("可用数量", "Capacity"), `<input data-resource-count type="number" min="1" step="1" value="${count}">`)}<button class="icon-button" title="${t("移除", "Remove")}" aria-label="${t("移除", "Remove")}">${icon("close")}</button></div>`;
    row.querySelector("button").onclick = () => row.remove();
    $("#resource-edit-rows").append(row);
  }
  Object.entries(state.resources.capacities || {}).forEach(([k, v]) =>
    add(k, v),
  );
  if (!Object.keys(state.resources.capacities || {}).length) add();
  $("#resource-add").onclick = () => add();
  $("#resource-cancel").onclick = closeModal;
  $("#resource-save").onclick = (e) =>
    busy(e.currentTarget, async () => {
      const capacities = {};
      for (const row of $$("[data-resource-row]", body)) {
        const name = $("[data-resource-name]", row).value.trim(),
          count = Number($("[data-resource-count]", row).value);
        if (!name) continue;
        if (name in capacities)
          throw Error(t("名称重复：", "Duplicate resource: ") + name);
        if (!Number.isInteger(count) || count < 1)
          throw Error(
            t("可用数量应为正整数", "Capacity must be a positive integer"),
          );
        capacities[name] = count;
      }
      await api("resources", { capacities });
      closeModal();
      emit("refresh");
      toast(t("资源数量已保存", "Resource capacities saved"));
    });
}
