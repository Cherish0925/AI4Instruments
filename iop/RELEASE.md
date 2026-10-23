IOP Runtime 0.6.0 adds a native desktop application and a redesigned browser interface, both connected to the same persistent instrument service.

- Native windows on Windows, macOS and Linux; system application menu entries for IOP Runtime and IOP Browser.
- Switch between desktop and browser while experiments continue. Both entry points start or connect to the local service.
- Six pages: overview, instruments and software, platforms, experiments, resources, and connection settings.
- Structured device discovery and registration, platform connection diagrams, operation forms and workflow submission.
- Separate experiment steps, results and file downloads; paged operation history and compact refresh requests.
- Chinese and English, light and dark themes, keyboard search and responsive layouts.
- Registered serial/VISA connections are identified in discovery results. Language switching preserves the live connection display.

Download the archive matching your operating system and CPU. Run install-desktop.ps1 on Windows or sh install-desktop.sh on macOS/Linux for desktop and browser use. Run install.ps1 / install.sh for browser or server use. Python 3.10+ is required; installers download dependencies and the archive includes the Rust executor. Desktop installation is an installed Python application with native window support and application launchers.

Linux packages target Ubuntu 22.04 / glibc 2.35+. macOS packages target Apple Silicon 14+ and Intel 15+. Windows packages support x86_64 and arm64. WSL uses the Linux service and devices exposed to WSL. Desktop requirements and commands are in iop/interface.md and iop/interface.zh-CN.md.

Stop the existing service before upgrading its installation. Existing configuration, experiments and data in ~/.iop are retained. Open IOP Runtime from the application menu, or use iop desktop / iop open. Closing the interface leaves the service running; iop stop ends the service.

中文：0.6.0 新增独立桌面窗口、系统应用菜单入口和桌面/浏览器切换，重新设计了设备登记、平台连接图、实验操作、结果、文件与资源页面。两种界面共用同一个常驻服务。下载对应系统的软件包，运行 install-desktop.ps1 或 install-desktop.sh，即可从系统应用菜单打开 IOP Runtime。需要 Python 3.10+；已有配置与实验数据继续保留。中文说明：iop/interface.zh-CN.md。
