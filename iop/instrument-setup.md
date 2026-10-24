# IOP · Instrument setup

[中文](instrument-setup.zh-CN.md) · [Agent integration](agent-setup.md) · [Drivers](drivers.md) · [Model descriptions](instruments/README.md)

IOP Runtime discovers connections, reads identity and saves instrument descriptions on the instrument computer. Desktop, browser, command-line and agent clients share these descriptions, platform configuration and experiment records.

## Automatic work in 0.8.1

| Connection or source | Information read | Result |
| --- | --- | --- |
| USB / serial | OS names, VID/PID, serial number, location, interfaces and driver details | Windows COM/ASRL aliases are grouped; interfaces with matching USB identifiers and serial numbers are linked |
| VISA instruments | USB, TCPIP and GPIB `INSTR` resources | Read `*IDN?` and save manufacturer, model, serial number, firmware and SCPI connection |
| LXI announcements | Local `_lxi`, `_scpi-raw`, `_hislip` and `_vxi-11` services | Identify through advertised control endpoints; web-only announcements indicate that a control interface is still needed |
| Configured SCPI | Saved TCP, serial or VISA endpoints | Identity reads pass through the experiment scheduler |
| Installed NI-DAQmx | Model, serial number, simulation flag, analog/digital/counter channels | Save SDK information; acquisition operations come from the corresponding driver |
| Installed Basler pypylon | Vendor, model, serial number, full name and device class | Save SDK information; image acquisition comes from the corresponding driver |
| Installed discovery plugins | Identity, interfaces and instrument descriptions returned by a plugin | Automatically register a supplied driver configuration; extensible to other vendors and device classes |
| Configured software | Installed executable paths | Reuse the program description and operations |

Providers run concurrently. VISA and SDK enumeration use separate processes with time limits, so one failed source does not cancel the others. Background scans run every 30 seconds by default; simultaneous client requests share a scan. Failed identity queries retry after 60 seconds or immediately through **Identify again**.

## From identity to operations

1. Supported interfaces read identity and save the connection, retaining the information source.
2. Match manufacturer and model against [model descriptions](instruments/README.md), then add operations, parameters, units and documentation. Unknown models retain SCPI `identify`, `query` and `write`, with model-specific operations listed as remaining setup.
3. Open instrument details to execute an operation, inspect its response, export the description or add model operations. All clients reuse saved information.
4. On reconnection, identified instruments confirm their identity before experiment commands. A different serial number does not silently replace the saved instrument.
5. An identified instrument at a newly discovered address keeps its ID using manufacturer, model and a usable serial number. The endpoint changes only when the old discovery provider is available and no longer reports the old endpoint, and the instrument has no accepted operations or reservations.

First-seen and scan times, identity responses, IDs, required settings, documentation and discovery records are retained locally. `present=true` means observed this scan; `false` means absent from an available provider; `null` means not confirmed. A configured network address alone does not establish presence.

## Remaining setup

USB-to-serial chip information identifies the interface, not the instrument behind it. An unknown serial device needs its protocol, baud rate and termination. Modbus register meanings and proprietary acquisition methods come from the instrument description or driver. Unknown serial ports are not tried with different protocols and baud rates.

Analog signals, optical paths, probes and sample relationships need electronic device descriptions, existing laboratory documentation or initial operator input. Agents read `lab_context.next_steps`, reuse known information and complete only missing fields. Platform descriptions retain physical connections, shared resources and initialization procedures; these relationships cannot be inferred from USB or serial names.

## Save model operations

```sh
iop instrument-profile                      # List bundled and local descriptions
iop instrument-profile my-instrument.json   # Save a model description
iop identify meter --wait                   # Read a registered instrument's identity
```

Descriptions match explicit manufacturer and model names, optionally serial numbers and firmware. See the [JSON Schema](schema/instrument-profile.schema.json). New operation names are added to already identified instruments. Existing operation definitions remain unchanged so accepted experiments retain their meaning. To change an existing operation, edit the device configuration and restart after experiments finish.

## Continuous experiments and data

Individual instruments can operate directly. Workflows use `after` for ordering and `bindings` for results. Put feedback loops in Python, TypeScript or other experiment programs. Independent devices operate concurrently; shared instruments and resources follow the experiment configuration. Identity reads use the same scheduler.

Run identifiers, parameters, results and files are saved together. Accepted experiments continue after clients close. Images and waveforms use driver file output and streaming transfer; hardware sampling and triggering belong to the corresponding driver.
