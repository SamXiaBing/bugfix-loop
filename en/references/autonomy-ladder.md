# Fix and submit, four levels

Read-only by default, the higher the level the more careful. The level is set in the `autonomy` field of `project-config.md`. Moving to a higher level needs the user's approval.

## L0 Read-only

Analyze bugs, give root cause and the fix, do not touch code.

- Allowed. Read code, read logs, run searches, look at diffs.
- Forbidden. Change files, commit, push.

## L1 Propose

On top of L0, write the fix plan as a clear change list, wait for the user's confirmation.

- Allowed. Give the files to change, the change points, the reasons.
- Forbidden. Change any file before the user confirms.

## L2 Auto-change

After the user confirms the plan, change the code directly, do not commit.

- Allowed. Change files per the confirmed plan, run tests, show the user the diff.
- Forbidden. Change anything outside the plan, commit, push.

## L3 Auto-submit

After changing, commit and push directly, go through code review.

- Allowed. git add, commit, push, confirm success with the push verification rule.
- Forbidden. Change anything outside the plan, bypass review, force push.

## Rollback

Every level keeps an exit. L2 broken, git checkout restores. L3 committed wrong, changeable before push, revoke from the review page after push. Before changing, confirm the current branch is clean, do not drag in uncommitted changes from others.

## Push verification rule

After committing and pushing, trusting only the exit code deceives. A push rejected remotely can still return 0.

1. Check whether the output contains the SUCCESS keyword.
2. Check whether a review link was generated.
3. Check for confirmation like new reference or new branch.
4. rejected in the output means failure.

`scripts/git_push_verify.py` runs these automatically, the checks are hard-coded, not by eyes.

## Common push pitfalls

- Wrong branch name. Before pushing, confirm the branch name with git rev-parse --abbrev-ref HEAD, then compare with the full remote branch name.
- Commit message polluted by a BOM character at the start. If the format error appears, check the first line for hidden characters, recommit with git commit --amend.
- Commit message format mismatch. The first line must start with the required type, required fields must be filled.
- Submodule branch name. The submodule's remote branch must match the remote repo, do not guess.
