# The daily loop

Make fixing bugs a fixed daily cycle. The order is, pull tickets, analyze one by one, optional fix and submit, write files. Review happens before pulling, and only when yesterday left analysis behind.

## Step 0, look at the environment

Open `project-config.md` and confirm three things.

1. Where the code repos are, the main repo and submodule paths.
2. Where the issue tracker is, and where you pull tickets from every day, a concrete filter or link that can be opened.
3. Where runtime evidence lives, logs, console, error reporting, or ticket attachments.

If `project-config.md` does not exist, run the environment setup first (see `references/bootstrap.md`).

## Step 1, review yesterday (only when yesterday's analysis exists)

Do this step only when yesterday left analysis behind. If there is none, or the user only wants new tickets, jump to step 2. Full process in `references/retrospective.md`.

1. Open yesterday's list `bugs_YYYY-MM-DD.md`.
2. For every bug you gave a conclusion, check the tracker for how others resolved it later, what they changed, what the comments say.
3. Compare the skill's last conclusion with the resolution in the ticket, and write any gap into the lesson library `lessons.md`.

No review debt. If yesterday had no analysis, skip the review today, do not force one.

## Step 2, pull today's tickets

1. Open the pull location recorded in the config, and pull the pending bugs.
2. Deduplicate, and create `bugs_YYYY-MM-DD.md` for today.
3. Mark every bug as pending.

## Step 3, analyze one by one

Each bug goes through `references/depth-gate.md` and `references/principles/debugging-principles.md`.

1. Scan the deviation table in `lessons.md` first. If something matches, follow the verification path directly, do not step the same pit again.
2. One at a time. Running several at once makes the tracker and browser fight, and attachments get lost.
3. Classify before locating. Decide which category this bug belongs to (see the principles).
4. Run the check actions, read description and comments, look at attachments, collect runtime evidence, search code, check recent commits, confirm who owns it, reproduce, confirm data really arrived.
5. Give a conclusion, only one of three, not enough info, undetermined, confirmed.

## Step 4, optional, fix and submit

Only with the user's permission. Default is read-only, give the root cause and the fix, do not touch code. Levels in `references/autonomy-ladder.md`.

## Step 5, write files

1. Update the main list status.
2. Write today's report `bugs_YYYY-MM-DD.md`, with the check-action table.
3. New lessons go into `lessons.md`.

## States of a bug

| State | Meaning | When |
|-------|---------|------|
| Pending | Not touched yet | after pulling |
| Not enough info | Key evidence unavailable | runtime evidence missing, cannot reproduce, not enough context |
| Undetermined | Analyzed, but no definite conclusion | process floor not met, or evidence not enough or contradictory |
| Confirmed | Evidence holds, several evidence agree | process floor met, evidence mutually confirming |
| Fixed | Self-fixed, or confirmed someone else fixed | commit landed, or review confirmed |

When marking fixed, note the source. Fixed by yourself, or by someone else. The review treats these two very differently.

## Common mistakes

- Skip the comparison when there is something to compare, yesterday had conclusions and the tracker has new progress
- Write a confirmed conclusion after only reading the description and searching a bit
- Analyze several bugs at once and lose attachments
- Treat not found as does not exist (see principles)
- Finish analysis without writing files or keeping lessons
