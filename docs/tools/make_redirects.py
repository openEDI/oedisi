#!/usr/bin/env python
"""Write meta-refresh redirect stubs for the old Sphinx doc URLs.

The previous Sphinx site published flat pages like ``getting_started.html``. The
MyST site uses folder URLs (``/quickstart/`` etc.), so we drop small redirect
pages into the built site to keep old bookmarks and inbound links working.

Usage::

    python docs/tools/make_redirects.py docs/_build/html
"""

from __future__ import annotations

import sys
from pathlib import Path

# old path (relative to site root) -> new URL (relative to the old page)
REDIRECTS = {
    "getting_started.html": "./quickstart/",
    "examples.html": "./beginner/",
    "design.html": "./advanced/architecture/",
    "oedisi_cli.html": "./advanced/cli/",
    "multi_container.html": "./advanced/multicontainer/",
    "source/oedisi.html": "../advanced/api/",
    "source/modules.html": "../advanced/api/",
}

STUB = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Page moved</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
</head>
<body>
<p>This page has moved. <a href="{target}">Continue &rarr;</a></p>
</body>
</html>
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    out_root = Path(sys.argv[1])
    if not out_root.exists():
        print(f"output directory does not exist: {out_root}", file=sys.stderr)
        return 1
    for old_path, target in REDIRECTS.items():
        dest = out_root / old_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(STUB.format(target=target))
        print(f"[redirect] {old_path} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
