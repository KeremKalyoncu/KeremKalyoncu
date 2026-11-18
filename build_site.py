"""Root launcher delegating to source/build_site.py without module shadowing."""

from __future__ import annotations

from pathlib import Path
import runpy


def main() -> None:
    target = Path(__file__).resolve().parent / "source" / "build_site.py"
    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
