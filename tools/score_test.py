#!/usr/bin/env python3
"""评分脚本。解析 AI 输出的 bug 报告，按测试用例的评分项打分。

用法
  python tools/score_test.py <用例ID> <报告.md> [--lang zh|en]

输出结构化评分卡，包含每项的通过/失败、得分、总得分。
退出码 0 表示全部通过，1 表示有失败项。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Windows 控制台 GBK 编码无法输出 emoji，强制 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 导入测试用例
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
from cases import get_case  # noqa: E402

# ---------------------------------------------------------------------------
# 解析 AI 输出
# ---------------------------------------------------------------------------

CONCLUSION_PATTERNS = [
    "确定结论",
    "信息不足",
    "无法定论",
    "已修复",
]


def extract_conclusion(text):
    """从报告中提取结论状态。

    优先在"根因结论"或"结论"标题附近查找，
    避免误匹配正文中提到的结论等级名称。
    """
    # 先尝试在"根因结论"或"结论"段落附近找
    conclusion_section_patterns = [
        r"结论等级[：:]\s*(\S+)",
        r"结论[：:]\s*(\S+)",
        r"结论[：:]\s*",
        r"结论等级\s*\|\s*(\S+)",   # markdown 表格: | 结论等级 | 确定结论 |
        r"结论等级\*\*\s*[：:]\s*(\S+)",  # 加粗+冒号: **结论等级**：**确定结论**
        r"结论等级\*\*\s*\|\s*\*\*(\S+)",  # 加粗+表格
    ]
    for pattern in conclusion_section_patterns:
        match = re.search(pattern, text)
        if match:
            section_start = match.start()
            # 从匹配位置往后 250 字符内找结论词
            section = text[section_start:section_start + 250]
            for c in CONCLUSION_PATTERNS:
                if c in section:
                    return c
    # fallback：优先找"根因结论"标题之后的段落，其次"结论"标题
    for section_header in ["## 根因结论", "### 根因结论", "根因结论", "### 结论", "## 结论"]:
        pos = text.find(section_header)
        if pos >= 0:
            section = text[pos:pos + 400]
            for c in CONCLUSION_PATTERNS:
                if c in section:
                    return c
    # 最后 fallback：取全文最后一次出现的结论词
    last_found = None
    for c in CONCLUSION_PATTERNS:
        pos = text.rfind(c)
        if pos >= 0:
            if last_found is None or pos > text.rfind(last_found):
                last_found = c
    return last_found


def extract_check_table(text):
    """提取检查动作表，返回 [(action, result), ...]。

    只解析"检查动作"标题之后的第一个表格，避免误读其他表格。
    """
    # 已知的九项检查动作关键词（用于匹配行）
    ACTION_KEYWORDS = {
        "读描述", "看附件", "拿运行证据", "运行证据", "搜代码", "读代码",
        "查最近提交", "最近提交", "确认归谁管", "归谁管", "复现",
        "确认数据", "数据真的", "数据到",
    }

    lines = text.splitlines()
    rows = []

    # 找到"检查动作"标题所在行
    table_start = None
    for i, line in enumerate(lines):
        if "检查动作" in line:
            table_start = i
            break

    if table_start is None:
        # 没有标题，尝试用关键词匹配所有表格行
        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            # 合并所有 cell 作为匹配文本
            full_text = " ".join(cells)
            if any(kw in full_text for kw in ACTION_KEYWORDS):
                # 找到结果列：优先用 ✅/❌/N/A 标记的那一列
                result = ""
                for cell in cells[1:]:
                    if cell and (cell in ("✅", "❌", "N/A", "NA", "n/a", "na") or
                                 DONE_RE.search(cell) or cell.lower() in SKIP_WORDS):
                        result = cell
                        break
                if not result:
                    result = cells[-1] if cells[-1] else cells[1]
                rows.append((full_text, result))
        return rows

    # 从标题行之后找第一个表格
    in_table = False
    for line in lines[table_start + 1:]:
        line = line.strip()
        if not line.startswith("|"):
            if in_table:
                break  # 表格结束
            continue
        in_table = True
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        # 跳过分隔行和表头
        first = cells[0]
        if first.startswith("-") or first in ("动作", "结果", "action", "result", "#"):
            continue
        # 找到结果列：优先用 ✅/❌/N/A 标记的那一列
        result = ""
        for cell in cells[1:]:
            if cell and (cell in ("✅", "❌", "N/A", "NA", "n/a", "na") or
                         DONE_RE.search(cell) or cell.lower() in SKIP_WORDS):
                result = cell
                break
        if not result:
            result = cells[1] if len(cells) > 1 else ""
        action = " ".join(c for c in cells if c and not c.startswith("-"))
        rows.append((action, result))
    return rows


SKIP_WORDS = {"n/a", "na", "not applicable", "不适用", "跳过"}
DONE_RE = re.compile(r"[✅✔完做已✓]")


def calc_depth_ratio(rows):
    """计算检查动作完成率。"""
    applicable = [r for r in rows if r[1].strip().lower() not in SKIP_WORDS]
    done = [r for r in applicable if DONE_RE.search(r[1]) or r[1].strip().lower() in {"done", "yes", "y", "完成", "已做"}]
    if not applicable:
        return 1.0, 0, 0
    return len(done) / len(applicable), len(done), len(applicable)


# ---------------------------------------------------------------------------
# 评分检查器
# ---------------------------------------------------------------------------


def check_conclusion(output_text, case_expected):
    """检查结论是否正确。"""
    expected = case_expected.get("conclusion")
    if not expected:
        return True, "无预期结论要求"
    actual = extract_conclusion(output_text)
    passed = actual == expected
    return passed, f"预期={expected}, 实际={actual}"


def check_root_cause(output_text, case_expected):
    """检查根因关键词是否出现。"""
    keywords = case_expected.get("root_cause_keywords", [])
    if not keywords:
        return True, "无根因关键词要求"
    text_lower = output_text.lower()
    hits = [kw for kw in keywords if kw.lower() in text_lower]
    passed = len(hits) > 0
    return passed, f"命中关键词: {hits}"


def check_classification(output_text, case_expected):
    """检查分类关键词。"""
    keywords = case_expected.get("classification_keywords", [])
    if not keywords:
        return True, "无分类关键词要求"
    hits = [kw for kw in keywords if kw in output_text]
    passed = len(hits) > 0
    return passed, f"命中: {hits}"


def check_depth_gate(output_text, case_expected):
    """检查检查动作完成率是否达标。"""
    min_ratio = case_expected.get("depth_gate_min_ratio", 0.5)
    if min_ratio == 0.0:
        return True, "无工序要求"
    rows = extract_check_table(output_text)
    if not rows:
        # 没有表格，检查文本里有没有提到检查动作
        if min_ratio == 0.0:
            return True, "无表格但无最低要求"
        return False, "报告中没有检查动作表"
    ratio, done, applicable = calc_depth_ratio(rows)
    passed = ratio >= min_ratio
    return passed, f"完成率 {ratio:.0%} ({done}/{applicable}), 最低 {min_ratio:.0%}"


def check_any_in_output(output_text, evidence):
    """检查输出中是否包含任意一个关键词。"""
    keywords = evidence.get("any_keywords", [])
    if not keywords:
        return False, "无关键词定义"
    hits = [kw for kw in keywords if kw.lower() in output_text.lower()]
    passed = len(hits) > 0
    return passed, f"命中: {hits}"


def check_must_not_contain(output_text, evidence):
    """检查输出中是否不包含某些关键词。"""
    forbidden = evidence.get("must_not_contain", [])
    if not forbidden:
        return True, "无禁止词"
    violations = [w for w in forbidden if w.lower() in output_text.lower()]
    passed = len(violations) == 0
    return passed, f"违规词: {violations}" if violations else "无违规"


def check_before_after(output_text, evidence):
    """检查 before_keywords 是否出现在 after_keywords 之前。"""
    before_kws = evidence.get("before_keywords", [])
    after_kws = evidence.get("after_keywords", [])
    if not before_kws or not after_kws:
        return False, "关键词不完整"

    text_lower = output_text.lower()
    before_pos = None
    for kw in before_kws:
        pos = text_lower.find(kw.lower())
        if pos >= 0:
            before_pos = pos
            break

    after_pos = None
    for kw in after_kws:
        pos = text_lower.find(kw.lower())
        if pos >= 0:
            after_pos = pos
            break

    if before_pos is None:
        return False, f"未找到分类关键词: {before_kws}"
    if after_pos is None:
        return True, "找到分类但未找到代码搜索（可能只做了分类）"
    passed = before_pos < after_pos
    return passed, f"分类位置={before_pos}, 搜索位置={after_pos}"


# ---------------------------------------------------------------------------
# 评分主流程
# ---------------------------------------------------------------------------

CHECK_FUNCTIONS = {
    "conclusion": lambda text, ev: check_conclusion(text, ev),
    "root_cause_keywords": lambda text, ev: check_root_cause(text, ev),
    "classification_keywords": lambda text, ev: check_classification(text, ev),
    "depth_gate_min_ratio": lambda text, ev: check_depth_gate(text, ev),
    "any_in_output": lambda text, ev: check_any_in_output(text, ev),
    "must_not_contain": lambda text, ev: check_must_not_contain(text, ev),
    "before_after": lambda text, ev: check_before_after(text, ev),
}


def score_case(case_id, report_path):
    """对一个测试用例的输出评分。返回评分卡字典。"""
    case = get_case(case_id)
    text = Path(report_path).read_text(encoding="utf-8")

    expected = case.get("expected", {})
    rule_evidence = case.get("rule_evidence", {})
    scoring_items = case.get("scoring", [])

    results = []
    total_weight = 0
    total_score = 0

    for item in scoring_items:
        item_id = item["id"]
        desc = item["description"]
        weight = item["weight"]
        check_type = item["check"]
        total_weight += weight

        # 确定 check 函数和参数
        passed = False
        detail = ""

        if check_type in CHECK_FUNCTIONS:
            # 直接用 expected 里的对应字段
            ev_key = check_type.replace("_min_ratio", "").replace("_keywords", "")
            if check_type in ("conclusion",):
                passed, detail = check_conclusion(text, expected)
            elif check_type in ("root_cause_keywords",):
                passed, detail = check_root_cause(text, expected)
            elif check_type in ("classification_keywords",):
                passed, detail = check_classification(text, expected)
            elif check_type in ("depth_gate_min_ratio",):
                passed, detail = check_depth_gate(text, expected)
            elif check_type == "any_in_output":
                # 从 item 里取 keywords
                ev = {"any_keywords": item.get("keywords", [])}
                passed, detail = check_any_in_output(text, ev)
            elif check_type == "must_not_contain":
                # 从 rule_evidence 里找对应的
                ev = rule_evidence.get(item_id, {})
                passed, detail = check_must_not_contain(text, ev)
            elif check_type == "before_after":
                ev = rule_evidence.get(item_id, {})
                passed, detail = check_before_after(text, ev)
        else:
            # 从 rule_evidence 里找对应的检查
            ev = rule_evidence.get(check_type, {})
            if not ev:
                # 尝试用 item_id 匹配
                ev = rule_evidence.get(item_id, {})

            if "any_keywords" in ev:
                passed, detail = check_any_in_output(text, ev)
            elif "must_not_contain" in ev:
                passed, detail = check_must_not_contain(text, ev)
            elif "before_keywords" in ev:
                passed, detail = check_before_after(text, ev)
            else:
                passed = False
                detail = f"未知检查类型: {check_type}"

        if passed:
            total_score += weight

        results.append({
            "id": item_id,
            "description": desc,
            "weight": weight,
            "passed": passed,
            "detail": detail,
        })

    return {
        "case_id": case_id,
        "case_name": case["name"],
        "bug_key": case["bug_key"],
        "probes": case["probes"],
        "total_weight": total_weight,
        "total_score": total_score,
        "percentage": round(total_score / total_weight * 100, 1) if total_weight else 0,
        "items": results,
    }


def format_scorecard(card):
    """格式化评分卡为可读文本。"""
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"用例: {card['case_id']} {card['case_name']}")
    lines.append(f"Bug: {card['bug_key']}")
    lines.append(f"探测规则: {', '.join(card['probes'])}")
    lines.append(f"{'='*60}")
    lines.append("")

    for item in card["items"]:
        tag = "✅ PASS" if item["passed"] else "❌ FAIL"
        lines.append(f"  {tag} [{item['weight']:>2}分] {item['description']}")
        lines.append(f"         {item['detail']}")
        lines.append("")

    lines.append(f"  总分: {card['total_score']}/{card['total_weight']} ({card['percentage']}%)")
    status = "✅ 通过" if card["total_score"] == card["total_weight"] else (
        "⚠️ 部分通过" if card["total_score"] > 0 else "❌ 不通过"
    )
    lines.append(f"  状态: {status}")
    lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="评分脚本")
    ap.add_argument("case_id", help="测试用例 ID，如 TC-001")
    ap.add_argument("report", help="AI 输出的报告文件路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = ap.parse_args()

    card = score_case(args.case_id, args.report)

    if args.json:
        print(json.dumps(card, ensure_ascii=False, indent=2))
    else:
        print(format_scorecard(card))

    sys.exit(0 if card["total_score"] == card["total_weight"] else 1)


if __name__ == "__main__":
    main()
