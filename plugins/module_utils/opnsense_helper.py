# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Shared helper for all OPNsense Ansible modules.

Provides the run_module() wrapper that handles:
- OpnsenseClient lifecycle (async with + finally close)
- Typed exception mapping to Ansible fail_json()
- Structured result formatting
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Callable, Coroutine

from ansible.module_utils.basic import AnsibleModule


def opn_argument_spec() -> dict[str, Any]:
    """Return the shared argument spec for OPNsense connection parameters."""
    return {
        "host": {"type": "str", "required": True},
        "key": {"type": "str", "required": True, "no_log": True},
        "secret": {"type": "str", "required": True, "no_log": True},
        "port": {"type": "int", "default": 443},
        "verify_ssl": {"type": "bool", "default": False},
    }


async def run_ensure(
    module: AnsibleModule,
    manager_factory: Callable,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Execute an ensure() call with proper try/except/finally.

    Args:
        module:          AnsibleModule instance.
        manager_factory: Callable that takes an OpnsenseClient and returns a manager.
        params:          Parameters to pass to manager.ensure().

    Returns:
        Dict with changed, action, uuid, diff keys for module.exit_json().

    Raises:
        SystemExit: Via module.fail_json() on any error — never returns on failure.
    """
    from opnsense.client import OpnsenseClient
    from opnsense.logging import configure_logging

    # Enable structured logging — JSON to file
    # Priority: /var/log/opnsense/ → ~/.opnsense/logs/
    if os.path.isdir("/var/log/opnsense"):
        log_dir = "/var/log/opnsense"
    else:
        log_dir = os.path.join(os.path.expanduser("~"), ".opnsense", "logs")
    os.makedirs(log_dir, exist_ok=True)
    configure_logging(
        level="DEBUG" if module._verbosity >= 2 else "INFO",
        log_file=os.path.join(log_dir, "ansible-opnsense.log"),
        colorize=False,  # no colors in module subprocess — JSON only
    )

    client = None
    try:
        client = OpnsenseClient(
            host=module.params["host"],
            key=module.params["key"],
            secret=module.params["secret"],
            port=module.params["port"],
            verify_ssl=module.params["verify_ssl"],
        )
        await client.__aenter__()

        mgr = manager_factory(client)
        result = await mgr.ensure(
            state=module.params["state"],
            params=params,
            check_mode=module.check_mode,
        )

        diff: dict[str, Any] = {}
        if result.before is not None:
            diff["before"] = result.before
        if result.after is not None:
            diff["after"] = result.after

        return {
            "changed": result.changed,
            "action": result.action,
            "uuid": result.uuid or "",
            "diff": diff,
        }

    except ImportError as exc:
        module.fail_json(
            msg="lib-opnsense is required but not installed. "
            "Install with: pip install opnsense",
            exception=str(exc),
        )
    except Exception as exc:
        _handle_opnsense_error(module, exc)
    finally:
        if client is not None:
            await client.close()

    # Unreachable — fail_json calls sys.exit, but mypy needs a return
    return {}


def _handle_opnsense_error(module: AnsibleModule, exc: Exception) -> None:
    """Map lib-opnsense exceptions to Ansible fail_json with typed messages."""
    try:
        from opnsense.exceptions import (
            OpnsenseAuthError,
            OpnsenseConnectionError,
            OpnsenseEndpointMissingError,
            OpnsenseError,
            OpnsenseServerError,
            OpnsenseTimeoutError,
            OpnsenseValidationError,
        )
    except ImportError:
        module.fail_json(msg=str(exc), exception=str(exc))
        return

    if isinstance(exc, OpnsenseAuthError):
        module.fail_json(
            msg=f"Authentication failed: {exc}. Check API key and secret.",
            status_code=401,
        )
    elif isinstance(exc, OpnsenseValidationError):
        module.fail_json(
            msg=f"Validation failed: {exc}",
            status_code=400,
            validations=exc.validations,
        )
    elif isinstance(exc, OpnsenseEndpointMissingError):
        module.fail_json(
            msg=f"Endpoint not found: {exc}. Check OPNsense version >= 26.1.",
            status_code=404,
        )
    elif isinstance(exc, OpnsenseTimeoutError):
        module.fail_json(
            msg=f"Request timed out: {exc}. Check connectivity and timeout settings.",
        )
    elif isinstance(exc, OpnsenseConnectionError):
        module.fail_json(
            msg=f"Connection failed: {exc}. Check host, port, and network.",
        )
    elif isinstance(exc, OpnsenseServerError):
        module.fail_json(
            msg=f"OPNsense server error: {exc}. Retry or check device health.",
            status_code=500,
        )
    elif isinstance(exc, OpnsenseError):
        module.fail_json(
            msg=str(exc),
            status_code=getattr(exc, "status_code", None),
        )
    else:
        module.fail_json(msg=f"Unexpected error: {exc}", exception=str(exc))


def run_module(
    module: AnsibleModule,
    manager_factory: Callable,
    params: dict[str, Any],
) -> None:
    """Synchronous entry point — wraps run_ensure() in asyncio.run().

    Args:
        module:          AnsibleModule instance.
        manager_factory: Callable that takes an OpnsenseClient and returns a manager.
        params:          Parameters to pass to manager.ensure().
    """
    result = asyncio.run(run_ensure(module, manager_factory, params))
    module.exit_json(**result)
