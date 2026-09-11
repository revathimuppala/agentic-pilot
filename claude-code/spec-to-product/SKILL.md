---
name: spec-to-product
description: Turns a rough feature idea into a fully specified, designed, and implemented feature through a staged, human-approved pipeline — a functional spec with non-functional requirements, Gherkin scenarios, an interactive HTML prototype, a design document, and a TDD/BDD/API-first implementation plan — each stage gated by your explicit approval before moving on, ending in real, tested code.
when_to_use: Use when the user wants to build a new feature or project from a rough idea and wants a structured, reviewable path from requirements through to tested code, rather than jumping straight to writing code.
disable-model-invocation: true
argument-hint: "[a rough description of the feature or product idea]"
---

# Spec → Product Copilot

A staged pipeline from a rough idea to real, tested code. **Every stage marked "STOP" is a hard
gate — do not proceed past it without an explicit approval from the user in this conversation.**
Never skip a gate because the user seems in a hurry, or because a stage's output "seems obviously
fine" — the entire point of this workflow is the discipline of staged review, not speed.

The idea to build is: $ARGUMENTS

If no argument was given, use the rough idea from the most recent message in this conversation.
If the idea is too vague to draft even a first-pass spec (e.g. one sentence with no clear user or
problem), ask 1-2 sharp clarifying questions before drafting anything — but don't over-ask; a
rough idea is expected to be rough.

## Stage 1 — Spec + Non-Functional Requirements (conversational)

Draft a first-pass structured spec as a `spec.md` file with these sections:

- **Problem Statement** — what's broken or missing, for whom.
- **Goals** — what success looks like.
- **Non-Goals / Out of Scope** — explicitly excluded, so scope doesn't silently creep later.
- **User Stories** — as "As a ___, I want ___, so that ___."
- **Acceptance Criteria** — concrete, testable, one set per user story.
- **Non-Functional Requirements** — performance targets, expected scale/concurrency, security or
  compliance needs, availability expectations, accessibility, browser/device support. **Actively
  ask about these if the user hasn't stated them** — don't silently invent numbers. Where you do
  assume a reasonable default, mark it clearly as `(assumed — confirm)` rather than presenting it
  as given.

Present the draft to the user and refine conversationally — the user will say things like
"tighten this acceptance criterion" or "add an edge case for X"; keep iterating on `spec.md`
until they say it's ready to move on. This stage has no formal approval gate of its own (it *is*
the negotiation) — the first hard gate comes after the next two stages.

## Stage 2 — Gherkin Feature Scenarios

From the finalized user stories and acceptance criteria, write Gherkin `Given/When/Then`
scenarios covering every acceptance criterion, plus edge cases implied by the NFRs (e.g. a stated
concurrency NFR should produce a scenario about concurrent access, not just the happy path).
Save as one or more `.feature` files.

## Stage 3 — Interactive HTML Prototype

Generate a single self-contained `prototype.html` (inline CSS/JS, no build step, no real backend)
mocking the key screens implied by the spec, with click-through navigation between them — enough
for the user to sanity-check the UI direction before design work starts. Tell the user they can
open it directly in a browser.

### STOP — Approval Gate 1

Present `spec.md`, the `.feature` files, and `prototype.html` together and ask explicitly:
**"Do you approve this spec, these scenarios, and this prototype, so I can move on to the design
document?"** Wait for an explicit yes. If the user requests changes, go back to Stage 1 with
their feedback — keep the existing spec and chat history rather than starting over.

## Stage 4 — Design Document

From the approved spec, scenarios, and prototype, write `design.md`: architecture overview, data
model, API design (endpoints/contracts, request/response shapes), and the tech/library choices,
with reasoning. **Explicitly address every NFR from Stage 1 by name** — a stated concurrency or
security requirement must visibly shape a decision here, not be silently dropped.

### STOP — Approval Gate 2

Present `design.md` and ask explicitly: **"Do you approve this design so I can move on to the
implementation plan?"** Wait for an explicit yes. If the user requests changes, revise
`design.md` and ask again — don't proceed until approved.

## Stage 5 — Implementation Plan

From the approved design document, write `implementation_plan.md`: a step-by-step plan broken
into small, independently reviewable increments. The plan **must** be:

- **TDD-first** — every increment writes the test before the implementation, not after.
- **BDD-first** — the Gherkin scenarios from Stage 2 drive the acceptance/integration tests, not
  an afterthought bolted on at the end.
- **API-first** — define and agree the API contract for a piece of functionality before wiring
  any UI to it.
- Following **Clean Code**, **SOLID**, and **DRY** throughout — call out where the plan
  deliberately avoids a premature abstraction, not just where it adds one.

### STOP — Approval Gate 3

Present `implementation_plan.md` and ask explicitly: **"Do you approve this implementation plan
so I can start building?"** Wait for an explicit yes. If the user requests changes, revise the
plan and ask again.

## Stage 6 — Implement

Follow the approved plan increment by increment: write the failing test first, then the minimal
implementation to pass it, refactor if needed, then move to the next increment. Report progress
briefly after each increment rather than going silent until everything is done.

## Stage 7 — Verify Tests (per increment)

Run the real test suite after each increment as it lands — this is standard TDD practice, not a
step deferred to the end. If a test fails, fix it before moving to the next increment.

## Stage 8 — Full Test Suite

Once every increment from the plan is implemented, run the **entire** test suite (not just the
tests added this session) to catch regressions, and report a clear pass/fail summary — counts,
and the full output for anything that failed.

## Stage 9 — Ready for Product Testing

Summarize what was built (changed/added files), confirm the full suite is green, and hand back to
the user explicitly: **"This is ready for your review as the product owner."** Do not describe it
as fully done or shipped — that call belongs to the user.
