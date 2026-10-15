# Operations

An instrument should expose what it can do and what it can observe in a form that a program can inspect, execute, and extend. AI4Instruments organizes this interface into **Basic Operations**, **Standard Operations**, and **Workflow Operations**. These names describe levels of composition, not competing control protocols.

## Basic Operations

A Basic Operation is an elementary, explicitly defined control or observation at a declared abstraction level. Examples include setting a controller output, reading a sensor channel, selecting a camera trigger source, or reading a completed frame. An instrument's **complete set of basic operations** is its declared foundation for programmable use.

“Complete” needs a boundary. For each device version, enumerate its controllable degrees of freedom, observable quantities, timing capabilities, and accessible states. A complete interface covers that inventory directly or through a documented composition that preserves the required behavior. Coverage of a published inventory does not establish access to undisclosed hardware capabilities.

“Basic” is also relative to a boundary. A camera's acquisition interface may expose `arm`, `trigger`, and `read_frame`; its sensor-development interface may additionally expose readout timing and register fields. Both can be useful. Neither should pretend that an exposure is physically instantaneous or that one API call corresponds to one transistor-level event.

Prefer distinct meanings and avoid duplicate operations whose differences cannot be explained. Do not require all operations to be mutually nonconflicting. Moving a stage and changing its velocity may affect the same controller; triggering an exposure and changing a readout mode may interact. Those relationships belong in the interface.

## The operation contract

Each operation needs enough information to construct a valid experiment and interpret what happened.

| Field | Question it answers |
| --- | --- |
| Identity and version | Which device, firmware, interface, and operation definition is this? |
| Inputs | What are the types, units, ranges, reference frames, and defaults? |
| State | In which states is the operation defined, and what state changes follow? |
| Effect and readback | What does a request change, and how is the resulting condition observed? |
| Timing | When is it accepted, started, and completed; which clock timestamps each event? |
| Resources | Which channels, axes, buffers, and shared controllers does it use? |
| Result | What data, status, measured condition, or completion handle is returned? |
| Exceptions | What does an interrupted, partial, unsupported, or indeterminate result mean? |
| Measurement context | Which calibration, uncertainty description, and acquisition settings apply? |

A requested temperature is not a measured temperature. An accepted move is not a completed move. An empty data buffer is not necessarily a zero signal. Interfaces must preserve these distinctions.

Reissuing an operation also has a meaning: a repeated setpoint may replace an earlier value, while a repeated trigger may create another measurement. Each definition should state that behavior. Device-local scheduling should be available when host communication cannot deliver the required timing.

## Standard Operations

A Standard Operation is a reusable procedure with an experimentally meaningful result. It composes Basic Operations and states the conditions under which the procedure has that meaning.

For example, `acquire_image` may select exposure and readout settings, arm the camera, trigger acquisition, wait for completion, and return a frame with its actual settings and timestamps. Its useful contract includes pixel encoding, dimensions, region of interest, saturation indicators, and the meaning of any correction applied to the data.

Other examples are dispensing a specified volume, performing a centrifugation cycle, recording an electrochemical sweep, and depositing a film under a defined process profile. “Standard” means a documented reusable procedure within a declared profile; it does not imply universal standardization or experimental validity on every device.

The composition should remain inspectable. A caller may need to replace a timing sequence, add a measurement, or work directly with Basic Operations when the existing procedure hides a relevant variable.

## Workflow Operations

A Workflow Operation coordinates procedures across devices, samples, and time. It expresses serial dependencies, parallel activity, transfers, feedback, and completion conditions.

An optical workflow can illuminate a sample, adjust a stage, collect an image, estimate a response, and choose the next setting. A materials workflow can connect formulation, synthesis, processing, characterization, and model revision. Parallel branches require explicit shared resources and synchronization points; visual proximity in a diagram does not establish that two actions can run together.

Workflow composition should preserve the original observations and the identity of each sample or specimen. A result becomes much less useful if its preparation history cannot be reconstructed.

## Reuse without prescribing a research direction

Operation descriptions explain capabilities. Experimental objectives specify what a study seeks. Evaluation records describe what previous uses achieved. Keep these three things separate.

Descriptions should not contain promotional instructions, hidden rewards, or assertions that an established workflow is always preferable. Retain factual evidence: a calibration result, measured latency, failed attempt, or reproducibility estimate can matter greatly to a new experiment. Such evidence needs its conditions and provenance rather than a universal preference score.

The interface should let a researcher or AI inspect an existing operation, compose it differently, revise it, or develop a new one. Novel experiments still need well-defined actions and interpretable observations. Open-ended research depends on that foundation.
