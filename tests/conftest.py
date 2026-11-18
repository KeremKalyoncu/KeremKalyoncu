"""Shared pytest fixtures for the KeremKalyoncu E2E & self-validation test suites."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Callable, Iterator

import pytest

from tests.cdp_harness import CDPHarness, LocalSiteServer

REPO_ROOT = Path(__file__).resolve().parents[1]
ATLAS_PLATES: tuple[str, ...] = (
    "atlas-hero.svg",
    "atlas-systems.svg",
    "atlas-trajectory.svg",
)
VIEWPORTS: tuple[tuple[int, int], ...] = (
    (1440, 900),
    (1280, 800),
    (768, 1024),
    (390, 844),
)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def readme_path(repo_root: Path) -> Path:
    return repo_root / "README.md"


@pytest.fixture(scope="session")
def index_html_path(repo_root: Path) -> Path:
    return repo_root / "index.html"


@pytest.fixture(scope="session")
def atlas_svg_paths(repo_root: Path) -> list[Path]:
    return [repo_root / "assets" / name for name in ATLAS_PLATES]


@pytest.fixture(scope="session")
def live_server(repo_root: Path) -> Iterator[LocalSiteServer]:
    with LocalSiteServer(repo_root) as srv:
        yield srv


@pytest.fixture(scope="session")
def cdp_harness() -> Iterator[CDPHarness]:
    harness = CDPHarness().open()
    try:
        yield harness
    finally:
        harness.close()


@pytest.fixture(scope="session")
def screenshot_dir(repo_root: Path) -> Path:
    env_dir = os.environ.get("E2E_SCREENSHOT_DIR", "").strip()
    out = Path(env_dir) if env_dir else (repo_root / "tests" / "artifacts" / "screenshots")
    out.mkdir(parents=True, exist_ok=True)
    return out


@pytest.fixture
def tmp_repo_factory(tmp_path: Path, repo_root: Path) -> Callable[..., Path]:
    """Create an isolated copy of the repository build inputs under ``tmp_path``."""

    def _make(name: str = "repo_copy", clean_outputs: bool = True) -> Path:
        dest = tmp_path / name
        dest.mkdir(parents=True, exist_ok=True)
        src_dir = repo_root / "source"
        if src_dir.exists():
            shutil.copytree(
                src_dir,
                dest / "source",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        for sub in ("assets", "output"):
            s = repo_root / sub
            if s.exists():
                shutil.copytree(s, dest / sub)
            else:
                (dest / sub).mkdir(exist_ok=True)
        for fname in ("README.md", "index.html"):
            f = repo_root / fname
            if f.exists():
                shutil.copy2(f, dest / fname)
        if clean_outputs:
            (dest / "index.html").unlink(missing_ok=True)
            assets_dir = dest / "assets"
            if assets_dir.exists():
                for svg in assets_dir.glob("atlas-*.svg"):
                    svg.unlink(missing_ok=True)
                for plate in ATLAS_PLATES:
                    (assets_dir / plate).unlink(missing_ok=True)
        return dest

    return _make
