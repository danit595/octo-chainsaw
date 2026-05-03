"""Entry point shim. The real app lives in src/octoautoclicker.

Run with `python autoclicker.py` or `python -m octoautoclicker` once the
package is on the import path.
"""

from __future__ import annotations

import os
import sys


def _ensure_path() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "src")
    if os.path.isdir(src) and src not in sys.path:
        sys.path.insert(0, src)


def main() -> int:
    _ensure_path()
    from octoautoclicker.app import main as app_main

    return app_main()


if __name__ == "__main__":
    sys.exit(main())
