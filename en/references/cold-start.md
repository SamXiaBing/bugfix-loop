# Cold start, learn the history first

On first deploy, or when you want to get familiar with the project's business fast, run a cold start. The purpose is not to fix bugs, it is to consume historical tickets and build a lesson library organized by business module.

## Prerequisites

project-config.md is set, the pull location can reach historical tickets. How business modules are divided, ask the user for a list, or infer from ticket titles.

## Steps

1. From the pull location, pull closed historical tickets in batches by business module. Closed tickets have final conclusions to compare.
2. Keep tickets of one module together, process one module at a time.
3. Walk the check table one by one, give conclusions.
4. Review, compare the changes in comments, find the gap between the skill's conclusion and the actual fix.
5. Write gaps into the lesson library by business module.
6. All modules done, the cold start ends. In the daily loop after that, read the lessons of a module before analyzing its tickets.

## Notes

- For historical tickets without runtime evidence, mark not enough info honestly, do not force analysis.
- A cold start is batch work, slow is fine, the point is library quality, not quantity.
- If one cold start cannot finish, continue by module next time.
