# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Integration tests — error propagation from pylib exceptions to Ansible fail_json against a live OPNsense device.

Requirements:
    - Live OPNsense device accessible via OPN_HOST, OPN_KEY, OPN_SECRET env vars
    - API user must have full admin privileges
    - Run with: pytest tests/integration/test_error_propagation.py -v

Test flow (ordered):
    1. Auth error 401              — OpnsenseAuthError maps to fail_json with status_code=401
    2. Validation error 400        — OpnsenseValidationError maps to fail_json with validations dict
    3. Endpoint missing 404        — OpnsenseEndpointMissingError maps to fail_json with status_code=404
    4. Timeout error                — OpnsenseTimeoutError maps to fail_json with 'timed out' message
    5. Connection error             — OpnsenseConnectionError maps to fail_json with 'Connection failed'
    6. Server error 500             — OpnsenseServerError maps to fail_json with status_code=500
    7. Ambiguous match error        — AmbiguousMatchError maps to fail_json with uuids and match_keys
    8. Field validation error       — FieldValidationError maps to fail_json with 'Input validation failed'
    9. Unexpected error             — RuntimeError maps to fail_json with 'Unexpected error'
    10. Generic OpnsenseError       — base exception maps to fail_json with status_code and message

Naming convention:
    All test objects use prefix 'inttest-' to avoid collision with real config.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "plugins", "module_utils"))
from opnsense_helper import _handle_opnsense_error  # noqa: E402
from opnsense.exceptions import (
    AmbiguousMatchError,
    FieldValidationError,
    OpnsenseAuthError,
    OpnsenseConnectionError,
    OpnsenseEndpointMissingError,
    OpnsenseServerError,
    OpnsenseTimeoutError,
    OpnsenseValidationError,
)


class TestErrorMapping:
    """Verify each pylib exception maps to correct fail_json call."""

    def _mock_module(self):
        m = MagicMock()
        m.fail_json = MagicMock(side_effect=SystemExit(1))
        return m

    def test_auth_error_401(self):
        module = self._mock_module()
        exc = OpnsenseAuthError("test", endpoint="auth/user/search")
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        module.fail_json.assert_called_once()
        call_kwargs = module.fail_json.call_args[1]
        assert call_kwargs["status_code"] == 401
        assert "Authentication failed" in call_kwargs["msg"]

    def test_validation_error_400(self):
        module = self._mock_module()
        exc = OpnsenseValidationError(
            "test", endpoint="fw/filter", validations={"rule.name": "required"},
        )
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        call_kwargs = module.fail_json.call_args[1]
        assert call_kwargs["status_code"] == 400
        assert "Validation failed" in call_kwargs["msg"]
        assert "validations" in call_kwargs
        assert call_kwargs["validations"] == {"rule.name": "required"}

    def test_endpoint_missing_404(self):
        module = self._mock_module()
        exc = OpnsenseEndpointMissingError("test", endpoint="x")
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        call_kwargs = module.fail_json.call_args[1]
        assert call_kwargs["status_code"] == 404
        assert "Endpoint not found" in call_kwargs["msg"]

    def test_timeout_error(self):
        module = self._mock_module()
        exc = OpnsenseTimeoutError("test", endpoint="x")
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        assert "timed out" in module.fail_json.call_args[1]["msg"]

    def test_connection_error(self):
        module = self._mock_module()
        exc = OpnsenseConnectionError("test", endpoint="x")
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        assert "Connection failed" in module.fail_json.call_args[1]["msg"]

    def test_server_error_500(self):
        module = self._mock_module()
        exc = OpnsenseServerError("test", endpoint="x")
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        assert module.fail_json.call_args[1]["status_code"] == 500

    def test_ambiguous_match_error(self):
        module = self._mock_module()
        exc = AmbiguousMatchError(
            message="2 matches",
            match_keys={"name": "test"},
            uuids=["uuid1", "uuid2"],
        )
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        call_kwargs = module.fail_json.call_args[1]
        assert "Ambiguous match" in call_kwargs["msg"]
        assert call_kwargs["uuids"] == ["uuid1", "uuid2"]
        assert call_kwargs["match_keys"] == {"name": "test"}

    def test_field_validation_error(self):
        module = self._mock_module()
        exc = FieldValidationError("port", "abc", "must be numeric")
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        assert "Input validation failed" in module.fail_json.call_args[1]["msg"]

    def test_unexpected_error(self):
        module = self._mock_module()
        exc = RuntimeError("something broke")
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        assert "Unexpected error" in module.fail_json.call_args[1]["msg"]

    def test_generic_opnsense_error(self):
        """OpnsenseError base class (not a specific subclass) is caught."""
        from opnsense.exceptions import OpnsenseError

        module = self._mock_module()
        exc = OpnsenseError("generic API error", status_code=502, endpoint="x")
        with pytest.raises(SystemExit):
            _handle_opnsense_error(module, exc)
        call_kwargs = module.fail_json.call_args[1]
        assert "generic API error" in call_kwargs["msg"]
        assert call_kwargs["status_code"] == 502
