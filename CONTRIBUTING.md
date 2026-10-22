# Contributing

Start with a concrete experimental capability or an observed limitation. A good contribution gives another researcher enough information to understand the behaviour, reproduce the relevant result and adapt it to their apparatus.

## Choose a contribution

| Contribution | Useful accompanying evidence |
| --- | --- |
| Instrument description or adapter | Model/configuration, capability inventory, units, state and timing semantics, characterised behaviour. |
| Basic Operation | A precise effect or observation, abstraction level, implementation and readback. |
| Standard Operation | Lower-level composition, applicability, completion criteria and returned data. |
| Workflow Operation | Dependencies, concurrent branches, sample identity, feedback decisions and results. |
| Circuit, firmware or mechanical improvement | The limitation motivating it, design changes and before-and-after characterisation. |
| Dataset or trajectory | Linked context, interventions, observations, analysis and conditions of reuse. |
| Documentation or paper improvement | A specific argument, correction, primary source or worked example. |

Describe capability, experimental evidence and task objectives separately. Preserve measured failures and inconclusive observations when they help explain behaviour. Name the exact implementation and apparatus to which a claim applies.

## Make a change

1. Open an issue describing the scientific or engineering problem, or submit a focused pull request for a concrete improvement.
2. Put Python implementation under `src/`, runnable experiments under `examples/iop/`, and explanatory design material under `docs/`. IOP has its main entry at `iop/`, with the Rust executor in `iop/daemon/`, TypeScript client in `iop/clients/typescript/`, and platform descriptions in `iop/schema/` and `iop/examples/`.
3. Run `python -m unittest discover -s tests -v` when changing the reference implementation. Add a behavioural test when a change introduces a meaningful new contract or fixes a fault.
4. For paper edits, update `paper/manuscript.md` and, when needed, `paper/references.json`. Run `python scripts/build_paper.py` and inspect the PDF and HTML before committing both outputs.
5. State what changed, why it matters, how it was checked and which results were observed on hardware or in simulation.

Use Basic Operations, Standard Operations and Workflow Operations consistently. Keep names short, descriptions factual and examples connected to a scientific question.

Code contributions use the MIT License. Documentation and original figures use CC BY 4.0. Include attribution for material you reuse under compatible terms.
