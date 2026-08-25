# How to keep the lesson library

The lesson library is the carrier of the skill getting better with use. It records gaps found when comparing, the resolution in the ticket by other developers, and the conclusion this skill gave last time, when the two do not match, record the lesson. Before analyzing a new bug, scan the deviation table, see whether something matches, and follow the verification path directly if so.

## Where the file lives

The library file is called `lessons.md`, next to `project-config.md`, in the same directory. Use `scripts/lesson_append.py` to append the first time, the script creates the file and the table header.

## What it looks like

```markdown
# Lesson library

## Deviation table

| Business module | Deviation type | Example | Lesson | Category | Verification path |
|-----------------|----------------|---------|--------|----------|-------------------|
| Orders page | Code logic mistaken for a config problem | BUG-101 | Check layout parameters before code logic | Display | Check anchor parameters first |
```

## Six fields of the deviation table

| Field | What to write |
|-------|---------------|
| Business module | Which business module the bug belongs to, orders, payments, login. Lessons of the same module are reused first |
| Deviation type | The shift from assumption to reality. Code logic mistaken for a config problem, performance guess mistaken for data timing |
| Example | An anonymous id of the bug, for looking it up |
| Lesson | One sentence, directly reusable next time |
| Category | Which symptom category, display, logic, data, resources |
| Verification path | What the right action is. Not just the root cause, the action |

## Append rules

- One row per lesson, append with `scripts/lesson_append.py`, the format stays correct.
- Keep only the newest record for the same kind of deviation. Update existing records, do not stack duplicates.
- A lesson must be an action, do not write things like be careful, pay attention, which cannot be executed.
- Tidy up once a week. Group similar lessons, merge into principles when possible, turn into check items when possible.

## Review record template

After each daily review, the report carries a fixed section.

```markdown
## Review record

### BUG-xxx
- My conclusion yesterday. What was written.
- What humans did later. What changed, who it was handed to, the final root cause.
- Why I failed to conclude. What method humans used, why I did not use it, what would differ if I had.
- The lesson extracted. One sentence, write it into the deviation table.
```

## How to use

Before analyzing a bug, check the deviation table for records of the same business module first, then the category and verification path. When something matches, follow the verification path directly, saving the time of stepping the same pit again. New deviations found in review go into the table the same day, do not save them up.
