# 04: Context and guards

**Goal:** give the agent the knowledge it can't work out from the code, and add rules that
are enforced _every_ time, not just when the agent remembers.

Work on a new branch: `exercise-04`.

## 1. AGENTS.md

`AGENTS.md` is a file coding agents read at the start of every session. It's where you put
what a new team member would need to be told. It's a shared convention that many coding
agents read, so the same file works whichever tool your team uses.

Write this file yourself, rather than using `/init`.

<details>
<summary>What does <code>/init</code> do, and why not use it?</summary>

`/init` is a command that explores the repo and writes a first version of the
file for you. It usually lists the folder structure, the main modules, how to install and
how to run the tests.

It's quick, but it isn't best practice:

- **It only knows what's in the code.** Almost everything it writes is something the agent
  could work out by reading the code anyway. The things you most need to say, like the
  business rules and the mistakes to avoid, aren't in the code, so it can't write them.
- **It costs context every session.** Every line is loaded into every session, whether the
  task needs it or not. A long generated file leaves less room for the actual work.
- **It buries what matters.** The few important rules get lost among the obvious ones, and
  the agent is less likely to follow them.
- **It goes stale.** A list of files and modules is out of date the next time someone
  refactors, and a file that's wrong is worse than no file.

A short, hand-written file that only holds what the code can't tell the agent does a better
job.

</details>

1. Write `AGENTS.md` by hand. Only include the things the code _can't_ tell the agent. Some
   ideas:
   - "Use `uv run` for all Python commands (`uv run pytest`, `uv run python ...`). Never `pip install`."
   - "UK till dates are day first (DD/MM/YYYY)."
   - "Money is held as integer pence, never floats."
   - "Never modify anything in `data/raw/`. It's the source of truth from the tills."
   - "Run `uv run pytest` before every commit."
2. **Review it like any other code.** For each line, ask: would the agent get this wrong
   without it? If not, delete it.
3. Start a **new** Claude session (`/clear`) and ask the same question as in exercise 01:
   `How do I run the tests?` Did the answer (or time to get the answer) change?

Keep it short. Every line in `AGENTS.md` takes up context in every session.

## 2. A skill

A **skill** is a set of instructions for a particular _kind_ of task. Claude loads it only
when the task matches, so unlike `AGENTS.md`, it doesn't cost context in every session.

You've just added a new till format (Edinburgh). Kettle & Crumb will open more branches.

1. Ask Claude to help you write a skill in `.claude/skills/add-till-format/SKILL.md`, based on
   what you learned in exercise 03 section 3. It should describe the steps, which files to touch
   and which tests to write.
2. Test it. Start a new session and say: `A Glasgow branch is opening with the same till as
Leeds. Add it.` Did Claude use the skill? Did it follow the steps?

## 3. Deterministic guards

`AGENTS.md` is a _request_. The agent usually follows it, but not always. For rules that
must **never** be broken, use something that runs every time, whatever the agent "decides".

### Permissions: protect the raw data and personal data

The repo already has a `.claude/settings.json`, which makes Claude start in manual mode. Add a
`deny` list to it:

```json
{
  "permissions": {
    "defaultMode": "manual",
    "deny": ["Edit(./data/raw/**)", "Read(./data/raw/loyalty_members.csv)"]
  }
}
```

An `Edit(...)` rule covers every tool that changes files, including creating them, so you
don't need a separate rule for writing.

Start a new session and **test the guard**:

- `Add a blank line to the end of data/raw/tills/leeds_2026-09-14.csv`
- `How many loyalty members are there in each branch?`

What happens? Could the agent get round it some other way, e.g. by running a shell command
that reads the file? What does that tell you about the difference between _permissions_ and
_sandboxing_?

### A hook: always run the tests

A **hook** is a command that Claude Code runs automatically at a set point, e.g. after every
file edit. Ask Claude to help you add a hook to `.claude/settings.json` that runs
`uv run pytest -q` after each edit to a Python file, and feeds any failures back to the agent.
(You can also look at the `/hooks` command.)

**Test the guard:** ask Claude to make a change that breaks a test, and check that the hook
catches it.

## Reflect

- What belongs in `AGENTS.md`, in a skill, and in a guard?
  - Is there anything you can remove from the `AGENTS.md` you created earlier?
- Someone on your team says, "We don't need tests, we've told the agent to be careful in
  AGENTS.md." What do you say to them?
- Should `.claude/settings.json` be committed to git? What about `.claude/settings.local.json`?
