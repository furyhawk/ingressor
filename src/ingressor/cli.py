from __future__ import annotations

import subprocess
import sys


def main() -> None:
    raise SystemExit(subprocess.call(["reflex", "run", *sys.argv[1:]]))
