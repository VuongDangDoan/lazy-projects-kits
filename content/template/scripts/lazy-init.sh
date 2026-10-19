#!/usr/bin/env bash
# lazy-init.sh — non-interactive onboarding for Lazy Bot factory mode. The factory copies this
# kit's template into a new project repo, writes .lazy/project.json (values the owner approved on
# the "Lập team" card) and runs this script from the repo root: it fills the {{…}} values of
# CLAUDE.md, README.md and style.md. Runs without credentials and without network; exit ≠ 0 = the factory
# aborts the project creation and cleans up.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
[[ -f .lazy/project.json ]] || { echo "lazy-init: thiếu .lazy/project.json" >&2; exit 1; }
python3 -B - <<'PY'
import json
p = json.load(open(".lazy/project.json", encoding="utf-8"))
lang = p.get("language") or "vi"
values = {
    "{{NAME}}": p["name"],
    "{{DISPLAY_NAME}}": p.get("displayName") or p["name"],
    "{{DESCRIPTION}}": " ".join((p.get("description") or "").split()).replace("{{", "{ {"),
    "{{LANGUAGE}}": {"vi": "tiếng Việt", "en": "English"}.get(lang, lang),
    "{{KIT_VERSION}}": p.get("kitVersion") or "",
}
for name in ("CLAUDE.md", "README.md", "style.md"):
    with open(name, encoding="utf-8") as f:
        s = f.read()
    for k, v in values.items():
        s = s.replace(k, v)
    with open(name, "w", encoding="utf-8") as f:
        f.write(s)
PY
if grep -l '{{' CLAUDE.md README.md style.md >/dev/null 2>&1; then
    echo "lazy-init: còn placeholder {{…}} trong CLAUDE.md/README.md/style.md" >&2; exit 1
fi
echo "lazy-init: OK"
