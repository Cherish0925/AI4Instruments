# Experimental designs

These examples describe how the three operation levels can support different forms of experimental work. They are proposed designs. The [runnable optical simulation](../examples/README.md) demonstrates software composition and feedback; it does not establish hardware performance or validate the other procedures below.

## Optics: measurement and adaptive alignment

**Research question:** How does a sample's response depend on illumination and alignment, and which measurement should follow?

| Level | Representative content |
| --- | --- |
| Basic Operations | Set a source parameter; request an axis position; read position; configure exposure; arm and trigger acquisition; retrieve a frame. |
| Standard Operations | Acquire an image with recorded settings; measure a background; move and verify settling; estimate a signal statistic. |
| Workflow Operations | Generate light, propagate it through the apparatus, interact with a sample, acquire a response, analyze it, and choose the next condition. |

The apparatus has state beyond its latest command: source output, stage position, camera configuration, background, and sample condition. Store the requested and observed conditions together. Separate raw frames from background corrections and derived scores so an alternative analysis can revisit the same measurements.

A high signal score is useful for alignment, but may not answer a scientific question. A research workflow can instead choose measurements that distinguish competing response models or estimate an uncertain parameter. The objective belongs to that study, not to the definition of `acquire_image`.

**Research value:** continuous measurement over a space too large or time-consuming for manual exploration, with a trace connecting each chosen condition to its evidence.

## Chemistry: formulation and reaction response

**Research question:** Which formulation and process conditions explain a measured reaction response?

Basic Operations expose pump motion or flow settings, valve selection, stirring control, temperature settings, sensor readings, and sampling actions. Standard Operations convert these into experimentally meaningful procedures such as dispensing a measured amount, mixing, applying a thermal profile, and acquiring an analytical measurement.

A workflow prepares a formulation, carries out a reaction sequence, collects measurements, and updates the next experimental choice. Some phases can overlap across vessels; others compete for a shared dispensing head or analytical instrument. Represent these dependencies explicitly.

The state record should include vessel identity, additions and their order, actual temperatures, elapsed times, and sampling history. A nominal recipe alone cannot explain differences caused by delivery error, mixing, thermal lag, or carryover. Calibration measurements connect actuator commands to delivered quantities.

**Research value:** relating observed outcomes to preparation and process history, then choosing experiments that resolve uncertainty about that relationship.

## Biology: longitudinal observation with adaptive handling

**Research question:** How does a sample's measured phenotype evolve under controlled conditions?

Basic Operations include positioning, image acquisition, fluid handling controls, environmental setpoints, and sensor readback. Standard Operations can provide measured dispensing, dilution, sample transfer, centrifugation cycles, or a defined passage procedure when the apparatus and specimen permit it.

A workflow begins with visual assessment, performs an appropriate handling procedure, maintains the environment, and returns to repeated observation. Imaging and handling histories remain linked to the same sample and its descendants. Time-lapse measurements require explicit time references and a record of interruptions.

Keep acquired images distinct from segmentation, tracking, and phenotype estimates. An updated analysis model should be able to reprocess earlier observations without rewriting the acquisition record. When an assessment changes the next action, preserve the estimate and uncertainty used at that decision point.

**Research value:** linking temporal behavior to documented interventions while making it possible to revise the analysis as the scientific question develops.

## Materials: synthesis, processing, and characterization

**Research question:** How do composition and processing history determine structure and performance?

Basic Operations expose dispensing or weighing measurements, atmosphere and pressure control, thermal control, motion, and characterization acquisition. Standard Operations may include precursor preparation, film deposition, an electrochemical sequence, a thermal treatment, or a characterization scan.

A workflow proposes a formulation, prepares precursors, processes the material under recorded conditions, transfers it to characterization, and connects measured structure and performance to the next design. A sample may be split into several specimens; preserve that relationship rather than treating each measurement as an unrelated row.

Store measured process profiles alongside nominal recipes. Record mounting, orientation, geometry, and preparation where they affect characterization. Raw diffraction patterns, microscopy data, or electrical measurements should remain available alongside derived descriptors.

**Research value:** learning from the full composition-process-structure-property relationship, including outcomes that challenge the current model.

## What transfers between domains

The common foundation is not a universal experimental recipe. It is a consistent way to describe actions, observations, timing, resources, composition, and evidence. Domain meaning remains essential: an image, a delivered volume, a cell lineage, and a processed specimen require different models.

An extensible interface preserves these differences while allowing each field to reuse the machinery of programmable experiments. New Standard Operations and Workflow Operations can then grow from the same inspectable foundation without restricting future research to today's examples.
