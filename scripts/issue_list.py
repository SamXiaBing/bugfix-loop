#!/usr/bin/env python3
"""主清单管理。不依赖任何缺陷系统，只管理一个 markdown 清单文件。

用法
  python issue_list.py init <日期> [--feed feed.json] [--key-re 正则] [--lang zh|en]    建当天的清单
  python issue_list.py merge <清单.md> [--feed feed.json] [--key-re 正则] [--lang zh|en]  合并新单并去重
  python issue_list.py status <清单.md> <KEY> <状态> [备注] [--key-re 正则] [--lang zh|en]  改一条的状态
  python issue_list.py report <清单.md> [--key-re 正则] [--lang zh|en]                   按状态统计

feed 是 JSON，可以来自适配器。格式是 {"issues": [{"key": "...", "title": "..."}]}。
没给 --feed 就从标准输入读，方便和适配器串起来。

bug 编号默认认三种，Jira 的 ABC-123、GitHub 的 #123、GitLab 的纯数字。
系统有别的编号格式就用 --key-re 传一个正则，比如 --key-re "[A-Z]+_\\d+"。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 默认认三种编号，Jira / GitHub / GitLab
KEY_RE = re.compile(r"([A-Za-z]+-\d+|#\d+|\d+)")

STATUS_ORDER = {
    "zh": ["待分析", "信息不足", "无法定论", "确定结论", "已修复"],
    "en": ["pending", "not enough info", "undetermined", "confirmed", "fixed"],
}
DEFAULT_STATUS = {"zh": "待分析", "en": "pending"}
LIST_TITLE = {"zh": "Bug 清单", "en": "Bug list"}


def compile_key_re(pattern):
    try:
        return re.compile(pattern)
    except re.error as e:
        print(f"无效的正则 {pattern}，{e}", file=sys.stderr)
        sys.exit(2)


def read_feed(path):
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    items = data if isinstance(data, list) else data.get("issues", [])
    return [(str(i.get("key", "")).strip(), str(i.get("title", "")).strip()) for i in items]


def parse_list(text, default_status, key_re):
    bugs, order = {}, []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        parts = [p.strip() for p in line[2:].split("|")]
        key = parts[0] if parts else ""
        if not key_re.fullmatch(key or ""):
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
    ap.add_argument("--key-re", dest="key_re", default=None,
                    help="bug 编号的自定义正则，默认认 Jira ABC-123 / GitHub #123 / GitLab 纯数字")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("date")
    p_init.add_argument("--feed")
    p_init.add_argument("--key-re", dest="key_re_sub", default=None)
    p_init.add_argument("--lang", choices=["zh", "en"], default="zh")

    p_merge = sub.add_parser("merge")
    p_merge.add_argument("list")
    p_merge.add_argument("--feed")
    p_merge.add_argument("--key-re", dest="key_re_sub", default=None)
    p_merge.add_argument("--lang", choices=["zh", "en"], default="zh")

    p_status = sub.add_parser("status")
    p_status.add_argument("list")
    p_status.add_argument("key")
    p_status.add_argument("state")
    p_status.add_argument("note", nargs="?")
    p_status.add_argument("--key-re", dest="key_re_sub", default=None)
    p_status.add_argument("--lang", choices=["zh", "en"], default="zh")

    p_report = sub.add_parser("report")
    p_report.add_argument("list")
    p_report.add_argument("--key-re", dest="key_re_sub", default=None)
    p_report.add_argument("--lang", choices=["zh", "en"], default="zh")

    args = ap.parse_args()
    lang = args.lang
    status_order = STATUS_ORDER[lang]
    default_status = DEFAULT_STATUS[lang]
    # --key-re 放主命令或子命令后都行
    pattern = args.key_re_sub or args.key_re
    key_re = compile_key_re(pattern) if pattern else KEY_RE

    if args.cmd == "init":
        path = Path(f"bugs_{args.date}.md")
        bugs, order = {}, []
        feed = read_feed(args.feed)  # 只读一次，stdin 只能读一遍
        for key, title in feed:
            if key and key_re.fullmatch(key) and key not in bugs:
                bugs[key] = {"key": key, "title": title, "status": default_status, "note": ""}
                order.append(key)
        dropped = sum(1 for k, _ in feed if k and not key_re.fullmatch(k))
        if dropped:
            print(f"提示，{dropped} 条编号不符合格式被跳过，编号要匹配 {key_re.pattern}，格式不对用 --key-re 换"
                  if lang == "zh" else
                  f"Note, {dropped} keys skipped for not matching {key_re.pattern}, use --key-re for other formats")
        path.write_text(render(bugs, order, f"{LIST_TITLE[lang]} {args.date}", status_order), encoding="utf-8")
        print(f"写进 {path}，共 {len(order)} 条" if lang == "zh" else f"Wrote {path}, {len(order)} items")

    elif args.cmd == "merge":
        path = Path(args.list)
        bugs, order = parse_list(path.read_text(encoding="utf-8"), default_status, key_re)
        added = 0
        for key, title in read_feed(args.feed):
            if key and key_re.fullmatch(key) and key not in bugs:
                bugs[key] = {"key": key, "title": title, "status": default_status, "note": ""}
                order.append(key)
                added += 1
        path.write_text(render(bugs, order, path.stem, status_order), encoding="utf-8")
        print(f"新增 {added} 条，共 {len(order)} 条" if lang == "zh" else f"Added {added}, {len(order)} total")

    elif args.cmd == "status":
        path = Path(args.list)
        bugs, order = parse_list(path.read_text(encoding="utf-8"), default_status, key_re)
        if args.key not in bugs:
            print(f"清单里没有 {args.key}" if lang == "zh" else f"{args.key} not in the list", file=sys.stderr)
            sys.exit(1)
        bugs[args.key]["status"] = args.state
        if args.note:
            bugs[args.key]["note"] = args.note
        path.write_text(render(bugs, order, path.stem, status_order), encoding="utf-8")
        print(f"{args.key} 改成 {args.state}" if lang == "zh" else f"{args.key} changed to {args.state}")

    elif args.cmd == "report":
        bugs, _ = parse_list(Path(args.list).read_text(encoding="utf-8"), default_status, key_re)
        counts = {}
        for b in bugs.values():
            counts[b["status"]] = counts.get(b["status"], 0) + 1
        for status in status_order:
            if status in counts:
                print(f"{status} {counts[status]}")
        print(f"总计 {len(bugs)}" if lang == "zh" else f"Total {len(bugs)}")


if __name__ == "__main__":
    main()
