# Experimental platform configuration

[中文](platforms.zh-CN.md) · [IOP](README.md) · [Schema](schema/platform.schema.json)

A service manages its computer's instruments. Platforms describe how those instruments form experimental systems. Several platforms can reference one device; the same scheduler coordinates its use.

| Relationship | Representation | Execution meaning |
| --- | --- | --- |
| Optical, fluid, electrical, trigger or sample connections | Platform `connections` | Document actual devices and ports; do not infer commands or synchronization from a connection label. |
| Shared instruments, samples, buses, vessels or spatial regions | Platform `resources` | Order conflicting operations. Resource IDs are global within one service. |
| Dependencies for this experiment | Experiment or procedure `steps[].after` | Wait for predecessors; run compatible independent branches concurrently. |

A resource lists the devices that use it. Its optional `operations` mapping restricts that use to named operations, for example `{"stage":["move_to"],"meter":["measure"]}`, allowing meter configuration alongside motion. Without a selection, all operations on that device use the resource.

An experiment's top-level `resources` reserves equipment and shared objects across steps until completion. Per-operation ordering alone does not preserve a complete change-condition, settle, measure sequence.

## Run two platforms

These commands use the simulated devices created by `init --demo`. Choose another `--home` directory when an existing installation contains real instruments.

```sh
iop init --demo
iop start
iop platform apply iop/examples/platform.json
iop platform apply iop/examples/independent-platform.json
iop platform initialize materials-bench --wait
iop run iop/examples/experiment.json --wait
iop open
```

The second platform uses `aux` and can run independently. To configure laboratory equipment:

```sh
iop discover
iop register devices.json
iop platform draft my-bench --devices camera stage meter --output my-bench.json
```

A person or agent fills in actual connections, shared resources and initialization steps, then runs:

```sh
iop platform preview my-bench.json
iop platform apply my-bench.json
iop platform initialize my-bench --wait
```

`preview` parses without saving or operating devices. `apply` saves a description. `initialize` submits the declared procedure using the usual scheduling, cancellation and recording mechanisms.

The existing temperature, balance, pump and acquisition program also uses platform descriptions:

```sh
iop register examples/iop/multi-instrument/devices.json
iop platform apply iop/examples/liquid-platform.json
iop platform initialize liquid-bench --wait
iop package examples/iop/multi-instrument --platform liquid-bench --resources bath balance pump daq --wait
```

This program uses measured mass to decide subsequent dispensing.

## Versions and continued execution

`iop platform show my-bench` returns the current revision. Supply that revision when updating, for example `iop platform apply my-bench.json --revision 1`. The next saved revision is 2. Use `iop platform history my-bench` to retrieve history.

Wait for affected experiments to finish before changing configuration. Each run retains the submitted platform definition and revision. Later changes leave earlier records intact. Shared resources apply across platforms and to direct calls that omit a platform.

```python
from ai4instruments.iop import Client
lab = Client()
run = lab.submit([
    {"id": "move", "device": "stage", "operation": "move_to", "arguments": {"angle_deg": 20}},
    {"id": "read", "device": "meter", "operation": "measure", "after": ["move"]},
], platform="materials-bench", resources=["stage", "meter"])
print(run.id)
# The caller may exit; reconnect with lab.run(run_id).
```

Remote agents use a reachable service endpoint and its token. The service hosts uploaded experiment packages on the instrument computer, so a long run needs no persistent cloud request. Analysis may run locally or remotely; instrument operations pass through the service.
