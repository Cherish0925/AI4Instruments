export const $ = (selector, root = document) => root.querySelector(selector);
export const $$ = (selector, root = document) => [
  ...root.querySelectorAll(selector),
];
const initial = new URLSearchParams(location.hash.slice(1));
export const state = {
  token: initial.get("token") || sessionStorage.getItem("iop-token") || "",
  view:
    initial.get("view") ||
    (location.hash.includes("=") ? "overview" : location.hash.slice(1)) ||
    "overview",
  lang: localStorage.getItem("iop-language") || "zh",
  desktop: initial.get("desktop") === "1",
  status: null,
  devices: [],
  platforms: [],
  runs: [],
  resources: { capacities: {}, allocation: [] },
  inventory: null,
  ui: null,
  connected: false,
};
if (state.token) sessionStorage.setItem("iop-token", state.token);
if (initial.has("token")) history.replaceState(null, "", "#" + state.view);
export const t = (zh, en) => (state.lang === "en" ? en : zh);
export const esc = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const paths = {
  grid: "M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z",
  device: "M5 3h14v18H5z M8 7h8 M8 11h3 M8 16h.01 M12 16h.01 M16 16h.01",
  network: "M9 2h6v5H9z M3 17h6v5H3z M15 17h6v5h-6z M12 7v5 M6 17v-5h12v5",
  activity: "M3 12h4l3-8 4 16 3-8h4",
  layers: "m3 7 9-5 9 5-9 5z M3 12l9 5 9-5 M3 17l9 5 9-5",
  settings:
    "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1z",
  search: "M10.5 3a7.5 7.5 0 1 0 0 15 7.5 7.5 0 0 0 0-15 M16 16l5 5",
  plus: "M12 5v14 M5 12h14",
  close: "m6 6 12 12 M18 6 6 18",
  refresh: "M20 8a8 8 0 1 0 0 8 M20 3v5h-5",
  monitor: "M3 4h18v13H3z M8 21h8 M12 17v4",
  "arrow-up-right": "M6 18 18 6 M6 6h12v12",
  arrow: "M4 12h16 m-6-6 6 6-6 6",
  play: "m8 4 12 8-12 8z",
  check: "m5 12 4 4L19 6",
  file: "M6 2h8l5 5v15H6z M14 2v6h5 M9 12h7 M9 16h7",
  download: "M12 3v12 m-5-5 5 5 5-5 M4 17v4h16v-4",
  upload: "M12 16V4 m-5 5 5-5 5 5 M4 17v4h16v-4",
  clock: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18 M12 7v5l3 2",
  code: "m8 5-6 7 6 7 M16 5l6 7-6 7 M14 3l-4 18",
  menu: "M4 6h16 M4 12h16 M4 18h16",
  sun: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M12 2v2 M12 20v2 M2 12h2 M20 12h2 M5 5l1 1 M18 18l1 1 M5 19l1-1 M18 6l1-1",
  moon: "M20 15A9 9 0 0 1 9 4a9 9 0 1 0 11 11",
  box: "m3 7 9-5 9 5v11l-9 4-9-4z M3 7l9 5 9-5 M12 12v10",
  link: "m10 13 4-4 M8 15l-1 1a4 4 0 0 1-6-6l5-5a4 4 0 0 1 6 0 M16 9l1-1a4 4 0 0 1 6 6l-5 5a4 4 0 0 1-6 0",
  info: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18 M12 10v7 M12 7h.01",
  chevron: "m9 5 7 7-7 7",
  stop: "M6 6h12v12H6z",
};
export const icon = (name) =>
  `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${paths[name] || paths.box}"/></svg>`;
export function icons(root = document) {
  $$("[data-icon]", root).forEach((n) => {
    n.innerHTML = icon(n.dataset.icon);
  });
}
export function translate(root = document) {
  $$("[data-en]", root).forEach((n) => {
    n.dataset.zh ??= n.textContent;
    n.textContent = state.lang === "en" ? n.dataset.en : n.dataset.zh;
  });
  $$("[data-en-placeholder]", root).forEach((n) => {
    n.dataset.zhPlaceholder ??= n.placeholder;
    n.placeholder =
      state.lang === "en" ? n.dataset.enPlaceholder : n.dataset.zhPlaceholder;
  });
  document.documentElement.lang = state.lang === "en" ? "en" : "zh-CN";
}
export async function api(path, body, options = {}) {
  const controller = new AbortController(),
    timer = setTimeout(() => controller.abort(), options.timeout || 30000);
  try {
    const r = await fetch("/v1/" + path, {
      method: body === undefined ? "GET" : "POST",
      headers: {
        Authorization: "Bearer " + state.token,
        "Content-Type": "application/json",
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
    let v;
    try {
      v = await r.json();
    } catch {
      throw Error(
        t(
          "服务返回了无法读取的响应",
          "The service returned an unreadable response",
        ),
      );
    }
    if (!r.ok) {
      const error = Error(v.error || r.statusText);
      error.status = r.status;
      throw error;
    }
    return v;
  } catch (error) {
    if (error.name === "AbortError")
      throw Error(
        t(
          "请求尚未返回，请刷新查看当前状态",
          "The request timed out. Refresh to check its current state.",
        ),
      );
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
export function toast(text, error = false) {
  const el = $("#toast");
  el.textContent = text;
  el.dataset.error = error;
  el.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => (el.hidden = true), error ? 8000 : 4000);
}
export async function busy(button, fn) {
  if (button?.disabled) return;
  const prior = button?.innerHTML;
  if (button) {
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
  }
  try {
    return await fn();
  } catch (e) {
    toast(e.message, true);
    return null;
  } finally {
    if (button) {
      button.disabled = false;
      button.removeAttribute("aria-busy");
      if (prior !== undefined) button.innerHTML = prior;
    }
  }
}
export function modal(title, html, eyebrow = "") {
  const el = $("#modal");
  delete el.dataset.runDetail;
  el.classList.remove("wide", "inspector");
  $("#modal-title").textContent = title;
  $("#modal-eyebrow").textContent = eyebrow;
  $("#modal-body").innerHTML = html;
  icons(el);
  if (!el.open) el.showModal();
  return $("#modal-body");
}
export const closeModal = () => $("#modal").close();
export function operationResult(value) {
  if (value === undefined || value === null)
    return `<p class="inline-note">${t("等待仪器返回", "Waiting for the instrument")}</p>`;
  const labels = {
    manufacturer: t("制造商", "Manufacturer"),
    model: t("型号", "Model"),
    serial_number: t("序列号", "Serial number"),
    firmware: t("固件", "Firmware"),
  };
  if (value.identity)
    return `<div class="identity-grid">${Object.entries(value.identity)
      .map(
        ([k, v]) =>
          `<div><small>${labels[k] || esc(k)}</small><strong>${esc(v)}</strong></div>`,
      )
      .join("")}</div><pre class="response-text">${esc(value.value)}</pre>`;
  if (value.value !== undefined)
    return `<pre class="response-text">${esc((typeof value.value === "object" ? JSON.stringify(value.value, null, 2) : String(value.value)).slice(0, 6000))}${value.unit ? " " + esc(value.unit) : ""}</pre>${String(value.value).length > 6000 ? `<small>${t("显示前 6000 字符，完整内容保存在实验记录中。", "Showing the first 6000 characters. The complete response is in the experiment record.")}</small>` : ""}`;
  if (value.sent === true)
    return `<p class="response-text">${t("命令已发送", "Command sent")} · <code>${esc(value.command)}</code></p>`;
  if (typeof value === "object" && !Array.isArray(value)) {
    const fields = Object.entries(value).filter(
      ([k]) => !["time", "source", "unit"].includes(k),
    );
    if (
      fields.length &&
      fields.every(([, v]) => v === null || typeof v !== "object")
    )
      return `<div class="identity-grid">${fields
        .slice(0, 12)
        .map(
          ([k, v]) =>
            `<div><small>${esc(k)}</small><strong>${esc(v)}${fields.length === 1 && value.unit ? " " + esc(value.unit) : ""}</strong></div>`,
        )
        .join("")}</div>`;
  }
  const text = JSON.stringify(value, null, 2);
  return `<pre class="response-text">${esc(text.slice(0, 6000))}${text.length > 6000 ? "…" : ""}</pre>`;
}
export const field = (label, input, note = "") =>
  `<label class="field"><span>${label}</span>${input}${note ? `<small>${note}</small>` : ""}</label>`;
export const empty = (glyph, title, description, action = "") =>
  `<div class="empty"><span class="empty-icon">${icon(glyph)}</span><h3>${title}</h3><p>${description}</p>${action}</div>`;
export function statusName(value) {
  return (
    {
      queued: t("等待中", "Queued"),
      running: t("运行中", "Running"),
      cancelling: t("正在停止", "Stopping"),
      completed: t("已完成", "Completed"),
      failed: t("未完成", "Failed"),
      cancelled: t("已停止", "Stopped"),
      interrupted: t("已中断", "Interrupted"),
      skipped: t("未执行", "Skipped"),
    }[value] || value
  );
}
export const badge = (value) =>
  `<span class="badge ${esc(value)}"><i></i>${esc(statusName(value))}</span>`;
export function date(value) {
  return value
    ? new Date(value).toLocaleString(state.lang === "en" ? "en-US" : "zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";
}
export function duration(seconds) {
  if (seconds == null) return "—";
  seconds = Math.max(0, Math.floor(seconds));
  return seconds < 60
    ? `${seconds}s`
    : seconds < 3600
      ? `${Math.floor(seconds / 60)}m ${seconds % 60}s`
      : `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}
export const size = (bytes) =>
  bytes < 1024
    ? `${bytes} B`
    : bytes < 1048576
      ? `${(bytes / 1024).toFixed(1)} KB`
      : `${(bytes / 1048576).toFixed(1)} MB`;
export function download(name, data, type = "application/json") {
  const url = URL.createObjectURL(
    new Blob(
      [typeof data === "string" ? data : JSON.stringify(data, null, 2) + "\n"],
      { type },
    ),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export const emit = (name, detail) =>
  document.dispatchEvent(new CustomEvent("iop:" + name, { detail }));
export const go = (view) => emit("navigate", view);
export function jsonDetails(value, label = t("查看原始数据", "Raw data")) {
  return `<details class="raw"><summary>${icon("code")}${label}</summary><pre>${esc(JSON.stringify(value, null, 2))}</pre></details>`;
}
export function readJSON(id) {
  try {
    return JSON.parse($(id).value || "{}");
  } catch {
    throw Error(
      t(
        "JSON 格式不正确，请检查逗号与引号",
        "Invalid JSON. Check commas and quotation marks.",
      ),
    );
  }
}
export const uniqueID = () =>
  globalThis.crypto?.randomUUID?.() ||
  "ui-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2);
