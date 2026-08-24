# Bug Fix Loop

Conclusions from AI bug analysis no longer read like guesses.

Once eight bugs were analyzed in a batch, and the report claimed 87.5% completion. Listing the check actions, most bugs only had reading the description and searching code done, runtime evidence was never collected, attachments were never looked at. Those confirmed conclusions were guesses. Bug Fix Loop exists to catch that kind of shallow depth.

## What holds it up

Fixing bugs is hard because of judgment, not because of process. Pulling tickets, reading logs, searching code, committing, everyone can do those. The hard part is deciding which layer the symptom belongs to, and whether the evidence is enough to conclude. Judging is exactly this skill's job. It finds root causes, writes conclusions, proposes fixes.

1. Review when there is something to review. Compare yesterday's analysis only when it exists. If there is none, or the user only wants new tickets, go straight to analysis. The comparison looks at two things, the resolution in the ticket by other developers, and the conclusion this skill gave last time.
2. The conclusion level rests on the evidence, not on how many analysis steps were performed. As process, run at least half of the applicable check actions, that is the floor. A few actions that give mutually confirming hard evidence are enough for a confirmed conclusion; all actions done but the evidence contradicts itself still cannot confirm.
3. Lessons are recorded at comparison time and read before analysis. After each review, write the gap between the two conclusions into the lesson library. Before analyzing a new ticket, scan the deviation table first, and follow the verification path directly when it matches.

## The daily loop

```text
1 review yesterday (only when it exists)  compare the fix in the ticket, write gaps into the lesson library
2 pull today's tickets                    from the configured pull location
3 analyze one by one                      scan lessons, nine check actions, give a conclusion
4 optional fix and submit                 L0 read-only to L3 auto submit, each level needs approval
5 write files                             update the list, record lessons

The lesson library grows, the analysis gets more accurate
```

## With and without

Without Bug Fix Loop
The AI reads the description, searches a bit, writes a confirmed conclusion, done.

With Bug Fix Loop
The AI reads the description, scans the lesson library, then walks through the nine check actions. Was runtime evidence collected, attachments looked at, recent commits checked. Is the evidence enough to conclude, gaps go into the lesson library. More accurate tomorrow.

## Who it's for

- Teams with a code repo and an issue tracker
- People who want AI-assisted bug analysis but find the conclusions unreliable
- People who want to accumulate bug-analysis experience systematically
- Any language and framework, Java, C++, Web, embedded

## Quick start

1. After installing, read `../references/bootstrap.md`, probe your environment, and write `project-config.md`. It records four things, code repos, issue tracker, where you pull tickets from every day, runtime evidence.
2. Run `../scripts/adapters/example_api.py --demo` to confirm the script works, then follow the sample to hook up your own tracker.
3. Read `../references/loop.md` every day and follow the order. Scripts live in `../scripts/`, all Python standard library, no third-party packages.

## Layout

| Path | What it holds |
|------|---------------|
| `../references/` | The daily loop, evidence check, review protocol, lesson library, fix and submit levels, environment setup, cold start |
| `../references/principles/` | Eight debugging principles, the core of the skill |
| `../references/project-types/` | Packs for project types, example-web is the template |
| `../scripts/` | Ready-to-run scripts that mechanize fixed steps |
| `../tests/` | Virtual-project self tests, run them after every change |

## Self test

After changing any doc or script, run these.

```text
python ../scripts/smoke_test.py
python ../tools/check_prose.py file.md
```

## Security

What it reads, what it writes, read-only by default, ticket content treated as untrusted data, see `../SECURITY.md`.

## License

Code (under `scripts/` and `tools/`) is MIT, see `../LICENSE`. Docs are CC BY 4.0, see `../LICENSE-docs`.

中文版，`README.md`。
