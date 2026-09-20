from __future__ import annotations

import argparse
import logging
from pathlib import Path

from keepassxc_browser_api import BrowserClient, BrowserConfig

from keepassxc_cli.config import CliConfig
from keepassxc_cli.output import ensure_scheme, _strip_kph

logger = logging.getLogger(__name__)

# Built-in fields that map directly onto Entry attributes. "totp" is handled
# specially because it requires a client call.
_BUILTIN_FIELDS = {
    "password": "password",
    "login": "login",
    "username": "login",
    "user": "login",
    "uuid": "uuid",
    "name": "name",
    "title": "name",
    "group": "group",
    "group_uuid": "group_uuid",
}


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "read",
        help="Print a single field from an entry as a bare value",
        description=(
            "Print one field of an entry as a bare value (no labels, no JSON) so it can be "
            "piped into other commands, e.g. kpxc-cli read account/API_KEY.\n"
            "Custom string attributes are matched without the 'KPH: ' prefix that KeePassXC "
            "uses internally, so 'API_KEY' finds a field stored as 'KPH: API_KEY'."
        ),
    )
    p.add_argument("item", help="Entry reference and field, e.g. profile_for_dev_account/API_KEY")
    p.add_argument("--uuid", default=None, help="Entry UUID (required when the reference matches multiple entries)")
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
    if "/" not in args.item:
        logger.error("Expected ENTRY/FIELD, e.g. profile_for_dev_account/API_KEY")
        return 1
    entry_ref, field = args.item.rsplit("/", 1)

    url = ensure_scheme(entry_ref)
    entries = client.get_logins(url)
    if not entries:
        logger.warning("No entries found for: %s", entry_ref)
        return 1

    if args.uuid is not None:
        entry = next((e for e in entries if e.uuid == args.uuid), None)
        if entry is None:
            logger.error("Entry %s not found for: %s", args.uuid, entry_ref)
            return 1
    elif len(entries) == 1:
        entry = entries[0]
    else:
        logger.error("Multiple entries found for %s — specify --uuid to disambiguate:", entry_ref)
        for e in entries:
            print(f"  {e.uuid}  {e.login}  ({e.name})")
        return 1

    value = _resolve_field(client, entry, field)
    if value is None:
        logger.error(
            "Field %r not found on entry %s. Available fields: %s",
            field,
            entry_ref,
            ", ".join(_available_fields(entry)),
        )
        return 1
    print(value)
    return 0


def _resolve_field(client: BrowserClient, entry, field: str) -> str | None:
    if field == "totp":
        return client.get_totp(entry.uuid)
    if field in _BUILTIN_FIELDS:
        return getattr(entry, _BUILTIN_FIELDS[field])
    target = _strip_kph(field)
    for sf in entry.string_fields:
        for stored_name, value in sf.items():
            if _strip_kph(stored_name) == target:
                return value
    return None


def _available_fields(entry) -> list[str]:
    fields = set(_BUILTIN_FIELDS) | {"totp"}
    for sf in entry.string_fields:
        for stored_name in sf:
            fields.add(_strip_kph(stored_name))
    return sorted(fields)