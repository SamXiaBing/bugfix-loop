#!/usr/bin/env python3
"""往经验库追加一条偏差记录。字段齐了才写，格式不会乱。

写入方式是先写临时文件再原子替换，写一半崩溃不会截断损坏 lessons.md。

用法
  python lesson_append.py --lessons lessons.md --module 订单页 --type "代码逻辑看成配置问题" \
      --example BUG-101 --lesson "先查布局参数再查代码逻辑" --category 显示 --path "先查锚点参数" [--lang zh|en]
"""

import argparse
import os
import sys
import tempfile
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


def atomic_append(path, content):
    """读全文，追加内容，临时文件写完原子替换回去。

    os.replace 在同一文件系统上是原子的，替换时刻之前读到的是旧全文，
    替换之后读到的是新全文，不存在写一半的状态。
    """
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(old + content)
        os.replace(tmp_name, path)
    except BaseException:
        # 替换失败就把临时文件清掉，原文件不动
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


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
        atomic_append(path, HEADER[args.lang])
    atomic_append(path, row + "\n")
    print("已追加一条" if args.lang == "zh" else "appended one")


if __name__ == "__main__":
    main()
