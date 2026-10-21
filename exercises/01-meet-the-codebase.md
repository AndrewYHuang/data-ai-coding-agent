# 01: Meet the codebase

**Goal:** use Claude Code to understand code you've never seen before, and check that what it
tells you is true.

Make sure you've done the [setup](../README.md#setup) first, and that `uv run pytest` runs.

## 1. Start Claude Code

From the repo's top-level folder:

```sh
claude
```

## 2. Ask your first questions

Try these, one at a time. Read each answer properly before moving on.

1. `Describe this codebase. What does it do, and how is it structured?`
2. `Walk me through what happens to a single row from data/raw/tills/leeds_2026-09-14.csv, from
the till export all the way to the daily summary.`
3. `How are the branches' till exports different from each other?`
4. `Which files in data/ does the pipeline actually read?`
5. `How do I run the tests and the pipeline?`

## 3. Fact-check the handover note

Before leaving, Andy got an AI agent to write most of the [handover note](../HANDOVER.md) and
pasted it in unedited. It reads well and it's confident, however **Discernment** means checking.

Below are ten claims from the handover note to check. For each one, fill in a row:

| #   | What the handover note says | What's actually true | Your evidence (`file:line`, or a row of data) |
| --- | --------------------------- | -------------------- | --------------------------------------------- |

You can use your own Claude session to help you investigate, e.g. `Where is read_products
called?` or `Show me the code that converts Dublin's prices`. But **you** decide what's true,
and every row needs evidence you've seen yourself in the code or the data. "The agent said
so" doesn't count, whichever agent said it.

**Some of these claims are wrong and some are right.** "The handover note was right" is a valid
answer, as long as you have the evidence.

1. **Which tills get processed?** Is there a file in `data/raw/tills/` that the pipeline never
   reads? What would make it start reading it?
2. **Price units.** All the CSVs have a column called `unit_price`. Is it the same unit for every
   branch? How does the code know the difference?
3. **Dublin's conversion.** Take one Dublin row and that day's rate from
   `data/raw/exchange_rates/`. Work out _by hand_ the pence value the code produces. Is it
   more or less than the euro price? Should it be?
4. **Negative quantities.** The handover note and the code comments both say they're till mistakes.
   Find a few in the data. What else is in those transactions? What do you think they are?
5. **Duplicates.** What exactly does the code treat as "the same row"? Could two genuinely
   different sales match?
6. **Product names.** Is `data/reference/products.json` used to clean product names? Search for
   where any function that reads it is _called_, not just where it's defined.
7. **Bad rows.** They're "handled gracefully". What actually happens to a row with a quantity
   of `two`? How would anyone find out it had happened?
8. **UK dates.** Is `01/02/2026` from the Leeds till read as 1st February or 2nd January?
9. **Running it.** Would the handover note's commands work on your machine, as it's set up
   for this repo? Why not?
10. **The 6am email.** Can you confirm from this repo that the summary is emailed every
    morning? If not, what would you need to check?

Compare your table with another learner's. Which claims were wrong? Which were _vague_, so
that they sounded right without actually saying anything? Read the "State of things" section
again. Do you agree with it now?

Finally, compare the handover note with the answers _your_ agent gave in section 2. Where did
they disagree? Which one was right?

## 4. Find the smells

Ask: `What would you be worried about if you had to maintain this code?`

Compare its list with your own. Did it spot:

- the `except: pass` in `clean_rows` that silently throws away bad rows?
- the file in `extract.py` that's opened but never closed?
- the branch names hard-coded in several places?

Did it flag anything that you think _isn't_ actually a problem?

## Reflect

- How long would it have taken you to understand this codebase without the agent?
- How did you decide which of its claims to trust?
- Some of the handover note's mistakes match the code comments word for word. Where do you
  think the agent that wrote it was getting its information from?
- For claim 10, the right answer is "I can't tell from this repo". Did your own agent say that
  when you asked? Why is that a good answer?
- Andy pasted the agent's write-up in unedited. What should Andy have done first?
- There's a file of customer personal data in `data/raw/`. Did the agent read it while
  exploring? Would you know if it had? (We'll come back to this in exercise 04.)
