# How to review

The point of a review is to find out why you got it wrong, and turn the lesson into a rule you can use next time. The value lives in the third question.

## Every bug with a conclusion needs three parts

### 1. What was my conclusion yesterday

Write down what you judged for this bug. Root-cause direction, ownership judgment, suggested next step. For example, I judged it was a rendering logic problem, not a config problem, and suggested changing some code.

### 2. What did humans do later

Check the tracker for progress. What developers, testers, or other teams changed, who it was handed to, what the final root cause was.

### 3. Why did I fail to reach the right conclusion

This part is the easiest to skip and the most important. Ask three questions.

- What method did humans use to reach the right conclusion. Logs, version comparison, local reproduction, or checking commits.
- Why did I not use the same method. I did not know the method exists, then add it to the principles, or I knew but did not do it, then enforce it with the check table.
- If I had done that action then, how would the conclusion have differed.

Writing only that the direction was right or wrong, without answering why it was not done right, means the review did not happen. The reason is often not lack of ability, it is not executing. Skip this step and you will make the same mistake again.

## After the review, update the lesson library

Turn the answer to the third question into a reusable lesson, and write it into `lessons.md`.

| Field | What to write |
|-------|---------------|
| Business module | Which business module the bug belongs to, orders, payments, login |
| Deviation type | The shift from assumption to reality. Code logic mistaken for a config problem, performance guess mistaken for data timing |
| Example | An anonymous id of the bug, for looking it up |
| Lesson | One sentence, directly reusable next time |
| Category | Which symptom category, display, logic, data, resources |
| Verification path | What the right action is. Not just the root cause, the action |

## When to review

Every day before analysis, review yesterday. Check once more before leaving work. New comments can appear at any time of day, checking once is easy to miss.

## Hard rules

- Until the review is done, no new tickets today.
- Writing only right or wrong, without why it was not done right, means the review did not happen.
