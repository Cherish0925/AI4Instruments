# Executable optical alignment

This example makes the operation model inspectable. Two independent positioning axes change the coupling into an optical detector. A search procedure chooses the next position from measured power, while the instrument descriptions contain only capabilities, parameters, and observed quantities.

The bench is a deterministic software simulation. Its purpose is to expose the relationships between commands, observations, composition, and experimental decisions in a small program that can be read in one sitting.

## Run

Python 3.10 or newer is sufficient. From the repository root:

```bash
python examples/optical_alignment.py --output runs/optical-alignment
python -m unittest discover -s tests -v
```

No package installation is required. The run writes:

| File | Content |
| --- | --- |
| `capabilities.json` | Operation IDs, argument units and ranges, timing semantics, result fields, model scope, and the three operation layers. |
| `trace.jsonl` | Ordered calls, parent-child relationships, measurements, objective evaluations, decisions, and the final result. |
| `summary.json` | Initial and final measured power, selected position, objective, seed, and evaluation count. |

The default seed is `17`. The observed output is:

```json
{
  "mode": "simulation",
  "seed": 17,
  "evaluations": 22,
  "initial_power_uW": 23.73404,
  "final_power_uW": 99.979081,
  "selected_position_mm": {"x": 0.65625, "y": -0.40625}
}
```

These values describe this simulator, not a physical alignment experiment. To change the measurement-noise sequence, pass `--seed 23`.

## From capabilities to a closed loop

| Layer | Operations | Composition |
| --- | --- | --- |
| **Basic Operations** | `x.write_target`, `x.read_position`, `y.write_target`, `y.read_position`, `detector.write_exposure`, `detector.read_exposure`, `detector.acquire` | Direct control or observation at the declared model boundary. |
| **Standard Operations** | `x.position`, `y.position`, `detector.capture` | Position and observe convergence; configure exposure, read it back, and acquire. |
| **Workflow Operations** | `optics.measure_at` | Position the two axes concurrently, then acquire after both have converged. |

The outer `align` function defines the experimental objective and search strategy. It is ordinary Python rather than a property of the device. A different strategy can use the same capabilities without changing their meaning.

In `optics.measure_at`, both positioning nodes can progress independently. The capture node waits for both completed observations. The DAG scheduler also supports serial chains, larger branching graphs, and dependency lists in arbitrary input order. A malformed graph is rejected before it starts, and a failed node cancels and drains the remaining tasks. Cancellation does not imply that already executed physical actions could be undone.

## What “complete” means here

[capabilities.json](capabilities.json) declares an abstraction level: **two-axis position and detector acquisition**. Its seven Basic Operations cover every control and observation represented by this model:

- Controls: x target, y target, and detector exposure.
- Observations: x position, y position, active detector exposure, and optical power.

This is a checkable coverage claim about a declared model. The model contains no electronics, firmware, polarization controller, or real device connection. Expanding its physical representation would require expanding the declared capabilities and reviewing the coverage claim.

The operation descriptions include dimensions and parameter bounds. A target must be supplied as `{"value": 0.5, "unit": "mm"}` within `[-2, 2]`; an exposure must use `ms` within `[1, 100]`. Unit conversion is explicit. Unknown fields, missing arguments, nonfinite values, and incompatible units are rejected before invoking a device handler.

## Commands, observations, and time

`x.write_target` returns a **commanded** target. It does not report that the axis has arrived. `x.read_position` returns an **observed** position, a sample index, and the axis's local model time. `x.position` repeatedly observes the axis until its measured error is at most `0.001 mm`.

The simulated mechanics follow a first-order response. At each position sample, the axis closes 75% of its remaining error. Each sample advances that axis's model time by 1 ms. The detector advances its own model time by the configured exposure on each acquisition. These local clocks are explicitly modeled quantities; the JSONL sequence is event order and is not a synchronized physical clock. `asyncio` expresses concurrency and dependencies, not hard real-time execution.

Operations on x and y are independent. This workflow serializes accesses to each individual device. The minimal runtime does not implement device locks or multi-process arbitration; a hardware adapter must map these access assumptions to the instrument's own execution model.

## Feedback and provenance

The synthetic power model is a Gaussian centered at `(0.65, -0.4) mm`, with width `0.45 mm` and peak `100 uW`. Seeded measurement noise scales with the inverse square root of exposure. The search procedure cannot read the center or ideal power through the operation API; it receives measured values.

The search evaluates the starting point, then tests positive and negative moves along each axis at step sizes `0.5`, `0.25`, `0.125`, `0.0625`, and `0.03125 mm`. Each accepted candidate is selected by the separate objective **maximize observed optical power**. A final acquisition returns the bench to the selected position and measures it again. This simple strategy illustrates feedback; it does not establish global optimization or robustness to arbitrary noise and drift.

Every call has a stable operation ID and a unique invocation ID. Nested calls carry a parent ID, and DAG calls carry their node ID. A detector acquisition has a measurement ID; the corresponding evaluation references that ID and records the score used in the decision. The trace therefore distinguishes:

1. What the controller requested.
2. What the instrument model reported.
3. How the experimental objective evaluated that observation.
4. Which next position the search selected.

The initial trace record identifies the seed, model version, mode, and initial state. Repeating a run in the same Python environment produces the same trace. The tests reconstruct objective evaluations from acquisition records and check parent-child links. This verifies trace consistency; it is not a replay engine for physical instruments.

## Change one layer at a time

- Replace the search in `align` to explore different experimental objectives or optimization methods.
- Modify `optics.measure_at` to change serial and parallel composition.
- Modify a Standard Operation to change its convergence or acquisition procedure.
- Replace Basic Operation handlers to connect a different model or a physical adapter, retaining accurate units, readback semantics, and capability coverage.

The seven tests cover command/readback separation, invalid inputs, concurrent independence and dependency ordering, malformed graphs, cancellation after failure, deterministic feedback and trace consistency, and agreement between the published capability manifest and the implementation.
