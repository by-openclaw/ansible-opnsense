# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Drive a Proxmox VE serial console over the termproxy websocket.

Why this exists: a freshly imaged OPNsense box has no API, no SSH and no configuration, so the
only way to hand it a `config.xml` is the appliance's own boot-time importer — and that importer
gates on a keypress (`opnsense-importer`, upstream `src/sbin/opnsense-importer`). Everything after
that first boot is ordinary API work; this module_util covers only the gap before it.

Transport: `POST /nodes/{node}/qemu/{vmid}/termproxy` returns a ticket, then
`wss://…/vncwebsocket` carries the session. Input frames are `0:{len}:{bytes}` on channel 0.
"""

from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request

HAS_WEBSOCKET = True
WEBSOCKET_IMPORT_ERROR = None
try:
    import websocket  # type: ignore
except ImportError as exc:  # pragma: no cover - exercised by the module's own check
    HAS_WEBSOCKET = False
    WEBSOCKET_IMPORT_ERROR = str(exc)


class PveConsoleError(Exception):
    """Anything that stops us reaching or driving the console."""


class PveConsole:
    """A Proxmox API client plus one serial-console session for a VM."""

    def __init__(self, host, node, vmid, token_id, token_secret, validate_certs=False, port=8006):
        self.host = host
        self.node = node
        self.vmid = int(vmid)
        self.auth = "PVEAPIToken={0}={1}".format(token_id, token_secret)
        self.validate_certs = bool(validate_certs)
        self.port = int(port)
        self._ws = None

    # ---------------- REST ----------------
    def _ctx(self):
        ctx = ssl.create_default_context()
        if not self.validate_certs:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def api(self, method, path, body=None):
        url = "https://{0}:{1}/api2/json{2}".format(self.host, self.port, path)
        headers = {"Authorization": self.auth}
        data = None
        if body is not None:
            data = urllib.parse.urlencode(body).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, context=self._ctx(), timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise PveConsoleError(
                "PVE API {0} {1} -> HTTP {2}: {3}".format(
                    method, path, exc.code, exc.read().decode(errors="replace")[:300]
                )
            )
        except Exception as exc:  # noqa: BLE001 - surfaced verbatim to the operator
            raise PveConsoleError("PVE API {0} {1} failed: {2}".format(method, path, exc))

    def status(self):
        return str(self.api("GET", "/nodes/{0}/qemu/{1}/status/current".format(self.node, self.vmid))["data"].get("status"))

    def start(self):
        return self.api("POST", "/nodes/{0}/qemu/{1}/status/start".format(self.node, self.vmid))

    # ---------------- console ----------------
    def open(self):
        """Open the termproxy websocket and complete its handshake."""
        if not HAS_WEBSOCKET:
            raise PveConsoleError("the python 'websocket-client' library is required: " + str(WEBSOCKET_IMPORT_ERROR))
        tp = self.api("POST", "/nodes/{0}/qemu/{1}/termproxy".format(self.node, self.vmid))["data"]
        qs = urllib.parse.urlencode({"port": tp["port"], "vncticket": tp["ticket"]})
        url = "wss://{0}:{1}/api2/json/nodes/{2}/qemu/{3}/vncwebsocket?{4}".format(
            self.host, self.port, self.node, self.vmid, qs
        )
        ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE} if not self.validate_certs else None)
        ws.connect(url, header=["Authorization: {0}".format(self.auth)], subprotocols=["binary"])
        ws.settimeout(0.1)
        ws.send_binary("{0}:{1}\n".format(tp["user"], tp["ticket"]).encode())
        self._ws = ws
        # the server answers OK once the session is live
        deadline = time.time() + 5
        buf = b""
        while time.time() < deadline:
            chunk = self.read()
            if chunk:
                buf += chunk
                if b"OK" in buf:
                    return
        raise PveConsoleError("termproxy did not acknowledge the session (no OK): {0!r}".format(buf[:80]))

    def read(self):
        """Non-blocking-ish read; b'' when nothing is pending."""
        try:
            chunk = self._ws.recv()
        except websocket.WebSocketTimeoutException:
            return b""
        except websocket.WebSocketConnectionClosedException:
            raise PveConsoleError("the console websocket closed unexpectedly")
        if isinstance(chunk, str):
            chunk = chunk.encode()
        return chunk

    def send(self, data):
        """Write to the guest on termproxy channel 0."""
        if isinstance(data, str):
            data = data.encode()
        self._ws.send_binary("0:{0}:".format(len(data)).encode() + data)

    def close(self):
        if self._ws is not None:
            try:
                self._ws.close()
            finally:
                self._ws = None
