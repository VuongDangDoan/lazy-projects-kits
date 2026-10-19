#!/usr/bin/env python3
"""lazy_init.py — helper of lazy-init.sh: .lazy/project.json → project.config.json + .lazy/.init.env."""
import json, re, shlex, unicodedata
from pathlib import Path

p = json.loads(Path(".lazy/project.json").read_text(encoding="utf-8"))

def slugify(s):
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

name = slugify(p["name"])
if not re.fullmatch(r"[a-z][a-z0-9-]{1,40}", name):
    raise SystemExit(f"lazy-init: tên dự án không hợp lệ: {p['name']!r}")
stack = (p.get("stack") or "").strip()
low = stack.lower()

def check_cmd():
    if re.search(r"\bgo\b|golang", low): return "go vet ./..."
    if re.search(r"next|nest|react|typescript|\bts\b|node|vue|angular", low):
        return "vue-tsc --noEmit" if "vue" in low else "npx --no-install tsc --noEmit -p tsconfig.json"
    if re.search(r"django|fastapi|flask|python", low): return "python -m mypy . --ignore-missing-imports"
    if re.search(r"laravel|php", low): return "./vendor/bin/phpstan analyse src --level=5"
    if "flutter" in low: return "flutter analyze"
    if re.search(r"spring|kotlin", low): return "./gradlew compileKotlin"
    return ""

used, modules = set(), []
for m in p.get("modules") or ["Core"]:
    slug = slugify(m) or "core"
    prefix = "BR-" + re.sub(r"[^A-Z]", "", slug.upper())[:3].ljust(3, "X")
    base, i = prefix, 2
    while prefix in used:
        prefix = f"{base[:-1]}{i}"; i += 1
    used.add(prefix)
    modules.append({"slug": slug, "name": m.strip(), "br_prefix": prefix})

short = (p.get("shortCode") or re.sub(r"[^A-Z]", "", name.upper())[:4] or "PRJ").upper()[:6]
cfg = {
    "$comment": "Single source of truth for project facts. Written by Lazy Bot factory (lazy-init.sh) from the approved team card.",
    "initialized": True,
    "factory_mode": True,
    "project": {"name": p.get("displayName") or p["name"], "short_code": short, "language": p.get("language") or "vi"},
    "repos": {
        "be": {"name": name, "stack": stack, "check_cmd": check_cmd()},
        "fe": {"name": "", "stack": "", "check_cmd": ""},
        "mobile": {"name": "", "stack": "", "check_cmd": ""},
    },
    "modules": modules,
}
Path("project.config.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

db = next((v for k, v in [("postgres", "PostgreSQL"), ("mysql", "MySQL"), ("sqlite", "SQLite"), ("mongo", "MongoDB")] if k in low), "—")
stacks = []
if "next" in low: stacks += ["be/nextjs-ts-pg.md:be-patterns.md", "fe/nextjs-shadcn.md:fe-patterns.md"]
elif "nest" in low: stacks += ["be/nestjs-ts-pg.md:be-patterns.md"]
if re.search(r"react native|expo", low): stacks += ["mobile/react-native-expo.md:mobile-patterns.md"]
desc = (p.get("description") or "").replace("\n", " ")[:120]
out = {"NAME": name, "DATABASE": db, "DOMAIN": desc or "—", "STACKS": " ".join(stacks)}
Path(".lazy/.init.env").write_text("".join(f"{k}={shlex.quote(v)}\n" for k, v in out.items()), encoding="utf-8")
