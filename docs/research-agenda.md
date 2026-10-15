# Research agenda

The central research question is whether instruments designed for inspectable, extensible programmatic use enable more capable and more transferable experimental work. The ambition includes experiments beyond sustained manual operation. It should be evaluated through demonstrated tasks and measurements.

## 1. Establish what is actually exposed

Build capability inventories for a small but varied set of instruments, such as a camera, motion controller, source, pump, and temperature controller. Map each declared control and observation to its Basic Operations.

Report coverage by capability class, including inaccessible functions and unsupported state combinations. A single percentage can conceal the difference between many minor settings and one missing experimental degree of freedom. Measure both individual operations and combinations that expose interactions.

**Deliverable:** a versioned inventory, operation definitions, and characterization records that another developer can inspect and repeat.

## 2. Test transfer across implementations

Implement a shared operation profile on devices with different controllers or vendors. Transfer a Standard Operation, then a multi-device workflow. Record which changes concern syntax, units, timing, calibration, sample handling, or genuinely different capabilities.

Useful measures include adapter changes, workflow edits, characterization effort, and the resulting experimental equivalence. Equivalent method names do not establish equivalent measurements. Compare results within stated uncertainty and under matched conditions.

**Deliverable:** one procedure executed across distinct implementations, with an explicit account of what transferred and what required revision.

## 3. Evaluate sustained experimental execution

Run sequences long enough to expose drift, buffer limits, synchronization errors, communication interruption, and changes in sample state. Record completed measurements, invalid or missing observations, interruption duration, and the physical state before and after continuation.

Report latency distributions, timing jitter, data completeness, and time spent producing usable observations. Count retries and repeat measurements separately. A command log that looks complete can still conceal an experiment that produced little interpretable data.

**Deliverable:** a reproducible endurance experiment with a timeline of requested actions, observed events, and usable results.

## 4. Measure the value of deeper access

Compare a fixed high-level interface with an interface that also permits changes to Basic Operations, device-local sequences, or firmware. Choose a task for which the deeper access has a plausible physical benefit: synchronized acquisition, adaptive sampling, reduced dead time, or a new measurement mode.

Hold the scientific objective and evaluation budget constant. Measure the resulting precision, throughput, information gained, or accessible parameter range. Include the effort required to develop and characterize the change. Deeper access is valuable when it improves experimental capability, not simply because it produces more code.

**Deliverable:** a measured example connecting a low-level modification to a scientific or engineering outcome.

## 5. Test open-ended composition

Compare reuse of existing Standard Operations with the ability to inspect, modify, and compose them for a new objective. Use tasks whose solution cannot be obtained by selecting an unchanged example workflow.

Evaluate whether the new procedure answers the intended question, preserves interpretable observations, and performs well under equal resource budgets. Novel code alone is not a scientific contribution; a useful new measurement or experimentally supported finding is.

**Deliverable:** a new experiment with an explicit account of which established assumptions or procedures needed to change.

## 6. Connect experimental traces to learning

Represent trajectories with the objective, available evidence, operation versions, requested actions, observed states, raw data references, analysis versions, and outcome. Preserve failed and inconclusive attempts with their actual context. Retrospective explanations should be distinguishable from information available at the time of a decision.

Investigate separate uses: learning device dynamics, predicting operation outcomes, selecting informative measurements, composing procedures, and improving scientific reasoning. Each requires a different target and evaluation.

Split evaluation by experimental campaign, device instance, laboratory, or task family where appropriate, rather than randomly separating adjacent frames from one run. Compare with models that lack the added trajectories, and test on held-out tasks. Evaluate successful experimental behavior and sample efficiency as well as prediction accuracy.

**Deliverable:** a documented dataset and controlled evaluation showing whether experimental experience improves subsequent performance.

## 7. Connect laboratories through reproducible meaning

Extend exchange beyond operation names to sample identity, preparation history, measurement context, calibration, and result formats. Begin with one transferable experiment between two laboratories. Record the adaptations needed and the sources of disagreement.

The long-term objective is a growing body of instruments, operations, and evidence that different laboratories can use and improve. Progress is visible when a new participant can reproduce a meaningful measurement, extend it, and return an interpretable result to the shared body of knowledge.
