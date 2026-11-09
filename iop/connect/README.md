# Connect a research host to IOP

IOP Runtime runs on the computer that operates the instruments. An agent host connects to that service; closing a chat, disabling the plugin, or updating the connector does not cancel an accepted experiment. The Skill explains the operating method. MCP advertises the instruments and operations available in this laboratory.

[中文](README.zh-CN.md) · [Installation guide (HTML)](guide.en.html) · [Download IOP](https://github.com/Cherish0925/AI4Instruments/releases/latest) · [Tool and service API](../../docs/runtime/http-api.md)

## Install from a marketplace

In Agentic Research OS, open **Extensions → Plugins → Add from link** and enter
`https://github.com/Cherish0925/AI4Instruments`. Select **iop-lab**, install it and
activate the installed revision. Its Skill and MCP server connect to the IOP
Runtime selected on the tool host. Install the [Runtime release](https://github.com/Cherish0925/AI4Instruments/releases/tag/iop-v0.8.5)
on the instrument computer first. The direct GitHub plugin requires `iop` on the
tool host's PATH. For an absolute executable path or a remote laboratory, use the
named connection below and import the returned `research_os` directory.

Codex: `codex plugin marketplace add Cherish0925/AI4Instruments`, then
`codex plugin add iop-lab@ai4instruments`.
Claude Code: `claude plugin marketplace add Cherish0925/AI4Instruments`, then
`claude plugin install iop-lab@ai4instruments`.

The GitHub marketplace is published by this project. Plugin updates and Runtime
updates are separate; the plugin does not replace drivers or laboratory data.

## Install one connection

Install the release on the lab computer. From IOP 0.8.4, run the following on the **agent execution host**. Use the full IOP executable printed by the installer when a desktop application does not inherit the terminal PATH.

```sh
iop connect --name bench --local
```

| Location of the experiment | Connection |
| --- | --- |
| Instruments on this computer | `iop connect --name bench --local`. Use `--lab-home PATH` to select a particular service data directory. |
| Lab computer accessible by SSH | `iop connect --name bench --ssh lab-server --remote-iop /opt/iop/venv/bin/iop`. Use a preconfigured, noninteractive OpenSSH account; absolute remote paths are quoted for a POSIX shell. `iop` on the remote PATH also works without the path option. Program paths are on the lab computer. |
| Existing IOP REST service | `iop connect --name bench --remote https://lab.example.org --token-env BENCH_IOP_TOKEN`. Install the IOP bridge on the agent host; supply the named secret in its execution environment. The URL is the service origin. Local file tools work on the bridge host. |
| Cloud client that accepts MCP HTTP | On the lab host provision `IOP_MCP_TOKEN` and run `iop mcp-http --port 8766`. Connect to `/mcp` via an administrator-provided HTTPS reverse proxy; use a bearer credential. Leave the upstream Host as `127.0.0.1:8766`. The gateway listens on loopback and serves one lab authority; OAuth-only clients need a compatible gateway. Remote clients cannot ask these MCP file tools to read or write the gateway computer's files. |

The connector writes a receipt with paths, without contacting an instrument. Its stable marketplace directory is separate from IOP data. One name selects one lab: use a different name for a second lab. Running `iop connect --name bench` again reuses that connection and prepares the installed connector version.

## Install in the host

| Host | Installation and update |
| --- | --- |
| Codex | `codex plugin marketplace add "<marketplace>"`, then `codex plugin add bench@iop-bench`. For direct MCP configuration, copy the printed `codex_toml` section. Refresh a Git marketplace with `codex plugin marketplace upgrade ai4instruments`, then install the new plugin revision. |
| Claude Code | `claude plugin marketplace add "<marketplace>"`, then `claude plugin install bench@iop-bench`. After regenerating the package, run `claude plugin update bench@iop-bench` and reload plugins. |
| Agentic Research OS | Stage the printed `research_os` directory inside the target Session workspace. Install it as a **plugin** under its laboratory name. Activate the installed revision in Extensions. On update, install against the current revision, then activate the new revision. The host carries its own included Skill and stdio launch settings. |
| Qiushi Engine | Import the printed `qiushi` directory as an **MCP package** in the target user's research workspace; use `qiushi_zip` for ZIP upload. Its current Linux execution backend exposes `bench tools` and `bench call TOOL JSON` through `run_shell`. Update through the same package installer. |
| Other stdio MCP clients | Read the printed `mcp` JSON. Register its executable and argument array in the host's MCP settings. If using a remote token, allow the named environment variable through to the child process. |
| HTTP/SDK programs | Use the existing REST, Python or TypeScript client with a specific laboratory endpoint. `/v1` is the IOP API; `/mcp` belongs to the separate MCP gateway. |

**Install directly from GitHub** when the agent host can run `iop mcp` on its PATH. Add marketplace `Cherish0925/AI4Instruments` in Codex or Claude Code; install `iop-lab@ai4instruments`. It uses the IOP connection of that process. For isolated labs or a GUI without that PATH, use the named connection above. A hosted product should assign an account, credential and lab to its execution worker; the connector does not provide tenant isolation.

**Upgrade separately.** Reinstalling the connector does not update the daemon or drivers. Old generated package directories remain available to clients using them. Upgrade the daemon with the matching platform installer after accepted work finishes. User data remains in the same IOP data directory. For the standalone connector ZIP, extract it and run `python install.py --name bench`; use the installed IOP Python or pass `--iop-python PATH`. The standalone connector also works with the 0.8.3 stdio service. The HTTP gateway requires 0.8.4.

## First experiment

Read `lab_context` and `describe_instrument`. Submit once with a stable `request_id`; keep the laboratory name and returned run ID. Read `experiment(run_id, include_result=true)` after reconnecting. Repeat a submission with its original request ID only for the identical experiment. A successful installation does not identify cables, samples, or an unknown instrument's command set.
