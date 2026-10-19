#!/usr/bin/env python3
"""kit_check.py <stage>|check — the gate of this kit (scripts/lazy-gate.sh calls it).

Lazy Bot factory runs the gate after each stage, before asking the owner: exit 0 = the stage's
files are there and complete; anything else = the stage is redone with this output. It only
reads files (no network, no writes). `check` validates every item of the repo (test command).

The rules of the kit are in SPEC below; the rest is the same in every lean kit.
"""
import os
import re
import sys

# ── Rules of the research kit ────────────────────────────────────────────────────────────────
AREA = "research"
STAGES = {  # stage → files that must be complete after it
    "scope": ["brief.md"],
    "research": ["brief.md", "sources.md"],
    "report": ["brief.md", "sources.md", "report.md"],
}
SECTIONS = {  # file → required "## " sections (Vietnamese name, English name), each with content
    "brief.md": [("Câu hỏi", "Questions"), ("Phạm vi", "Scope"), ("Tiêu chí", "Criteria"),
                 ("Nguồn dự kiến", "Planned sources"), ("Đầu ra", "Output")],
    "sources.md": [("Nguồn", "Sources"), ("Khoảng trống", "Gaps")],
    "report.md": [("Tóm tắt", "Summary"), ("Phân tích", "Analysis"), ("Khuyến nghị", "Recommendation"),
                  ("Hạn chế", "Limitations"), ("Nguồn", "Sources")],
}
MIN_SOURCES = 3
ENTRY = re.compile(r"^\s*\[(\d+)\]\s+(.*)$")
URL = re.compile(r"https?://\S+")
CITE = re.compile(r"\[(\d+)\]")


def sources_of(item):
    """[n] → has a link, from the item's sources.md."""
    out = {}
    for line in strip_comments(read(os.path.join(item, "sources.md"))).splitlines():
        m = ENTRY.match(line)
        if m:
            n = int(m.group(1))
            out[n] = out.get(n, False) or bool(URL.search(m.group(2)))
    return out


def check_sources(item, text, errs):
    seen, dup = {}, []
    for line in strip_comments(text).splitlines():
        m = ENTRY.match(line)
        if m:
            n = int(m.group(1))
            if n in seen:
                dup.append(n)
            seen[n] = seen.get(n, False) or bool(URL.search(m.group(2)))
    if dup:
        errs.append(f"{item}/sources.md: số nguồn trùng {sorted(set(dup))} — mỗi nguồn một số")
    linked = sum(1 for v in seen.values() if v)
    if linked < MIN_SOURCES:
        errs.append(f"{item}/sources.md cần ≥ {MIN_SOURCES} nguồn có link dạng \"[n] Tiêu đề — … — https://…\" (có {linked})")
    return f"{linked} nguồn có link"


def check_report(item, text, errs):
    cited = {int(n) for n in CITE.findall(strip_comments(text))}
    if not cited:
        errs.append(f"{item}/report.md chưa trích nguồn nào — mỗi số liệu / khẳng định cần [n] của sources.md")
        return ""
    known = sources_of(item)
    missing = sorted(n for n in cited if n not in known)
    if missing:
        errs.append(f"{item}/report.md trích {', '.join(f'[{n}]' for n in missing)} nhưng sources.md không có — "
                    "thêm nguồn đó hoặc bỏ trích dẫn")
    return f"trích {len(cited)} nguồn"


EXTRA = {"sources.md": check_sources, "report.md": check_report}
# ── end of the kit's rules ───────────────────────────────────────────────────────────────────

COMMENT = re.compile(r"<!--.*?-->", re.S)
FILLER = re.compile(r"^[\s\-*|:.…_>#]*$")


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def strip_comments(text):
    return COMMENT.sub("", text)


def sections(text):
    """'## name' (lower case) → content lines without comments and filler."""
    out, cur = {}, None
    for line in strip_comments(text).splitlines():
        if line.startswith("## "):
            cur = line[3:].strip().lower()
            out.setdefault(cur, [])
        elif line.startswith("# "):
            cur = None
        elif cur is not None and not FILLER.match(line):
            out[cur].append(line)
    return out


def check_file(item, name, errs):
    path = os.path.join(item, name)
    text = read(path)
    if not text.strip():
        errs.append(f"thiếu {path} — chép từ templates/{name} rồi điền")
        return
    got = sections(text)
    for names in SECTIONS.get(name, []):
        heads = [h for h in got if any(h.startswith(n.lower()) for n in names)]
        if not heads:
            errs.append(f"{path} thiếu mục \"## {names[0]}\"")
        elif not any(got[h] for h in heads):
            errs.append(f"{path}: mục \"## {names[0]}\" còn trống (mới có chú thích của mẫu)")
    note = EXTRA[name](item, text, errs) if name in EXTRA else ""
    return note


def current_item():
    text = read(os.path.join("context", "active.md"))
    m = re.search(r"^\s*(?:Thư mục|Folder)\s*:\s*`?(" + AREA + r"/[a-z0-9][a-z0-9-]*)`?", text, re.M)
    if m:
        if not os.path.isdir(m.group(1)):
            return None, f"context/active.md trỏ tới {m.group(1)} nhưng thư mục không có"
        return m.group(1), None
    items = all_items()
    if len(items) == 1:
        return items[0], None
    return None, ("context/active.md chưa ghi thư mục việc (dòng \"Thư mục: " + AREA + "/<slug>\") — "
                  "chạy scripts/new-item.sh <slug>")


def all_items():
    if not os.path.isdir(AREA):
        return []
    return sorted(os.path.join(AREA, d) for d in os.listdir(AREA)
                  if os.path.isdir(os.path.join(AREA, d)) and not d.startswith((".", "_")))


def run(item, files, errs):
    notes = []
    for name in files:
        before = len(errs)
        note = check_file(item, name, errs)
        if len(errs) == before:
            notes.append(name + (f" ({note})" if note else ""))
    return notes


def main(argv):
    stage = argv[1] if len(argv) > 1 else ""
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    errs = []
    if stage == "check":
        for item in all_items():
            present = [n for n in SECTIONS if read(os.path.join(item, n)).strip()]
            notes = run(item, present, errs)
            if notes:
                print(f"✓ {item}: {', '.join(notes)}")
    elif stage in STAGES:
        item, err = current_item()
        if err:
            errs.append(err)
        else:
            notes = run(item, STAGES[stage], errs)
            if not errs:
                print(f"✓ {stage} — {item}: {', '.join(notes)}")
    else:
        print(f"lazy-gate: giai đoạn lạ '{stage}' ({'|'.join(STAGES)}|check)", file=sys.stderr)
        return 2
    for e in errs:
        print("✗ " + e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
