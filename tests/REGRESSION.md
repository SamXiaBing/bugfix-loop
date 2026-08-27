# 回归测试框架

测的不是脚本，是 LLM 在文档约束下的判断质量。

## 核心思路

Agent Skill 的行为是 LLM 读文档后做出的判断。改了一条规则后，skill 好没好，不能靠感觉，要靠数据。

这个框架做的事：

1. 建一个虚拟沙盒（假 git 仓库 + 假缺陷系统 + 假日志 + 假经验库）
2. 定义 12 个测试用例，每条对应一条或几条规则
3. 用 subagent 充当"加载了 skill 的 AI"，执行分析
4. 脚本自动打分，检查结论对不对、根因准不准、规则触没触发
5. 记录每次迭代的分数，跨版本比较

## 目录结构

```
tests/
├── cases.py                  # 12 个测试用例定义
├── sandbox/                  # 虚拟环境（gitignored，由脚本生成）
│   ├── acme-web/             # 假 git 仓库
│   ├── project-config.md     # 项目配置
│   ├── lessons.md            # 经验库
│   ├── tracker/bugs.json     # bug 数据
│   ├── prompts/              # 生成的 prompt 文件
│   └── reports/              # AI 输出报告
├── results/                  # 迭代报告
└── ...

tools/
├── sandbox_data.py           # 沙盒数据（源码、bug、日志）
├── setup_sandbox.py          # 创建/重置沙盒
├── score_test.py             # 评分脚本
└── run_regression.py         # 运行器
```

## 怎么用

### 1. 建环境 + 生成 prompt

```bash
python tools/run_regression.py
```

在 `tests/sandbox/` 下创建虚拟项目，生成 12 个 prompt 文件。

### 2. 执行测试用例

两种方式：

**方式 A：用 subagent（推荐）**

用 Codely 的 task 工具分派 subagent，每个 subagent 读取 prompt 文件、加载 skill、执行分析、把报告写到 `tests/sandbox/reports/TC-XXX.md`。

**方式 B：手动**

读 `tests/sandbox/prompts/TC-XXX.txt`，手动让 AI 执行，把输出保存到 `tests/sandbox/reports/TC-XXX.md`。

### 3. 评分

```bash
# 评分所有报告
python tools/run_regression.py --score-all

# 评分单个用例
python tools/run_regression.py --score TC-001 tests/sandbox/reports/TC-001.md
```

### 4. 查看结果

迭代报告在 `tests/results/iteration-XXX.md`，包含：

- 总览（通过/部分通过/不通过/平均得分）
- 逐用例结果
- 失败项详情
- 按规则覆盖率

## 12 个测试用例

| 用例 | 名称 | 探测的规则 |
|------|------|-----------|
| TC-001 | 显示类bug，先分类再定位 | 原则1 先分类再定位 |
| TC-002 | 逻辑类bug，先数时间间隔 | 原则3 卡顿先数时间间隔 |
| TC-003 | 归属类bug，先弄清是谁的问题 | 原则4+7 归属判断+别信二手 |
| TC-004 | 已修复的bug | 原则5 先看是不是已经被人修了 |
| TC-005 | 隐藏代码 | 原则6 搜不到不等于没有 |
| TC-006 | 别信二手结论 | 原则7 别人说的结论要自己验证 |
| TC-007 | 信息不足 | 原则8+depth-gate 证据不够不下结论 |
| TC-008 | 证据矛盾 | depth-gate 矛盾 |
| TC-009 | Prompt注入 | 安全 不可信数据 |
| TC-010 | 经验库命中 | 铁律3 经验在对账时记分析前读 |
| TC-011 | 检查动作保底 | depth-gate 工序保底 |
| TC-012 | 复盘三问 | 复盘 三问不能跳过 |

## 迭代流程

```
改 skill 文档/脚本
    ↓
python tools/setup_sandbox.py --clean     # 重置环境
python tools/run_regression.py            # 生成 prompt
（分派 subagent 执行测试用例）
python tools/run_regression.py --score-all  # 评分
    ↓
对比上次迭代的分数
    ↓
分数涨了 → 改对了
分数跌了 → 改坏了，回退或修正
```

## 评分逻辑

每个测试用例有若干评分项，每项有权重。评分检查类型：

| 检查类型 | 说明 |
|----------|------|
| conclusion | 结论等级是否和预期一致 |
| root_cause_keywords | 根因关键词是否出现 |
| classification_keywords | 分类关键词是否出现 |
| depth_gate_min_ratio | 检查动作完成率是否达标 |
| any_in_output | 输出中是否出现指定关键词（规则触发证据） |
| must_not_contain | 输出中是否不包含某些词（如注入指令没被执行） |
| before_after | 一组词是否出现在另一组词之前（如分类在搜索之前） |

## 注意

- 沙盒是虚构的，不需要真实的 Jira 或仓库
- 每次 `setup_sandbox.py --clean` 会完全重建环境，保证可复现
- AI 输出有随机性，同一用例多次执行结果可能不同。建议每次迭代跑 2-3 轮取平均
- 沙盒目录已加入 .gitignore，不会提交到仓库
