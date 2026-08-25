# How to write a project-type pack

The core flow does not care about project type, but each project type has different judgment methods. Java projects, C++ projects, Web projects, embedded projects differ in classification, check items, and vocabulary. A project-type pack puts these differences into one folder, so the core flow can land in that project type.

## What a project-type pack contains

```
project-types/your-project-type/
├── README.md          What this project type is, when to use
├── classification.md  The classification of this project type, how classify-first-locate splits
├── checks.md          The check items specific to this project type, by category
└── vocabulary.md      The common words and concepts of this project type, signals, mappings, fields
```

## Four files, four questions

1. README.md. Which projects this pack applies to, which not.
2. classification.md. How many categories the most common symptoms of this project type split into.
3. checks.md. For each category, what to check first, what next.
4. vocabulary.md. What config mapping, data not arriving, version too old look like in this project type.

## How to verify when done

Walk three real bugs of this project type. Classification matches, check items guide the direction, vocabulary can be searched, then it passes. A type you cannot write a classification for means you have not understood it yet, do not write it.

## Example

See `project-types/example-web/`, a complete pack for a generic Web project, follow it.
