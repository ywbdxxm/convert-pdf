# docs/skills/ — archive of global Claude Code configuration

This directory is a **read-only archive** (mirror) of files that live in the user's global Claude Code config:

| Archive path | Live path | Purpose |
|---|---|---|
| `CLAUDE.global.md` | `~/.claude/CLAUDE.md` | Global user-level entry-point directing Claude to the relevant skill per task category |
| `using-manual-bundles/SKILL.md` | `~/.claude/skills/using-manual-bundles/SKILL.md` | Skill: how to consume `manuals/processed/docling_bundle/<doc_id>/` (this project's primary deliverable) |
| `ai-workstation-architecture/SKILL.md` | `~/.claude/skills/ai-workstation-architecture/SKILL.md` | Skill: portable 6-layer architecture for any Linux / WSL / GPU AI workstation — Python / venv / uv / micromamba / torch / CUDA / Docker / mirrors / caches. Architecture + hard rules travel; env names / paths / mirror URLs are per-host and must be re-anchored. |

## Why it's archived here

The global config files are outside the project directory (`~/.claude/`), so they don't get committed with this repo's history. Keeping a copy inside the project repo:

1. Documents what the skill + CLAUDE.md contains at the time of the project report (Phase 60)
2. Lets anyone cloning the project see exactly how the bundle is meant to be consumed by Claude Code
3. Provides a reference for reinstalling the skill on a new machine (copy into `~/.claude/skills/`)

## Deploy to a new machine

```sh
mkdir -p ~/.claude/skills/using-manual-bundles ~/.claude/skills/ai-workstation-architecture
cp docs/skills/using-manual-bundles/SKILL.md ~/.claude/skills/using-manual-bundles/SKILL.md
cp docs/skills/ai-workstation-architecture/SKILL.md ~/.claude/skills/ai-workstation-architecture/SKILL.md
cp docs/skills/CLAUDE.global.md ~/.claude/CLAUDE.md   # or merge into existing
```

> `ai-workstation-architecture` is **machine-portable**: the 6-layer architecture, tool-to-layer mapping, hard rules, and known pitfalls apply to any Linux / WSL / GPU host. The re-anchor commands at the top of the skill discover per-host values (base env path, mirror config, driver / CUDA version) on entry. Deploy it on any machine; nothing in the skill is hardcoded to one box.

## Testing the skill (TDD-for-skills, see superpowers:writing-skills)

**Baseline (RED)** — ask the question without the skill active:

> "I'm doing embedded development with ESP32-S3. What function does GPIO14 serve by default after reset, and cite your source?"

Without the skill, the agent typically ignores `manuals/processed/docling_bundle/`, falls back to external Espressif MCP / training data, and cites a URL.

**With skill (GREEN)** — same question after `~/.claude/skills/using-manual-bundles/SKILL.md` is loaded:

The agent should:
1. `ls manuals/processed/docling_bundle/` first
2. Read the bundle README
3. Check `alerts.json` before citing
4. Cite `doc_id p.X + chunk_id/table_id` + path to raw PDF

Both behaviors were verified for this skill on 2026-04-19 (see project git log around the skill-creation commit).
