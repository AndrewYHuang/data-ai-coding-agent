# 01: Meet the codebase

**Goal:** use Claude Code to understand code you've never seen before, and check that what it
tells you is true.

Make sure you've done the [setup](../README.md#setup) first, and that `uv run pytest` runs.

## 1. Start Claude Code

From the repo's top-level folder:

```
claude
```

## 2. Ask your first questions

Try these, one at a time. Read each answer properly before moving on.

1. `Describe this codebase. What does it do, and how is it structured?`
2. `Walk me through what happens to a single row from data/raw/tills/leeds_2026-09-14.csv, from
   the till export all the way to the daily summary.`
3. `How are the four branches' till exports different from each other?`
4. `How do I run the tests and the pipeline?`

## 3. Check what it told you

The agent sounds confident whether it's right or not. **Discernment** means checking.

For each answer above, pick **one specific claim** and check it yourself by opening the file
it mentions. For example:

- Does Dublin's CSV really have its columns in a different order? Open it.
- Is Manchester's price really in pence? How can you tell from the data? How does the code
  know?
- For question 4, did it say `pytest`/`python` or `uv run pytest`/`uv run python`? Why might
  that matter? (Hold that thought for exercise 04.)

Write down anything it got **wrong**, **vague** or **missed out**.

## 4. Find the smells

Ask: `What would you be worried about if you had to maintain this code?`

Compare its list with your own. Did it spot:

- the `except: pass` in `clean_rows` that silently throws away bad rows?
- the file in `extract.py` that's opened but never closed?
- the branch names hard-coded in several places?

Did it flag anything that you think *isn't* actually a problem?

## Discuss

- How long would it have taken you to understand this codebase without the agent?
- How did you decide which of its claims to trust?
- There's a file of customer personal data in `data/raw/`. Did the agent read it while
  exploring? Would you know if it had? (We'll come back to this in exercise 04.)
