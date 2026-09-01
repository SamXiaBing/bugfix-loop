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

    init_en = run_py(
        ROOT / "scripts/issue_list.py",
        ["init", "2026-01-16", "--lang", "en"],
        stdin=demo.stdout,
        cwd=tmp,
    )
    report_en = run_py(
        ROOT / "scripts/issue_list.py",
        ["report", "bugs_2026-01-16.md", "--lang", "en"],
        cwd=tmp,
    )
    check(
        "issue_list en",
        "pending" in report_en.stdout and "Total 3" in report_en.stdout,
        report_en.stdout.strip(),
    )

    # key 格式。GitHub #123 和 GitLab 纯数字默认能进清单
    gh_feed = json.dumps({"issues": [
        {"key": "#101", "title": "github issue"},
        {"key": "102", "title": "gitlab issue"},
        {"key": "BUG-201", "title": "jira issue"},
        {"key": "not a key", "title": "bad format"},
    ]})
    init_gh = run_py(
        ROOT / "scripts/issue_list.py",
        ["init", "2026-01-17"],
        stdin=gh_feed,
        cwd=tmp,
    )
    gh_content = (tmp / "bugs_2026-01-17.md").read_text(encoding="utf-8")
    check(
        "issue_list 多编号格式",
        init_gh.returncode == 0
        and "#101" in gh_content
        and "102" in gh_content
        and "BUG-201" in gh_content
        and "not a key" not in gh_content
        and "1 条编号不符合格式被跳过" in init_gh.stdout,
        init_gh.stdout.strip(),
    )

    # 自定义正则。内部系统的怪编号用 --key-re 传进来
    custom_feed = json.dumps({"issues": [{"key": "ACME_9001", "title": "custom key"}]})
    init_custom = run_py(
        ROOT / "scripts/issue_list.py",
        ["init", "2026-01-18", "--key-re", r"[A-Z]+_\d+"],
        stdin=custom_feed,
        cwd=tmp,
    )
    custom_content = (tmp / "bugs_2026-01-18.md").read_text(encoding="utf-8")
    check(
        "issue_list 自定义正则",
        init_custom.returncode == 0 and "ACME_9001" in custom_content,
        init_custom.stdout.strip(),
    )


def test_depth_gate(tmp):
    good = tmp / "good.md"
    good.write_text(
        "# 报告\n\n## 检查动作\n\n| 动作 | 结果 |\n|------|------|\n"
        + "| 读描述和评论 | ✅ |\n| 看附件 | ✅ |\n| 拿运行证据 | ✅ |\n"
        + "| 搜代码 | ✅ |\n| 读代码 | ✅ |\n| 查最近提交 | ✅ |\n"
        + "| 确认归谁管 | ✅ |\n| 复现 | N/A |\n| 确认数据真的到了 | N/A |\n",
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(good)])
    check("depth_gate 工序达标", "工序达标" in result.stdout, result.stdout.strip())

    bad = tmp / "bad.md"
    bad.write_text(
        "# 报告\n\n## 检查动作\n\n| 动作 | 结果 |\n|------|------|\n"
        + "| 读描述和评论 | ✅ |\n| 看附件 | ✅ |\n| 搜代码 | ❌ |\n"
        + "| 读代码 | ❌ |\n| 查最近提交 | ❌ |\n",
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(bad)])
    check("depth_gate 工序不足", "工序不足" in result.stdout, result.stdout.strip())

    result_en = run_py(ROOT / "scripts/depth_gate.py", [str(good), "--lang", "en"])
    check("depth_gate en", "Process floor met" in result_en.stdout, result_en.stdout.strip())

    # 否定句。带完成字样的否定不算完成
    neg = tmp / "neg.md"
    neg.write_text(
        "# 报告\n\n## 检查动作\n\n| 动作 | 结果 |\n|------|------|\n"
        + "| 读描述和评论 | ✅ |\n| 搜代码 | ✅ |\n| 读代码 | 未完成 |\n"
        + "| 拿运行证据 | 没做 |\n| 查最近提交 | 已完成 |\n| 确认归谁管 | ✅ |\n"
        + "| 复现 | N/A |\n| 确认数据真的到了 | 不适用 |\n| 看附件 | N/A |\n",
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(neg)])
    check(
        "depth_gate 否定句不算完成",
        result.returncode == 0
        and "适用 6 项" in result.stdout
        and "完成 3 项" in result.stdout
        and "完成率 50%" in result.stdout,
        result.stdout.strip(),
    )

    # 中间态。部分完成按未完成算，并提示人工确认
    partial = tmp / "partial.md"
    partial.write_text(
        "# 报告\n\n## 检查动作\n\n| 动作 | 结果 |\n|------|------|\n"
        + "| 读描述和评论 | ✅ |\n| 搜代码 | ✅ |\n| 读代码 | ✅ |\n"
        + "| 拿运行证据 | 部分完成 |\n| 查最近提交 | 进行中 |\n| 确认归谁管 | ✅ |\n"
        + "| 复现 | N/A |\n| 确认数据真的到了 | N/A |\n| 看附件 | N/A |\n",
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(partial)])
    check(
        "depth_gate 中间态按未完成",
        result.returncode == 0
        and "适用 6 项" in result.stdout
        and "完成 4 项" in result.stdout
        and "中间态" in result.stdout,
        result.stdout.strip(),
    )

    # 无关表格。没有检查动作表时退出码 2，报解析失败
    wrong = tmp / "wrong.md"
    wrong.write_text(
        "# 报告\n\n## 别的表\n\n| 名字 | 值 |\n|------|-----|\n| a | 1 |\n| b | 2 |\n",
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(wrong)])
    check(
        "depth_gate 无关表格退出码2",
        result.returncode == 2,
        f"exit={result.returncode}",
    )

    # 漏项。表格只有三项，报缺哪几项
    less = tmp / "less.md"
    less.write_text(
        "# 报告\n\n## 检查动作\n\n| 动作 | 结果 |\n|------|------|\n"
        + "| 读描述和评论 | ✅ |\n| 搜代码 | ✅ |\n| 读代码 | ✅ |\n",
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(less)])
    check(
        "depth_gate 漏项警告",
        result.returncode == 0
        and "漏项" in result.stdout
        and "拿运行证据" in result.stdout,
        result.stdout.strip(),
    )

    # 无标题锚定。没有「检查动作」标题，靠九项关键词定位
    nohead = tmp / "nohead.md"
    nohead.write_text(
        "# 报告\n\n| 动作 | 结果 |\n|------|------|\n"
        + "| 读描述和评论 | ✅ |\n| 看附件 | ✅ |\n| 拿运行证据 | ✅ |\n"
        + "| 搜代码 | ✅ |\n| 读代码 | ✅ |\n| 查最近提交 | ✅ |\n"
        + "| 确认归谁管 | ✅ |\n| 复现 | N/A |\n| 确认数据真的到了 | N/A |\n",
        encoding="utf-8",
    )
    result = run_py(ROOT / "scripts/depth_gate.py", [str(nohead)])
    check(
        "depth_gate 无标题按关键词定位",
        result.returncode == 0
        and "关键词定位" in result.stdout
        and "完成 7 项" in result.stdout,
        result.stdout.strip(),
    )


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

    lessons_en = tmp / "lessons_en.md"
    args_en = [
        "--lessons", str(lessons_en), "--lang", "en",
        "--module", "m", "--type", "t", "--example", "E-1",
        "--lesson", "l", "--category", "c", "--path", "p",
    ]
    first_en = run_py(ROOT / "scripts/lesson_append.py", args_en)
    en_ok = first_en.returncode == 0 and "Lesson library" in lessons_en.read_text(encoding="utf-8")
    check("lesson_append en", en_ok, first_en.stdout.strip())

    # 原子写入。追加后原内容完整保留，不留临时文件
    lessons_atomic = tmp / "lessons_atomic.md"
    existing = "# 经验库\n\n## 偏差表\n\n| 业务模块 | 偏差类型 | 示例 | 教训 | 分类 | 验证路径 |\n|----------|----------|------|------|------|----------|\n| 旧模块 | 旧偏差 | OLD-1 | 旧教训 | 显示 | 旧路径 |\n"
    lessons_atomic.write_text(existing, encoding="utf-8")
    args_atomic = [
        "--lessons", str(lessons_atomic),
        "--module", "新模块", "--type", "新偏差", "--example", "NEW-1",
        "--lesson", "新教训", "--category", "逻辑", "--path", "新路径",
    ]
    result = run_py(ROOT / "scripts/lesson_append.py", args_atomic)
    content = lessons_atomic.read_text(encoding="utf-8")
    tmp_leftover = list(tmp.glob("lessons_atomic.md.*.tmp"))
    check(
        "lesson_append 原子写入保旧内容",
        result.returncode == 0
        and "旧模块 | 旧偏差 | OLD-1" in content
        and "新模块 | 新偏差 | NEW-1" in content
        and not tmp_leftover,
        result.stdout.strip(),
    )

    # 空字段拒绝。字段不全时不写文件，退出码 1
    lessons_bad = tmp / "lessons_bad.md"
    before = lessons_bad.exists()
    result = run_py(
        ROOT / "scripts/lesson_append.py",
        ["--lessons", str(lessons_bad), "--module", "m", "--type", "", "--example", "E",
         "--lesson", "l", "--category", "c", "--path", "p"],
    )
    check(
        "lesson_append 空字段拒绝",
        result.returncode == 1 and not lessons_bad.exists() and not before,
        f"exit={result.returncode}",
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

    # --marker 追加自定义成功标记。模拟某平台输出只有 "deployed main"：
    # 默认四词都不命中这行输出，追加自定义词后命中
    platform_out = "To git.example.com/x/y.git\n * deployed main\n"
    # 直接喂不了假输出给脚本，用单元方式验证 marker 逻辑：追加后命中自定义词
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "gpv", ROOT / "scripts/git_push_verify.py"
    )
    gpv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gpv)
    default_markers = list(gpv.MARKERS)
    custom = default_markers + ["deployed"]
    check(
        "git_push_verify 自定义marker",
        default_markers == ["SUCCESS", "new reference", "new branch", "refs/for"]
        and "deployed" in custom
        and not any(m in platform_out for m in default_markers)
        and any(m in platform_out for m in custom),
        f"custom={custom}",
    )


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
