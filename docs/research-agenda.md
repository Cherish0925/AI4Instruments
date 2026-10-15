# Research agenda

AI4Instruments asks how instruments and computational research methods can develop together, so that each expands what the other can accomplish. The ambition includes experiments beyond the duration, coordination, precision, and exploratory capacity of sustained manual work. Progress should connect new capabilities to the scientific or engineering questions they make tractable.

## Make experimental capability explicit

The first problem is to describe what an instrument enables without reducing it to its current application software. Map physical mechanisms to controls, observations, timing relationships, and accessible combinations. Compare the resulting description with what the instrument actually does.

Completeness is a research question about this mapping. Counting commands is insufficient: one missing synchronized control or independent observation can exclude an entire class of experiments. Study which capability gaps matter, how they arise across hardware and software layers, and how new designs remove them.

## Establish what transfers

Transfer can concern a single method, a multi-instrument experiment, an interpretation of data, or an instrument design. Test these separately across different implementations, tasks, physical systems, and laboratories. The relevant invariant may be a measured quantity or causal relationship, while numerical parameters and apparatus must change.

Measure the adaptation required and whether the resulting experiment retains its intended meaning. A universal framework should make differences explicit and support new scientific types. It should not achieve apparent generality by removing the information that distinguishes one measurement from another.

## Expand capability through deeper development

Investigate when access to Basic Operations, controllers, firmware, circuits, and physical design makes a scientific difference. Compare alternative implementations of the same experimental objective. Useful outcomes include a new measurable regime, improved resolution, reduced dead time, more reliable inference, or a previously inaccessible combination of interventions.

Hardware and software should be considered jointly. A new controller sequence may exploit an existing capability; an added sensor may reveal the state needed for better control; a mechanical or circuit redesign may enable a fundamentally different method. Account for development and characterization effort alongside the resulting benefit.

## Sustain research while revising its methods

Long-duration autonomy requires an evolving account of instrument and sample state. Examine drift, changing calibration, interruptions, resource contention, and observations that contradict the current model. Measure the production of interpretable evidence over time, not merely the fraction of commands that return successfully.

Research also changes its own procedures. Evaluate tasks that require constructing or revising Standard Operations and Workflow Operations, rather than selecting an unchanged example. Compare methods by how well they resolve the scientific objective under a stated resource budget. Novelty can appear in measurement design, intervention, interpretation, or the instrument itself.

## Turn experimental experience into transferable learning

Real-world trajectories connect decisions to consequences that cannot be obtained from text alone. Record the objective, evidence available at each decision, operation and instrument versions, requested actions, observed conditions, raw data, analyses, and outcomes. Failed and inconclusive attempts can reveal dynamics or assumptions absent from successful runs.

Different learning questions need different targets: predicting device behavior, estimating physical state, designing informative measurements, composing methods, improving code, or reasoning about mechanisms. Evaluate improvement on new experiments, apparatus, or laboratories; adjacent observations from one run cannot establish broad transfer.

The same evidence can improve an instrument's design and the system that uses it. Study this interaction explicitly: a learned model proposes a revised method or instrument, measurements assess its effect, and the resulting experience informs the next revision. The goal is cumulative experimental competence, demonstrated through subsequent work.

## Build a shared experimental ecosystem

Develop exchange around meaningful capabilities, physical entities, methods, designs, and evidence. Preserve local specialization while making interfaces and results understandable elsewhere. A new participant should be able to inspect an existing contribution, reproduce its relevant behavior, extend it, and return a result that others can use.

Useful milestones are connected demonstrations: an instrument exposes a previously hidden degree of freedom; a method transfers between distinct implementations; an investigation creates a new operation; experimental experience improves later decisions; or laboratories combine capabilities to answer a question none could address alone. Together these advances move from isolated automation toward a growing, collaborative capacity for research.
