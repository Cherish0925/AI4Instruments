---
name: iop-lab
description: Use IOP to operate instruments or scientific software, submit experiments, and retrieve laboratory results.
---

# Operate a laboratory

Read `lab_context` on the selected connection. Keep its name alongside the run ID: IDs belong to the service that issued them. Reuse the saved platform. Read `describe_instrument` for operation names, arguments and units. A discovered port alone does not identify an instrument, a sample or its wiring.

When building a platform, use the manufacturer's device description and the observed connections. Ask the operator only for information that cannot be read or a physical change that cannot be performed remotely. Preview and save the platform definition; run its initialization procedure separately if the experiment needs it.

Submit an operation graph with `submit_experiment`, or a research program with `submit_program`. Declare dependencies for steps whose order matters and shared resources for operations that cannot overlap. Keep timing that requires a hardware clock or trigger on the instrument. Program paths and download destinations refer to the computer running the MCP bridge.

Choose a request ID before submitting. Save the returned run ID; a receipt means the service accepted the run. If the reply is lost, repeat the identical submission with its original request ID. Read `experiment` for operations, status, results and files. Closing the client leaves the laboratory service running. Use `cancel_experiment` only when cancellation is intended. Continue an interrupted program through its saved checkpoints when the program supports it.
