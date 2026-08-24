#!/usr/bin/env python3
"""提交并推送，然后验证推送真的成功。只看 exit code 会骗人。

用法
  python git_push_verify.py <仓库> [--branch 分支] [--ref 引用]

--ref 不填时默认 HEAD:{branch}。走审查流程的系统（比如 refs/for 风格）填
--ref "refs/for/{branch}"。
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
    args = ap.parse_args()

    root = Path(args.repo)
    branch = args.branch
    if branch is None:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root, capture_output=True, text=True,
        )
        branch = proc.stdout.strip() or "HEAD"

    ref = (args.ref or "HEAD:{branch}").format(branch=branch)
    print(f"推送到 {ref}")

    proc = subprocess.run(
        ["git", "push", "origin", ref],
        cwd=root, capture_output=True, text=True,
    )
    output = proc.stdout + proc.stderr
    print(output)

    if "rejected" in output.lower():
        print("推送被拒绝，输出里有 rejected", file=sys.stderr)
        sys.exit(1)
    if not any(m in output for m in MARKERS):
        print("推送验证失败，输出里没有成功标记，回去看错误", file=sys.stderr)
        sys.exit(1)
    print("推送验证通过")


if __name__ == "__main__":
    main()
