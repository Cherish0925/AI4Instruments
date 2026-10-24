# IOP · Instrument setup

[中文](instrument-setup.zh-CN.md) · [Agent connection](agent-setup.md) · [Drivers](drivers.md) · [Software](software.md)

An instrument description contains its identity, connection, driver, operations, parameters, units, returned data and completion conditions. People, agents and experiment programs use the same definition.

## From a connection to operations

1. Discover interfaces. Serial, VISA and configured programs appear as configurable interfaces; USB inventory is shown separately. On Windows, a COM port and its corresponding VISA ASRL address form one group. Raw interfaces remain available through the API.
2. Select the instrument driver. A serial connection does not determine whether the device uses SCPI, Modbus or a vendor binary language. Import an existing description when available. For SCPI, use the baud rate and line ending specified by the instrument manual.
3. Save the description. IDs are generated automatically and remain editable. Exported configurations can be shared and imported. Identical registrations reuse the existing device.
4. Execute a defined operation. SCPI identification sends `*IDN?` and displays manufacturer, model, serial number and firmware beside the operation. Other operations expose their declared parameters and results. Saving configuration is distinct from receiving an instrument response.
5. Extend model capabilities through installed drivers or documented commands with parameters, units and completion conditions. SDK devices use an independent driver process; implementations in Java, C, C++, C#, Python and other languages share that interface.

## Configure once, reuse

Read `lab_context` for saved devices and platforms and `describe_instrument` for operations. Use `register_instruments` for multiple devices; each item returns a device or an error. IOP handles IDs, scan coordination and records. Wiring, sample placement and research intent come from existing experiment documentation or the operator when unavailable from devices.

Platforms describe physical connections, shared objects, resource capacities and initialization procedures. Standalone devices can be invoked directly. Workflows use `after` for dependencies and `bindings` for previous results. Independent devices run concurrently; shared devices and resources follow the saved scheduling definition.

## Continuous experiments and data

Submit known steps together. Run feedback-dependent loops inside experiment programs using Python, TypeScript or HTTP. Run identifiers, parameters, operation results and files are retained together. Accepted experiments continue when the interface or agent closes.

SCPI text reads use a buffer, preserve trailing responses and handle line endings split across packets. Serial settings include `baudrate`, `bytesize`, `parity`, `stopbits`, `xonxoff`, `rtscts` and `dsrdtr`. Images and waveforms use driver file outputs and streaming file transfer; vendor-specific binary acquisition belongs in its corresponding driver.

Read compact status summaries first, then results, paged operations or files when needed. Instrument drivers define completion conditions, hardware triggering and sampling rates; IOP coordinates dependencies and resources between them.
