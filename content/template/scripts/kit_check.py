#!/usr/bin/env python3
"""kit_check.py <stage>|check — the gate of this kit (content) (scripts/lazy-gate.sh calls it).

Lazy Bot factory runs the gate after each stage, before asking the owner: exit 0 = the stage's
files are there and complete; anything else = the stage is redone with this output. It only
reads files (no network, no writes). `check` validates every item of the repo (test command).

The rules of the kit are in SPEC below; the rest is the same in every lean kit.
"""
import os
import re
import sys

# ── Rules of the content kit ─────────────────────────────────────────────────────────────────
AREA = "content"
STAGES = {  # stage → files that must be complete after it
    "brief": ["brief.md"],
    "draft": ["brief.md", "draft.md"],
    "edit": ["brief.md", "draft.md", "final.md", "review.md"],
}
SECTIONS = {  # file → required "## " sections (Vietnamese name, English name), each with content
    "brief.md": [("Độc giả", "Audience"), ("Mục tiêu", "Goal"), ("Kênh", "Channel"), ("Giọng văn", "Voice"),
                 ("Thông điệp chính", "Key messages"), ("Dàn ý", "Outline"), ("Độ dài", "Length"),
                 ("Nguồn", "Sources")],
    "draft.md": [],
    "final.md": [],
    "review.md": [("Checklist", "Checklist"), ("Thay đổi so với bản nháp", "Changes from draft"),
                  ("Câu hỏi cho chủ", "Questions for the owner")],
}
MIN_WORDS = 150
WORD = re.compile(r"[^\W_]+")
TICK = re.compile(r"^\s*[-*]\s*\[(.)\]\s*(.*)$")


def target_words(item):
    """The first number of the brief's length section (\"khoảng 1.200 từ\" ⇒ 1200), 0 when none."""
    got = sections(read(os.path.join(item, "brief.md")))
    for head, lines in got.items():
        if head.startswith(("độ dài", "length")):
            m = re.search(r"\d[\d.,]*", " ".join(lines))
            if m:
                return int(re.sub(r"[.,]", "", m.group(0)))
    return 0


def check_text(item, text, errs, name):
    body = strip_comments(text)
    if not re.search(r"^# \S", body, re.M):
        errs.append(f"{item}/{name} cần tiêu đề ở dòng \"# …\"")
    words = len(WORD.findall(re.sub(r"https?://\S+", "", body)))
    target = target_words(item)
    low = max(MIN_WORDS, int(target * 0.6)) if target else MIN_WORDS
    if words < low:
        errs.append(f"{item}/{name} mới có {words} từ — cần ≥ {low}" + (f" (60% của {target} từ trong brief)" if target else ""))
    elif target and words > target * 1.6:
        errs.append(f"{item}/{name} có {words} từ — dài quá 160% của {target} từ trong brief; cắt bớt hoặc sửa Độ dài ở brief")
    return f"{words} từ"


def check_review(item, text, errs):
    ticks = [TICK.match(line) for line in strip_comments(text).splitlines()]
    ticks = [m for m in ticks if m]
    open_ = [m.group(2) for m in ticks if m.group(1) == " "]
    vague = [m.group(2) for m in ticks if m.group(1) == "~" and " — " not in m.group(2)]
    if open_:
        errs.append(f"{item}/review.md còn mục chưa đạt: " + "; ".join(open_) + " — sửa bản cuối rồi đánh [x], hoặc [~] kèm \" — lý do\"")
    if vague:
        errs.append(f"{item}/review.md: mục [~] cần \" — lý do\": " + "; ".join(vague))
    if not any(m.group(1).lower() == "x" for m in ticks):
        errs.append(f"{item}/review.md chưa đánh [x] mục nào trong Checklist")
    return f"{sum(1 for m in ticks if m.group(1).lower() == 'x')}/{len(ticks)} mục đạt"


EXTRA = {
    "draft.md": lambda item, text, errs: check_text(item, text, errs, "draft.md"),
    "final.md": lambda item, text, errs: check_text(item, text, errs, "final.md"),
    "review.md": check_review,
}
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
