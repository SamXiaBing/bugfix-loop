# Bug Fix Loop

让 AI 分析 bug 时给出的结论，不再是猜的。

有一次批量分析八条 bug，报告说完成率 87.5%。把检查动作列出来一数，大部分 bug 其实只做了读描述和搜代码两项，运行证据一条都没拿，附件一条都没看。那些确定结论都是猜测。Bug Fix Loop 就是把这种浮躁的深度抓出来。

## 这是什么

一个 AI 智能体技能（Agent Skill），不是脚本库，也不是普通工具。宿主 AI（Claude Code、Cursor、Codely CLI 这类）读根目录的 `SKILL.md` 学会一套 bug 分析流程，`references/` 和 `scripts/` 是它运行时按需加载的文档和脚本。

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

装完怎么确认，对 AI 说"分析 bug"或者"拉今天的单"，它应该按 `references/loop.md` 的流程开始。

## 它靠什么站住

修 bug 难在判断，不在跑流程。拿单、下日志、搜代码、提交这些步骤谁都会，难的是判断症状属于哪一层，以及证据够不够下结论。这个 skill 的活就是判断，下根因、给结论、提修法。

1. 复盘按需做。有昨天的分析才对账，没有或用户只要新单，就直接分析。对账比两样东西，缺陷单里别人的解决结论，和 skill 上次给的分析结论。
2. 结论等级看证据撑不撑得住，不由已经做了多少分析步骤决定。适用的检查动作至少做一半，这是保底；少数动作给出相互印证的硬证据，够自信也能下确定结论；动作全做但证据互相矛盾，一样下不了。
3. 经验在对账时记，分析前读。每次复盘把两样结论的差距写进经验库，分析新单之前先扫一眼偏差表，命中的直接按验证路径走。

## 每天怎么转

```text
1 复盘昨天（有才做）  对比别人的解决结论，差距写进经验库
2 拉今天的单          从默认拉单位置拉待分析的单
3 逐条分析            扫经验库，9 项检查动作，给结论
4 可选修复提交        L0 只读到 L3 自动提交，逐级授权
5 写进文件            更新清单，教训记进经验库

经验库越攒越多，越用越准
```

## 有和没有的区别

没有 Bug Fix Loop
AI 读完 bug 描述，搜两下代码，写一句确定结论，完。

有 Bug Fix Loop
AI 读完描述，先扫经验库，再逐条过 9 项检查动作。运行证据拿到了吗，附件看了吗，最近提交查了吗。证据够不够下结论，差距记进经验库。明天更准。

## 看看长什么样

```text
$ python scripts/adapters/example_api.py --demo | python scripts/issue_list.py init 2026-01-15
写进 bugs_2026-01-15.md，共 3 条

$ python scripts/issue_list.py report bugs_2026-01-15.md
待分析 3
总计 3

$ python scripts/depth_gate.py 当日报告.md
检查动作 9 项，适用 7 项，完成 7 项，完成率 100%
工序达标，适用动作做了一半以上，等级看证据对不对得上
```

## 适合谁

- 有代码仓库加缺陷跟踪系统的开发团队
- 想让 AI 分析 bug 但发现结论不靠谱的人
- 想把 bug 分析经验系统化攒下来的人
- 不挑语言和框架，Java、C++、Web、嵌入式都能用

## 快速开始

1. 装好之后，读 `references/bootstrap.md`，探测自己的环境，写 `project-config.md`。里面记四样东西，代码仓库、缺陷系统、每天从哪里拉单（要一个能打开的具体位置，筛选器或链接都行，原样记下）、运行证据。
2. 跑 `python scripts/adapters/example_api.py --demo`，确认脚本能用，再照着样板接项目的缺陷系统。
3. 每天读 `references/loop.md`，按顺序走。脚本在 `scripts/`，全用 Python 标准库，不需要装第三方包。

## 目录结构

| 目录 | 装什么 |
|------|--------|
| `references/` | 每天怎么走、证据门槛、复盘协议、经验库、修复提交分级、环境探测、冷启动 |
| `references/principles/` | 八条调试基本原则，整个 skill 的核心 |
| `references/project-types/` | 项目类型适配包，example-web 是样板 |
| `scripts/` | 可用脚本，固定动作机械化 |
| `en/` | 英文版文档 |
| `tests/` | 虚拟项目自测，改完先跑 |

## 自测

改完任何文档或脚本，先跑一遍。

```text
python scripts/smoke_test.py
python tools/check_prose.py 文件.md
```

不变量清单在 `tests/checklist.md`。

## 安全

读什么、写什么、默认只读、缺陷单内容按不可信数据处理，见 `SECURITY.md`。

## 许可证

代码（scripts/ 和 tools/）用 MIT，见 `LICENSE`。文档用 CC BY 4.0，见 `LICENSE-docs`。

English version，`README.en.md`。
