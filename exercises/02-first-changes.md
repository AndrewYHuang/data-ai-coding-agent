# 02: First changes

**Goal:** make your first code changes with an agent, use git, and feel the difference between
the permission modes.

Andy started pulling the parsing logic out of `clean_rows` into four small helper functions at
the bottom of `kettle/transform.py`, but only got as far as the docstrings. The tests are
already written in `tests/test_transform.py`, and they currently fail.

```
uv run pytest tests/test_transform.py
```

**Rule for this exercise: don't change the tests.** The tests are the spec. If you think a
test is wrong, talk to your trainer.

## 1. Before you start: make a branch

Ask Claude to do it, then check with `git branch` yourself:

```
Create and switch to a new git branch called exercise-02
```

## 2. `format_pence`: manual mode

In this repo, Claude Code starts in **manual** mode, where it asks before every edit and command.
(That's set in `.claude/settings.json`. Elsewhere it defaults to **auto** mode.)

```
Implement format_pence in kettle/transform.py so that its tests in tests/test_transform.py pass.
```

When it asks for permission, **read what it wants to do before you say yes**. Once the tests
pass, ask it to commit:

```
Commit this change with a sensible message
```

Then check `git log` yourself. Is the commit message accurate?

## 3. `parse_price_to_pence`: plan mode

Press **Shift+Tab** until you see **plan mode**. In plan mode, Claude researches and proposes
a plan, but can't change any files.

```
Implement parse_price_to_pence so its tests pass.
```

Read the plan. Look at the test cases for `"4.35"` and `"0.29"`. Does the plan handle them?
Try the plan's suggestion in a Python shell (`uv run python`) - e.g.

```python
>>> int(float("4.35") * 100)
```

If the plan has a problem, tell Claude before you approve it. When you're happy, approve the
plan, let it implement, run the tests and commit.

## 4. `parse_till_timestamp` and `normalise_product_name`: auto-accept edits

Press **Shift+Tab** until you see **accept edits** mode. Claude will now edit files without
asking each time.

Do both functions. Then **review the diff before you commit**. Either use the "diff" view in claude, your IDE, or try running:

```
git diff
```

You can't approve edits one by one any more, so reviewing the diff is how you stay
accountable. Check:

- Does `parse_till_timestamp("01/02/2026 09:00")` give **1st February**? (UK dates are day first.)
- Did Claude change anything apart from those two functions?
- Did it touch the tests?

## 5. Wrap up

```
uv run pytest
```

Everything should pass. Commit, and then compare notes with the person next to you.

## Reflect

- Which permission mode did you prefer? When would you use each one?
- Did the agent ever try to "fix" a failing test by changing the test? How would you know?
- The four helpers exist now, but is `clean_rows` actually _using_ any of them? Should it?
