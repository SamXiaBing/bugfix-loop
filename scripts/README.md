# 可用脚本

全部用 Python 标准库写，不需要装任何第三方包，python3 就能跑。每个脚本只做一件固定的事，把日常循环里机械的部分接走，让纪律没法被糊弄。

| 脚本 | 干什么 | 对应哪一步 |
|------|--------|-----------|
| `issue_list.py` | 建清单、合并去重、改状态、统计 | 拉单、写进文件 |
| `git_recent.py` | 进仓库拉最新，看最近几天改了什么 | 先看是不是已经被人修了 |
| `depth_gate.py` | 读检查动作表，算完成率，给结论等级 | 证据够不够 |
| `lesson_append.py` | 往经验库追加一条偏差记录，格式不会乱 | 经验必须记下来 |
| `git_push_verify.py` | 推送并验证，只看 exit code 会骗人 | 修复和提交分级 |
| `adapters/example_api.py` | 缺陷源适配器样板，--demo 可离线自测 | 拉单 |

## 用法一句话

```text
python issue_list.py init 2026-01-15 --feed feed.json
python issue_list.py merge bugs_2026-01-15.md --feed feed.json
python issue_list.py status bugs_2026-01-15.md BUG-101 确定结论 已定位根因
python issue_list.py report bugs_2026-01-15.md
python git_recent.py /path/to/project --days 3 --path Assets/Foo
python depth_gate.py 当日报告.md
python lesson_append.py --lessons lessons.md --type 代码逻辑看成配置问题 --example BUG-101 --lesson 先查布局再查代码 --category 显示 --path 先查锚点参数
python git_push_verify.py /path/to/project
python adapters/example_api.py --demo | python issue_list.py init 2026-01-15
```

## 自测

每个脚本都有对应的冒烟测试，见 `../tests/run-002.md`。改脚本之后先跑一遍，别带着坏脚本开工。
