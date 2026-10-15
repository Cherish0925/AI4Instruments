# Designing instruments for programmable research

AI4Instruments treats an instrument as something that can be designed, understood, programmed, measured, and improved through a continuous research process. The central idea is **AI design and implementation + AI development and use**. The same experimental evidence that informs a scientific question can also reveal how the instrument should change.

## Start with experimental possibilities

The initial design brief should describe what the instrument must make possible: accessible inputs, observable responses, spatial and temporal scales, resolution, stability, sample conditions, and interaction with other equipment. A list of familiar workflows is useful, but insufficient. Future experiments may require combinations of controls that the original workflow never used.

Maintain a capability inventory alongside the physical design. For each degree of freedom, record its physical mechanism, control path, available readback, constraints, and calibration method. Record missing observations as well: an actuator command without an independent measurement leaves a different experimental uncertainty from a closed measurement loop.

## Design across the whole lifecycle

| Stage | Design artifact | Question carried forward |
| --- | --- | --- |
| Concept | Experimental requirements and capability inventory | Which effects and observations should be possible? |
| Physical design | Mechanical, optical, fluidic, thermal, and electrical models | Which couplings determine achievable behavior? |
| Implementation | Schematics, component choices, firmware, and host interfaces | Can the intended behavior be generated and measured? |
| Manufacturing and assembly | Revision records, tolerances, assembly procedures, and test fixtures | How does the built unit differ from the design? |
| Characterization and calibration | Response measurements, uncertainty, drift, and operating envelopes | What does this particular unit actually do? |
| Experimental use | Programs, readbacks, raw observations, and sample histories | Which behaviors help or limit the research? |
| Redesign | Traced changes to hardware, firmware, and operations | Does the modification improve the measured capability? |

AI participation can occur at every stage, but evidence must connect the stages. A simulation predicts behavior; fabrication and measurement establish the behavior of the realized instrument.

## Electrical control connects programs to physical processes

Programmable electronics provide a practical bridge between software and many actuators and sensors. A useful design exposes this bridge clearly: controller commands, electrical outputs, physical effects, sensing, digitization, and returned data.

Electronics do not exhaust the instrument's physics. Geometry, friction, fluid transport, optical alignment, thermal inertia, materials, and sample history may dominate performance. An electrical interface can command a valve; it does not by itself establish the delivered volume. Programmability and observability should therefore be designed together.

For existing equipment, the bridge may pass through a vendor API, serial commands, an acquisition card, or a mechanical retrofit. For new equipment, the design can make these paths explicit from the beginning.

## Expose meaningful depth

A useful instrument can provide several connected entry points:

- Experiment procedures for common tasks.
- Basic Operations for independently addressable controls and observations.
- Controller and firmware interfaces for timing, buffering, signal processing, and new operating modes.
- Hardware design information for modifications to electronics and the physical apparatus.

The deeper interfaces need machine-readable register definitions where applicable, units and signal scaling, clock relationships, memory layouts, build instructions, revision identifiers, and characterization procedures. Merely exposing an undocumented register bank does not make an instrument understandable.

The analogy to GPU kernel optimization is productive: access below a high-level library can reveal useful combinations and remove unnecessary overhead. Instrument optimization additionally changes a physical process. A faster command sequence may still be limited by settling, diffusion, exposure, or signal-to-noise requirements. Improvements should be demonstrated in the relevant observable, not inferred from fewer software calls.

## Put execution at the appropriate timescale

Host programs are appropriate for experiment planning, analysis, and many device commands. Tightly timed sequences may belong in a microcontroller, FPGA, camera sequencer, or other local controller. The host should be able to define such sequences, start them, and retrieve both data and execution records.

Specify whether timing refers to command dispatch, device acceptance, electrical output, or a measured physical event. Where instruments use different clocks, document how their timestamps can be compared and the uncertainty of that comparison. This turns synchronization from an assumption into an experimental quantity.

## Make improvement cumulative

Publish enough design and characterization information for another laboratory to reproduce an interface and assess a result. A common operation vocabulary can coexist with device-specific extensions; capability discovery should make the distinction explicit.

When an experiment reveals a limitation, trace it to a layer: insufficient observation, controller behavior, software composition, physical design, or sample variability. Then change the relevant layer and repeat the measurement. This is how AI4Instruments can become more than a collection of drivers: instrument development and scientific use become a shared, inspectable cycle.
