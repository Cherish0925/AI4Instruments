# IOP instrument service

[中文](README.zh-CN.md) · [Architecture](architecture.md) · [HTTP API](http-api.md) · [Device drivers](drivers.md) · [Source](../../src/ai4instruments/iop)

0.8.2 improves [instrument setup](../../iop/instrument-setup.md), parallel scheduling and repeated program calls. [Agent integration](../../iop/agent-setup.md) uses the same saved laboratory configuration. [Application interfaces and system support](../../iop/product.md).

IOP Runtime runs on the computer connected to your instruments. It maintains device connections, executes experiment programs, schedules serial and parallel operations, and retains parameters, readings, results and files. People and agents share the HTTP API, Python client and command line. A browser interface displays instruments, accepts experiments and shows results.

**Implemented in 0.8.2:** background service, device registration and discovery, dependency scheduling, reservations across steps, experiment package execution, persistent records, Python client, browser interface and operating-system login startup.

Rust handles SDK, command and experiment processes; Python handles HTTP and workflow scheduling; TypeScript supplies the complete client. See the [current architecture](architecture.md).

**New in 0.5.0:** ready dependency scheduling, result bindings, counted resources, command programs, HTTP jobs, installable driver entry points, progress events and streaming file uploads. [Execution](../../iop/execution.md) · [Software and drivers](../../iop/software.md). Open the [IOP project](../../iop/README.md) or [configure a platform](../../iop/platforms.md).

**New in 0.6.0:** a native desktop window, browser switching, application menu entries and a redesigned interface for devices, platforms, experiments and resources. [Desktop and browser guide](../../iop/interface.md).

## Install and start

Release archives include Python and core dependencies. Extract and run `install.ps1` (Windows) or `sh install.sh` (macOS / Linux) for offline core installation. The corresponding `install-desktop` script downloads additional native UI dependencies.

For a source installation, use Python 3.10 or later and run in the repository directory:

```sh
python -m pip install ".[devices]"
iop init
iop start
iop open
```

Use `python3` where that is your Python command. If `iop` is not on your command path, replace it with `python -m ai4instruments.iop`.

For installation into a separate Python environment in your user directory, run `sh install.sh` on Linux, macOS or WSL, or `powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1` on Windows. The installer prints the exact commands for that environment. A server needs no desktop: use the CLI or HTTP API.

The downloadable IOP bundle also contains an installable wheel:

The installation script selects the platform-specific wheel in `dist/` automatically.

The `[devices]` extra installs serial, VISA, USB discovery and Modbus dependencies. Omit it for TCP instruments, simulation or drivers already installed. The core uses only the Python standard library.

| System | Background execution | `iop service install` |
| --- | --- | --- |
| Linux | Detached process | systemd user service |
| Windows | Detached process | Task Scheduler task at current-user login |
| macOS | Detached process | Current-user launchd LaunchAgent |
| WSL | Linux process | systemd user service where enabled |

`iop start` survives closing the terminal. To enable login startup, run `iop stop`, wait until `iop status` reports that the service has stopped, then run `iop service install`. `iop service uninstall` removes startup configuration and retains data. On an unattended Linux server, an administrator can use the same `iop serve` command in a system service or enable systemd lingering for the user. The Windows task and macOS LaunchAgent start after login.

WSL sees devices exposed to WSL. For a Windows-only vendor SDK, run the service on Windows and connect from WSL over HTTP. See [Microsoft's WSL USB instructions](https://learn.microsoft.com/en-us/windows/wsl/connect-usb) for USB attachment.

## Run an experiment

Before starting a configuration with no physical instruments registered, add the three simulated devices:

```sh
iop init --demo
iop start
iop devices
iop run examples/iop/parallel.json --wait
iop package examples/iop/polarization --resources stage meter optical-path --wait
```

The single-point workflow moves a stage and configures a detector concurrently, then measures after both complete. The scan package repeats this process and saves `scan.csv`, `result.json` and program output. Its default scan contains seven angles. All simulated readings identify their source as `simulation`.

Use the Python client to submit parameters consistently across operating systems:

```python
from ai4instruments.iop import Client

lab = Client()
run = lab.submit_package(
    "examples/iop/polarization",
    project="polarization-study",
    resources=["stage", "meter", "optical-path"],
    parameters={"angles_deg": [0, 15, 30, 45]},
)
print(run.id)
print(run.result())
for file in run.files():
    print(file["id"], file["name"], file["size"])
```

Once accepted, the experiment continues when the submitting client exits or disconnects. Reconnect using `Client().run(run_id)`. Use `info()` for its record, `files()` for retained files, and `download(file_id, "scan.csv")` to retrieve data.

## General structure and a multi-instrument experiment

The service works with devices, named operations, experiment programs, dependencies, shared resources and data. Its scheduler has no optical, chemical or model-specific logic. Drivers and instrument descriptions express device differences; experiment packages express research procedures.

| Layer | Implemented support |
| --- | --- |
| Communication and drivers | SCPI TCP / serial / VISA, Modbus TCP / RTU, HTTP JSON, custom Python drivers |
| Instrument descriptions | Named operations, parameter types, units, ranges, resources and driver-defined completion |
| Persistent service | Registration, discovery, dependency scheduling, program processes, data storage and retrieval |
| Experiment programs | Python logic, loops, feedback, fitting and analysis; other languages can use HTTP |

A complete temperature, weighing, dosing and acquisition example:

```sh
iop register examples/iop/multi-instrument/devices.json
iop package examples/iop/multi-instrument --resources bath balance pump daq sample --wait
```

The program prepares a temperature controller, balance and acquisition device concurrently, calculates successive doses from returned mass readings, and reads temperature, mass and signals in parallel after dosing. It retains a CSV and final result. Its devices are explicitly simulated so the full program can run without hardware. Physical replacements must provide the corresponding operations, units and completion behavior.

SCPI, Modbus and HTTP adapters perform actual communication. Description examples cover a [power meter](../../examples/iop/scpi-meter.json), [temperature controller](../../examples/iop/modbus-temperature.json) and [environment sensor](../../examples/iop/http-sensor.json). Cameras, microscopes, robots, mass spectrometers, flow instruments and proprietary buses can use the same driver interface through vendor SDKs or existing control software. This release does not bundle drivers for every model in those families.

## Connect instruments

```sh
iop discover
iop register examples/iop/scpi-meter.json
iop devices
```

Before registering the example, replace its address, commands, units and completion query with those documented for your instrument.

| Connection | Implementation |
| --- | --- |
| USB inventory | Linux sysfs, Windows PnP, macOS system_profiler |
| Serial ports | pySerial discovery, including available USB IDs and serial numbers |
| VISA resources | PyVISA enumeration through the installed backend |
| SCPI instruments | Persistent TCP, serial or VISA connection; text queries, writes, named operations and completion queries |
| Modbus instruments | TCP / RTU; register and coil access, named operations, scaling and shared-bus serialization |
| HTTP instruments | Description-driven JSON requests and response selection |
| Vendor SDKs, cameras, motion systems, existing platforms | Installed Python driver specified as `module:Class` |
| Automatic registration | Configured discovery profiles match connection metadata and supply device records |

**A discovered connection needs a matching instrument description and driver before its capabilities can be used.** USB inventory also includes non-instrument peripherals. Network instruments use configured addresses; VISA may additionally discover network resources supported by its backend.

A new model normally adds a driver or description without changing the scheduler, records or client. Drivers use software available on their host, so operating system, CPU architecture and vendor SDK must match. See [Device drivers](drivers.md).

## Execution order

An operation can start when **its dependencies have completed and its devices and shared resources are available**.

| Situation | Behavior |
| --- | --- |
| Independent devices | Execute concurrently within the worker limit |
| Several calls to one device | Execute one at a time |
| A step has an `after` list | Wait for every named predecessor |
| Operations share a sample, optical path or motion region | Declare the same shared resource name |
| A scan must retain its experimental setup between steps | List its devices and shared resources in the submission's `resources` |
| More work than available workers | Queue it while unrelated devices remain usable |

A run acquires its complete reservation together, avoiding partial reservations that wait for each other. Different devices inside that run may still operate concurrently. A package with a reservation must list every device it uses at submission. For a workflow with a reservation, the service also includes every device used by its steps.

Without a run reservation, each operation releases its device when it finishes. Use this for independent readings; reserve the full set for scans and other continuous procedures. Clients must use the same service to let it coordinate access to the same instrument.

Cancellation stops pending steps, signals active drivers and ends the experiment program process. A device remains occupied until its driver call returns. Drivers define completion and bounded response times. Device clocks, controllers and hardware triggers provide precise synchronization and high-speed feedback.

## Experiment packages

A package is a directory or ZIP containing a program and optional `package.json`. The service retains the original archive, creates a run directory and launches a separate process. Fitting, optimization, data processing and decisions about the next experiment can all live in that program.

```json
{"name":"polarization-scan","version":"1.0","command":["{python}","experiment.py"]}
```

`{python}` selects the service's Python environment. Commands may also name other installed programs. Install program dependencies in the execution environment. Packages execute as the service user and are installed experimental software for that platform.

Inside the program:

```python
import os
from pathlib import Path
from ai4instruments.iop import Client

run = Client().current_run()
angle = run.invoke("stage", "move_to", {"angle_deg": 15})
reading = run.invoke("meter", "measure")
Path(os.environ["IOP_RUN_DIR"], "reading.txt").write_text(str(reading))
run.save_result({"position": angle, "reading": reading})
```

For parallel work, call `run.invoke` from multiple threads; the service still schedules each device. See the [complete scan](../../examples/iop/polarization/experiment.py). JSON workflows provide fixed step graphs without uploading programs. External clients can also use `Client.invoke` for individual operations. Logic not yet submitted by an external client cannot continue after that client exits; submit the complete research process as a package when it must run independently.

## Records and restart

Data defaults to `~/.iop`. Change it with `IOP_HOME` or `iop --home /path/to/data ...`. Global options `--home` and `--endpoint` precede the subcommand.

| File | Contents |
| --- | --- |
| `config.json` | Address, workers, instruments, discovery profiles and connection token |
| `records.sqlite3` | Runs, operations, ordered events and file index |
| `runs/<run_id>/experiment.json` | Submitted definition and parameters |
| `runs/<run_id>/package.zip` | Original uploaded program |
| `runs/<run_id>/run.json` | Final run record |
| `runs/<run_id>/output/` | Data and results |
| `runs/<run_id>/stdout.txt`, `stderr.txt` | Program output |
| `service.log` | Background service output |

Each submission receives a `run_id`; each operation receives an `operation_id`. Runs retain instrument descriptions at submission. Events retain starts, ends, returned values and errors. A caller-supplied `request_id` identifies a repeated request and returns the original record without executing it twice.

After restart, work that never started remains queued. Previously started work without a complete ending becomes `interrupted`, with its existing data retained. This version does not automatically replay those physical actions. Establish device position and experiment progress before submitting subsequent work.

Defaults are eight device workers and four package processes. Adjust `workers` and `package_workers` in `config.json` and restart. Choose these counts for the computer, instruments and experiments. The service does not independently change experimental algorithms, device parameters or completion conditions.

## Clients and servers

The default endpoint is `127.0.0.1:8765`. For other computers, set `host` to the required network interface and give clients the endpoint and the token in `config.json`:

```python
lab = Client("http://lab-computer:8765", token="platform-token")
```

`IOP_ENDPOINT` and `IOP_TOKEN` provide the same settings through the environment. `iop open` opens the browser interface using local connection settings. See the [HTTP API](http-api.md). Different instrument computers may run separate services; experiments connect to the relevant endpoint. Resource scheduling in this version covers one service instance.

## Source installation and development

Build the native executor for command programs and independent SDK workers:

```sh
cargo build --release --locked --manifest-path iop/daemon/Cargo.toml
```

Put `iop-execd` (`iop-execd.exe` on Windows) on the executable path or set `IOP_EXECD` to its absolute path. Distribution archives already contain this binary.


```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m pip wheel --no-deps . --wheel-dir dist
```

Continuous integration covers Linux, Windows and macOS with Python 3.10 and 3.12. Checks exercise parallelism, device ordering, reservations, restart records, package processes, HTTP clients and a local TCP instrument endpoint. Each physical model still needs verification of its commands and completion behavior in its corresponding driver.
