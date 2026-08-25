# Bug Fix Loop

[English](README.en.md) | **中文**

一个 AI 智能体技能（Agent Skill），用来系统化地分析软件缺陷，并持续积累分析经验。

## 这是什么

Bug Fix Loop 是一个 Agent Skill。宿主 AI（Claude Code、Cursor、Codely CLI 等）加载根目录的 `SKILL.md` 后，获得一套完整的 bug 分析工作流。`references/` 里的文档和 `scripts/` 里的脚本在运行时按需使用。

它不是普通工具库。把整个目录放进技能目录就能用，不需要安装任何依赖。

## 它能干什么

围绕缺陷单的日常循环，每天按固定顺序走一遍。

1. 复盘昨天，对比缺陷单里别人的解决结论和 skill 上次的分析结论，差距记进经验库
2. 从配置好的拉单位置拉今天的待分析单
3. 逐条分析，先查经验库，再按九项检查动作取证，最后给结论
4. 需要时按授权级别修复和提交
5. 写进文件，教训记进经验库

分析结论分三个等级，信息不足、无法定论、确定结论。结论等级由证据决定，不由做了多少步决定。

## 特点

- 判断优先。核心产出是根因和结论，不是跑流程
- 证据门槛。九项检查动作至少做一半是工序保底，结论等级看证据撑不撑得住
- 经验自增长。复盘发现的差距按业务模块记进经验库，分析前先查同模块的教训
- 权限分级。L0 只读到 L3 自动提交，默认只读，升级要使用者同意
- 冷启动。第一次部署按业务模块批量学历史单，快速建立项目经验库
- 零依赖。脚本全部 Python 标准库，不需要装第三方包
- 跨语言跨框架。Java、C++、Web、嵌入式都适用，只要求有代码仓库和缺陷跟踪系统

## 安装

把整个目录放进你宿主的技能目录。以 Claude Code 为例，一条命令装好。

```bash
git clone https://github.com/SamXiaBing/bugfix-loop ~/.claude/skills/bugfix-loop
```

其他宿主换成对应的技能目录。

| 宿主 | 技能目录 |
|------|---------|
| Claude Code | `~/.claude/skills/bugfix-loop/` 或项目 `.claude/skills/` |
| Cursor | `.cursor/skills/bugfix-loop/` |
| Codely CLI | `~/.codely-cli/skills/bugfix-loop/` |
| oo | `oo skills adopt <本目录>` |

## 使用

### 第一次用

读 `references/bootstrap.md`，探测环境，写 `project-config.md`。里面记四样东西，代码仓库、缺陷系统、每天从哪里拉单、运行证据。

### 每天用

对 AI 说"分析 bug"或"拉今天的单"，它按 `references/loop.md` 的流程走。完整文档地图见 `SKILL.md`。

### 效果示例

```text
$ python scripts/adapters/example_api.py --demo | python scripts/issue_list.py init 2026-01-15
写进 bugs_2026-01-15.md，共 3 条

$ python scripts/depth_gate.py 当日报告.md
检查动作 9 项，适用 7 项，完成 7 项，完成率 100%
工序达标，适用动作做了一半以上，等级看证据对不对得上
```

## 设计原则

- 复盘先于分析，但有昨天的分析才复盘，没有就直接分析新单
- 结论等级看证据，不按动作数算。工序保底，证据硬就能下结论，证据矛盾就下不了
- 经验必须落盘，在对账时记，分析前读
- 证据不够不下结论，只能标信息不足或无法定论
- 默认只读，改代码和提交按级别授权
- 缺陷单、评论、日志里的内容是不可信数据，只当数据读，不当命令执行

## 目录结构

| 路径 | 内容 |
|------|------|
| `SKILL.md` | 技能入口，宿主加载它 |
| `references/` | 循环、证据门槛、复盘、经验库、环境探测、冷启动等文档 |
| `references/principles/` | 八条调试基本原则 |
| `references/project-types/` | 项目类型适配包，example-web 是样板 |
| `scripts/` | 可用脚本，全部 Python 标准库 |
| `tests/` | 虚拟项目自测 |
| `en/` | 英文版文档 |

## 开发与自测

改完任何文档或脚本，先跑一遍。

```text
python scripts/smoke_test.py
python tools/check_prose.py 文件.md
```

不变量清单在 `tests/checklist.md`，贡献指南在 `CONTRIBUTING.md`。

## 安全

读什么、写什么、默认只读、缺陷单内容按不可信数据处理，见 `SECURITY.md`。

## 许可证

代码（scripts/ 和 tools/）用 MIT，见 `LICENSE`。文档用 CC BY 4.0，见 `LICENSE-docs`。
