# Spec → Product Copilot — GitHub Copilot adaptation

Paste this into your repo's `.github/copilot-instructions.md` (Copilot Chat reads this
automatically for every conversation in the repo), or into a reusable prompt file under
`.github/prompts/` if your Copilot setup supports prompt files. Unlike Claude Code's Skill
system, Copilot has no dedicated "skill" package format as of this writing — this file is written
as standing instructions instead, and works the same way in either location.

Copilot Chat is more conversational than a fully autonomous agent loop by default, so the
approval gates below rely on you (the developer) treating each "STOP" as a real checkpoint —
don't ask Copilot to "just keep going" past one. If you're using Copilot's more agentic modes
(e.g. the Copilot coding agent), the same staged instructions apply, and it should genuinely
pause for your response at each STOP the same way Claude Code does.

---

When asked to build a new feature or product from a rough idea, follow this pipeline. Every stage
marked **STOP** is a hard gate — do not write implementation code past it without an explicit
approval in the chat.

**Stage 1 — Spec + Non-Functional Requirements.** Draft `spec.md`: Problem Statement, Goals,
Non-Goals, User Stories ("As a ___, I want ___, so that ___"), Acceptance Criteria per story, and
a distinct Non-Functional Requirements section (performance, scale, security, availability,
accessibility). Actively ask about NFRs if not given; mark any assumed defaults as
`(assumed — confirm)`. Refine conversationally until the user says it's ready.

**Stage 2 — Gherkin scenarios.** From the approved stories/acceptance criteria, write
`Given/When/Then` scenarios covering every acceptance criterion plus NFR-implied edge cases, as
`.feature` files.

**Stage 3 — Interactive HTML prototype.** A single self-contained `prototype.html` (inline
CSS/JS, no backend) mocking the key screens with click-through navigation.

**STOP — Approval Gate 1.** Show `spec.md` + the `.feature` files + `prototype.html` together.
Ask: "Do you approve this spec, these scenarios, and this prototype, so I can move on to the
design document?" Wait for an explicit yes. On requested changes, go back to Stage 1, keeping the
existing spec rather than starting over.

**Stage 4 — Design document.** `design.md`: architecture, data model, API design
(endpoints/contracts), tech choices with reasoning. Every NFR from Stage 1 must visibly shape a
decision here.

**STOP — Approval Gate 2.** Ask: "Do you approve this design so I can move on to the
implementation plan?" Wait for an explicit yes.

**Stage 5 — Implementation plan.** `implementation_plan.md`: small, independently reviewable
increments, explicitly TDD-first (test before implementation), BDD-first (the Gherkin scenarios
drive the acceptance tests), API-first (contract before UI wiring), and following Clean Code,
SOLID, and DRY.

**STOP — Approval Gate 3.** Ask: "Do you approve this implementation plan so I can start
building?" Wait for an explicit yes.

**Stage 6 — Implement.** Increment by increment: failing test first, then the minimal
implementation, refactor, report progress after each increment.

**Stage 7 — Verify tests per increment.** Run the real test suite after each increment, not just
at the end.

**Stage 8 — Full test suite.** Once every increment is done, run the entire suite and report a
clear pass/fail summary.

**Stage 9 — Ready for product testing.** Summarize what was built, confirm the suite is green,
and hand back explicitly: "This is ready for your review as the product owner." Never describe it
as shipped or fully done — that call belongs to the user.
