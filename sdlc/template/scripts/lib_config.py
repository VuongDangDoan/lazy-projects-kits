"""lib_config.py — shared loader for project.config.json.

Every validator imports this instead of hard-coding module names, BR prefixes,
or repo names. When the config is missing or not yet initialized, callers get
empty collections and are expected to SKIP the corresponding checks (the
workspace is pre-/onboard — nothing to validate against yet).

Config shape (project.config.json at workspace root):
{
  "initialized": true,
  "project": {"name": "...", "short_code": "...", "language": "vi"},
  "repos":   {"be": {"name": "...", "stack": "...", "check_cmd": "..."}, ...},
  "modules": [{"slug": "employee", "name": "Employee", "br_prefix": "BR-EMP"}, ...]
}
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "project.config.json"


def load() -> dict | None:
    """Return the parsed config, or None when missing/unreadable."""
    if not CONFIG_PATH.exists():
        return None
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def is_initialized() -> bool:
    cfg = load()
    return bool(cfg and cfg.get("initialized"))


def module_slugs() -> set[str]:
    """Known module slugs. Empty set → skip module-name checks."""
    cfg = load()
    if not cfg:
        return set()
    return {m.get("slug", "") for m in cfg.get("modules", []) if m.get("slug")}


def br_prefix_map() -> dict[str, str]:
    """BR prefix → '<slug>-domain.md'. Empty dict → resolve BRs by full scan."""
    cfg = load()
    if not cfg:
        return {}
    out: dict[str, str] = {}
    for m in cfg.get("modules", []):
        if m.get("br_prefix") and m.get("slug"):
            out[m["br_prefix"]] = f"{m['slug']}-domain.md"
    return out


def repo_names() -> list[str]:
    """Configured source-repo directory names (order: be, fe, mobile)."""
    cfg = load()
    if not cfg:
        return []
    return [r.get("name", "") for r in cfg.get("repos", {}).values() if r.get("name")]


def short_code() -> str:
    cfg = load()
    return (cfg or {}).get("project", {}).get("short_code", "")
