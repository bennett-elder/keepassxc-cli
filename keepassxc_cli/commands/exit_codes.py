from __future__ import annotations

import argparse
import json
from pathlib import Path

from keepassxc_browser_api import BrowserClient, BrowserConfig

from keepassxc_cli.config import CliConfig

EXIT_CODES: list[dict] = [
    {"code": 0, "name": "SUCCESS",           "description": "Command completed successfully"},
    {"code": 1, "name": "ERROR",             "description": "Generic or unexpected error"},
    {"code": 2, "name": "CONNECTION_ERROR",  "description": "Could not connect to KeePassXC (not running or socket missing)"},
    {"code": 3, "name": "DATABASE_LOCKED",   "description": "KeePassXC database is locked"},
    {"code": 4, "name": "ACCESS_DENIED",     "description": "KeePassXC denied access to entries"},
]


def add_parser(subparsers: argparse._SubParsersAction, fmt_parent: argparse.ArgumentParser | None = None) -> None:
    parents = [fmt_parent] if fmt_parent else []
    p = subparsers.add_parser("exit-codes", parents=parents, help="List all exit codes and their meanings")
    p.set_defaults(func=run)


def run(
    client: BrowserClient,
    args: argparse.Namespace,
    cli_config: CliConfig,
    browser_config: BrowserConfig,
    browser_config_path: Path,
    *,
    fmt: str = "table",
) -> int:
    if fmt == "json":
        print(json.dumps(EXIT_CODES, indent=2))
    else:
        col_w = 6
        name_w = max(len(e["name"]) for e in EXIT_CODES)
        print(f"{'CODE':<{col_w}}  {'NAME':<{name_w}}  DESCRIPTION")
        print(f"{'-' * col_w}  {'-' * name_w}  {'-' * 40}")
        for e in EXIT_CODES:
            print(f"{e['code']:<{col_w}}  {e['name']:<{name_w}}  {e['description']}")
    return 0
