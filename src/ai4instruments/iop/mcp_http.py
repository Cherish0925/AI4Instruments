"""Streamable HTTP for hosts without a local MCP process."""

import hmac
import os
import sys


def application(client, token):
    if not token or not token.isascii() or any(c.isspace() for c in token):
        raise ValueError("Set IOP_MCP_TOKEN to a nonempty ASCII bearer token without spaces.")
    from .mcp import create_server

    server = create_server(client, http=True)
    options = dict(stateless_http=True, json_response=True) if sys.version_info >= (3, 11) else {}
    app = server.streamable_http_app(**options)
    expected = ("Bearer " + token).encode("ascii")

    async def authenticated(scope, receive, send):
        if scope["type"] == "http":
            headers = [v for k, v in scope.get("headers", ()) if k == b"authorization"]
            if len(headers) != 1 or not hmac.compare_digest(headers[0], expected):
                await send(
                    {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [(b"www-authenticate", b"Bearer")],
                    }
                )
                await send({"type": "http.response.body", "body": b"Unauthorized"})
                return
        await app(scope, receive, send)

    return authenticated


def run(home, endpoint, port):
    token = os.environ.get("IOP_MCP_TOKEN")
    if not token:
        raise ValueError("Set IOP_MCP_TOKEN in the gateway environment before starting it.")
    import uvicorn
    from .desktop import ensure_service

    app = application(ensure_service(home, endpoint), token)
    uvicorn.run(app, host="127.0.0.1", port=port, proxy_headers=False, access_log=False)
