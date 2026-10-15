# Experimental relations and examples

An experimental architecture should extend when a new question introduces a new instrument or physical interaction. The examples below are organized around relations that recur across research, rather than a list of supported disciplines. Each relation can appear within many fields, and an experiment can combine several. These are design examples; the [runnable reference](../examples/README.md) is a software simulation of optical alignment.

## Produce an interaction and observe its response

An experiment establishes a source, a path of interaction, a target, and an observation. In optics, light is generated, propagates through free space, fiber, or a chip, interacts with matter, and reaches a detector. Electrical excitation and readout, acoustic scattering, and mechanical loading share aspects of this organization while retaining different physical models.

Basic Operations expose source controls, switching, positioning, detector configuration, triggering, and readout. Standard Operations create an interpretable measurement: for a CMOS camera, this includes exposure, gain, region of interest, timing, pixel encoding, and the identity of corrections. Workflow Operations coordinate excitation and acquisition, compare observations with a hypothesis, and choose the next condition.

The essential relations include geometry, propagation, delay, bandwidth, background, and the connection between the applied stimulus and measured response. Changing a detector setting may alter the interpretation of the data; changing a sample may alter the entire response model. Preserve raw observations and actual settings so that new interpretations can be tested.

A reused alignment method may improve collection efficiency, but maximizing intensity need not answer the research question. The same measurement operations can instead investigate a response law, discriminate between mechanisms, or find a previously unobserved regime. That choice belongs to the investigation.

## Transform matter and connect preparation to properties

Many experiments relate a material's history to its later behavior. Reagent addition, stirring, and heating; precursor synthesis and controlled-atmosphere processing; thin-film deposition; electrochemical sequences; and solid-state synthesis or sintering all instantiate parts of this relation.

Basic Operations expose the relevant actuators and observations: material delivery, motion, temperature, pressure, atmosphere, electrical stimulus, and sensing. Standard Operations express measured dispensing, mixing, a process profile, a deposition step, or a characterization method. Workflow Operations connect formulation, transformation, transfer, measurement, and the next design decision.

A materials investigation might proceed from a proposed formulation to precursor synthesis, precision shaping under vacuum or a specified atmosphere, and X-ray diffraction or electron microscopy, then relate structure to performance. The transferable structure is the connection between preparation, realized state, and observation. It does not require every experiment to use that sequence or those techniques.

Nominal recipes are insufficient when delivery, mixing, thermal lag, or processing history affects the result. Keep measured profiles and sample identity, including division into specimens and later combination. Characterization geometry and preparation are part of the evidence. A result then describes a particular material with a recoverable history rather than an isolated number.

## Intervene in a system that changes over time

Living samples, aging materials, cycling devices, and evolving environments continue changing between commands. An operation's effect depends on when it occurs and on the accumulated history. Long-duration research therefore requires a model of continuity, not just a sequence of independent tasks.

A biological example begins with visual assessment of a sample, followed by handling such as aspiration, enzymatic treatment, or dosing, then controlled environmental maintenance and repeated imaging. Centrifugation, cell passage and inoculation, precision pipetting, and gradient dilution can become Standard Operations with explicit specimen-dependent conditions. Workflow Operations connect assessment, standardized dispensing, intervention, time-lapse observation, and phenotype analysis with the next experimental choice.

The same organizational problem appears when studying fatigue or device degradation: loading and measurement histories belong to the object under study, and earlier interventions affect later responses. Shared descriptions of time, identity, state, and intervention can transfer; biological lineage and mechanical damage still need their respective scientific meanings.

Preserve observations separately from segmentation, phenotype estimates, fitted parameters, or other analysis. Record which estimate informed each action. Later models can then revisit earlier data without turning retrospective knowledge into evidence that was available during the experiment.

## Coordinate physical work across instruments and locations

Some experiments are limited by the availability and arrangement of apparatus rather than by any individual operation. Preparation may occur at one station, specialized characterization at another, and analysis elsewhere. Parallel experiments may share a source, environment, manipulator, or measurement device.

Workflow composition must represent both information flow and physical flow. A dataset can be copied while a specimen must be transported; a measurement can consume or modify a specimen; queueing can change its condition before the next procedure. Execution requires explicit dependencies, identity, transfer conditions, and meaningful completion observations.

Across laboratories, a common operation name is a starting point. Transfer also needs compatible physical quantities, units, calibration, specimen preparation, timing, and result interpretation. Where instruments differ, capability descriptions should expose the difference so that the method can be adapted deliberately.

This permits collaboration without making every laboratory identical. One facility can contribute a new measurement method, another a different instrument implementation, and another a replicated result. The accumulated resource is an expanding set of methods, designs, observations, and explanations. None of these examples is intended to close that set.
