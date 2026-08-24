# Debugging principles

This is the core of the skill. Eight debugging principles that have nothing to do with language or project type, learned the hard way in real projects. Each one carries a real example. The examples are hints only, your project may look nothing like them.

## 1. Classify first, then locate

When you get a bug, do not reach for the code search first. Many things that look like code problems actually live in config, data, versions, or the ownership layer. Decide which category the symptom belongs to, display, layout, logic, data, resources, build, then decide where to start.

Real example. A mispositioned element, we checked layout and anchor parameters first, then code logic. It was indeed the layout parameters, not a single line of code changed.

## 2. A conclusion needs evidence that agrees

To say a layer is fine, several evidence must point to the same conclusion. One single phenomenon is easy to be fooled by, it looks like A, the root cause is B. The method is to list what you should see if this really were the layer's problem, verify each one, and only exclude the layer when all of them check out.

Real example. A black screen, looking at the screen alone tells you nothing. Four evidence settled it, whether the process was running, whether startup logs looked normal, whether it was paused, whether load was normal. All four normal, then we could say the problem was in the display composition layer, not the rendering layer.

## 3. For lag, count the time intervals first

For lag, delay, and jitter, do quantitative analysis first, count intervals, frequencies, and values, then talk about root cause. Do not guess performance and animation up front. Qualitative judgment cannot locate the failing link, a number can point upstream. The method is to locate the problem timestamp, record the timestamps of key events one by one, compute intervals to find the outlier, then locate the failing link.

Real example. A laggy operation that could not be reproduced locally. Counting message intervals one by one showed a position where reporting was delayed by almost double. The conclusion was data source delay, not local rendering.

## 4. Confirm whose problem it is before entering the repo

Confirm which process, module, screen, or repo the symptom belongs to, then enter the matching repo. Do not default to the repo you know. One screen can be rendered by several projects together. Entering the wrong repo means looking for something that does not exist in the wrong place. The method is to check attachments to confirm which app and screen, confirm which repo owns it, then enter.

Real example. A display glitch where the video showed several apps in sequence, and the problem was in the last one. The first attempt analyzed the wrong project, everything was wrong.

## 5. Check whether someone already fixed it

Before deep analysis, pull the latest code and check recent commits, confirm whether the target file was touched. Files touched by many people are likely already fixed by someone. Deriving a root cause from old code is wasted effort, and you may misjudge an already-fixed bug as still needing a fix. The method is to pull first, check git log, see whether the target file appears in recent commits, then judge whether it is fixed-but-unverified or still needs work.

Real example. A problem located to one line in a config file, and the fix commit had landed days earlier. Pulling and checking commits would have revealed it immediately, no need to re-derive the root cause.

## 6. Not found does not mean it does not exist

Zero matches on a keyword search does not mean the code is absent. Config mapping, version switches, naming differences, and submodules can hide it. Ruling it out of this repo is the easiest escape and the easiest to get wrong. The method is to chase the mapping, config, and version chain, the target may be pointed to another sub-app or repo by some mapping.

Real example. A feature with zero matches on a search, ruled out of this repo. In fact a config switch pointed it to another sub-app, and the code was right here.

## 7. Verify what others say before believing it

AI reports, someone saying it was handed off, comments that state a conclusion, all second-hand. Verify before believing. The judgment logic behind a second-hand conclusion may not apply to your scene, for example it does not know that some rendering actually projects to a different screen. The method is to treat second-hand conclusions as leads, not conclusions, verify code and runtime evidence, then decide.

Real example. An AI report ruled the problem out of this layer, because the report attributed by process name and did not know some rendering projected to a different screen. Verified the code and overturned it.

## 8. No conclusion without enough evidence

If the check actions are not done, only undetermined or not enough info is allowed, never confirmed. This prevents shallow depth, where every bug has a conclusion on the surface but half the actions were never done. The method is to attach the check table to every bug, when the process floor is not met, the conclusion cannot be confirmed.

Real example. A batch analysis claimed a high completion rate. Looking at the check table, most bugs only had reading the description and searching code, runtime evidence, attachments, and reproduction were almost never done. Those conclusions were guesses.
