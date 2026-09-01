#!/usr/bin/env python3
"""提交并推送，然后验证推送真的成功。只看 exit code 会骗人。

用法
  python git_push_verify.py <仓库> [--branch 分支] [--ref 引用] [--marker 词]... [--lang zh|en]

--ref 不填时默认 HEAD:{branch}。走审查流程的系统（比如 refs/for 风格）填
--ref "refs/for/{branch}"。

--marker 可重复追加平台专属的成功标记词，比如 GitHub 原生推送输出
"main -> main"，就加 --marker "main -> main"。默认四个标记保留。
"""

import argparse
import subprocess
import sys
from pathlib import Path

MARKERS = ["SUCCESS", "new reference", "new branch", "refs/for"]


def main():
    ap = argparse.ArgumentParser(description="推送并验证")
    ap.add_argument("repo")
    ap.add_argument("--branch", default=None)
    ap.add_argument("--ref", default=None)
    ap.add_argument("--marker", dest="extra_markers", action="append", default=[],
                    help="追加平台专属的成功标记词，可重复传")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh")
    args = ap.parse_args()

    markers = MARKERS + [m for m in args.extra_markers if m]

    root = Path(args.repo)
    branch = args.branch
    if branch is None:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root, capture_output=True, text=True,
        )
        branch = proc.stdout.strip() or "HEAD"

    ref = (args.ref or "HEAD:{branch}").format(branch=branch)
    print(f"推送到 {ref}" if args.lang == "zh" else f"Pushing to {ref}")

    proc = subprocess.run(
        ["git", "push", "origin", ref],
        cwd=root, capture_output=True, text=True,
    )
    output = proc.stdout + proc.stderr
    print(output)

    if "rejected" in output.lower():
        print("推送被拒绝，输出里有 rejected" if args.lang == "zh" else "Push rejected, rejected found in the output", file=sys.stderr)
        sys.exit(1)
    if not any(m in output for m in markers):
        print("推送验证失败，输出里没有成功标记，回去看错误。平台输出不一样就加 --marker 传它的成功标记"
              if args.lang == "zh" else
              "Push verification failed, no success marker in the output. Pass --marker for platform-specific markers", file=sys.stderr)
        sys.exit(1)
    print("推送验证通过" if args.lang == "zh" else "Push verified")


if __name__ == "__main__":
    main()
