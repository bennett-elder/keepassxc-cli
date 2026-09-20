#!/usr/bin/env python
"""PyInstaller bootstrap for CI release builds.

Mirrors the installed console script entry point. Passing __main__.py to
PyInstaller directly runs it as a top-level script, breaking its relative
imports (`from .commands import ...`). Importing the package as a module
first keeps the parent package intact so PyInstaller bundles it correctly.

Build (requires the `build` extra and `--hidden-import _cffi_backend`,
which pynacl's cffi dependency needs at runtime):
    pyinstaller --onefile --hidden-import _cffi_backend \
        --paths . \
        --name kpxc-cli packaging/pyinstaller-entry.py

Note: `--paths .` is required with modern setuptools editable installs, which
inject a meta-path finder rather than a sys.path entry — static analysis
can't see the project root without it.
"""
from __future__ import annotations

from keepassxc_cli.__main__ import main

if __name__ == "__main__":
    main()