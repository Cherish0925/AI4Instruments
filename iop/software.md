# Software and driver extensions

[IOP Runtime](README.md) · [中文](software.zh-CN.md) · [Execution](execution.md)

Choose the adapter that matches the tool's existing interface. Scheduling and records stay consistent; adapters express device commands, model operations and domain-specific formats.

| Existing interface | Adapter |
| --- | --- |
| SCPI or Modbus | Built-in adapter plus model-specific description |
| Python SDK | `module:Class` or an installed driver entry point |
| Persistent C / C++ / C# / Java SDK | `process` JSON-lines worker |
| Command-line program | `command`, starting a program for each operation |
| Synchronous HTTP JSON | `http` operation description |
| HTTP submission, status and result API | `http` with a `job` description |

## Executable programs

```json
{"id":"processor","driver":"command","config":{
  "mode":"software","concurrency":4,"cwd":"/absolute/path/to/program",
  "requirements":{"cpu":1},
  "operations":{"calculate":{"command":["{python}","calculate.py"],
    "parameters":{"x":{"type":"number"}}}}
}}
```

Configure the `cpu` capacity before submitting work. `command` is an executable and argument array, passed without a shell. It can instead invoke Node.js, a compiled Rust/C/C++ executable, `dotnet analysis.dll` or `java -jar analysis.jar`.

| Input or output | Content |
| --- | --- |
| Standard input and `IOP_REQUEST_FILE` | JSON containing operation, arguments, run ID, operation ID and output directory |
| `IOP_ARGUMENTS_JSON` | Argument JSON |
| `IOP_OUTPUT_DIR` | This operation's independent output directory |
| `IOP_RESULT_FILE` | JSON result written by the program |
| `IOP_PROGRESS_FILE` | Optional JSON with a 0–1 `fraction` and a `message` |
| Standard output and standard error | Written directly to files |

`{python}` selects the service's interpreter. `{request}`, `{output}` and `{result}` select the corresponding paths. `${name}` passes one argument as a single command-line argument; arrays and objects use JSON. `config.env` adds environment variables. `timeout` is in seconds; the default 0 imposes no total duration limit.

Exit code 0 indicates success. The result file's JSON becomes the operation result; absent a result file, the operation returns the exit code. Output files stay with the experiment. A small wrapper can translate this format into an existing solver's arguments and exported results.

Run the complete example on the service computer:

```sh
python iop/examples/software/register.py
```

It registers an array-processing program, runs two dependent operations and saves CSV files. Replace the processor with the actual computation or analysis program.

## Asynchronous HTTP services

```json
{"id":"remote-solver","driver":"http","config":{
  "mode":"software","base_url":"http://compute-host:9000",
  "operations":{"solve":{
    "parameters":{"model":{"type":"string"}},
    "method":"POST","path":"/jobs","body":{"model":"${model}"},
    "job":{"id_path":["id"],"status":{"path":"/jobs/{job_id}"},
      "state_path":["state"],"result_path":["result"],
      "completed":["completed"],"failed":["failed"],"cancelled":["cancelled"],
      "cancel":{"method":"POST","path":"/jobs/{job_id}/cancel","body":{}},
      "poll_interval":1,"timeout":0}
  }}
}}
```

Match paths, fields and state names to the actual service. `progress_path` may select a 0–1 progress value. IOP follows the submitted job until its service confirms completion. After requesting cancellation, it waits for the remote terminal state. If an accepted job's outcome becomes unavailable, its ID and unresolved outcome remain in the operation record for subsequent inspection.

## Installable driver packages

Declare the entry point in the adapter package's `pyproject.toml`:

```toml
[project.entry-points."ai4instruments.drivers"]
lab-sensor = "my_lab.sensor:Sensor"
```

After installing the package into IOP's Python environment, `iop adapters` lists it and a device record may use `"driver":"lab-sensor"`. Implement `describe()`, `invoke(operation, arguments, context)` and `close()`. The context supplies cancellation, progress and output files. SDKs needing separate environments use the [independent driver interface](drivers.md).

## Discovery and reconnection

Software discovery profiles in `config.json` name candidate executables:

```json
{"software_profiles":[{"id":"solver","executables":["solver","/opt/solver/bin/solver"]}]}
```

`iop discover` returns found paths without starting a calculation. Existing `profiles` rules may match `transport:"command"` and `program:"solver"` to register the corresponding description. Supported models and operations come from that description.

`iop reconnect DEVICE` reconnects a device and any other devices sharing its SDK worker. Accepted operations using those devices must finish first. Platform definitions, records and unrelated devices remain available.
