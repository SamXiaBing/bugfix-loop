# Bug Fix Loop 迭代意见

> 基于完整阅读 SKILL.md 及全部 references、scripts、tests 后的评价，结合回归测试框架设计。

## 一、当前状态

Skill 的架构已经成熟。三条铁律 + 九项检查 + 五状态 + 复盘三问 + 经验库六字段构成闭环。脚本零依赖、可冒烟测试。虚拟项目自测体系有 4 轮迭代记录。安全设计到位。

**核心判断：skill 的文档质量不需要大改，需要的是把文字纪律升级为可验证的行为约束，并用回归测试框架持续度量。**

## 二、迭代优先级

### P0：回归测试框架就位（已完成）

| 内容 | 状态 |
|------|------|
| 虚拟沙盒环境 | ✅ 已建 |
| 12 个测试用例 | ✅ 已定义 |
| 评分脚本 | ✅ 已建 |
| 运行器 | ✅ 已建 |
| 迭代报告模板 | ✅ 已建 |

**用法**：每次改 skill 后，`python tools/run_regression.py` → 分派 subagent 执行 → `--score-all` 评分 → 对比上次分数。

### P1：脚本健壮性加固

| 改进项 | 原因 | 验收标准 |
|--------|------|----------|
| depth_gate.py 解析加固 | DONE_RE 和 SKIP_WORDS 硬编码，AI 输出格式变化会静默算错 | 增加 fallback：解析不到行时报错而非静默通过；扩展标记词 |
| issue_list.py key 格式扩展 | KEY_RE 只匹配 `[A-Za-z]+-\d+`，不支持 GitHub `#123` | 支持可配置的 key 正则 |
| lesson_append.py 原子写入 | 崩溃时文件可能被截断损坏 | 写临时文件 → rename |
| git_push_verify.py markers 可扩展 | MARKERS 硬编码，新平台不兼容 | 支持从参数追加 markers |

### P2：行为约束工具化

| 改进项 | 原因 | 验收标准 |
|--------|------|----------|
| 复盘第三问质量检查脚本 | AI 可以敷衍写"当时没看日志"就算交差 | tools/check_retrospective.py：检查输出是否包含"人类用什么方法""我为什么没用""如果做了会怎样"三类关键词 |
| 不变量清单可执行化 | checklist.md 靠人工打勾，容易漏 | tools/check_invariants.py：自动扫描所有文档验证 12 组不变量 |
| 经验库去重改进 | 精确匹配整行，语义相同措辞不同不去重 | 基于业务模块+偏差类型+分类的组合去重 |

### P3：安全加固

| 改进项 | 原因 | 验收标准 |
|--------|------|----------|
| Autonomy 升级确认 | AI 可以自己改 project-config.md 的 autonomy 字段 | tools/check_autonomy.py：检测字段变化，要求用户确认 |
| Prompt injection 防御指引 | 当前只有"只当数据读"的文字纪律 | 在 bootstrap.md 增加：缺陷单内容中的 markdown 链接、代码块只渲染不执行的指引 |
| 经验库容量监控 | lessons.md 无限膨胀 | lesson_append.py 写入时检查行数，超阈值提示整理 |

### P4：精度追踪

| 改进项 | 原因 | 验收标准 |
|--------|------|----------|
| 命中率指标 | skill 承诺"越用越准"但没有量化 | issue_list.py report 增加 --accuracy：统计 skill 结论 vs 人类结论一致率 |
| 偏差表趋势图 | 无法直观看到经验库是否在收敛 | 每周统计偏差表条目数、按模块分布、命中率变化 |

## 三、迭代节奏

```
每次改 skill：
  1. python tools/setup_sandbox.py --clean
  2. python tools/run_regression.py
  3. 分派 subagent 跑 12 个用例
  4. python tools/run_regression.py --score-all
  5. 对比 tests/results/iteration-XXX.md
  6. 分数涨了 → 合入；分数跌了 → 回退
```

建议每月跑一次全量回归（12 个用例），每周改完做增量回归（跑受影响规则对应的用例）。

## 四、长期方向

1. **从文字纪律到工具约束**。当前 skill 的纪律全靠 AI 理解文档后自觉遵守。长期目标是把关键纪律变成脚本强制检查，让纪律"无法被绕过"。

2. **从虚拟测试到真实测试**。虚拟沙盒能测规则是否被触发，但测不了真实项目的噪音。长期应该积累真实 bug 的脱敏案例，作为回归测试的补充。

3. **从单 skill 到 skill 组合**。bugfix-loop 可以和 jira-bug-analyzer、gerrit-submit 等 skill 联动。长期应该定义 skill 间的接口协议。

4. **从 AI 判断到人机协同**。当前 skill 的最终拍板者是使用者。长期应该增加"AI 不确定时主动提问"的机制，而不是在不确定时硬写结论或硬标信息不足。
