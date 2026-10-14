# 04: Context and guards

**Goal:** give the agent the knowledge it can't work out from the code, and add rules that
are enforced *every* time, not just when the agent remembers.

Work on a new branch: `exercise-04`.

---

## Part A: CLAUDE.md

`CLAUDE.md` is a file Claude Code reads at the start of every session. It's where you put
what a new team member would need to be told.

1. Run `/init` inside Claude Code. It explores the repo and writes a first `CLAUDE.md`.
2. **Review it like any other code.** Is it accurate? Is anything important missing? Is
   there anything you could delete because the agent could work it out from the code anyway?
3. Add the things the code *can't* tell it. Some ideas:
   - "Use `uv run` for all Python commands (`uv run pytest`, `uv run python ...`). Never `pip install`."
   - "UK till dates are day first (DD/MM/YYYY)."
   - "Money is held as integer pence, never floats."
   - "Never modify anything in `data/raw/`. It's the source of truth from the tills."
   - "Run `uv run pytest` before every commit."
4. Start a **new** Claude session (`/clear`) and ask the same question as in exercise 01:
   `How do I run the tests?` Did the answer change?

Keep it short. Every line in `CLAUDE.md` takes up context in every session.

---

## Part B: a skill

A **skill** is a set of instructions for a particular *kind* of task. Claude loads it only
when the task matches, so unlike `CLAUDE.md`, it doesn't cost context in every session.

You've just added a new till format (Edinburgh). Kettle & Crumb will open more branches.

1. Ask Claude to help you write a skill in `.claude/skills/add-till-format/SKILL.md`, based on
   what you learned in exercise 03 part C. It should describe the steps, which files to touch
   and which tests to write.
2. Test it. Start a new session and say: `A Glasgow branch is opening with the same till as
   Leeds. Add it.` Did Claude use the skill? Did it follow the steps?

---

## Part C: deterministic guards

`CLAUDE.md` is a *request*. The agent usually follows it, but not always. For rules that
must **never** be broken, use something that runs every time, whatever the agent "decides".

### Permissions: protect the raw data and personal data

Create `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Edit(./data/raw/**)",
      "Write(./data/raw/**)",
      "Read(./data/raw/loyalty_members.csv)"
    ]
  }
}
```

Start a new session and **test the guard**:

- `Add a blank line to the end of data/raw/tills/leeds_2026-09-14.csv`
- `How many loyalty members are there in each branch?`

What happens? Could the agent get round it some other way, e.g. by running a shell command
that reads the file? What does that tell you about the difference between *permissions* and
*sandboxing*?

### A hook: always run the tests

A **hook** is a command that Claude Code runs automatically at a set point, e.g. after every
file edit. Ask Claude to help you add a hook to `.claude/settings.json` that runs
`uv run pytest -q` after each edit to a Python file, and feeds any failures back to the agent.
(You can also look at the `/hooks` command.)

**Test the guard:** ask Claude to make a change that breaks a test, and check that the hook
catches it.

---

## Discuss

- Which rules belong in `CLAUDE.md`, which in a skill, and which in a guard?
- Someone on your team says, "We don't need tests, we've told the agent to be careful in
  CLAUDE.md." What do you say to them?
- Should `.claude/settings.json` be committed to git? What about `.claude/settings.local.json`?
