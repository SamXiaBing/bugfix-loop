#!/usr/bin/env python3
"""创建或重置沙盒环境。

在 tests/sandbox/ 下创建一个完整的虚拟项目环境：
  - acme-web/ 假 git 仓库（带源码和 commit 历史）
  - project-config.md 项目配置
  - lessons.md 经验库（预设一条偏差记录）
  - tracker/bugs.json 缺陷数据
  - reports/ AI 输出目录

用法
  python tools/setup_sandbox.py [--clean]

--clean 先删除已有沙盒再重建。
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 导入沙盒数据
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sandbox_data import BUGS, COMMITS, LESSONS_PRESET  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SANDBOX = ROOT / "tests" / "sandbox"
REPO = SANDBOX / "acme-web"


def run(cmd, cwd=None, check=True):
    """运行命令，返回 (returncode, stdout, stderr)。"""
    proc = subprocess.run(
        cmd, cwd=cwd or ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"命令失败: {' '.join(cmd)}\n{proc.stderr}")
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def init_git_repo():
    """初始化假 git 仓库并写入 commit 历史。"""
    if REPO.exists():
        shutil.rmtree(REPO)
    REPO.mkdir(parents=True)

    run(["git", "init", "-q"], cwd=REPO)
    run(["git", "config", "user.email", "test@acme.example"], cwd=REPO)
    run(["git", "config", "user.name", "Acme Test"], cwd=REPO)

    for commit in COMMITS:
        for rel_path, content in commit["files"].items():
            full = REPO / rel_path
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            run(["git", "add", rel_path], cwd=REPO)
        run(["git", "commit", "-q", "-m", commit["message"]], cwd=REPO)


def write_project_config():
    """写 project-config.md。"""
    config = f"""# 项目配置

## 代码仓库

- 主仓库：{REPO}
- 代码托管：git.acme.example/acme-web（虚构）
- 子模块：{REPO / "packages" / "api"}（虚构）

## 缺陷系统

- 系统：类 Jira issue tracker（虚构）
- 地址：issues.acme.example（虚构）
- 拉单位置：filter=backlog-critical
- 适配器：scripts/adapters/example_api.py

## 运行证据

- 日志：{REPO / "logs" / "api.log"}
- 附件：{SANDBOX / "tracker" / "attachments"}

## 权限

autonomy: L0

## 语言

language: zh
"""
    (SANDBOX / "project-config.md").write_text(config, encoding="utf-8")


def write_lessons():
    """写经验库。"""
    (SANDBOX / "lessons.md").write_text(LESSONS_PRESET, encoding="utf-8")


def write_bug_data():
    """写 bug 数据 JSON。"""
    tracker_dir = SANDBOX / "tracker"
    tracker_dir.mkdir(parents=True, exist_ok=True)

    # bug 数据
    (tracker_dir / "bugs.json").write_text(
        json.dumps({"issues": BUGS}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 附件目录（放占位文件）
    att_dir = tracker_dir / "attachments"
    att_dir.mkdir(exist_ok=True)
    for bug in BUGS:
        for att in bug.get("attachments", []):
            att_path = att_dir / att["name"]
            if not att_path.exists():
                att_path.write_text(
                    f"[虚拟附件] {att['name']}\n属于 {bug['key']}: {bug['title']}\n"
                    "这是一个占位文件，实际测试时由 AI 读取文件名判断附件是否存在。\n",
                    encoding="utf-8",
                )


def create_dirs():
    """创建目录结构。"""
    SANDBOX.mkdir(parents=True, exist_ok=True)
    (SANDBOX / "reports").mkdir(exist_ok=True)


def main():
    ap = argparse.ArgumentParser(description="创建或重置沙盒环境")
    ap.add_argument("--clean", action="store_true", help="先删除已有沙盒再重建")
    args = ap.parse_args()

    if args.clean and SANDBOX.exists():
        import stat

        def on_rm_error(func, path, exc_info):
            """Windows 上 git 对象文件可能只读，改权限后重试。"""
            os.chmod(path, stat.S_IWRITE)
            func(path)

        shutil.rmtree(SANDBOX, onerror=on_rm_error)

    create_dirs()
    print("[1/5] 创建目录结构")

    init_git_repo()
    print("[2/5] 初始化 git 仓库")

    write_project_config()
    print("[3/5] 写入 project-config.md")

    write_lessons()
    print("[4/5] 写入 lessons.md")

    write_bug_data()
    print("[5/5] 写入 bug 数据和附件")

    # 验证
    code, out, _ = run(["git", "log", "--oneline"], cwd=REPO)
    print(f"\n沙盒就绪：{SANDBOX}")
    print(f"git 仓库：{REPO}")
    print(f"commit 历史：\n{out}")
    print(f"bug 数据：{len(BUGS)} 条")
    print(f"\n下一步：python tools/run_regression.py")


if __name__ == "__main__":
    main()
