import assert from "node:assert/strict";
import { spawn, execFileSync } from "node:child_process";
import { mkdtemp, readFile, rm, mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
const root = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const home = await mkdtemp(join(tmpdir(), "iop-interface-"));
const images = process.env.IOP_UI_SCREENSHOTS;
if (images) await mkdir(images, { recursive: true });
const child = spawn(
  process.env.PYTHON || "python",
  [
    "-u",
    "-c",
    `import sys
from ai4instruments.iop.config import initialize,save_json,home_path
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.cli import serve
from ai4instruments.iop.store import now
p=home_path(sys.argv[1]); c=initialize(p,False,0);c['discovery_interval']=0;c['resource_pools']={'cpu':8,'gpu':2};save_json(p/'config.json',c)
def inventory(self):
    self.discovery={'connections':[{'transport':'serial','address':'COM7','name':'Simulated serial connection','manufacturer':'Simulation','serial_number':'SIM-007','status':'discovered'}],'providers':[{'name':'serial','available':True}],'updated':now()}
    return self.discovery
Engine.scan=inventory
serve(p)
`,
    home,
  ],
  {
    cwd: root,
    env: { ...process.env, PYTHONPATH: join(root, "src") },
    stdio: ["ignore", "pipe", "pipe"],
  },
);
let browser, endpoint, token;
let stderr = "";
child.stderr.on("data", (data) => (stderr += data.toString()));
const pause = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
try {
  endpoint = await new Promise((resolve, reject) => {
    let out = "";
    child.stdout.on("data", (data) => {
      out += data;
      const match = out.match(/http:\/\/127\.0\.0\.1:\d+/);
      if (match) resolve(match[0]);
    });
    child.once("exit", (code) =>
      reject(Error("Service exited " + code + " " + stderr)),
    );
  });
  token = JSON.parse(await readFile(join(home, "config.json"), "utf8")).token;
  const api = async (path, body) => {
    const r = await fetch(endpoint + "/v1/" + path, {
      method: body === undefined ? "GET" : "POST",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await r.json();
    assert.ok(r.ok, JSON.stringify(data));
    return data;
  };
  browser = await chromium.launch({
    ...(process.env.IOP_CHROMIUM
      ? { executablePath: process.env.IOP_CHROMIUM }
      : {}),
    args: ["--no-sandbox", "--no-proxy-server"],
  });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1050 },
    colorScheme: "light",
  });
  let errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.addInitScript(
    (value) => sessionStorage.setItem("iop-token", value),
    token,
  );
  await page.goto(endpoint);
  await page.waitForFunction(
    () =>
      document.querySelector("#service-caption")?.textContent ===
      "运行服务在线",
  );
  assert.equal(await page.locator("#nav-devices").innerText(), "0");
  assert.ok(
    !(await page.locator("body").innerText()).includes("[object Object]"),
  );
  if (images) await page.mouse.move(0, 0);
  if (images)
    await page.screenshot({
      path: join(images, "overview-empty.png"),
      fullPage: true,
      style: "#toast{visibility:hidden}",
    });
  await page.click("#overview-discover");
  await page.waitForSelector('[data-register="0"]');
  assert.equal(await page.locator("#discovery-section pre").count(), 0);
  await page.click('[data-register="0"]');
  assert.equal(await page.locator("#reg-driver").inputValue(), "scpi-serial");
  assert.equal(await page.locator("#reg-port").inputValue(), "COM7");
  const generatedID = await page.locator("#reg-id").inputValue();
  assert.ok(generatedID);
  await page.fill("#reg-name", "模拟串口设备");
  await page.click("#reg-save");
  await page.waitForSelector(`[data-device="${generatedID}"]`);
  await api("devices", {
    id: "sim-axis",
    driver: "simulated",
    config: { kind: "stage" },
  });
  await api("devices", {
    id: "sim-sensor",
    driver: "simulated",
    config: { kind: "meter", stage: "sim-axis" },
  });
  await page.click("#refresh-button");
  await page.waitForSelector('[data-device="sim-axis"]');
  if (images) await page.mouse.move(0, 0);
  if (images)
    await page.screenshot({
      path: join(images, "instruments.png"),
      fullPage: true,
      style: "#toast{visibility:hidden}",
    });
  await page.click('[data-view="platforms"]');
  await page.click("#platform-new");
  await page.fill("#platform-name", "仪器协同平台（模拟）");
  await page.fill("#platform-id", "bench-01");
  await page.fill("#platform-description", "用于界面与执行流程的模拟平台");
  await page.check('[name="platform-device"][value="sim-axis"]');
  await page.check('[name="platform-device"][value="sim-sensor"]');
  await page.click("#connection-add");
  await page.fill('[data-port="from"]', "trigger-out");
  await page.fill('[data-port="to"]', "trigger-in");
  await page.fill("[data-kind]", "trigger");
  await page.click("#platform-save");
  await page.waitForSelector('[data-platform-edit="bench-01"]');
  assert.equal(
    (await api("platforms"))[0].definition.connections[0].kind,
    "trigger",
  );
  if (images) await page.mouse.move(0, 0);
  if (images)
    await page.screenshot({
      path: join(images, "platform.png"),
      fullPage: true,
      style: "#toast{visibility:hidden}",
    });
  await page.click("#new-run");
  await page.fill("#experiment-name", "串行与并行协同（模拟）");
  await page.selectOption("#experiment-platform", "bench-01");
  await page.selectOption('[data-step="step-1"] [data-step-operation]', "wait");
  await page.fill('[data-step="step-1"] [data-parameter="duration"]', "0.1");
  await page.click("#experiment-add");
  await page.selectOption(
    '[data-step="step-2"] [data-step-device]',
    "sim-sensor",
  );
  await page.selectOption('[data-step="step-2"] [data-step-operation]', "wait");
  await page.fill('[data-step="step-2"] [data-parameter="duration"]', "0.1");
  await page.click("#experiment-submit");
  await page.waitForSelector("#run-detail-summary .badge.completed");
  assert.equal(await page.locator(".operation-row").count(), 2);
  await page.click('[data-detail-tab="results"]');
  await page.waitForSelector("#detail-results .result-grid");
  if (images) await page.mouse.move(0, 0);
  if (images)
    await page.screenshot({
      path: join(images, "experiment.png"),
      fullPage: true,
      style: "#toast{visibility:hidden}",
    });
  await page.click("#modal-close");
  await page.click('[data-view="resources"]');
  await page.click("#resources-edit");
  await page.locator("[data-resource-count]").first().fill("12");
  await page.click("#resource-save");
  await page.waitForFunction(
    () => document.querySelector("#toast")?.textContent === "资源数量已保存",
  );
  assert.equal((await api("resources")).capacities.cpu, 12);
  await page.click('[data-view="overview"]');
  if (images) await page.mouse.move(0, 0);
  if (images)
    await page.screenshot({
      path: join(images, "overview.png"),
      fullPage: true,
      style: "#toast{visibility:hidden}",
    });
  await page.keyboard.press("Control+k");
  await page.fill("#palette-input", "sim-axis");
  await page.click('[data-palette="0"]');
  await page.waitForSelector("#device-operation");
  const deviceDownload = page.waitForEvent("download");
  await page.click("#device-export");
  const exportedDevice = await deviceDownload;
  const description = JSON.parse(
    await readFile(await exportedDevice.path(), "utf8"),
  );
  assert.equal(description.driver, "simulated");
  assert.equal(description.config.kind, "stage");
  await page.selectOption("#device-operation", "position");
  await page.click("#device-invoke");
  await page.waitForSelector("#device-response .badge.completed");
  assert.ok(
    (await page.locator("#device-response").innerText()).includes(
      "angle_actual",
    ),
  );
  if (images)
    await page.screenshot({
      path: join(images, "instrument-response.png"),
      fullPage: true,
      style: "#toast{visibility:hidden}",
    });
  await page.click("[data-device-run]");
  await page.waitForSelector("#run-detail-summary .badge.completed");
  await page.click("#modal-close");
  await page.click('[data-view="settings"]');
  const contextDownload = page.waitForEvent("download");
  await page.click("#agent-context-export");
  const exportedContext = await contextDownload;
  const labContext = JSON.parse(
    await readFile(await exportedContext.path(), "utf8"),
  );
  assert.equal(labContext.service.name, "IOP Runtime");
  assert.equal(labContext.platforms[0].id, "bench-01");
  assert.ok(!JSON.stringify(labContext).includes(token));
  await page.selectOption("#theme-select", "dark");
  await page.selectOption("#language-select", "en");
  assert.equal(
    await page.locator("#view-title").innerText(),
    "Connection & settings",
  );
  assert.equal(
    await page.locator("#service-caption").innerText(),
    "Service online",
  );
  await page.click('[data-view="overview"]');
  if (images) await page.mouse.move(0, 0);
  if (images)
    await page.screenshot({
      path: join(images, "overview-dark.png"),
      fullPage: true,
      style: "#toast{visibility:hidden}",
    });
  await page.setViewportSize({ width: 390, height: 844 });
  if (images) await page.mouse.move(0, 0);
  if (images)
    await page.screenshot({
      path: join(images, "mobile.png"),
      fullPage: true,
      style: "#toast{visibility:hidden}",
    });
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > innerWidth,
    ),
    false,
  );
  assert.ok(
    await page
      .locator("#sidebar")
      .evaluate((e) => e.getBoundingClientRect().right <= 0),
  );
  await page.click("#menu-toggle");
  await page.click("[data-view=devices]");
  await page.waitForSelector("[data-device=sim-axis]");
  assert.ok(
    await page
      .locator("#sidebar")
      .evaluate((e) => e.getBoundingClientRect().right <= 0),
  );
  await page.setViewportSize({ width: 1440, height: 1050 });
  const archive = execFileSync(process.env.PYTHON || "python", [
    "-c",
    String.raw`import io,sys,zipfile,json
b=io.BytesIO()
with zipfile.ZipFile(b,'w') as z:
 z.writestr('package.json',json.dumps({'name':'interface-program','command':['{python}','experiment.py']}))
 z.writestr('experiment.py',"from ai4instruments.iop import Client\nrun=Client().current_run()\nrun.save_file('data.csv', b'time,value\\n0,12\\n')\nrun.save_result({'samples':1})\n")
sys.stdout.buffer.write(b.getvalue())`,
  ]);
  await page.click("#new-run");
  await page.fill("#experiment-name", "Program upload and file download");
  await page.click("[data-compose=package]");
  await page.setInputFiles("#experiment-archive", {
    name: "experiment.zip",
    mimeType: "application/zip",
    buffer: archive,
  });
  await page.click("#experiment-submit");
  await page.waitForSelector("#run-detail-summary .badge.completed");
  await page.click("[data-detail-tab=results]");
  await page.waitForSelector("#detail-results .result-grid");
  assert.match(await page.locator("#detail-results").innerText(), /samples/);
  await page.click("[data-detail-tab=files]");
  const row = page.locator("#detail-files tr").filter({ hasText: "data.csv" });
  await row.waitFor();
  await page.evaluate(() => delete window.showSaveFilePicker);
  const downloadPromise = page.waitForEvent("download");
  await row.locator("button").click();
  const downloaded = await downloadPromise;
  assert.equal(downloaded.suggestedFilename(), "data.csv");
  assert.equal(
    await readFile(await downloaded.path(), "utf8"),
    "time,value\n0,12\n",
  );
  await page.click("#modal-close");
  const lasting = await api("runs", {
    name: "Continues after browser closes",
    steps: [
      {
        id: "wait",
        device: "sim-axis",
        operation: "wait",
        arguments: { duration: 1 },
      },
    ],
  });
  await page.close();
  await pause(1300);
  assert.equal(
    (await api("runs/" + lasting.id + "?details=false")).state,
    "completed",
  );
  assert.deepEqual(errors, []);
  console.log(
    "Interface passed: discovery, registration, topology, workflow, results, resources, search, language, themes, mobile, program ZIP, file download and service continuity.",
  );
} finally {
  if (browser) await browser.close();
  if (endpoint)
    await fetch(endpoint + "/v1/shutdown", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
      body: "{}",
    }).catch(() => {});
  if (child.exitCode === null)
    await new Promise((resolve) => {
      const timer = setTimeout(() => child.kill(), 4000);
      child.once("exit", () => {
        clearTimeout(timer);
        resolve();
      });
    });
  await rm(home, { recursive: true, force: true });
}
