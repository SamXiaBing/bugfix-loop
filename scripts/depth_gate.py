#!/usr/bin/env python3
"""打点表判定。读当日报告里的检查动作表，算完成率，报工序。

报告里的检查动作表长这样

| 动作 | 结果 |
|------|------|
| 读描述和评论 | ✅ |
| 看附件 | N/A |

用法
  python depth_gate.py <报告.md> [--lang zh|en]
"""

import argparse
import re
import sys
from pathlib import Path

DONE_RE = re.compile(r"[✅✔完做已]")
SKIP_WORDS = {"n/a", "na", "not applicable", "不适用", "跳过"}
DONE_WORDS = {"done", "yes", "y", "完成", "已做"}
SKIP_HEADERS = {"动作", "结果", "action", "result"}


def skip_marker(value):
    return value.strip().lower() in SKIP_WORDS


def done_marker(value):
    v = value.strip()
    return bool(DONE_RE.search(v)) or v.lower() in DONE_WORDS


def main():
    ap = argparse.ArgumentParser(description="打点表判定")
    ap.add_argument("report")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    args = ap.parse_args()
    text = Path(args.report).read_text(encoding="utf-8")

    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        action, result = cells[0], cells[1]
        if not action or action in SKIP_HEADERS or action.startswith("-"):
            continue
        rows.append((action, result))

    if not rows:
        print(
            "报告里没有检查动作表" if args.lang == "zh" else "no check-action table in the report",
            file=sys.stderr,
        )
        sys.exit(1)

    applicable = [r for r in rows if not skip_marker(r[1])]
    done = [r for r in applicable if done_marker(r[1])]
    ratio = len(done) / len(applicable) if applicable else 1.0

    if args.lang == "zh":
        print(f"检查动作 {len(rows)} 项，适用 {len(applicable)} 项，完成 {len(done)} 项，完成率 {ratio:.0%}")
        print("工序达标，适用动作做了一半以上，等级看证据对不对得上" if ratio >= 0.5 else "工序不足，适用的检查动作至少做一半，再谈结论等级")
    else:
        print(f"{len(rows)} check actions, {len(applicable)} applicable, {len(done)} done, {ratio:.0%}")
        print("Process floor met, the level depends on the evidence" if ratio >= 0.5 else "Process floor not met, run at least half of the applicable actions first")


if __name__ == "__main__":
    main()
