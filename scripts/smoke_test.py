#!/usr/bin/env python3
"""一键冒烟测试。跑一遍所有脚本，验证它们没被改坏。

用法
  python scripts/smoke_test.py

全部通过退出码 0，有失败退出码 1。git 不可用时会跳过 git 相关测试并说明。
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES = []


def run_py(script, args, stdin=None, cwd=None):
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd or ROOT,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def check(name, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def test_issue_list(tmp):
    demo = run_py(ROOT / "scripts/adapters/example_api.py", ["--demo"])
    init = run_py(
        ROOT / "scripts/issue_list.py",
        ["init", "2026-01-15"],
        stdin=demo.stdout,
        cwd=tmp,
    )
    check(
        "issue_list init",
        init.returncode == 0 and (tmp / "bugs_2026-01-15.md").exists(),
        init.stdout.strip(),
    )

    feed = json.dumps({"issues": [{"key": "BUG-104", "title": "x"}]})
    merge = run_py(
        ROOT / "scripts/issue_list.py",
        ["merge", "bugs_2026-01-15.md"],
        stdin=feed,
        cwd=tmp,
    )
    check("issue_list merge", "新增 1 条" in merge.stdout, merge.stdout.strip())

    run_py(
        ROOT / "scripts/issue_list.py",
        ["status", "bugs_2026-01-15.md", "BUG-101", "确定结论"],
        cwd=tmp,
    )
    report = run_py(
        ROOT / "scripts/issue_list.py", ["report", "bugs_2026-01-15.md"], cwd=tmp
    )
    check(
        "issue_list status+report",
        "确定结论 1" in report.stdout,
        report.stdout.strip(),
    )


def test_depth_gate(tmp):
    good = tmp / "good.md"
    good.write_text(
        "# 报告\n\n## 检查动作\n\n| 动作 | 结果 |\n|------|------|\n"
        + "".join(f"| a{i} | ✅ |\n" for i in range(7))
        + "".join(f"| b{i} | N/A |\n" for i in range(2)),
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(good)])
    check("depth_gate 工序达标", "工序达标" in result.stdout, result.stdout.strip())

    bad = tmp / "bad.md"
    bad.write_text(
        "# 报告\n\n## 检查动作\n\n| 动作 | 结果 |\n|------|------|\n"
        + "| a | ✅ |\n| b | ✅ |\n| c | ❌ |\n| d | ❌ |\n| e | ❌ |\n",
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(bad)])
    check("depth_gate 工序不足", "工序不足" in result.stdout, result.stdout.strip())


def test_lesson_append(tmp):
    lessons = tmp / "lessons.md"
    args = [
        "--lessons", str(lessons),
        "--module", "m", "--type", "t", "--example", "E-1",
        "--lesson", "l", "--category", "c", "--path", "p",
    ]
    first = run_py(ROOT / "scripts/lesson_append.py", args)
    second = run_py(ROOT / "scripts/lesson_append.py", args)
    check(
        "lesson_append 追加+去重",
        "已追加" in first.stdout and "已经记过" in second.stdout,
        second.stdout.strip(),
    )


def test_git(tmp):
    if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
        print("[SKIP] git 不可用，跳过 git 相关测试")
        return
    repo = tmp / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=repo)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo)
    (repo / "a.txt").write_text("hi", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=repo)
    subprocess.run(["git", "commit", "-q", "-m", "first"], cwd=repo)

    recent = run_py(ROOT / "scripts/git_recent.py", [str(repo), "--days", "300"])
    check("git_recent 列提交", "first" in recent.stdout, recent.stdout.strip())

    push = run_py(ROOT / "scripts/git_push_verify.py", [str(repo), "--branch", "main"])
    check("git_push_verify 失败识别", push.returncode == 1, f"exit={push.returncode}")


def main():
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        test_issue_list(tmp)
        test_depth_gate(tmp)
        test_lesson_append(tmp)
        test_git(tmp)
    if FAILURES:
        print(f"\n失败 {len(FAILURES)} 项，{', '.join(FAILURES)}")
        sys.exit(1)
    print("\n冒烟测试全部通过")


if __name__ == "__main__":
    main()
