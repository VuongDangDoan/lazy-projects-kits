#!/usr/bin/env bash
# tests/lean-kits.sh — checks the research and content kits end to end in temporary copies:
# init from .lazy/project.json, new-item (incl. a slug taken on another factory's branch), and
# every gate failing on missing / unfilled files then passing once filled. Needs bash, git, python3.
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
fails=0
ok()   { echo "  ✓ $*"; }
bad()  { echo "  ✗ $*"; fails=$((fails + 1)); }
pass() { local d="$1"; shift; if out=$("$@" 2>&1); then ok "$d"; else bad "$d — $out"; fi; }
fail() { local d="$1" want="$2"; shift 2; if out=$("$@" 2>&1); then bad "$d — exit 0"; elif [[ "$out" != *"$want"* ]]; then bad "$d — $out"; else ok "$d"; fi; }
g() { git -c user.email=t@t -c user.name=t "$@"; }

copy() { # copy <kit> <dir> — the project repo the factory would create
    mkdir -p "$2/.lazy" && cp -R "$here/$1/template/." "$2/" && cp "$here/$1/kit.yaml" "$2/.lazy/kit.yaml"
    printf '{"name":"x","displayName":"Dự án X","description":"Mục tiêu X","language":"vi","kit":"%s","kitVersion":"0.1.0"}\n' "$1" > "$2/.lazy/project.json"
    (cd "$2" && git init -q -b main && g add -A && g commit -qm init)
}

echo "research"
r="$tmp/research"; copy research "$r"; cd "$r"
pass "init" scripts/lazy-init.sh
grep -q "Dự án X — dự án nghiên cứu (bộ research@0.1.0)" CLAUDE.md && ok "CLAUDE.md filled" || bad "CLAUDE.md not filled"
fail "scope without item" "chưa ghi thư mục việc" scripts/lazy-gate.sh scope
d=$(scripts/new-item.sh pg); [[ "$d" == research/pg ]] && ok "new-item" || bad "new-item: $d"
fail "brief unfilled" 'mục "## Câu hỏi" còn trống' scripts/lazy-gate.sh scope
for s in "Câu hỏi" "Phạm vi" "Tiêu chí" "Nguồn dự kiến" "Đầu ra"; do printf '## %s\nx y\n' "$s"; done > "$d/brief.md"
pass "scope" scripts/lazy-gate.sh scope
fail "no sources" "thiếu research/pg/sources.md" scripts/lazy-gate.sh research
printf '## Nguồn\n[1] A — https://a.example\n[2] B — no link\n## Khoảng trống\nKhông có.\n' > "$d/sources.md"
fail "too few sources" "cần ≥ 3 nguồn có link" scripts/lazy-gate.sh research
printf '[3] C — https://c.example\n[4] D — https://d.example\n' >> "$d/sources.md"
pass "research" scripts/lazy-gate.sh research
for s in "Tóm tắt" "Phân tích" "Khuyến nghị" "Hạn chế" "Nguồn"; do printf '## %s\nChọn A [1] [9]\n' "$s"; done > "$d/report.md"
fail "dangling citation" "trích [9] nhưng sources.md không có" scripts/lazy-gate.sh report
sed -i.bak 's/\[9\]/[3]/' "$d/report.md" && rm -f "$d/report.md.bak"
pass "report" scripts/lazy-gate.sh report
pass "check" scripts/lazy-gate.sh check
g add -A && g commit -qm item && git clone -q --bare . "$tmp/r.git" && git remote add origin "$tmp/r.git"
git checkout -qb factory/may-b/T-1 && scripts/new-item.sh hosting >/dev/null && g add -A && g commit -qm b && git push -q origin factory/may-b/T-1
git clone -q "$tmp/r.git" "$tmp/r2" && cd "$tmp/r2" && git fetch -q origin '+refs/heads/factory/*:refs/remotes/origin/factory/*'
d=$(scripts/new-item.sh hosting); [[ "$d" == research/hosting-2 ]] && ok "slug taken on another branch ⇒ -2" || bad "slug on other branch: $d"

echo "content"
c="$tmp/content"; copy content "$c"; cd "$c"
pass "init" scripts/lazy-init.sh
grep -q "Blog\|Dự án X" style.md && ok "style.md filled" || bad "style.md not filled"
d=$(scripts/new-item.sh blog)
fail "brief unfilled" 'mục "## Độc giả" còn trống' scripts/lazy-gate.sh brief
for s in "Độc giả" "Mục tiêu" "Kênh" "Giọng văn" "Thông điệp chính" "Dàn ý" "Nguồn / dữ kiện"; do printf '## %s\nx y\n' "$s"; done > "$d/brief.md"
printf '## Độ dài\nkhoảng 500 từ\n' >> "$d/brief.md"
pass "brief" scripts/lazy-gate.sh brief
{ echo "# Tiêu đề"; for _ in $(seq 100); do printf 'chữ '; done; } > "$d/draft.md"
fail "draft too short" "cần ≥ 300" scripts/lazy-gate.sh draft
{ echo "# Tiêu đề"; for _ in $(seq 400); do printf 'chữ '; done; } > "$d/draft.md"
pass "draft" scripts/lazy-gate.sh draft
cp "$d/draft.md" "$d/final.md"; cp templates/review.md "$d/review.md"
fail "checklist open" "còn mục chưa đạt" scripts/lazy-gate.sh edit
python3 - "$d/review.md" <<'PY'
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read().replace("- [ ]", "- [x]")
s = s.replace("<!-- Các sửa chính và vì sao -->", "Cắt mở bài.").replace('<!-- Điều cần chủ quyết; không có thì ghi "Không có." -->', "Không có.")
open(p, "w", encoding="utf-8").write(s)
PY
pass "edit" scripts/lazy-gate.sh edit
pass "check" scripts/lazy-gate.sh check

echo
if (( fails > 0 )); then echo "FAIL ($fails)"; exit 1; fi
echo "PASS"
