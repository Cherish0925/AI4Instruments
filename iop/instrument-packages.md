# Instrument support packages

[中文](instrument-packages.zh-CN.md) · [Model descriptions](instruments/README.md) · [Driver API](drivers.md) · [Platforms](platforms.md)

IOP 0.8.3 reads model descriptions from installed Python packages. A package can supply discovery, drivers and model descriptions while the Runtime continues to handle scheduling, configuration and experiment records.

| Content | Entry-point group | Loading |
| --- | --- | --- |
| Drivers | `ai4instruments.drivers` | Load a driver class by name |
| SDK discovery | `ai4instruments.discovery` | Run enumeration in a separate process |
| Model descriptions | `ai4instruments.instrument_profiles` | Read packaged JSON without importing the package or starting its SDK |

## Find and apply

```sh
iop instrument-catalog --manufacturer Stanford_Research_Systems --model SR830
iop instrument-catalog --id srs-sr830 --details
```

Results contain operation names, original documentation, source and package version. Pages contain 50 entries by default; continue with `next_offset`. Python, TypeScript and HTTP expose the same query. MCP `instrument_profiles` returns a summary unless `details=true` is supplied.

Open an instrument, choose “Add model operations”, select an installed description and choose “Use for this instrument”. Existing operations are retained; missing operations are added and a configuration version is saved. Finish accepted experiments using that instrument before changing it. Independent instruments continue working.

Automatic matching prefers laboratory descriptions, then installed packages, then built-in descriptions. Within a source tier, narrower model, serial-number or firmware conditions take precedence. Equally applicable descriptions remain explicit alternatives; generic SCPI operations remain available. Reading the catalogue sends no instrument commands.

## Package layout

| File | Content |
| --- | --- |
| `pyproject.toml` | Installation metadata and entry point |
| `my_lab_instruments/__init__.py` | May be empty |
| `my_lab_instruments/instruments/*.json` | Model descriptions |

```toml
[build-system]
requires = ["setuptools>=70.1"]
build-backend = "setuptools.build_meta"

[project]
name = "my-lab-instruments"
version = "0.1.0"
requires-python = ">=3.10"

[project.entry-points."ai4instruments.instrument_profiles"]
models = "my_lab_instruments:instruments"

[tool.setuptools.package-data]
my_lab_instruments = ["instruments/*.json"]
```

The entry-point value names a Python package and resource directory separated by a colon; dots denote directory components. It is not a callable. JSON follows the [model description schema](schema/instrument-profile.schema.json); the existing [SR830 description](instruments/srs-sr830.json) is an example. Commands, units and completion behavior come from the corresponding instrument programming manual.

Run `python -m pip install .` with the Python executable in the IOP installation, then restart after current experiments finish. `iop mcp-config` reports that executable as `command`. An invalid package file does not remove other model descriptions; catalogue results identify the affected package and file in `errors`.

## Shared Modbus buses

Register each instrument on an RS-485 bus or TCP gateway with its own `config.device_id`. A bus address and device address identify one registered instrument. Operations retain that instrument's address.

TCP accepts the full 0–255 unit-identifier field, including 0 and 255 used by directly connected TCP devices. Serial instruments use individual addresses 1–247. Set the value specified by the instrument or gateway manual; see the [Modbus TCP implementation guide](https://www.modbus.org/file/secure/messagingimplementationguide.pdf).

Modbus devices in one process share their connection and serialize requests on the bus. Editing an idle instrument's name or operations keeps its neighbours' connection open. Independent buses run concurrently. Baud rate, byte size, stop bits and parity agree across one serial bus; each device can use its own response timeout. Failed reads or writes are not automatically repeated.

For process isolation, place devices sharing a bus in the same `process` worker. Multiple processes cannot own the same exclusive serial port. Instruments remain separate in the device list; connection details list every registered instrument on that bus.
