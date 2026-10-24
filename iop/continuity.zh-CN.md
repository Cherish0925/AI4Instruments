# IOP · 持续实验

[English](continuity.md) · [安装](../docs/runtime/README.zh-CN.md) · [HTTP API](../docs/runtime/http-api.md) · [程序示例](../examples/iop/resumable-acquisition)

0.8.2 将设备发现、仪器配置、程序进度和连续数据接入同一套运行流程。配置和数据属于实验室的 Runtime；更换 Agent、关闭窗口或断开客户端后，已经受理的工作继续。

## 连接与配置

各发现来源完成后立即显示结果；仪器身份也逐台更新。较慢的 VISA 或厂商 SDK 不再拖住已经发现的连接。后台扫描按设定周期运行，扫描时间计入周期。`present` 表示最近一次发现结果，`communication` 表示最近一次操作返回，`state` 表示驱动与资源状态；三者分别记录。

在仪器详情选择“编辑说明”，可修改名称、地址、参数和完整操作说明。配置保留版本；选择旧版本并保存即可恢复。仪器有已受理的实验时，修改会返回具体原因。独立设备的实验继续执行。

```python
from ai4instruments.iop import Client
lab = Client()
current = lab.device_history('meter')[0]
definition = current['definition']
definition['config']['name'] = 'Measurement station'
lab.configure_device('meter', definition, current['revision'])
```

同一 SDK 进程服务多台设备时，仍以整组配置更新并重启服务。自动型号匹配继续补充缺少的操作；已有操作需要替换时使用仪器配置。

## Agent 读取的信息

`lab.context()` 默认返回简洁概况：设备、平台、当前任务和未完成设置。完整仪器说明通过 `/v1/devices/{id}` 获取，完整平台通过 `/v1/platforms/{id}` 获取。超过 100 台设备时按返回的地址继续分页。

后续读取使用 `lab.changes(context['cursor'])`；只传变化摘要和详情地址，测量数组与文件内容不进入概况。需要完整清单时使用 `lab.context(detail='full')`。MCP 对应 `lab_context(after=cursor)`；设备分页使用 `device_offset`。错误保留短说明，并提供 `code`、相关字段、当前版本或下一数据序号。

## 程序保存与续接

程序包在 `package.json` 声明 `"resume": true`。程序读取并保存自己的进度：

```python
run = lab.current_run()
progress = run.checkpoints().get('main', {}).get('state', {'next': 0})
for index in range(progress['next'], 100):
    result = run.invoke('meter', 'read_batch', request_id=f'{run.id}-{index}')
    # 保存本批数据，然后保存下一批的位置。
    run.checkpoint({'next': index + 1})
```

中断后使用 `iop resume RUN_ID --request-id continue-1`、`run.resume()`，或界面的“从保存的进度继续”。原实验编号、文件和操作记录继续使用；每次运行的终端输出单独保存。进度保存要求本程序的仪器操作已经返回。

这恢复的是程序明确保存的进度。程序使用稳定的操作 ID，已经完成的调用返回原结果；仪器尚未返回的动作不会自动重发。发生这类中断时，通过说明中标记 `effect: "observe"` 的状态读取操作获得当前状态，再调用 `/v1/resources/resolve` 记录结果并继续。通用 `query` 不自动被视为状态读取。排队且尚未开始的实验仍自动恢复。

## 连续数据

程序、相机适配器、采集卡适配器或计算软件可以将数据分批交给 Runtime：

```python
stream = run.stream('voltage', {
    'format': 'float32-le',
    'channels': [{'name': 'voltage', 'unit': 'V'}],
    'sample_rate_hz': 100000
})
stream.append(batch_bytes, sequence=0)
print(stream.info()['next_sequence'])
```

每块直接传输二进制；按序保存，重复上传同一序号与内容会返回已有记录。描述记录数据格式、通道、单位及采样条件；数据块通过现有文件接口下载。传输使用分段读写，不占用仪器调度锁。程序等待上一块保存后再提交下一块，保持内存用量可控。

采样时钟、触发、设备缓冲与采集停止由相应仪器驱动管理。高采样率使用仪器的批量采集接口；Runtime 的数据块用于保存和传递这些结果。

## SDK 运行

已安装的 Python 驱动可使用相同的 Rust 进程管理，无需另写通信程序：

```json
{
  "id": "camera",
  "driver": "vendor_camera:Camera",
  "config": {"serial_number": "CAM-001"},
  "execution": {"mode": "process", "startup_timeout": 30, "timeout": 300, "cancel_timeout": 2}
}
```

启动、操作和取消分别计时。SDK 卡住或退出时，相关进程结束，其他设备继续；重连重新建立该驱动。默认的进程内驱动保持原行为。共享总线或共享 SDK 使用已有 `process` 驱动描述整组设备。驱动包和厂商原生库安装在相应运行环境中。

## 安装

Windows、macOS、Linux 的 x86_64 / ARM64 发行包包含 Python、Rust 执行程序及 Runtime／Agent 依赖。`install.ps1` 或 `sh install.sh` 可离线安装核心、浏览器入口和 Agent 接口。桌面安装脚本另外下载当前系统的图形依赖；厂商驱动、USB 内核驱动与专用 SDK 按设备安装。

升级保留实验室目录。安装器先停止空闲的旧服务；有已受理实验时，先完成或停止这些实验再升级。源码安装仍支持 Python 3.10+。WSL 使用 Linux 包与已提供给 WSL 的设备。
