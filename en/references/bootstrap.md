# First use, get to know the project environment

This skill does not know where the project's code repos are, what the issue tracker is, or where runtime evidence lives. On first use, ask these clearly and write them into `project-config.md`. After that, no need to ask again each day.

## What to ask

1. Code repos. Main repo path, submodules, where the code hosting is.
2. Issue tracker. What system, what address, where you pull pending tickets from every day, how credentials are given. The pull location must be something concrete and openable, a saved filter, a search link, or a list address, write it down as-is, never let the AI invent one.
3. Runtime evidence. Logs, console, error reporting, ticket attachments, where they usually are.

## Probe order

Look in the environment first, ask the user only what is missing.

1. Check whether the current directory is a git repo. Run git remote -v, it shows the hosting and repo path.
2. Find the project root. Look for marker files like README, package.json, pyproject.toml.
3. Find log directories. Common names, logs, log, out.
4. For what cannot be found, ask once, at most three questions. Do not ask over and over.

## Write the config

Write what you learned into `project-config.md`, follow the fields in `config.example.yaml`. The format does not need to be strict, as long as a human can read it, but four things must be there, code repos, issue tracker, where you pull tickets from, runtime evidence. The pull location must be openable, a saved filter, a search link, or a list address.

## Verify once

After writing the config, run through it to confirm it works.

1. Open the pull location recorded in the config, pull one page of tickets, see whether it works. Use `scripts/adapters/example_api.py` as the template for your tracker, run `--demo` first to verify the script itself.
2. Enter the main repo, git pull, see whether it gets the latest.
3. Find runtime evidence for an old bug, see whether it can be retrieved.

All three pass, the environment is known. Fix whatever fails first, do not start with a broken config.

## What the config must not contain

Passwords, tokens, and private keys must not be written into `project-config.md`. Reference them by environment variable, see the token_env field in `config.example.yaml`. Config files can be shared, credentials must not travel with them.
