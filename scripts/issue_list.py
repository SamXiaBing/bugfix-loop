#!/usr/bin/env python3
"""主清单管理。不依赖任何缺陷系统，只管理一个 markdown 清单文件。

用法
  python issue_list.py init <日期> [--feed feed.json] [--lang zh|en]    建当天的清单
  python issue_list.py merge <清单.md> [--feed feed.json] [--lang zh|en]  合并新单并去重
  python issue_list.py status <清单.md> <KEY> <状态> [备注] [--lang zh|en]  改一条的状态
  python issue_list.py report <清单.md> [--lang zh|en]                   按状态统计

feed 是 JSON，可以来自适配器。格式是 {"issues": [{"key": "...", "title": "..."}]}。
没给 --feed 就从标准输入读，方便和适配器串起来。
"""

import argparse
import json
import re
import sys
from pathlib import Path

KEY_RE = re.compile(r"[A-Za-z]+-\d+")

STATUS_ORDER = {
    "zh": ["待分析", "信息不足", "无法定论", "确定结论", "已修复"],
    "en": ["pending", "not enough info", "undetermined", "confirmed", "fixed"],
}
DEFAULT_STATUS = {"zh": "待分析", "en": "pending"}
LIST_TITLE = {"zh": "Bug 清单", "en": "Bug list"}


def read_feed(path):
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    items = data if isinstance(data, list) else data.get("issues", [])
    return [(str(i.get("key", "")).strip(), str(i.get("title", "")).strip()) for i in items]


def parse_list(text, default_status):
    bugs, order = {}, []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        parts = [p.strip() for p in line[2:].split("|")]
        key = parts[0] if parts else ""
        if not KEY_RE.fullmatch(key or ""):
            continue
        bugs[key] = {
            "key": key,
            "title": parts[1] if len(parts) > 1 else "",
            "status": parts[2] if len(parts) > 2 else default_status,
            "note": parts[3] if len(parts) > 3 else "",
        }
        order.append(key)
    return bugs, order


def render(bugs, order, heading, status_order):
    lines = [f"# {heading}", ""]
    groups = {}
    for key in order:
        b = bugs[key]
        groups.setdefault(b["status"], []).append(b)

    def dump(status, items):
        lines.append(f"## {status} ({len(items)})")
        for b in items:
            note = f" | {b['note']}" if b.get("note") else ""
            lines.append(f"- {b['key']} | {b['title']} | {b['status']}{note}")
        lines.append("")

    seen = set()
    for status in status_order:
        if status in groups:
            dump(status, groups[status])
            seen.add(status)
    for status, items in groups.items():
        if status not in seen:
            dump(status, items)
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description="主清单管理")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("date")
    p_init.add_argument("--feed")
    p_init.add_argument("--lang", choices=["zh", "en"], default="zh")

    p_merge = sub.add_parser("merge")
    p_merge.add_argument("list")
    p_merge.add_argument("--feed")
    p_merge.add_argument("--lang", choices=["zh", "en"], default="zh")

    p_status = sub.add_parser("status")
    p_status.add_argument("list")
    p_status.add_argument("key")
    p_status.add_argument("state")
    p_status.add_argument("note", nargs="?")
    p_status.add_argument("--lang", choices=["zh", "en"], default="zh")

    p_report = sub.add_parser("report")
    p_report.add_argument("list")
    p_report.add_argument("--lang", choices=["zh", "en"], default="zh")

    args = ap.parse_args()
    lang = args.lang
    status_order = STATUS_ORDER[lang]
    default_status = DEFAULT_STATUS[lang]

    if args.cmd == "init":
        path = Path(f"bugs_{args.date}.md")
        bugs, order = {}, []
        for key, title in read_feed(args.feed):
            if key and key not in bugs:
                bugs[key] = {"key": key, "title": title, "status": default_status, "note": ""}
                order.append(key)
        path.write_text(render(bugs, order, f"{LIST_TITLE[lang]} {args.date}", status_order), encoding="utf-8")
        print(f"写进 {path}，共 {len(order)} 条" if lang == "zh" else f"Wrote {path}, {len(order)} items")

    elif args.cmd == "merge":
        path = Path(args.list)
        bugs, order = parse_list(path.read_text(encoding="utf-8"), default_status)
        added = 0
        for key, title in read_feed(args.feed):
            if key and key not in bugs:
                bugs[key] = {"key": key, "title": title, "status": default_status, "note": ""}
                order.append(key)
                added += 1
        path.write_text(render(bugs, order, path.stem, status_order), encoding="utf-8")
        print(f"新增 {added} 条，共 {len(order)} 条" if lang == "zh" else f"Added {added}, {len(order)} total")

    elif args.cmd == "status":
        path = Path(args.list)
        bugs, order = parse_list(path.read_text(encoding="utf-8"), default_status)
        if args.key not in bugs:
            print(f"清单里没有 {args.key}" if lang == "zh" else f"{args.key} not in the list", file=sys.stderr)
            sys.exit(1)
        bugs[args.key]["status"] = args.state
        if args.note:
            bugs[args.key]["note"] = args.note
        path.write_text(render(bugs, order, path.stem, status_order), encoding="utf-8")
        print(f"{args.key} 改成 {args.state}" if lang == "zh" else f"{args.key} changed to {args.state}")

    elif args.cmd == "report":
        bugs, _ = parse_list(Path(args.list).read_text(encoding="utf-8"), default_status)
        counts = {}
        for b in bugs.values():
            counts[b["status"]] = counts.get(b["status"], 0) + 1
        for status in status_order:
            if status in counts:
                print(f"{status} {counts[status]}")
        print(f"总计 {len(bugs)}" if lang == "zh" else f"Total {len(bugs)}")


if __name__ == "__main__":
    main()
