import {
  $,
  $$,
  state,
  t,
  esc,
  icon,
  icons,
  translate,
  api,
  busy,
  toast,
  modal,
  closeModal,
  empty,
  badge,
  date,
  duration,
  download,
  go,
  emit,
} from "./core.js";
import {
  renderDevices,
  bindDevices,
  scan,
  registerDevice,
  inspectDevice,
} from "./devices.js";
import {
  renderPlatforms,
  bindPlatforms,
  platformCard,
  bindCards,
  editPlatform,
} from "./platforms.js";
import {
  renderRuns,
  bindRuns,
  runRows,
  bindRunRows,
  newExperiment,
  inspectRun,
} from "./runs.js";
import { renderResources, bindResources } from "./resources.js";
const titles = {
  overview: () => t("概览", "Overview"),
  devices: () => t("仪器与软件", "Instruments & software"),
  platforms: () => t("实验平台", "Platforms"),
  runs: () => t("实验任务", "Experiments"),
  resources: () => t("运行资源", "Resources"),
  settings: () => t("连接与设置", "Connection & settings"),
};
let refreshing = false,
  scheduled = null,
  lastInventory = 0,
  lastRender = "",
  needRefresh = false;
function overview() {
  const s = state.status,
    active = state.runs.filter((r) =>
      ["queued", "running", "cancelling"].includes(r.state),
    ),
    hasPlatforms = state.platforms.length > 0;
  return `<div class="page-heading"><div><span class="eyebrow">LABORATORY OVERVIEW</span><h1>${t("实验室概览", "Laboratory overview")}</h1><p>${t("仪器、实验平台与正在进行的研究。", "Instruments, experimental platforms and work in progress.")}</p></div><div class="live-label"><span class="dot ${state.connected ? "online" : "offline"}"></span>${state.connected ? t("运行服务在线", "Service online") : t("等待连接", "Awaiting connection")}</div></div><div class="stats">${[
    [
      t("已注册设备", "Registered devices"),
      s?.devices,
      "device",
      t("实体仪器与软件", "Instruments and software"),
    ],
    [
      t("实验平台", "Platforms"),
      s?.platforms,
      "network",
      t("设备、连接与初始化", "Devices and connections"),
    ],
    [
      t("运行中的实验", "Running experiments"),
      s?.active_runs,
      "activity",
      (s?.queued_runs ?? 0) + " " + t("个等待中", "queued"),
    ],
    [
      t("正在执行的操作", "Active operations"),
      s?.active_operations,
      "layers",
      t("按依赖与资源调度", "Scheduled by dependencies and resources"),
    ],
  ]
    .map(
      ([label, n, glyph, note]) =>
        `<div class="stat"><div class="stat-label">${label}${icon(glyph)}</div><div class="stat-value">${n ?? "—"}</div><small>${note}</small></div>`,
    )
    .join("")}</div>${
    !hasPlatforms
      ? `<section class="onboarding"><div><span class="eyebrow">SET UP YOUR LABORATORY</span><h2>${state.devices.length ? t("把已注册仪器组成实验平台", "Build a platform from your instruments") : t("连接你的第一个实验平台", "Connect your first experimental platform")}</h2><p>${t("IOP 在这台计算机上持续运行。先接入仪器和软件，保存平台连接关系，然后让人或 Agent 提交实验程序。", "IOP runs continuously on this computer. Register instruments and software, describe their connections, then submit experiments from your programs or agents.")}</p><div class="actions"><button class="button primary" id="overview-discover">${icon("search")}${t("发现设备", "Discover devices")}</button><button class="button" id="overview-platform">${icon("network")}${t("建立平台", "Create platform")}</button></div></div><div class="setup-flow">${[
          [
            "device",
            t("接入仪器与软件", "Register instruments & software"),
            t(
              "识别连接，选择驱动与可用操作",
              "Identify connections, drivers and operations",
            ),
          ],
          [
            "network",
            t("保存实验平台", "Describe the platform"),
            t(
              "配置物理连接、共享资源与初始化",
              "Set connections, shared resources and initialization",
            ),
          ],
          [
            "play",
            t("执行实验，保留结果", "Run experiments and retain results"),
            t(
              "串行与并行执行，过程与数据统一保存",
              "Coordinate operations and retain data together",
            ),
          ],
        ]
          .map(
            ([glyph, title, note]) =>
              `<div class="setup-step"><span class="step-icon">${icon(glyph)}</span><div><strong>${title}</strong><small>${note}</small></div></div>`,
          )
          .join("")}</div></section>`
      : ""
  }<div class="layout-two"><div class="stack"><section ${hasPlatforms ? "" : "hidden"}><div class="section-title" style="margin-top:0"><h2>${t("实验平台", "Platforms")}</h2><button class="button ghost small" data-go="platforms">${t("查看全部", "View all")}${icon("arrow")}</button></div>${
    hasPlatforms
      ? state.platforms
          .slice(0, 3)
          .map((p) => platformCard(p, true))
          .join("")
      : `<div class="panel">${empty("network", t("还没有平台配置", "No platform configuration"), t("平台将仪器、连接关系和初始化方法保存在一起。", "A platform keeps instruments, their connections and initialization together."), `<button class="button small" id="overview-new-platform">${icon("plus")}${t("新建平台", "New platform")}</button>`)}</div>`
  }</section><section class="panel"><div class="panel-header"><h2>${t("最近实验", "Recent experiments")}</h2><button class="button ghost small" data-go="runs">${t("查看记录", "View history")}${icon("arrow")}</button></div>${state.runs.length ? `<div class="table-wrap"><table><tbody>${runRows(state.runs.slice(0, 5), true)}</tbody></table></div>` : empty("file", t("实验记录将在这里保留", "Experiment history lives here"), t("每次实验都保留操作、结果和输出文件。", "Each experiment retains its operations, results and output files."))}</section></div><div class="stack"><section class="panel"><div class="panel-header"><h2>${t("当前执行", "Now running")}</h2><span class="count">${active.length}</span></div>${
    active.length
      ? `<div class="panel-body"><ul class="mini-list">${active
          .slice(0, 6)
          .map(
            (r) =>
              `<li><span class="device-icon">${icon("activity")}</span><button class="button ghost small" data-run="${esc(r.id)}">${esc(r.name || r.id)}</button>${badge(r.state)}</li>`,
          )
          .join("")}</ul></div>`
      : empty(
          "clock",
          t("等待下一次实验", "Ready for the next experiment"),
          t(
            "服务保持运行，可随时接收本地或远端程序的任务。",
            "The service stays available for experiments from local and remote programs.",
          ),
          `<button class="button small" id="overview-new-run">${icon("plus")}${t("新建实验", "New experiment")}</button>`,
        )
  }</section><section class="panel"><div class="panel-header"><h2>${t("运行服务", "Runtime service")}</h2><span class="dot ${state.connected ? "online" : "offline"}"></span></div><div class="panel-body"><div class="settings-row"><span>${t("计算机", "Computer")}</span><code>${esc(s?.hostname || "—")}</code></div><div class="settings-row"><span>${t("版本", "Version")}</span><code>${esc(s?.version || "—")}</code></div><div class="settings-row"><span>${t("运行时间", "Uptime")}</span><code>${duration(s?.uptime_s)}</code></div><div class="settings-row"><span>${t("运行地址", "Address")}</span><code>${esc(location.host)}</code></div></div></section></div></div>`;
}
function bindOverview() {
  bindCards();
  bindRunRows();
  $$("[data-go]").forEach((b) => (b.onclick = () => navigate(b.dataset.go)));
  $("#overview-discover")?.addEventListener("click", async () => {
    navigate("devices");
    await scan($("#scan"));
  });
  $("#overview-platform")?.addEventListener("click", () => editPlatform());
  $("#overview-new-platform")?.addEventListener("click", () => editPlatform());
  $("#overview-new-run")?.addEventListener("click", () => newExperiment());
}
function settings() {
  const s = state.status;
  return `<div class="page-heading"><div><span class="eyebrow">PREFERENCES</span><h1>${t("连接与设置", "Connection & settings")}</h1><p>${t("桌面与浏览器使用同一个运行服务，切换后实验继续进行。", "Desktop and browser use the same service. Experiments continue when you switch or close a window.")}</p></div></div><div class="layout-two"><div class="panel"><section class="settings-section"><h3>${t("界面", "Appearance")}</h3><div class="settings-row"><span>${t("主题", "Theme")}</span><select id="theme-select"><option value="light">${t("浅色", "Light")}</option><option value="dark">${t("深色", "Dark")}</option><option value="system">${t("跟随系统", "System")}</option></select></div><div class="settings-row"><span>${t("语言", "Language")}</span><select id="language-select"><option value="zh">简体中文</option><option value="en">English</option></select></div></section><section class="settings-section"><h3>${t("使用方式", "Application mode")}</h3><p class="inline-note">${state.desktop ? t("当前在桌面窗口中。浏览器可同时连接并查看相同的实验。", "You are using the desktop window. A browser can connect to the same experiments at the same time.") : t("当前在浏览器中。安装桌面组件后，可从系统应用菜单直接打开独立窗口。", "You are using a browser. Install the desktop component to open a dedicated window from your application menu.")}</p><button class="button" id="settings-mode" style="margin-top:15px">${icon("monitor")}${state.desktop ? t("在浏览器中打开", "Open in browser") : t("打开桌面应用", "Open desktop app")}</button></section><section class="settings-section"><h3>${t("服务连接", "Service connection")}</h3><div class="settings-row"><span>${t("地址", "Address")}</span><code>${esc(location.origin)}</code></div><div class="settings-row"><span>${t("连接状态", "Connection")}</span><span>${state.connected ? t("已连接", "Connected") : t("未连接", "Disconnected")}</span></div><button class="button small" id="settings-connection" style="margin-top:18px">${t("更换连接令牌", "Change connection token")}</button></section></div><div class="stack"><section class="panel"><div class="panel-header"><h2>IOP Runtime</h2><span class="badge">${esc(s?.version || "—")}</span></div><div class="panel-body"><p class="inline-note">${t("运行在实验室计算机上的仪器运行服务。人、Agent 与实验程序使用相同的接口、配置和记录。", "A persistent instrument service on the laboratory computer. People, agents and experiment programs share the same interface, configuration and records.")}</p><div class="settings-row"><span>${t("系统", "System")}</span><code>${esc(s?.system || "—")}</code></div><div class="settings-row"><span>${t("计算机", "Computer")}</span><code>${esc(s?.hostname || "—")}</code></div><div class="settings-row"><span>${t("操作执行线程", "Operation workers")}</span><code>${s?.workers ?? "—"}</code></div><div class="settings-row"><span>${t("程序执行数量", "Program slots")}</span><code>${s?.package_workers ?? "—"}</code></div><div class="actions" style="margin-top:23px"><a class="button small" href="https://github.com/Cherish0925/AI4Instruments/tree/main/iop" target="_blank" rel="noreferrer">${t("使用说明", "Documentation")}${icon("arrow-up-right")}</a><a class="button small" href="https://github.com/Cherish0925/AI4Instruments/releases/latest" target="_blank" rel="noreferrer">${t("下载更新", "Downloads")}${icon("arrow-up-right")}</a></div></div></section><section class="panel"><div class="panel-header"><h2>${t("Agent 接入", "Agent connection")}</h2><span class="badge">MCP · API · SDK</span></div><div class="panel-body"><p class="inline-note">${t("Agent 读取已有仪器说明和平台配置，再提交实验。只需补充尚未记录的实际接线、样品和实验要求。", "Agents read existing instrument and platform descriptions, then submit experiments. Supply only physical wiring, sample details and requirements that have not been recorded.")}</p><div class="settings-row"><span>${t("读取实验室配置", "Read laboratory setup")}</span><code>iop context --start</code></div><div class="settings-row"><span>${t("MCP 连接配置", "MCP connection settings")}</span><code>iop mcp-config</code></div><div class="actions" style="margin-top:18px"><button class="button small" id="agent-context-export">${icon("download")}${t("导出实验室说明", "Export laboratory description")}</button><a class="button small" href="https://github.com/Cherish0925/AI4Instruments/blob/main/iop/agent-setup${state.lang === "zh" ? ".zh-CN" : ""}.md" target="_blank" rel="noreferrer">${t("接入说明", "Connection guide")}${icon("arrow-up-right")}</a></div></div></section></div></div>`;
}
function bindSettings() {
  $("#theme-select").value = localStorage.getItem("iop-theme") || "light";
  $("#theme-select").onchange = (e) => setTheme(e.target.value);
  $("#language-select").value = state.lang;
  $("#language-select").onchange = (e) => {
    state.lang = e.target.value;
    localStorage.setItem("iop-language", state.lang);
    translate();
    updateConnection(state.connected);
    updateServiceLabels();
    updateMode();
    render(true);
  };
  $("#settings-mode").onclick = switchMode;
  $("#settings-connection").onclick = connectionDialog;
  $("#agent-context-export").onclick = (event) =>
    busy(event.currentTarget, async () => {
      download("iop-laboratory.json", await api("context"));
    });
}
function setTheme(theme) {
  localStorage.setItem("iop-theme", theme);
  document.documentElement.dataset.theme =
    theme === "system"
      ? matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light"
      : theme;
}
function render(force = false) {
  const signature = JSON.stringify([
    state.view,
    state.lang,
    state.devices,
    state.platforms,
    state.runs,
    state.resources,
    state.status?.devices,
    state.status?.active_runs,
    state.status?.active_operations,
    state.status?.queued_runs,
  ]);
  if (!force && signature === lastRender) return;
  if (
    !force &&
    $("#content").contains(document.activeElement) &&
    ["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName)
  )
    return;
  lastRender = signature;
  $("#view-title").textContent = titles[state.view]();
  document.title = "IOP Runtime · " + titles[state.view]();
  $$("[data-view]").forEach((b) =>
    b.setAttribute(
      "aria-current",
      b.dataset.view === state.view ? "page" : "false",
    ),
  );
  const views = {
    overview: [overview, bindOverview],
    devices: [renderDevices, bindDevices],
    platforms: [renderPlatforms, bindPlatforms],
    runs: [renderRuns, bindRuns],
    resources: [renderResources, bindResources],
    settings: [settings, bindSettings],
  };
  const [markup, bind] = views[state.view];
  $("#content").innerHTML = markup();
  bind();
}
function navigate(view) {
  if (!titles[view]) view = "overview";
  state.view = view;
  history.replaceState(null, "", "#" + view);
  $("#sidebar").classList.remove("open");
  render(true);
  window.scrollTo(0, 0);
}
function updateConnection(connected, error) {
  state.connected = connected;
  $("#connection-dot").className = "dot " + (connected ? "online" : "offline");
  $("#service-caption").textContent = connected
    ? t("运行服务在线", "Service online")
    : t("未连接到服务", "Service unavailable");
  const banner = $("#connection-banner");
  banner.hidden = connected;
  if (!connected) {
    banner.innerHTML = `<span>${esc(error || t("请输入连接令牌，或从 iop open 打开界面。", "Enter a connection token, or open the interface with iop open."))}</span><button class="button small" id="connection-action">${t("连接设置", "Connect")}</button>`;
    $("#connection-action").onclick = connectionDialog;
  }
  $("#new-run").disabled = !connected;
}
function updateServiceLabels() {
  if (!state.status) return;
  $("#footer-status").textContent =
    t("服务持续运行 · ", "Service running · ") +
    duration(state.status.uptime_s);
  $("#updated-at").textContent =
    t("更新于 ", "Updated ") +
    new Date().toLocaleTimeString(state.lang === "en" ? "en-US" : "zh-CN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
}
export async function refresh(force = false) {
  if (refreshing) {
    needRefresh ||= force;
    return;
  }
  if (!state.token) {
    updateConnection(false);
    render();
    return;
  }
  refreshing = true;
  clearTimeout(scheduled);
  try {
    const full = force || Date.now() - lastInventory > 15000;
    const tasks = [api("status"), api("runs?limit=200&details=false")];
    if (full) tasks.push(api("devices"), api("platforms"));
    const values = await Promise.all(tasks);
    state.status = values[0];
    state.resources = values[0].resources;
    state.runs = values[1];
    if (full) {
      state.devices = values[2];
      state.platforms = values[3];
      lastInventory = Date.now();
    }
    if (!state.ui) {
      const [ui, inventory] = await Promise.all([
        api("ui"),
        api("discovery?cached=true"),
      ]);
      state.ui = ui;
      state.inventory = inventory.updated ? inventory : null;
      updateMode();
    }
    updateConnection(true);
    $("#nav-devices").textContent = state.status.devices;
    $("#nav-platforms").textContent = state.status.platforms;
    $("#nav-runs").textContent = state.status.active_runs || "";
    $("#sidebar-version").textContent = state.status.version;
    $("#host-label").textContent = state.status.hostname;
    updateServiceLabels();
    render(force);
  } catch (error) {
    updateConnection(
      false,
      error.status === 401
        ? t(
            "连接令牌不正确，请重新连接。",
            "The connection token is incorrect. Reconnect to the service.",
          )
        : t(
            "暂时无法连接运行服务。",
            "The runtime service is currently unavailable.",
          ),
    );
  } finally {
    refreshing = false;
    const next = needRefresh;
    needRefresh = false;
    scheduled = setTimeout(
      () => refresh(next),
      next
        ? 0
        : document.hidden
          ? 20000
          : state.status?.active_runs
            ? 3000
            : 10000,
    );
  }
}
function connectionDialog() {
  modal(
    t("连接运行服务", "Connect to runtime"),
    `<p class="inline-note" style="margin-bottom:20px">${esc(location.origin)}</p><label class="field"><span>${t("连接令牌", "Connection token")}</span><input id="connection-token" type="password" autocomplete="off" placeholder="${t("来自服务配置或启动命令", "From the service configuration or launch command")}"></label><div class="form-actions"><button class="button" id="connection-cancel">${t("取消", "Cancel")}</button><button class="button primary" id="connection-save">${t("连接", "Connect")}</button></div>`,
    "CONNECTION",
  );
  $("#connection-cancel").onclick = closeModal;
  $("#connection-save").onclick = (e) =>
    busy(e.currentTarget, async () => {
      const previous = state.token;
      state.token = $("#connection-token").value.trim();
      try {
        await api("status");
        sessionStorage.setItem("iop-token", state.token);
        closeModal();
        state.ui = null;
        await refresh(true);
      } catch (error) {
        state.token = previous;
        throw error;
      }
    });
}
function updateMode() {
  const button = $("#mode-switch");
  button.innerHTML =
    icon("monitor") +
    `<span>${state.desktop ? t("在浏览器中打开", "Open in browser") : t("打开桌面应用", "Open desktop app")}</span>` +
    icon("arrow-up-right");
}
window.addEventListener("pywebviewready", () => {
  state.desktop = true;
  updateMode();
  if (state.view === "settings") render(true);
});
async function switchMode() {
  if (state.desktop && window.pywebview?.api)
    return busy($("#mode-switch"), () =>
      window.pywebview.api.open_browser(state.view),
    );
  if (state.ui?.local && state.ui?.desktop_available)
    return busy($("#mode-switch"), async () => {
      await api("ui/desktop", { view: state.view });
      toast(
        t(
          "正在打开桌面窗口，实验继续运行",
          "Opening the desktop window. Experiments keep running.",
        ),
      );
    });
  modal(
    t("IOP 桌面应用", "IOP Desktop"),
    `<p class="inline-note">${t("桌面窗口与浏览器连接同一个运行服务，使用相同的设备、平台和实验记录。", "The desktop window and browser connect to the same runtime and share instruments, platforms and experiment history.")}</p><div class="section-title"><h3>${t("安装并打开", "Install and open")}</h3></div><p class="inline-note">${t("下载当前版本，运行 install-desktop.ps1（Windows）或 install-desktop.sh（macOS / Linux）。安装后从系统应用菜单打开 IOP Runtime。", "Download the current release and run install-desktop.ps1 on Windows or install-desktop.sh on macOS / Linux. Then open IOP Runtime from the application menu.")}</p><pre style="margin-top:18px">iop desktop</pre><div class="form-actions"><a class="button primary" href="https://github.com/Cherish0925/AI4Instruments/releases/latest" target="_blank" rel="noreferrer">${icon("download")}${t("下载安装包", "Download installer")}</a></div>`,
    "DESKTOP",
  );
}
function palette() {
  const text = $("#palette-input").value.trim().toLowerCase();
  const entries = [
    ...Object.entries(titles).map(([view, fn]) => ({
      label: fn(),
      type: t("页面", "Page"),
      glyph: "grid",
      action: () => navigate(view),
    })),
    ...state.devices.map((d) => ({
      label: d.name || d.id,
      extra: d.id,
      type: t("设备", "Device"),
      glyph: "device",
      action: () => inspectDevice(d.id),
    })),
    ...state.platforms.map((p) => ({
      label: p.definition.name || p.id,
      extra: p.id,
      type: t("平台", "Platform"),
      glyph: "network",
      action: () => editPlatform(p),
    })),
    ...state.runs.map((r) => ({
      label: r.name || r.id,
      extra: r.id,
      type: t("实验", "Experiment"),
      glyph: "activity",
      action: () => inspectRun(r.id),
    })),
  ]
    .filter((e) =>
      (e.label + " " + (e.extra || "")).toLowerCase().includes(text),
    )
    .slice(0, 14);
  $("#palette-results").innerHTML = entries.length
    ? entries
        .map(
          (e, i) =>
            `<button class="palette-item" data-palette="${i}">${icon(e.glyph)}<span>${esc(e.label)}</span><small>${e.type}</small></button>`,
        )
        .join("")
    : `<p class="palette-empty">${t("没有匹配的设备或实验", "No matching devices or experiments")}</p>`;
  $$("[data-palette]").forEach(
    (b) =>
      (b.onclick = () => {
        $("#palette").close();
        entries[Number(b.dataset.palette)].action();
      }),
  );
}
function openPalette() {
  palette();
  $("#palette").showModal();
  $("#palette-input").focus();
}
icons();
translate();
setTheme(localStorage.getItem("iop-theme") || "light");
if (!titles[state.view]) state.view = "overview";
updateMode();
render();
refresh(true);
$$("[data-view]").forEach((b) => (b.onclick = () => navigate(b.dataset.view)));
$("#new-run").onclick = () => newExperiment();
$("#refresh-button").onclick = (e) =>
  busy(e.currentTarget, () => refresh(true));
$("#modal-close").onclick = closeModal;
$("#modal").addEventListener("close", () => {
  delete $("#modal").dataset.runDetail;
});
$("#search-open").onclick = openPalette;
$("#palette-input").oninput = palette;
$("#mode-switch").onclick = switchMode;
$("#menu-toggle").onclick = () => $("#sidebar").classList.toggle("open");
document.addEventListener("click", (e) => {
  if (
    !$("#sidebar").contains(e.target) &&
    !$("#menu-toggle").contains(e.target)
  )
    $("#sidebar").classList.remove("open");
});
document.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    openPalette();
  }
});
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) refresh();
});
window.addEventListener("hashchange", () => navigate(location.hash.slice(1)));
window.addEventListener("pywebviewready", () => {
  state.desktop = true;
  updateMode();
});
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
  if (localStorage.getItem("iop-theme") === "system") setTheme("system");
});
document.addEventListener("iop:navigate", (e) => navigate(e.detail));
document.addEventListener("iop:refresh", () => refresh(true));
document.addEventListener("iop:run", (e) => inspectRun(e.detail));
