# Spec → Product Copilot

A reusable AI-assistant workflow that turns a rough feature idea into real, tested code through a
staged, human-approved pipeline:

```
Idea → Spec + NFRs (conversational) → Gherkin scenarios → Interactive HTML prototype →
  [approval] → Design Document → [approval] → Implementation Plan
  (TDD-first, BDD-first, API-first, Clean Code, SOLID, DRY) → [approval] →
  Implement → Verify Tests (per increment) → Full Test Suite → Ready for Product Testing →
  Post-MVP Enhancement Cycles (each one repeats the pipeline, scoped to its own delta)
```

No stage skips ahead without an explicit human approval. Every stage's output lives under a
versioned directory (`spec-to-prod/<N>-<slug>/` — version 1 is the initial MVP, version 2+ are later
enhancement cycles) tracked by a top-level `spec-to-prod/versions.md` and a per-version
`workflow_state.md`, so the pipeline resumes exactly where it left off in a brand-new session
instead of restarting from Stage 1. The same workflow content is packaged three ways, for
whichever AI coding tool you use:

| Tool | File | Install |
|---|---|---|
| **Claude Code** | [`claude-code/spec-to-product/SKILL.md`](claude-code/spec-to-product/SKILL.md) | Copy the `spec-to-product/` folder into `~/.claude/skills/` (all your projects) or `<project>/.claude/skills/` (that project only). Invoke with `/spec-to-product <your rough idea>`. |
| **GitHub Copilot** | [`github-copilot/spec-to-product-instructions.md`](github-copilot/spec-to-product-instructions.md) | Paste the contents into your repo's `.github/copilot-instructions.md` (or a `.github/prompts/` prompt file, if your Copilot setup supports those). Copilot has no dedicated skill-package format, so this is standing instructions rather than an invokable command. |
| **Any other AI coding tool** | [`generic-playbook.md`](generic-playbook.md) | Paste into whatever custom-instructions / rules / system-prompt mechanism your tool supports (Cursor `.cursorrules`, Windsurf rules, a custom GPT's instructions, etc.). Assumes only file read/write and running a test command. |

All three describe the identical ten-stage pipeline — pick the packaging that matches your tool,
not a different workflow.

## Why staged, human-approved generation

Letting an AI assistant go straight from "build me X" to a pile of code skips the two things that
actually determine whether the result is *right*: agreeing what "right" means (the spec, including
the non-functional requirements people usually forget to state), and agreeing *how* it'll be
built (the design and implementation plan) before code exists to be un-done. This workflow forces
both checkpoints, plus a cheap, fast prototype to catch UI misunderstandings before the design
doc — and the implementation plan itself is only worth reviewing because it commits to
TDD/BDD/API-first/Clean Code/SOLID/DRY discipline for every increment, not just "eventually add
tests."
