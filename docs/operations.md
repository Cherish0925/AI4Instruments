# Operations

An instrument makes a part of the physical world accessible to deliberate intervention and observation. Its programmable interface should express that access: what can change, what can be measured, where and when an interaction occurs, and how the resulting evidence is obtained. This definition applies to individual components, complete instruments, assemblies, and distributed experimental facilities. It does not depend on a discipline, vendor, control protocol, or particular kind of AI.

AI4Instruments uses **Basic Operations**, **Standard Operations**, and **Workflow Operations** to describe three roles in constructing experiments. They are compositional roles, not a fixed catalogue of scientific actions. A procedure can become a constituent of another procedure; a new instrument can introduce controls and observations for which no existing operation name is suitable.

## Basic Operations: access to experimental degrees of freedom

A Basic Operation exposes an elementary control or observation at a specified interface. Examples are selecting a controller output, reading a sensor channel, setting a trigger condition, or retrieving an acquired record. The defining property is an explicit, independently usable meaning at that interface, rather than a particular command size or duration.

**A complete set of basic operations** gives access to all controllable and observable degrees of freedom within a stated instrument configuration and abstraction level, including their valid combinations. Establishing completeness requires an inventory of controls, observations, modes, timing relationships, and combinations. An interface that exposes every individual setting but prevents their meaningful simultaneous use may still conceal a substantial part of the instrument's capability.

The inventory should connect each exposed operation to the physical mechanism it controls or observes. It should also identify what is available only through a deeper interface, what requires a hardware modification, and what remains uncharacterized. This makes the boundary a subject of instrument development rather than a permanent restriction imposed by the original software.

At a camera acquisition interface, `arm`, `trigger`, and `read_frame` can be basic. At a sensor-development interface, readout timing, register fields, and signal-processing stages may also be exposed. Neither level eliminates the other. Basic does not mean instantaneous, indivisible in nature, or guaranteed to execute without interruption.

Prefer distinct meanings and avoid unexplained duplication. Physical independence cannot be assumed: two controls may share a power supply, change the same sample, or alter one another's effect. Represent these couplings instead of requiring every operation to be mutually nonoverlapping or nonconflicting.

## Describe relations, preserve physical meaning

A common description needs to express the relations that experiments depend on without replacing the language of each science.

| Relation | Information needed for composition |
| --- | --- |
| Intervention and target | The affected entity, controlled quantity, units, reference frame, and intended change. |
| Observation and source | The measured quantity, sensing location, acquisition conditions, calibration, and uncertainty. |
| State and history | Preconditions, persistent changes, preparation history, and whether a repetition creates a new event. |
| Space and connectivity | Coordinate transforms, physical connections, sample locations, and routes of transfer. |
| Time and dependency | Duration, completion criteria, clocks, synchronization, and ordering requirements. |
| Resources and coupling | Shared channels, actuators, buffers, environments, specimens, and concurrent-use relationships. |
| Result and evidence | Requested values, observed values, execution status, raw data, and interpretation. |

The vocabulary can be extended. A waveform, composition, image, stress field, and cell lineage retain their own structures. Generality comes from making these structures discoverable and composable, rather than forcing them into a universal numerical setpoint.

An operation definition includes its identity and version, parameter types, relevant relations, and result semantics. An accepted command, an electrically generated signal, and an observed physical change are different events. Likewise, an empty buffer, a zero measurement, and a missing measurement have different meanings. A delayed or partial result must remain distinguishable from completed execution.

## Standard Operations: reusable experimental methods

A Standard Operation combines controls and observations into a method with an experimentally meaningful outcome. Image acquisition, calibrated dispensing, a temperature profile, an impedance measurement, and a centrifugation cycle are examples. Each method states the conditions under which its result has the claimed meaning.

For instance, acquiring an image involves more than returning an array: exposure, illumination, timing, pixel encoding, geometry, and any corrections determine what the array represents. A dispensing procedure relates actuator motion to delivered material through calibration and observations. The meaningful abstraction is established through this physical relationship.

“Standard” means a reusable, documented method; it does not mean compulsory, universally standardized, or optimal for every experiment. Its implementation and assumptions should be inspectable. A researcher or AI can replace a constituent operation, introduce a different measurement, revise a method, or create a new one. The definition need not privilege procedures that happened to be implemented first.

## Workflow Operations: experimental organization

A Workflow Operation organizes methods, physical entities, instruments, and decisions over time. It can include serial and parallel execution, branching, iteration, transfer, and feedback. Its scope may be a short measurement, a prolonged investigation, or a coordinated experiment across facilities.

Composition requires more than matching input and output types. A transferred specimen must actually reach the next apparatus in the required condition; a measurement may depend on an earlier intervention having settled; two nominally separate branches may modify a shared environment. These relationships belong to the experimental program.

Workflows should retain access to their constituents and support revision during research. Existing workflows are useful accumulated knowledge. They do not define the space of permissible scientific questions or require every future experiment to follow the same decomposition.

## Capability, objective, and experience

Keep three meanings distinct. **Capability descriptions** explain what an instrument or procedure does. **Study objectives** explain what the current investigation seeks and how its choices are evaluated. **Evidence records** explain what happened under specified conditions.

Capability descriptions should contain no promotional instructions, hidden incentives, or preferred research conclusions. Measured performance, calibration, failures, and prior results remain valuable evidence, with their conditions and provenance. Their relevance to a new objective is a scientific judgment, not a preference embedded in an operation name.

The same operations can serve a language-model agent, a learned controller, Bayesian optimization, an evolutionary search, or a conventional experimental program. Each can choose and revise methods through its own reasoning or optimization process. Interoperability concerns what can be done and learned from the result, not how the next action is selected.
