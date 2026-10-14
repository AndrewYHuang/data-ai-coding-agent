# 05 (stretch): Spec-driven development

**Goal:** write down *what* you want before the agent writes *how*, and use that spec to check
its work.

In exercise 03 you went straight from the ticket to tests. With a larger feature, it pays to
agree the behaviour in writing first.

## The feature

Head office wants a new report: **`output/product_summary_<date>.csv`**, with sales per product
per branch, using the canonical catalogue names and categories.

## 1. Write the spec (you, with the agent's help)

Create `specs/product-summary.md`. Ask Claude to interview you about the feature. Have it ask
you questions rather than guess. Your spec should answer, at least:

- What are the columns, and in what order? What format is money in?
- How are refunds counted?
- What happens to rows whose product isn't in the catalogue?
- What happens on a day with no data for a branch?
- How will we know it's correct? (Hint: what should the product totals for a branch add up to?)

Read the finished spec yourself. **Would a colleague who's never seen this repo build the same
thing from it?**

## 2. Implement against the spec

In a **new session**:

```
Implement specs/product-summary.md using TDD. Write tests for each rule in the spec first.
```

## 3. Check against the spec

Go through the spec line by line and find the test that covers each rule. Any rule
without a test is a rule nobody checked.

## Discuss

- Did writing the spec change what you asked for?
- Where did the agent's questions surface something you hadn't thought about?
- When is a spec worth the effort, and when is a ticket enough?
