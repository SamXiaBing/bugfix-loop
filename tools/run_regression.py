#!/usr/bin/env python3
"""回归测试运行器。编排完整流程。

用法
  python tools/run_regression.py                     # 建环境 + 生成所有 prompt
  python tools/run_regression.py --score-all        # 评分所有报告 + 生成迭代报告
  python tools/run_regression.py --score TC-001 FILE # 评分单个用例
  python tools/run_regression.py --list             # 列出所有用例

流程
  1. setup_sandbox.py 创建虚拟环境
  2. 本脚本为每个用例生成 prompt 文件
  3. 用 subagent 或手动执行 prompt，输出写到 tests/sandbox/reports/
  4. 本脚本评分并生成迭代报告
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
from cases import TEST_CASES, get_case  # noqa: E402

SANDBOX = ROOT / "tests" / "sandbox"
REPORTS = SANDBOX / "reports"
PROMPTS = SANDBOX / "prompts"
RESULTS = ROOT / "tests" / "results"

SKILL_PATH = ROOT / "SKILL.md"
REFERENCES = ROOT / "references"
REPO_PATH = SANDBOX / "acme-web"
CONFIG_PATH = SANDBOX / "project-config.md"
LESSONS_PATH = SANDBOX / "lessons.md"
TRACKER_PATH = SANDBOX / "tracker" / "bugs.json"


# ---------------------------------------------------------------------------
# 生成 prompt
# ---------------------------------------------------------------------------


def generate_analysis_prompt(case):
    """为分析类测试用例生成 prompt。"""
    bug_key = case["bug_key"]
    prompt = f"""你是一个 bug 分析 AI。请按照 bugfix-loop skill 的流程分析以下 bug。

## 环境

- skill 入口：{SKILL_PATH}
- 参考文档目录：{REFERENCES}
- 代码仓库：{REPO_PATH}
- 项目配置：{CONFIG_PATH}
- 经验库：{LESSONS_PATH}
- bug 数据：{TRACKER_PATH}

## 任务

1. 读取 {SKILL_PATH}，按里面的流程走
2. 读取 project-config.md 了解环境
3. 从 {TRACKER_PATH} 读取 bug 数据，找到 {bug_key}
4. 按 loop.md 的流程逐条分析这条 bug
5. 先读 lessons.md 的偏差表
6. 按 depth-gate.md 的九项检查动作做检查
7. 按 debugging-principles.md 的原则做判断
8. 给出结论（确定结论/信息不足/无法定论）
9. 输出一份完整的 bug 分析报告

## 输出格式

输出一个 markdown 报告，包含以下部分：

### 基本信息
- Bug ID
- 标题
- 分类（显示/逻辑/数据/资源/构建）

### 检查动作表

| 动作 | 结果 |
|------|------|
| 读描述和评论 | ✅ / ❌ / N/A |
| 看附件 | ✅ / ❌ / N/A |
| 拿运行证据 | ✅ / ❌ / N/A |
| 搜代码 | ✅ / ❌ / N/A |
| 读代码 | ✅ / ❌ / N/A |
| 查最近提交 | ✅ / ❌ / N/A |
| 确认归谁管 | ✅ / ❌ / N/A |
| 复现 | ✅ / ❌ / N/A |
| 确认数据真的到了 | ✅ / ❌ / N/A |

### 分析过程
（写清楚每一步做了什么，发现了什么）

### 根因结论
（写明根因和结论等级）

### 教训
（如果有新教训，写出来）

请现在开始分析。先读 SKILL.md，然后按流程走。
"""
    return prompt


def generate_retrospective_prompt(case):
    """为复盘类测试用例生成 prompt。"""
    prompt = f"""你是一个 bug 分析 AI。请按照 bugfix-loop skill 的复盘流程做一次复盘。

## 环境

- skill 入口：{SKILL_PATH}
- 参考文档目录：{REFERENCES}
- 经验库：{LESSONS_PATH}

## 任务

对 BUG-101 做一次复盘。以下是已知信息：

### 昨天我的结论

{case.get("yesterday_conclusion", "")}

### 人类后来做了什么

{case.get("human_resolution", "")}

## 要求

1. 读取 {SKILL_PATH} 和 references/retrospective.md
2. 按复盘协议写三部分：
   - 昨天我的结论是什么
   - 人类后来做了什么
   - 我为什么没能得出正确结论（即使这次对了也要写）
3. 提炼一条教训，写进偏差表格式

## 输出格式

### 复盘记录

#### BUG-101
- 昨天我的结论：（写具体内容）
- 人类后来做了什么：（写具体内容）
- 我为什么没能得出：（写具体内容，包括人类用什么方法、我为什么没用、如果做了会怎样）
- 提炼的教训：（一句话，写进偏差表）

请现在开始复盘。先读 SKILL.md 和 retrospective.md，然后按流程走。
"""
    return prompt


def generate_onboarding_prompt(case):
    """为首次部署引导测试用例生成 prompt。

    模拟一个没配过环境的用户，随手发了一条消息。
    关键：prompt 里不给 project-config.md 路径，不给 bug 数据路径，
    只给 skill 入口和代码仓库，看 AI 是否引导初始化。
    """
    prompt = f"""你是一个 AI 助手。用户刚装了一个叫 bugfix-loop 的 skill。

## 环境

- skill 入口：{SKILL_PATH}
- 参考文档目录：{REFERENCES}
- 代码仓库：{REPO_PATH}

## 场景

这是首次使用，还没有 project-config.md，环境未初始化。不要去找 project-config.md，直接按 SKILL.md 的流程走首次初始化。

## 用户的消息

帮我看看 BUG-101 这个 bug

## 你的任务

按照 bugfix-loop skill 的流程回应用户。先读 {SKILL_PATH}，按里面的"第一次用"流程走。不要直接分析 bug，先完成初始化。

把你的完整回应写入 D:\\AIWorkSpace\\bugfix-loop\\tests\\sandbox\\reports\\TC-013.md
"""
    return prompt


def generate_usage_guide_prompt(case):
    """为使用方式告知测试用例生成 prompt。"""
    prompt = f"""你是一个 AI 助手。用户刚装了一个叫 bugfix-loop 的 skill。

## 环境

- skill 入口：{SKILL_PATH}
- 参考文档目录：{REFERENCES}
- 代码仓库：{REPO_PATH}
- 项目配置：{CONFIG_PATH}
- 经验库：{LESSONS_PATH}
- bug 数据：{TRACKER_PATH}

## 用户的消息

你能干什么？怎么用？

## 你的任务

按照 bugfix-loop skill 的流程回应用户。先读 {SKILL_PATH}，然后按里面的指引走。

把你的完整回应写入 D:\\AIWorkSpace\\bugfix-loop\\tests\\sandbox\\reports\\TC-014.md
"""
    return prompt


def generate_path_feedback_prompt(case):
    """为成果物路径反馈测试用例生成 prompt。"""
    bug_key = case["bug_key"]
    prompt = f"""你是一个 bug 分析 AI。请按照 bugfix-loop skill 的流程分析以下 bug。

## 环境

- skill 入口：{SKILL_PATH}
- 参考文档目录：{REFERENCES}
- 代码仓库：{REPO_PATH}
- 项目配置：{CONFIG_PATH}
- 经验库：{LESSONS_PATH}
- bug 数据：{TRACKER_PATH}

## 任务

1. 读取 {SKILL_PATH}，按里面的流程走
2. 读取 project-config.md 了解环境
3. 从 {TRACKER_PATH} 读取 bug 数据，找到 {bug_key}
4. 按 loop.md 的流程逐条分析这条 bug
5. 先读 lessons.md 的偏差表
6. 按 depth-gate.md 的九项检查动作做检查
7. 按 debugging-principles.md 的原则做判断
8. 给出结论（确定结论/信息不足/无法定论）
9. 输出一份完整的 bug 分析报告

## 输出格式

输出一个 markdown 报告，包含以下部分：

### 基本信息
- Bug ID
- 标题
- 分类（显示/逻辑/数据/资源/构建）

### 检查动作表

| 动作 | 结果 |
|------|------|
| 读描述和评论 | ✅ / ❌ / N/A |
| 看附件 | ✅ / ❌ / N/A |
| 拿运行证据 | ✅ / ❌ / N/A |
| 搜代码 | ✅ / ❌ / N/A |
| 读代码 | ✅ / ❌ / N/A |
| 查最近提交 | ✅ / ❌ / N/A |
| 确认归谁管 | ✅ / ❌ / N/A |
| 复现 | ✅ / ❌ / N/A |
| 确认数据真的到了 | ✅ / ❌ / N/A |

### 分析过程
（写清楚每一步做了什么，发现了什么）

### 根因结论
（写明根因和结论等级）

### 教训
（如果有新教训，写出来）

请现在开始分析。先读 SKILL.md，然后按流程走。最后把完整报告写入 D:\\AIWorkSpace\\bugfix-loop\\tests\\sandbox\\reports\\TC-015.md
"""
    return prompt


def generate_prompt(case):
    """根据用例类型生成 prompt。"""
    if case.get("is_onboarding"):
        return generate_onboarding_prompt(case)
    if case.get("is_usage_guide"):
        return generate_usage_guide_prompt(case)
    if case.get("is_path_feedback"):
        return generate_path_feedback_prompt(case)
    if case.get("is_retrospective"):
        return generate_retrospective_prompt(case)
    return generate_analysis_prompt(case)


# ---------------------------------------------------------------------------
# 评分和报告
# ---------------------------------------------------------------------------


def score_all():
    """评分所有报告，生成迭代报告。"""
    from score_test import score_case, format_scorecard

    cards = []
    for case in TEST_CASES:
        case_id = case["id"]
        report_path = REPORTS / f"{case_id}.md"
        if not report_path.exists():
            print(f"[跳过] {case_id}：报告不存在 ({report_path})")
            continue
        try:
            card = score_case(case_id, str(report_path))
            cards.append(card)
            print(format_scorecard(card))
        except Exception as e:
            print(f"[错误] {case_id}：{e}")

    if not cards:
        print("\n没有可评分的报告。先运行测试用例生成报告。")
        return

    # 生成迭代报告
    generate_iteration_report(cards)


def generate_iteration_report(cards):
    """生成本次迭代的报告。"""
    RESULTS.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()

    # 找到下一个迭代号
    existing = sorted(RESULTS.glob("iteration-*.md"))
    next_num = len(existing) + 1

    report_path = RESULTS / f"iteration-{next_num:03d}.md"

    lines = [f"# 回归测试迭代 {next_num:03d}", ""]
    lines.append(f"日期：{today}")
    lines.append(f"测试用例数：{len(cards)}")
    lines.append("")

    # 总览
    total_pass = sum(1 for c in cards if c["total_score"] == c["total_weight"])
    total_partial = sum(1 for c in cards if 0 < c["total_score"] < c["total_weight"])
    total_fail = sum(1 for c in cards if c["total_score"] == 0)
    avg_score = sum(c["percentage"] for c in cards) / len(cards)

    lines.append("## 总览")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 全通过 | {total_pass}/{len(cards)} |")
    lines.append(f"| 部分通过 | {total_partial}/{len(cards)} |")
    lines.append(f"| 不通过 | {total_fail}/{len(cards)} |")
    lines.append(f"| 平均得分 | {avg_score:.1f}% |")
    lines.append("")

    # 按用例详列
    lines.append("## 逐用例结果")
    lines.append("")
    lines.append(f"| 用例 | 名称 | 探测规则 | 得分 | 百分比 | 状态 |")
    lines.append(f"|------|------|----------|------|--------|------|")
    for c in cards:
        status = "✅" if c["total_score"] == c["total_weight"] else ("⚠️" if c["total_score"] > 0 else "❌")
        probes = ", ".join(c["probes"])
        lines.append(f"| {c['case_id']} | {c['case_name']} | {probes} | {c['total_score']}/{c['total_weight']} | {c['percentage']}% | {status} |")
    lines.append("")

    # 失败项详情
    failures = []
    for c in cards:
        for item in c["items"]:
            if not item["passed"]:
                failures.append((c["case_id"], c["case_name"], item))
    if failures:
        lines.append("## 失败项详情")
        lines.append("")
        for case_id, case_name, item in failures:
            lines.append(f"### {case_id} {case_name} - {item['description']}")
            lines.append(f"- 权重：{item['weight']}")
            lines.append(f"- 详情：{item['detail']}")
            lines.append("")

    # 按规则统计
    lines.append("## 按规则覆盖率")
    lines.append("")
    rule_stats = {}
    for c in cards:
        for probe in c["probes"]:
            if probe not in rule_stats:
                rule_stats[probe] = {"total": 0, "passed": 0}
            rule_stats[probe]["total"] += 1
    for c in cards:
        all_passed = c["total_score"] == c["total_weight"]
        for probe in c["probes"]:
            if all_passed:
                rule_stats[probe]["passed"] += 1
    lines.append(f"| 规则 | 测试次数 | 通过 | 覆盖率 |")
    lines.append(f"|------|----------|------|--------|")
    for rule, stats in sorted(rule_stats.items()):
        rate = stats["passed"] / stats["total"] * 100 if stats["total"] else 0
        lines.append(f"| {rule} | {stats['total']} | {stats['passed']} | {rate:.0f}% |")
    lines.append("")

    report_text = "\n".join(lines)
    report_path.write_text(report_text, encoding="utf-8")
    print(f"\n迭代报告已写入：{report_path}")
    print(f"总览：{total_pass} 全通过 / {total_partial} 部分通过 / {total_fail} 不通过 / 平均 {avg_score:.1f}%")


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def setup_and_generate():
    """建环境 + 生成所有 prompt。"""
    # 运行 setup_sandbox
    import subprocess
    import os
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "setup_sandbox.py"), "--clean"],
        cwd=ROOT, capture_output=True, env=env,
    )
    try:
        print(proc.stdout.decode("utf-8", errors="replace"))
    except Exception:
        print(proc.stdout)
    if proc.returncode != 0:
        try:
            print(f"沙盒创建失败：{proc.stderr.decode('utf-8', errors='replace')}", file=sys.stderr)
        except Exception:
            print(f"沙盒创建失败：{proc.stderr}", file=sys.stderr)
        sys.exit(1)

    # 生成 prompt
    PROMPTS.mkdir(parents=True, exist_ok=True)
    for case in TEST_CASES:
        prompt = generate_prompt(case)
        prompt_path = PROMPTS / f"{case['id']}.txt"
        prompt_path.write_text(prompt, encoding="utf-8")

    print(f"\n已生成 {len(TEST_CASES)} 个 prompt 文件：{PROMPTS}")
    print(f"\n执行方式：")
    print(f"  1. 对每个用例，用 subagent 或手动执行 prompt")
    print(f"  2. 将输出保存到 {REPORTS / '<TC-XXX>.md'}")
    print(f"  3. 运行 python tools/run_regression.py --score-all 评分")
    print(f"\n用例列表：")
    for case in TEST_CASES:
        print(f"  {case['id']}  {case['name']}  (bug: {case.get('bug_key', 'N/A')})")


def main():
    ap = argparse.ArgumentParser(description="回归测试运行器")
    ap.add_argument("--score-all", action="store_true", help="评分所有报告")
    ap.add_argument("--score", nargs=2, metavar=("CASE_ID", "FILE"), help="评分单个用例")
    ap.add_argument("--list", action="store_true", help="列出所有用例")
    args = ap.parse_args()

    if args.list:
        for case in TEST_CASES:
            probes = ", ".join(case["probes"])
            print(f"{case['id']}  {case['name']}  bug={case.get('bug_key', 'N/A')}  probes={probes}")
        return

    if args.score:
        from score_test import score_case, format_scorecard
        card = score_case(args.score[0], args.score[1])
        print(format_scorecard(card))
        sys.exit(0 if card["total_score"] == card["total_weight"] else 1)

    if args.score_all:
        score_all()
        return

    # 默认：建环境 + 生成 prompt
    setup_and_generate()


if __name__ == "__main__":
    main()
