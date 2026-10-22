IOP Runtime 0.5.0 connects instruments, executable programs and remote jobs through one persistent experiment service.

- Ready-queue scheduling, result-to-argument bindings, counted resources and explicit device concurrency.
- Rust execution for experiment programs and command-line tools, including process-tree completion and cancellation on Linux, macOS and Windows.
- Asynchronous HTTP job submission, progress, cancellation and results; installed driver-package entries and reconnection.
- Completed package calls move out of active memory and remain in paged SQLite history. File transfers stream directly and event queries can wait for new records.
- Python and TypeScript clients support packages, operations, results and files. The browser includes resource configuration and installed adapters.

Download the archive matching the operating system and CPU. Python 3.10+ is required; the native Rust executor is included. Linux packages target Ubuntu 22.04 / glibc 2.35+. macOS packages target Apple Silicon 14+ and Intel 15+. Windows packages support x86_64 and arm64. WSL uses the matching Linux package and devices exposed to WSL.

Run install.sh (Linux/macOS/WSL) or install.ps1 (Windows), then iop init, iop start and iop open. Existing configurations and experimental records are retained. The installer uses the same user installation directory as 0.4.0; stop the existing service before replacing its executable files.

The release contains a general runtime and adapter interfaces. Specific instruments and software use their installed SDKs, executable programs or network APIs. HTTP and workflow scheduling remain Python; Rust handles process execution. The TypeScript package is included as a separate .tgz asset.

中文：本版加入依赖就绪调度、结果传递、资源数量、普通程序与远端任务接入、进度、流式文件和完整 TypeScript 客户端。源码与中英文说明位于仓库顶层 iop/。已有配置和记录继续使用。
