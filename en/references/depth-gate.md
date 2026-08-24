# The evidence check

## Why this check exists

The most common failure in bug analysis is not wrong judgment, it is judging too fast. Read the description, search a bit, and write a confirmed conclusion. This check uses one hard rule to stop that habit. At least half of the applicable check actions must be done, that is the process floor, the level depends on the evidence.

## The check actions (nine)

| # | Action | What it means | Counts when |
|---|--------|---------------|-------------|
| 1 | Read description and comments | Read the whole ticket and all comments, miss no context | always |
| 2 | Look at attachments | Screenshots, videos, reproduction steps | attachments exist |
| 3 | Collect runtime evidence | Logs, console, event stream, error reporting, locate the problem timestamp, see actual behavior | evidence exists |
| 4 | Search code | Find where the key logic or config is | always |
| 5 | Read code | Read the actual file and line, searching is not enough | always |
| 6 | Check recent commits | git pull, then git log for recent days, confirm nobody already fixed it | always |
| 7 | Confirm who owns it | Which process, module, repo, screen the symptom belongs to, do not default to yourself | always |
| 8 | Reproduce | Try to reproduce locally or in an editor | reproducible |
| 9 | Confirm data really arrived | Did the data, signal, or request actually arrive, do not assume it did | interaction or state involved |

## How to judge

Count the applicable actions, then count the done ones. The number reports the process floor, it does not set the level by itself.

- Process. At least half of the applicable actions must be done. This is the floor, it stops conclusions after one or two actions.
- Level. The level rests on the evidence. A few actions that give mutually confirming hard evidence are enough for a confirmed conclusion. All actions done but the evidence contradicts itself still cannot confirm.
- Not enough info. Key evidence unavailable, no runtime evidence, cannot reproduce, mark not enough info.
- Contradiction. Done enough but the evidence contradicts itself, keep investigating, no forced conclusion.

## Where this check came from

Once eight bugs were analyzed in a batch, and the report claimed 87.5% completion. Listing the check actions, reading description and comments was done for all eight, searching code for six, reading code only two, collecting runtime evidence zero, looking at attachments zero. Most bugs only had two actions done, far below half. Those confirmed conclusions were guesses based on second-hand information. This check exists to catch that kind of shallow depth.

## Requirements

Every bug's daily report must carry the nine check actions, each marked done, not done, or not applicable, plus one note. The table is evidence for the conclusion, not a formality.
