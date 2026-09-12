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

## Durable rule — Versioned directory structure + workflow state (resume across sessions)

This skill has no memory of its own between sessions — a fresh Claude Code session invoking this
skill again knows nothing about work already done unless it's written to disk. To make the
pipeline **resumable rather than silently restarted from Stage 1**, and to keep each enhancement
cycle after the initial MVP cleanly separated, every project's spec-to-product artifacts live
under a versioned directory tree, **not** as flat files at the project root:

```
<project-root>/spec-to-prod/
  versions.md               ← master index: current version, one-line label + status per version
  1-mvp/                    ← version 1 is always the initial MVP
    spec.md      spec.html
    features/*.feature
    prototype.html
    design.md    design.html
    implementation_plan.md  implementation_plan.html
    workflow_state.md
    prompts.md
  2-<slug>/                 ← version 2+ are post-MVP enhancement cycles (see Stage 10 below)
    ... same shape ...
```

Each version's folder is named `<N>-<slug>` — a leading integer (the only part any logic parses
to find "current" or "next" version, via e.g. `^(\d+)-`) plus a short, human-readable kebab-case
slug (e.g. `2-tax-optimization`) so the directory listing is self-documenting. The slug is a
mnemonic only, chosen once when the version is created and never re-derived for meaning or
re-parsed — `versions.md`'s label column is the authoritative description, and the slug is
allowed to go slightly stale if a version's scope shifts after naming.

Every path referenced elsewhere in this document (`spec.md`, `features/*.feature`,
`prototype.html`, `design.md`, `implementation_plan.md`) means that file **inside the current
version's folder** — `spec-to-prod/<N>-<slug>/spec.md`, etc. — never a flat file at the project
root.

**On every invocation of this skill, before doing anything else**: check whether
`spec-to-prod/versions.md` already exists in the target project directory.
- **If it exists**: read it to find the current version's folder name, then read that version's
  `workflow_state.md` for its exact stage/gate status. Report this to the user and **resume from
  there** — do not restart Stage 1, do not re-draft `spec.md` from scratch, and do not treat the
  invocation's argument as a brand-new idea unless the user explicitly says they want to start
  over (or is clearly asking for a new enhancement — see Stage 10). Read the actual stage-output
  files for their real content; `workflow_state.md` and `versions.md` only track *where things
  stand*, they never duplicate deliverable content.
- **If it doesn't exist**: this is a new project. Create `spec-to-prod/versions.md` and
  `spec-to-prod/1-mvp/workflow_state.md` as the very first action, before drafting anything else,
  seeded with the idea and Stage 1 marked in-progress.

**Update the current version's `workflow_state.md` (and `versions.md`'s status column)
immediately after every meaningful step** — write-through, not batched at the end of a turn:
starting a stage, finishing a stage, an approval gate being approved or sent back for changes, and
any edit to a stage-output file.

**`workflow_state.md` format** — short and scannable, not a duplicate of the deliverables
themselves:

```markdown
# Workflow State — <project/idea name> (version <N>-<slug>)

- Idea / enhancement: <one-line>
- Started: <date>
- Last updated: <date>

## Stages

| Stage | Status | Output(s) |
|---|---|---|
| 1 — Spec + NFRs | done / in progress / not started | spec.md |
| 2 — Gherkin scenarios | ... | features/*.feature |
| 3 — Interactive prototype | ... | prototype.html |
| Gate 1 | pending / approved \<date\> / changes requested \<date\> | |
| 4 — Design document | ... | design.md |
| Gate 2 | ... | |
| 5 — Implementation plan | ... | implementation_plan.md |
| Gate 3 | ... | |
| 6 — Implement | ... | |
| 7 — Verify tests per increment | ... | |
| 8 — Full test suite | ... | |
| 9 — Ready for product testing | ... | |

## Current position
<1-2 sentences: what's actively being worked, what's pending>

## Next action
<1 sentence: the very next concrete thing to do or ask>
```

Neither `workflow_state.md` nor `versions.md` is a deliverable presented for approval — unlike
`spec.md`/`design.md`/`implementation_plan.md`, they are never rendered to HTML, just kept
accurate and current.

## Durable rule — Raw prompt logging

Append every user message verbatim to the current version's `prompts.md` (inside
`spec-to-prod/<N>-<slug>/`) **before** taking any other action in response to it — including a
mid-turn message that arrives while another action is already in flight. Number entries
sequentially, quoted verbatim, so `prompts.md` is a complete provenance trail of what was actually
asked versus what was inferred or assumed. A new version starts a fresh `prompts.md` rather than
appending to a prior version's log.

## Durable rule — HTML rendering of every markdown deliverable

For every markdown deliverable this workflow produces or edits — `spec.md`, `design.md`,
`implementation_plan.md` (not the `.feature` files or `prototype.html`, which are already meant
to be read as-is), each inside the current version's `spec-to-prod/<N>-<slug>/` folder — keep a
same-named `.html` rendition next to it (e.g. `spec.md` → `spec.html`), and keep it open in
Chrome:

- **Use `render_md.py`** (lives next to this SKILL.md, in the skill's own directory) to do this:
  `python3 <skill-dir>/render_md.py path/to/spec-to-prod/<N>-<slug>/spec.md` — it renders a styled HTML
  page (real typographic hierarchy, not a raw markdown dump; `(assumed — ...)` / `(open — ...)`
  markers get their own visual treatment) to the same path with a `.html` extension, and opens it
  in Chrome (`--no-open` to skip the open step; requires `pip install markdown`). Don't hand-roll
  bespoke HTML per document — extend the script if the rendering needs to change, so every
  deliverable stays consistent.
- **On first creation of the doc**: run the script.
- **On every subsequent edit to the `.md` file** — during Stage 1's conversational iteration, a
  Stage 4 design revision, or a Stage 5 plan revision — run the script again immediately, in the
  same turn as the edit, before moving on to anything else, so the visible page never lags behind
  the source of truth.
- The `.md` file is still the actual source of truth being negotiated/approved at each gate —
  the `.html` file is a read-only rendering of it, never edited directly.

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

## Stage 10 — Post-MVP Enhancement Cycles

Once a version reaches Stage 9, the pipeline for that version is done — but the project isn't
over. When the user comes back with a new feature request, a change, or an addition, **don't**
edit version 1's files in place and don't treat it as a brand-new project either. Instead:

- **Open a new version**: create `spec-to-prod/<N+1>-<slug>/` (next integer after the highest
  existing version's leading number, plus a short new slug describing this enhancement), add a
  row for it in `versions.md`, and set it as the current version.
- **Amend, don't restart, the living documents**: `spec.md` for the new version starts as a copy
  of the prior version's `spec.md` with the new module/story/AC *appended* (or an existing section
  revised), not a fresh document — same for `features/`, and for the prototype (copy forward, then
  edit only what the enhancement touches). Never re-litigate or re-derive parts of the product the
  enhancement doesn't touch.
- **Same three gates, scoped to the delta**: Gate 1 asks the user to approve the *addition* to the
  spec/scenarios/prototype, not a re-review of the whole product; likewise for Gates 2 and 3 against
  the new version's `design.md`/`implementation_plan.md`.
- **Size the ceremony to the change**: a small, well-understood addition can move through the gates
  quickly with a short delta review; a large, module-sized enhancement deserves the same full
  rigor as the original MVP. Use judgment, but don't skip a gate just because the change feels
  small — ask the user if unsure.
- Stages 6-9 for the new version implement, test, and ship only the delta — the existing MVP code
  is the starting point, not something rebuilt.
