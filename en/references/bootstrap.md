# First use, get to know the project environment

This skill does not know where the project's code repos are, what the issue tracker is, or where runtime evidence lives. On first use, ask these clearly and write them into `project-config.md`. After that, no need to ask again each day.

Whatever the user says first, if there is no `project-config.md`, run this step first. When the user says "look into this bug for me", set up the environment first anyway. Analyzing without a configured environment is guessing.

## What to ask, six things

1. Code repos. Main repo path, submodules, where the code hosting is.
2. Issue tracker. What system, what address, where you pull pending tickets from every day, how credentials are given. The pull location must be something concrete and openable, a saved filter, a search link, or a list address, write it down as-is, never let the AI invent one. Note that you want a filter or a search link, not a board or a dashboard page. Dashboards are for display, you cannot pull tickets from them. If the user gives the wrong thing, say so and ask for a filter or a search link.
3. Runtime evidence. Logs, console, error reporting, ticket attachments, where they usually are.
4. Business type. What kind of project this is, web frontend, mobile, backend service, embedded, game engine, or something else. The business type decides the classification and the check order. Use a project-type pack when one exists, otherwise fall back to the generic flow.
5. Reference material. Is there a PRD, design doc, API doc, architecture diagram, where do they live. Not mandatory, but they save detours during analysis. If there is none, tell the user the AI can only infer from code and tickets.
6. Business modules. What modules the project has, order, payment, login and so on. Ask the user for a list when one exists, otherwise derive it from ticket titles. Cold start organizes historical tickets by module.

## Probe order

Look in the environment first, ask the user only what is missing.

1. Check whether the current directory is a git repo. Run git remote -v, it shows the hosting and repo path.
2. Find the project root. Look for marker files like README, package.json, pyproject.toml, CMakeLists.txt.
3. Find log directories. Common names, logs, log, out.
4. For what cannot be found, ask once, at most three questions. Do not ask over and over.

## Write the config

Write what you learned into `project-config.md`, follow the fields in `config.example.yaml`. The format does not need to be strict, as long as a human can read it, but five things must be there, code repos, issue tracker, where you pull tickets from, runtime evidence, business type. The pull location must be openable, a saved filter, a search link, or a list address. Reference material gets a path when it exists, write none when it does not.

## Verify once

After writing the config, verify each source one by one. Every step must actually run, never assume it works.

1. Open the pull location recorded in the config, pull one page of tickets, see whether it works. Use `scripts/adapters/example_api.py` as the template for your tracker, run `--demo` first to verify the script itself.
2. Enter the main repo, git pull, see whether it gets the latest. Then run git log, look for recent commits, confirm this is a live repo, not an archived one.
3. Find runtime evidence for an old bug, see whether it can be retrieved. Whether logs can be read, whether attachments can be downloaded. Verify attachment download separately, do not assume being able to list tickets means being able to download attachments, some systems use different endpoints for reading and downloading.
4. If there is reference material, open it and check it can be read.

Record the result of every step. Mark what passed as passed, mark what failed as failed, say what failed.

## When the setup is incomplete

After verification, some sources may not work. A broken source does not mean the skill is useless, but the user must know the consequences.

- Cannot pull tickets from the tracker. The daily loop cannot run, but single-ticket analysis still works. The user hands the bug description and attachments to the AI manually, analysis proceeds as usual.
- Cannot pull the latest from the repo. Analysis still works, but recent commits cannot be checked, so you may analyze something somebody already fixed.
- Cannot get runtime evidence. Analysis still works, but conclusion levels may be capped, many bugs can only be marked not enough info.
- Cannot download attachments. Analysis still works, but screenshots and recordings are out of reach, display and interaction bugs suffer the most.
- No reference material. Analysis still works, but business understanding relies on code and tickets alone, context may be missed.

Tell the user the consequence of each item, so they know what can be done now and what cannot. The user decides whether to fix the environment first or start with the limitations.

## What the config must not contain

Passwords, tokens, and private keys must not be written into `project-config.md`. Reference them by environment variable, see the token_env field in `config.example.yaml`. Config files can be shared, credentials must not travel with them.
