#!/usr/bin/env python3
"""往经验库追加一条偏差记录。字段齐了才写，格式不会乱。

用法
  python lesson_append.py --lessons lessons.md --module 订单页 --type "代码逻辑看成配置问题" \
      --example BUG-101 --lesson "先查布局参数再查代码逻辑" --category 显示 --path "先查锚点参数" [--lang zh|en]
"""

import argparse
from pathlib import Path

FIELDS = ["module", "type", "example", "lesson", "category", "path"]
HEADER = {
    "zh": (
        "# 经验库\n\n## 偏差表\n\n"
        "| 业务模块 | 偏差类型 | 示例 | 教训 | 分类 | 验证路径 |\n"
        "|----------|----------|------|------|------|----------|\n"
    ),
    "en": (
        "# Lesson library\n\n## Deviation table\n\n"
        "| Business module | Deviation type | Example | Lesson | Category | Verification path |\n"
        "|-----------------|----------------|---------|--------|----------|-------------------|\n"
    ),
}


def main():
    ap = argparse.ArgumentParser(description="追加经验记录")
    ap.add_argument("--lessons", required=True)
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    for f in FIELDS:
        ap.add_argument(f"--{f}", required=True)
    args = ap.parse_args()

    values = {f: getattr(args, f).strip() for f in FIELDS}
    for f in FIELDS:
        if not values[f]:
            print(f"字段 {f} 是空的，不写" if args.lang == "zh" else f"field {f} is empty, not written", file=sys.stderr)
            sys.exit(1)

    path = Path(args.lessons)
    row = "| {module} | {type} | {example} | {lesson} | {category} | {path} |".format(**values)
    if path.exists() and row in path.read_text(encoding="utf-8"):
        print("这条已经记过了，跳过" if args.lang == "zh" else "already recorded, skipped")
        return
    if not path.exists():
        path.write_text(HEADER[args.lang], encoding="utf-8")
    with path.open("a", encoding="utf-8") as fh:
        fh.write(row + "\n")
    print("已追加一条" if args.lang == "zh" else "appended one")


if __name__ == "__main__":
    main()
