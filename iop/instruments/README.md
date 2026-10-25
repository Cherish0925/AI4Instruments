# Instrument model descriptions

[仪器接入](../instrument-setup.zh-CN.md) · [Instrument setup](../instrument-setup.md) · [Schema](../schema/instrument-profile.schema.json)

型号说明将已读出的制造商与型号对应到具体命令、参数、单位和原始资料。它们补充通用 SCPI 连接，不代表该型号的全部功能。0.8.1 包含下列 9 个型号的部分操作；其他 SCPI 仪器仍可识别并使用通用查询和命令。

Model descriptions map reported manufacturer/model names to documented operations. They extend the generic SCPI connection and cover selected operations, not every instrument feature. Version 0.8.1 contains the following nine models; other SCPI instruments retain generic identification, queries and commands.

| File | Models | Operations | Source |
| --- | --- | --- | --- |
| [srs-sr830.json](srs-sr830.json) | SR830 | X, Y, magnitude, phase, simultaneous X/Y, reference frequency | [SRS manual](https://www.thinksrs.com/downloads/pdfs/manuals/SR830m.pdf), Remote Programming, pp. 5-4, 5-15, 5-19 |
| [rigol-dp800-three-channel.json](rigol-dp800-three-channel.json) | DP831, DP831A, DP832, DP832A | Channel voltage/current/power, output state, output enable | [RIGOL programming guide, manufacturer document hosted by Batronix](https://www.batronix.com/pdf/Rigol/ProgrammingGuide/DP800_ProgrammingGuide_EN.pdf), pp. 2-34–2-36, 2-63 |
| [rigol-dp800-two-channel.json](rigol-dp800-two-channel.json) | DP821, DP821A | Same operations with two-channel selection | Same guide |
| [rigol-dp800-one-channel.json](rigol-dp800-one-channel.json) | DP811, DP811A | Same operations with CH1 | Same guide |

Discovery only reads identity. Measurement and output commands run when an experiment or operator requests them. Local descriptions take precedence over installed packages, which take precedence over built-in descriptions. Within a source tier, narrower identity matches take precedence; equally applicable descriptions remain explicit alternatives. Existing device operations take precedence. Descriptions are stored in `config.json.instrument_profiles` and packaged in distributions.

Automated verification uses protocol simulators and mocked SDK enumeration. These profiles have not been exercised on physical instruments in this development environment.

See [instrument support packages](../instrument-packages.md) for independent distribution and catalogue queries.

## Add another model

Use the manufacturer's reported identity and programming manual. Record a source link; describe only commands supported by the matched models. Save with `iop instrument-profile file.json`, `POST /v1/instrument-profiles`, or the instrument detail panel. SDK drivers use the separate discovery extension interface below.

## SDK discovery extensions

Install a Python package into the Runtime's environment and declare:

```toml
[project.entry-points."ai4instruments.discovery"]
my_vendor = "my_vendor.discovery:discover"
```

The callable takes no arguments and returns a JSON-serializable list:

```python
def discover():
    return [{
        "transport": "sdk",
        "address": "my_vendor:SN123",
        "identity": {"manufacturer": "My Vendor", "model": "M1", "serial_number": "SN123"},
        "identity_source": "my-vendor-sdk",
        "channels": ["input0", "input1"],
        "device": {"id": "m1-sn123", "driver": "my_vendor:Instrument", "config": {"serial": "SN123"}}
    }]
```

Return actual SDK results rather than a fixed example. The `device` field is optional. When present, it uses the normal [driver API](../drivers.md) and is registered automatically. Without it, identity and channels remain visible with `driver` in the required setup fields. Each enumeration runs in its own process with a 20-second timeout. Installed SDKs retain their OS, driver and architecture requirements.

Built-in SDK enumeration: [NI-DAQmx Python](https://nidaqmx-python.readthedocs.io/en/stable/) and [Basler pypylon](https://github.com/basler/pypylon). Network discovery follows the [LXI specification](https://public.lxistandard.org/specifications/LXI_1.5_Specifications/LXI_Device_Specification_1.5.01_2017-03-14.pdf). OS metadata uses [pySerial](https://pyserial.readthedocs.io/en/latest/tools.html), [PyVISA](https://pyvisa.readthedocs.io/en/latest/introduction/names.html), Windows [Win32_PnPEntity](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-pnpentity), Linux sysfs and macOS system_profiler.
