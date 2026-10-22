# 软件与驱动扩展

[IOP Runtime](README.zh-CN.md) · [English](software.md) · [实验执行](execution.zh-CN.md)

根据工具已有的接口选择接入方式。协议、调度和记录保持一致；设备命令、模型操作与专业数据格式由适配器表达。

| 工具提供的接口 | 使用方式 |
| --- | --- |
| SCPI、Modbus | 内置适配器与型号对应的仪器说明 |
| Python SDK | `module:Class` 驱动，或安装提供驱动入口的包 |
| 持续运行的 C / C++ / C# / Java 等 SDK | `process` 独立驱动接口 |
| 命令行或可执行文件 | `command`，每项操作启动一个程序 |
| 同步 HTTP JSON | `http` 操作说明 |
| 提交任务、查询状态、返回结果的 HTTP 服务 | `http` 的 `job` 配置 |

## 普通可执行程序

```json
{
  "id":"processor",
  "driver":"command",
  "config":{
    "mode":"software",
    "concurrency":4,
    "cwd":"/absolute/path/to/program",
    "requirements":{"cpu":1},
    "operations":{
      "calculate":{
        "command":["{python}","calculate.py"],
        "parameters":{"x":{"type":"number"}}
      }
    }
  }
}
```

先配置 `cpu` 的容量，再登记。`command` 是程序及参数数组；各个元素原样传入程序，不经过 shell。可以换成 `node analysis.mjs`、编译后的 Rust / C / C++ 程序、`dotnet analysis.dll` 或 `java -jar analysis.jar` 对应的参数数组。

| 程序输入与输出 | 内容 |
| --- | --- |
| 标准输入、`IOP_REQUEST_FILE` | JSON：操作名、参数、实验编号、操作编号、输出目录 |
| `IOP_ARGUMENTS_JSON` | 参数 JSON |
| `IOP_OUTPUT_DIR` | 本次操作的独立输出目录 |
| `IOP_RESULT_FILE` | 程序写入的 JSON 结果文件 |
| `IOP_PROGRESS_FILE` | 可选 JSON：`fraction` 为 0–1，`message` 为进度说明 |
| 标准输出、标准错误 | 直接保存为文件 |

参数数组中的 `{python}` 使用服务的 Python；`{request}`、`{output}`、`{result}` 指向上述文件和目录。`${name}` 将一个参数作为独立命令行参数传入，数组和对象采用 JSON。`config.env` 添加程序需要的环境变量。`timeout` 以秒计，默认为 0，表示不设总时长。

程序以退出码 0 表示成功；写入 `IOP_RESULT_FILE` 的值作为操作结果，没有结果文件时返回退出码。输出目录内的文件随实验保存。提供厂商接口的旧程序可以加一层很薄的启动脚本，完成参数转换与结果导出。

在服务计算机上运行完整示例：

```sh
python iop/examples/software/register.py
```

该示例登记一个数组处理程序，运行两个有数据依赖的步骤，并保存 CSV。它展示的是程序接入格式，可以替换成实际求解器或分析程序。

## 异步 HTTP 任务

```json
{
  "id":"remote-solver","driver":"http",
  "config":{
    "mode":"software","base_url":"http://compute-host:9000",
    "operations":{
      "solve":{
        "parameters":{"model":{"type":"string"}},
        "method":"POST","path":"/jobs","body":{"model":"${model}"},
        "job":{
          "id_path":["id"],
          "status":{"path":"/jobs/{job_id}"},
          "state_path":["state"],"result_path":["result"],
          "completed":["completed"],"failed":["failed"],"cancelled":["cancelled"],
          "cancel":{"method":"POST","path":"/jobs/{job_id}/cancel","body":{}},
          "poll_interval":1,"timeout":0
        }
      }
    }
  }
}
```

按服务实际接口修改路径、字段和状态名。`progress_path` 可指向 0–1 的进度值。IOP 取得任务编号后持续查询；发出取消请求后，等待远端报告结束。远端已经受理但结果无法取得时，操作记录保留任务编号和未确定的状态，供后续查询。

## 可安装驱动包

第三方驱动包在 `pyproject.toml` 声明入口：

```toml
[project.entry-points."ai4instruments.drivers"]
lab-sensor = "my_lab.sensor:Sensor"
```

在 IOP 的 Python 环境中安装包后，`iop adapters` 显示入口，设备记录可直接使用 `"driver":"lab-sensor"`。驱动实现 `describe()`、`invoke(operation, arguments, context)`、`close()`；上下文支持取消、进度和文件输出。厂商 SDK 需要独立环境时，使用[独立驱动进程](drivers.md)。

## 软件发现与重新连接

`config.json` 可以列出可执行程序的候选名称或路径：

```json
{"software_profiles":[{"id":"solver","executables":["solver","/opt/solver/bin/solver"]}]}
```

`iop discover` 返回找到的路径，不启动计算。已有 `profiles` 规则可按 `transport:"command"` 和 `program:"solver"` 匹配并登记对应说明。软件本身支持的模型和操作由说明提供。

`iop reconnect DEVICE` 重新建立连接；共用一个 SDK 进程的设备一起重连。已经受理的相关操作结束后才能执行重连。平台配置、历史数据与无关设备保持可用。
