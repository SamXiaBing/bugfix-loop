#!/usr/bin/env python3
"""进仓库，拉最新，看最近几天改了什么。对应基本原则里的「先看是不是已经被人修了」。

用法
  python git_recent.py <仓库路径...> [--days 3] [--path 目标文件或目录]
"""

import argparse
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


def run(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def main():
    ap = argparse.ArgumentParser(description="查看仓库最近提交")
    ap.add_argument("repos", nargs="+")
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--path", default=None)
    args = ap.parse_args()

    since = (date.today() - timedelta(days=args.days)).isoformat()
    for repo in args.repos:
        root = Path(repo)
        if not (root / ".git").exists():
            print(f"[跳过] {repo} 不是 git 仓库")
            continue
        print(f"===== {repo} =====")
        code, out, err = run(["git", "pull", "--ff-only"], root)
        if code != 0:
            print(f"pull 失败，{err[:200]}")
        log = ["git", "log", "--oneline", f"--since={since}"]
        if args.path:
            log += ["--", args.path]
        code, out, _ = run(log, root)
        print(out if out else f"最近 {args.days} 天没有提交")
        print()


if __name__ == "__main__":
    main()
