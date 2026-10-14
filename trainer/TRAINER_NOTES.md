# Trainer notes

These notes and the rest of the `solutions` branch are for trainers only. Don't merge them into
`main`.

## The solutions branch

There is one commit per exercise step, so you can diff each step on its own
(`git log --oneline main..solutions`):

| Commit | Exercise |
|---|---|
| Exercise 02: implement the transform helpers | 02 |
| Exercise 03A: characterisation tests | 03 part A (bugs marked `BUG?`) |
| Exercise 03B: fix Dublin EUR to GBP conversion (KC-101) | 03 part B |
| Exercise 03C: support Edinburgh's JSON Lines till (KC-104) | 03 part C |
| Stretch KC-102: count refunds, only drop exact duplicates | 03 stretch |
| Stretch KC-103: clean rows with the helpers and the catalogue | 03 stretch |
| Exercise 04: CLAUDE.md, skill, deny rules and test hook | 04 |
| Exercise 05: product summary spec and implementation | 05 |

At the end, `uv run pytest` gives 66 passing tests, including `tests/test_reconciliation.py`,
which checks every branch and day against the Z-reports.

---

## Exercise 01: answer key

Learners fact-check ten claims in `HANDOVER.md`. In the story, Andy had an AI agent write
most of it and pasted it in unedited.

| # | Handover note's claim | True? | Evidence |
|---|---|---|---|
| 1 | Every till file is picked up | ✗ | `BRANCHES` is hard-coded in `kettle/pipeline.py`. `edinburgh_2026-09-16.jsonl` is never read. |
| 2 | Every `unit_price` is in pounds | ✗ | Manchester's is in pence (`350`). `clean_rows` has a separate case for `manchester`. |
| 3 | Dublin is converted using that day's rate | ✗ in practice | It multiplies by the rate when it should divide. €5.25 × 1.1712 gives 615p, but the right answer is 448p. |
| 4 | Negative quantities are till mistakes | ✗ | They're refunds: each is a single-line transaction with its own ID, e.g. `LDS-0914-0024` on 14 September. |
| 5 | Only exact duplicates are removed | ✗ | The duplicate check uses `(branch, sold_at, product)`, so different sales of the same product in the same minute are merged (e.g. `LDS-0914-0022` and `-0023`). |
| 6 | Names are matched to the catalogue | ✗ | `read_products` is never called. Names only get `.strip().title()`. |
| 7 | Bad rows are "handled gracefully" | Vague | A bare `except: pass` drops them with no trace. |
| 8 | UK dates are read day first | ✓ | `strptime("%d/%m/%Y %H:%M")` |
| 9 | Run with `pip` and `python -m` | ✗ | The repo uses uv (`uv run ...`), and plain `python` may not be installed. |
| 10 | The summary is emailed at 6am | Can't verify | Nothing in the repo sends email, so learners can't confirm it from the repo. The right answer is "I'd have to check the server or ask the ops manager". |

Where the mistakes came from:
- **Claims 3 and 4:** the code comments (`# convert to GBP`, and "some tills export negative
  numbers by mistake"). The agent repeated what the comments say instead of what the code
  does.
- **Claim 6:** `read_products()` exists in `extract.py` but is never called. The agent saw
  the function and assumed it was used.
- **Claims 1, 9 and 10:** Andy's own beliefs, which the agent wrote up as fact.

That's the discussion point: an agent repeats whatever confident sources it's given, and it
doesn't flag what it couldn't check.

**Why it's a recorded write-up, not a live trap.** We tested live agents (Sonnet and Opus) on
the exercise questions, and they caught most of the traps by reading the code. A project skill
that told the agent to "fall for" the traps was refused: the agent ignored it and told the
learner about it. A pre-written handover note gives every learner the same mistakes to find.

---

## Exercise 02: things to watch for

- **`parse_price_to_pence("4.35", "pounds")`:** agents often write `int(float(value) * 100)`,
  which gives 434. The tests catch it. The fix is `Decimal`, or `round()`.
- **`parse_till_timestamp("01/02/2026 09:00")`:** this must be 1 February. Check that the agent
  didn't reach for `dateutil` or month-first parsing.
- **`normalise_product_name("Flat", ...)`:** this must return `None`. Fuzzy or prefix matching
  fails the test.
- Look out for any agent "fixing" a test instead of the code.

---

## Exercise 03: expected figures

All for 14 September. The Z-reports are in `data/raw/z_reports.csv`.

| Branch | Z-report | Starting code | After KC-101 | After KC-102 | After KC-103 |
|---|---|---|---|---|---|
| Leeds | £759.70 | £746.80 | £746.80 | **£759.70** | £759.70 |
| Manchester | £874.30 | £875.70 | £875.70 | **£874.30** | £874.30 |
| York | £651.10 | £664.70 | £664.70 | £653.30 | **£651.10** |
| Dublin | €790.85 (≈ £675.25) | £917.66 | £668.92 | £678.61 | **£675.11** |

- **Dublin (KC-101):** €790.85 ÷ 1.1712 = £675.25. The starting code shows £917.66, about 36%
  too high because the rate is applied the wrong way (1.1712² ≈ 1.37).
- **Dublin after every fix:** £675.11. The 14p gap from £675.25 is rounding, because each
  item's price is converted separately. `test_reconciliation.py` allows up to 50p.
- **York after KC-102:** still out by one item, because the till exported a corrupt row with
  no product name. KC-103 (matching to the catalogue) drops it.
- **Edinburgh on the 16th:** its Z-report says 120 transactions, 207 items and £664.00. A
  correct KC-104 implementation matches this exactly.
- **Part A's watch-out:** agents writing characterisation tests will record the Dublin bug as
  expected behaviour (`1371`p for €11.71). That's fine, as long as learners mark it `BUG?`.

---

## Exercise 04: notes

- **`.claude/settings.json`** ships on `main` with `"defaultMode": "manual"`. Learners add the
  `deny` list.
- **Deny rules:** Claude Code 2.1.x matches file rules with `Edit(...)` only, and an `Edit`
  rule covers every file-editing tool. A `Write(...)` rule is ignored, with a warning at
  startup.
- **The test hook:** the solution is `.claude/hooks/run_tests.py`.
  - It replies with JSON `{"decision": "block", "reason": ...}` rather than exiting with code
    2.
  - On Windows, the exit code from `uv run` reached Claude Code as 1 rather than 2. That was
    logged as a hook error and never shown to Claude.
  - Checked with headless `claude -p`: an edit that breaks a test produces "PostToolUse:Edit
    hook blocking error ... Tests are failing after this edit", and Claude sees it.
- **Testing the deny rule:** reading `loyalty_members.csv` with the Read tool is blocked
  ("File is in a directory that is denied by your permission settings"). A shell command could
  still read it. That gap is the permissions-versus-sandboxing discussion point.

---

## Regenerating the data

```
uv run python trainer/generate_data.py
```

The generator is seeded and reproduces `data/` byte for byte, with LF line endings. If you
change it, every figure in `TICKETS.md` and in these notes will need re-checking.
