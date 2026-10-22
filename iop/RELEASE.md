IOP 0.4.0 adds experimental platform configuration and initialization to the persistent instrument service.

- Multiple platforms per computer, shared devices and operation-specific resource use.
- Saved configuration revisions, connection diagrams and reusable initialization procedures.
- Rust supervision for independent SDK processes; Python and executable driver interfaces.
- Python and TypeScript clients, HTTP API, CLI and browser interface.
- Existing SCPI, Modbus, HTTP and experiment-package support.

Download the archive matching your OS and CPU. Python 3.10+ is required; the archive includes the Rust executor. Linux packages target Ubuntu 22.04 / glibc 2.35+. macOS packages target Apple Silicon 14+ and Intel 15+. WSL uses the matching Linux package and devices exposed to WSL.

Workflow scheduling remains in Python. Device-model support depends on the configured driver and vendor SDK. Automated checks use simulated devices and local protocol endpoints; actual instrument combinations are recorded separately as laboratories use them.

中文说明：https://github.com/Cherish0925/AI4Instruments/blob/main/iop/README.zh-CN.md
