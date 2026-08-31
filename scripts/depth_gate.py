#!/usr/bin/env python3
"""打点表判定。读当日报告里的检查动作表，算完成率，报工序。

报告里的检查动作表长这样

| 动作 | 结果 |
|------|------|
| 读描述和评论 | ✅ |
| 看附件 | N/A |

表格怎么找
  优先取「检查动作」标题后面的第一张表。
  没有标题时，用九项动作关键词匹配表格行，命中不足三项视为找不到表。

判定规则
  结果以否定词开头（未/没/不/待/暂）不算完成，哪怕后面带完成字样。
  中间态（部分完成、进行中、⏳）按保守归为未完成，单独提示人工确认。
  找不到表格时退出码 2，不算工序不足。

退出码
  0 工序达标
  1 工序不足
  2 解析失败（没有表格或表格认不出来）

用法
  python depth_gate.py <报告.md> [--lang zh|en]
"""

import argparse
import re
import sys
from pathlib import Path

DONE_RE = re.compile(r"[✅✔]")
SKIP_WORDS = {"n/a", "na", "not applicable", "不适用", "跳过"}
DONE_WORDS = {"done", "yes", "y", "完成", "已做", "已"}
NEGATIVE_PREFIXES = ("未", "没", "不", "待", "暂", "无法")
PARTIAL_MARKERS = ("部分", "进行中", "⏳", "半")
SKIP_HEADERS = {"动作", "结果", "action", "result"}

# 九项检查动作的关键词，用于无标题时锚定表格行
ACTION_KEYWORDS = [
    "读描述", "看附件", "拿运行证据", "运行证据",
    "搜代码", "读代码", "查最近提交", "最近提交",
    "确认归谁管", "归谁管", "复现", "确认数据",
]

# 「检查动作」标题的识别
SECTION_RE = re.compile(r"#{0,6}\s*.{0,8}检查动作.{0,8}")


def skip_marker(value):
    return value.strip().lower() in SKIP_WORDS


def done_marker(value):
    """完成判定。否定优先，中间态保守归未完成。"""
    v = value.strip()
    low = v.lower()
    if low in SKIP_WORDS:
        return None  # 不适用，不参与分母
    # 否定开头，明确未完成，优先级最高
    if v.startswith(NEGATIVE_PREFIXES):
        return False
    # 中间态，保守归未完成
    if any(m in v for m in PARTIAL_MARKERS):
        return False
    if low in DONE_WORDS:
        return True
    return bool(DONE_RE.search(v))


def parse_table_lines(lines):
    """从行列表里解析表格行，返回 [(action, result), ...]。"""
    rows = []
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            if rows:
                break  # 表格结束
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        action, result = cells[0], cells[1]
        if not action or action in SKIP_HEADERS or action.startswith("-"):
            continue
        rows.append((action, result))
    return rows


def looks_like_check_table(rows):
    """判断表格行里有多少行命中九项动作关键词。"""
    hit = 0
    for action, _ in rows:
        if any(kw in action for kw in ACTION_KEYWORDS):
            hit += 1
    return hit


def find_missing_actions(rows):
    """找出九项里没有出现在表格里的动作，返回缺失关键词列表。"""
    joined = " ".join(action for action, _ in rows)
    missing = []
    # 每项动作用一组同义关键词代表
    for label, kws in [
        ("读描述和评论", ["读描述"]),
        ("看附件", ["看附件"]),
        ("拿运行证据", ["拿运行证据", "运行证据"]),
        ("搜代码", ["搜代码"]),
        ("读代码", ["读代码"]),
        ("查最近提交", ["查最近提交", "最近提交"]),
        ("确认归谁管", ["确认归谁管", "归谁管"]),
        ("复现", ["复现"]),
        ("确认数据真的到了", ["确认数据"]),
    ]:
        if not any(kw in joined for kw in kws):
            missing.append(label)
    return missing


def extract_rows(text):
    """定位检查动作表。优先标题锚定，其次关键词匹配。返回 (rows, anchor)。"""
    lines = text.splitlines()

    # 1) 「检查动作」标题后面的第一张表。表要像检查表（至少 3 行命中九项动作
    #    关键词），不像就继续找下一个标题，防止叙述句里的「检查动作」误锚定
    for i, line in enumerate(lines):
        if SECTION_RE.search(line):
            rows = parse_table_lines(lines[i + 1:])
            if rows and looks_like_check_table(rows) >= 3:
                return rows, "section"

    # 2) 全文按表格块收集，选命中九项关键词最多的表
    all_rows = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            block = parse_table_lines(lines[i:])
            if block:
                all_rows.append(block)
            while i < len(lines) and lines[i].strip().startswith("|"):
                i += 1
        else:
            i += 1

    # 选命中关键词最多的表
    best, best_hit = None, 0
    for block in all_rows:
        hit = looks_like_check_table(block)
        if hit > best_hit:
            best, best_hit = block, hit

    if best and best_hit >= 3:
        return best, "keywords"
    return None, "none"


def main():
    ap = argparse.ArgumentParser(description="打点表判定")
    ap.add_argument("report")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    args = ap.parse_args()
    text = Path(args.report).read_text(encoding="utf-8")

    rows, anchor = extract_rows(text)
    zh = args.lang == "zh"

    if not rows:
        print(
            "报告里没有检查动作表，或表格认不出来。确认报告里有九项检查动作的表格。"
            if zh else
            "No check-action table found. Make sure the report has the nine-action table.",
            file=sys.stderr,
        )
        sys.exit(2)

    applicable = [r for r in rows if done_marker(r[1]) is not None]
    done = [r for r in applicable if done_marker(r[1]) is True]
    partial = [r for r in applicable if done_marker(r[1]) is False and any(m in r[1] for m in PARTIAL_MARKERS)]
    ratio = len(done) / len(applicable) if applicable else 1.0

    missing = find_missing_actions(rows)

    if zh:
        print(f"检查动作 {len(rows)} 项，适用 {len(applicable)} 项，完成 {len(done)} 项，完成率 {ratio:.0%}")
        print("工序达标，适用动作做了一半以上，等级看证据对不对得上" if ratio >= 0.5 else "工序不足，适用的检查动作至少做一半，再谈结论等级")
        if anchor == "keywords":
            print("提示：报告里没有「检查动作」标题，表格是按九项动作关键词定位的")
        if missing:
            print(f"警告：表格里缺这些动作项，可能漏项，{('、'.join(missing))}")
        if partial:
            names = "、".join(r[0] for r in partial)
            print(f"提示：这些动作是中间态，按未完成算，请人工确认，{names}")
    else:
        print(f"{len(rows)} check actions, {len(applicable)} applicable, {len(done)} done, {ratio:.0%}")
        print("Process floor met, the level depends on the evidence" if ratio >= 0.5 else "Process floor not met, run at least half of the applicable actions first")
        if anchor == "keywords":
            print("Note: no 'check actions' heading found, table located by action keywords")
        if missing:
            print(f"Warning: missing actions in the table, {', '.join(missing)}")
        if partial:
            names = ", ".join(r[0] for r in partial)
            print(f"Note: partial states counted as not done, please review, {names}")

    sys.exit(0 if ratio >= 0.5 else 1)


if __name__ == "__main__":
    main()
