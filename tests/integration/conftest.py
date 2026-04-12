# Copyright (c) 2026 BY-SYSTEMS SRL. MIT License.
# SPDX-License-Identifier: MIT
# Repo: https://github.com/by-openclaw/ansible-opnsense
"""Ansible integration test fixtures — requires live OPNsense device."""
from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest

from opnsense.client import OpnsenseClient
from opnsense.credentials import get_credentials
from opnsense.logging import configure_logging


def pytest_configure(config):
    """One log file per pytest run."""
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S")
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    configure_logging(
        level="DEBUG",
        log_file=os.path.join(log_dir, f"ansible-inttest-{ts}.log"),
        colorize=True,
    )


@pytest.fixture
async def opn_client():
    """Create a live OpnsenseClient from env credentials."""
    creds = get_credentials()
    async with OpnsenseClient(
        host=creds.host,
        key=creds.key,
        secret=creds.secret,
        port=creds.port,
        verify_ssl=creds.verify_ssl,
    ) as client:
        yield client
