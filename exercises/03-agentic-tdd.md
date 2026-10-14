# 03: Agentic TDD: characterise, fix, extend

**Goal:** use test-driven development to keep an agent honest. Pin down what the code does
now, then fix a bug, then add a feature, with a test written first every time.

Work on a new branch: `exercise-03`.

Use the loop from the presentation for each part: **Explore → Plan → Code → Commit**.

---

## Part A: characterisation tests

Before changing code you don't understand, write tests that record **what it does today**.
These are *characterisation tests*. They don't say the behaviour is right, but they warn you
when you change it by accident.

1. Ask Claude to write characterisation tests for `clean_rows` and `build_summary`. Ask for
   small, hand-written input rows in the tests (not the real data files), so that each test
   is easy to read.
2. **Review every test it writes.** For each one, can you work out the expected value by
   hand? If not, ask Claude to simplify it.
3. Run them: `uv run pytest`. Commit.

> **Watch out.** An agent writing tests against existing code will happily record *bugs* as
> "expected behaviour". Look at the Dublin tests it wrote. Does the expected GBP value look
> right to you? Look at the tests for a negative quantity. Is that what *should* happen?
> Characterisation tests are fine as a snapshot, but you should know which of them are
> recording bugs. Mark those with a comment such as `# BUG? see KC-101`.

---

## Part B: fix a bug (ticket KC-101)

Read [KC-101 in TICKETS.md](../TICKETS.md).

1. **Explore:** ask Claude to investigate. Before it touches any code, work out for yourself
   what Dublin's revenue *should* be on the 14th, using the Z-report and the exchange rate
   file. (A calculator is fine.)
2. **Red:** ask for a failing test that shows the bug, using a tiny example you can check by
   hand (e.g. one €11.71 item at a rate of 1.1712 should be £10.00). Run it and **see it
   fail**. If it passes, it isn't testing the bug.
3. **Green:** ask for the smallest fix that makes it pass. Your characterisation test from
   Part A should now fail too, so update it. That's exactly the warning it was there to give.
4. **Check:** run the pipeline for the 14th and compare Dublin with your hand calculation.
5. Commit, mentioning `KC-101` in the message.

Is Dublin now *exactly* right? If not, why not? (See KC-102.)

---

## Part C: add a feature (ticket KC-104)

Read [KC-104](../TICKETS.md). Edinburgh's till exports JSON Lines and uses SKUs.

1. **Explore:** ask Claude to compare the Edinburgh file with the CSV exports and the product
   catalogue. What's different?
2. **Plan:** use plan mode. Ask for a plan that's driven by tests. Push back if the plan:
   - copies and pastes the CSV logic instead of reusing it
   - has no test for "no Edinburgh file on the 14th"
   - changes how the other branches are processed
3. **Code:** for each step, write a test first and see it fail, then implement.
4. **Check:** run the pipeline for the 14th (no Edinburgh file) and the 16th. Compare
   Edinburgh's figures with `data/raw/z_reports.csv`.
5. Commit, mentioning `KC-104`.

---

## Stretch

- **KC-102:** the totals still don't reconcile. There are (at least) two more bugs. Find
  them, test-first. Hint: what does `abs()` do to a refund? What does the de-duplication key
  consider "the same row"?
- **KC-103:** make `clean_rows` use your exercise 02 helpers, including
  `normalise_product_name`. What should happen to rows whose product doesn't match the
  catalogue?
- Write a test that runs the whole pipeline and checks every branch against the Z-reports.

## Discuss

- When did the agent write a test that was wrong? How did you catch it?
- Did seeing the test fail first ever save you?
- Who is accountable for the Dublin numbers that went to head office?
