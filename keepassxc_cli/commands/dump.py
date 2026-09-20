from __future__ import annotations

import argparse
import logging
from pathlib import Path

from keepassxc_browser_api import BrowserClient, BrowserConfig

from keepassxc_cli.config import CliConfig
from keepassxc_cli.output import ensure_scheme, print_entry_detail

logger = logging.getLogger(__name__)


def add_parser(subparsers: argparse._SubParsersAction, fmt_parent: argparse.ArgumentParser | None = None) -> None:
    parents = [fmt_parent] if fmt_parent else []
    p = subparsers.add_parser(
        "dump",
        parents=parents,
        help="Show every field on matching entries, including raw KPH: attribute names and passwords",
    )
    p.add_argument("url", help="URL or search string")
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
    url = ensure_scheme(args.url)
    entries = client.get_logins(url)
    if not entries:
        logger.warning("No entries found for: %s", args.url)
        return 1
    for entry in entries:
        # Dump everything: password, TOTP, and raw KPH: string field names.
        print_entry_detail(entry, fmt, show_password=True, show_kph_prefix=True)
        if fmt == "table" and len(entries) > 1:
            print()
    return 0