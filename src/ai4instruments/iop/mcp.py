"""MCP tools forward to the same IOP service used by the desktop and SDKs."""
from __future__ import annotations
import json
import importlib.util
import sys
from pathlib import Path
from typing import Literal
from urllib.parse import quote


def create_server(client):
    try:
        if sys.version_info >= (3, 11):
            from mcp.server import MCPServer as Server
        else:
            from mcp.server.fastmcp import FastMCP as Server
    except ImportError as error:
        raise RuntimeError('Run the IOP release installer with IOP_AGENT=1, or install ".[agent]" from the source directory.') from error
    from mcp.types import ToolAnnotations
    read_only = ToolAnnotations(readOnlyHint=True, openWorldHint=False)

    server = Server('IOP Runtime', instructions=(
        'Read lab_context first. Reuse saved instrument and platform descriptions. '
        'Ask for physical wiring and sample details only when missing. '
        'Read describe_instrument before choosing operations and arguments. '
        'Saving platform configuration does not execute initialization. '
        'Submit experiments or programs once, retain the returned ID and inspect them later. '
        'Reuse request_id after a connection failure; the runtime schedules devices and retains results.'))

    @server.tool()
    def lab_context(refresh: bool = False, after: int | None = None, device_offset: int | None = None) -> dict:
        """Read a compact laboratory overview. Pass its cursor as after on subsequent reads to receive only changes. Device and platform descriptions are fetched when needed."""
        if device_offset is not None:
            return client.device_page(device_offset)
        return client.changes(after) if after is not None else client.context(refresh)

    @server.tool(annotations=read_only)
    def describe_instrument(device: str) -> dict:
        """Read a registered instrument's operations, parameters and units."""
        return client.request('/v1/devices/' + quote(device, safe=''))

    @server.tool(annotations=read_only)
    def configuration_schema(name: Literal['device', 'platform', 'workflow', 'instrument-profile']) -> dict:
        """Read the JSON schema before preparing a device, platform or workflow definition."""
        return client.schema(name)

    @server.tool()
    def register_instrument(definition: dict) -> dict:
        """Register an installed driver and connection configuration. Repeating the identical definition reuses the device."""
        return client.register(definition)

    @server.tool()
    def instrument_configuration(device: str, definition: dict | None = None, expected_revision: int | None = None) -> dict:
        """Read current and previous instrument settings, or save a replacement definition at the current revision while idle. Reapply a previous definition to restore it."""
        if definition is None:
            return {'versions': client.device_history(device)}
        return client.configure_device(device, definition, expected_revision)

    @server.tool()
    def register_instruments(definitions: list[dict]) -> dict:
        """Register multiple instrument descriptions. IDs may be omitted. Each result names its input index and device or error; successful items remain saved."""
        return client.register_many(definitions)

    @server.tool()
    def discover_instruments(refresh: bool = True) -> dict:
        """Start a shared background scan, or read its cached results with refresh=false. While scanning=true, other laboratory work can continue. Interfaces and USB inventory are separate collections in the summary."""
        return client.start_discovery() if refresh else client.inventory()

    @server.tool()
    def identify_instrument(device: str, request_id: str | None = None) -> dict:
        """Query a configured SCPI instrument through the experiment scheduler. Identity is saved and matching model operations are added. Returns a run ID immediately."""
        return client.identify(device, request_id).info(details=False)

    @server.tool(annotations=read_only)
    def instrument_profiles() -> list[dict]:
        """Read installed model descriptions and their source manuals. Discovery reports required configuration for each connection."""
        return client.instrument_profiles()

    @server.tool()
    def save_instrument_profile(definition: dict) -> dict:
        """Save a reusable model description: id, exact manufacturer/model match, driver, config.operations and source documentation. Use commands from that model's programming manual."""
        return client.save_instrument_profile(definition)

    @server.tool()
    def retry_instrument_discovery(connection_key: str | None = None) -> dict:
        """Retry discovery after correcting a connection or installing a driver. Existing experiments keep their instruments."""
        return client.retry_discovery(connection_key)

    @server.tool()
    def configure_platform(definition: dict, expected_revision: int = 0, preview: bool = False) -> dict:
        """Save devices, physical connections, shared resources and procedures. Use the current revision, or 0 for a new platform. Preview checks the definition without saving; neither option executes a procedure."""
        if preview:
            return client.request('/v1/platforms/preview', {'definition': definition})
        return client.configure_platform(definition, expected_revision)

    @server.tool()
    def configure_resources(capacities: dict[str, int]) -> dict:
        """Set the full collection of named CPU, GPU, software-license or other resource capacities. Read lab_context for current values first."""
        return client.configure_resources(capacities)

    @server.tool()
    def run_procedure(platform: str, request_id: str, procedure: str = 'initialize') -> dict:
        """Execute a saved platform procedure. Returns immediately with its run ID."""
        return client.procedure(platform, procedure, request_id).info(details=False)

    @server.tool()
    def submit_experiment(steps: list[dict], request_id: str, name: str = 'Experiment',
                          platform: str | None = None, resources: list[str] | None = None,
                          requirements: dict[str, int] | None = None) -> dict:
        """Submit instrument operations with after dependencies and optional result bindings. Returns immediately. Reuse request_id only for the identical submission."""
        return client.submit(steps, name=name, platform=platform, resources=resources or [],
                             requirements=requirements, request_id=request_id).info(details=False)

    @server.tool()
    def submit_program(path: str, request_id: str, platform: str | None = None,
                       resources: list[str] | None = None, parameters: dict | None = None,
                       requirements: dict[str, int] | None = None) -> dict:
        """Upload an experiment directory or ZIP from this MCP host to the instrument service. The service executes it independently of the agent connection."""
        return client.submit_package(Path(path).expanduser(), request_id=request_id, platform=platform,
                                     resources=resources or [], parameters=parameters,
                                     requirements=requirements).info(details=False)

    @server.tool(annotations=read_only)
    def experiment(run_id: str, after: int = 0, include_result: bool = False) -> dict:
        """Read experiment status, the next 100 operation records and output file descriptions. Pass the returned cursor as after; request the result when needed."""
        run = client.run(run_id)
        result = {'run': run.info(details=False), 'operations': run.operations(after, 100), 'files': run.files()}
        if include_result:
            result['result'] = client.request('/v1/runs/' + quote(run_id, safe='') + '/result')
        return result

    @server.tool()
    def cancel_experiment(run_id: str) -> dict:
        """Request cancellation. In-flight instrument operations finish or report their actual cancellation before their resources are released."""
        return client.run(run_id).cancel()

    @server.tool()
    def continue_program(run_id: str, request_id: str | None = None) -> dict:
        """Read saved program progress, or pass request_id to continue a stopped program that declares resume:true. The program reads its progress and reuses completed operation IDs."""
        run = client.run(run_id)
        if request_id is None:
            return {'run': run.info(details=False), 'checkpoints': run.checkpoints()}
        run.resume(request_id)
        return run.info(details=False)

    @server.tool()
    def reconnect_instrument(device: str) -> dict:
        """Reconnect a registered instrument or SDK worker after its accepted operations have ended."""
        return client.reconnect(device)

    @server.tool()
    def resolve_resources(resources: list[str], observation: str) -> dict:
        """Return interrupted resources to use after recording the observed instrument state. Read resource_holds in lab_context for the exact resource names."""
        return client.request('/v1/resources/resolve', {'resources': resources, 'observation': observation})

    @server.tool()
    def download_file(artifact_id: str, destination: str) -> dict:
        """Download an experiment output to a new file on this MCP host. Use artifact IDs returned by experiment."""
        path = Path(destination).expanduser().resolve()
        if path.exists():
            raise ValueError('Choose a new output filename: ' + str(path))
        client.run('').download(artifact_id, path)
        return {'path': str(path), 'size': path.stat().st_size}

    @server.resource('iop://laboratory')
    def laboratory_resource() -> str:
        return json.dumps(client.context(), ensure_ascii=False)

    return server


def run(home, endpoint=None):
    if importlib.util.find_spec('mcp') is None:
        raise RuntimeError('Install the Agent component: python -m pip install "ai4instruments[agent]"')
    from .desktop import ensure_service
    client = ensure_service(home, endpoint)
    create_server(client).run(transport='stdio')
