# Bug Fix Loop

A generic daily loop for reducing software bugs. Configure the environment once, then walk the same fixed order every day, review yesterday, pull today's tickets, analyze one by one, and write conclusions and lessons into files. It does not care about language or framework. Java, C++, Web, and embedded projects all work, and it gets more accurate the longer you use it.

## What holds it up

Fixing bugs is hard because of judgment, not because of process. Judging is exactly this skill's job. It finds root causes, writes conclusions, proposes fixes. The three hard rules govern how that judgment is made, so it rests on evidence instead of guesses. The final call belongs to the user.

1. Review when there is something to review. Compare yesterday's analysis only when it exists. If there is none, or the user only wants new tickets, go straight to analysis. The comparison looks at two things, the resolution in the ticket by other developers, and the conclusion this skill gave last time.
2. The conclusion level rests on the evidence, not on how many analysis steps were performed. As process, run at least half of the applicable check actions, that is the floor. A few actions that give mutually confirming hard evidence are enough for a confirmed conclusion; all actions done but the evidence contradicts itself still cannot confirm.
3. Lessons are recorded at comparison time and read before analysis. After each review, write the gap between the two conclusions into the lesson library. Before analyzing a new ticket, scan the deviation table first, and follow the verification path directly when it matches.

## Quick start

1. After installing, read `references/bootstrap.md`, probe your environment, and write `project-config.md`. It records four things, code repos, issue tracker, where you pull tickets from every day (a concrete openable location, a filter or a link, written down as-is), where runtime evidence lives.
2. Run `python scripts/adapters/example_api.py --demo` to confirm the script works, then follow the sample to hook up your own tracker.
3. Read `references/loop.md` every day and follow the order. Scripts live in `scripts/`, all Python standard library, no third-party packages.

## Layout

| Path | What it holds |
|------|---------------|
| `references/` | The daily loop, evidence check, review protocol, lesson library, fix and submit levels, environment setup |
| `references/principles/` | Eight debugging principles, the core of the skill |
| `references/project-types/` | Packs for project types, example-web is the template |
| `scripts/` | Ready-to-run scripts that mechanize fixed steps |
| `en/` | English docs |
| `tests/` | Virtual-project self tests, run them after every change |

## Self test

After changing any doc or script, run these.

```text
python scripts/smoke_test.py
python tools/check_prose.py file.md
```

The invariant checklist lives in `tests/checklist.md`.

## License

Code (under `scripts/` and `tools/`) is MIT, see `LICENSE`. Docs are CC BY 4.0, see `LICENSE-docs`.

中文版，`README.md`。
