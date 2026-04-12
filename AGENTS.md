# Repository Guidance

## Planning With Files

For complex tasks with 3+ steps, research, or longer implementation work:

1. Read `~/.codex/skills/planning-with-files/SKILL.md`
2. Create or maintain `task_plan.md`, `findings.md`, and `progress.md` in the project root
3. Keep those files updated throughout the task

## Workstation Architecture Principles

This repository assumes a **steady-state workstation** design, not ad hoc per-project environment setup.

### Layer 1: WSL System Layer

Use system-level installation only for reusable host infrastructure:

- WSL base OS tooling
- Docker Engine
- NVIDIA Container Toolkit / container runtime
- CUDA bridge/runtime exposed by WSL
- compilers and common build tools
- OCR binaries and similar cross-project tools

These belong at the machine level because they are reused across projects.

### Layer 2: Shared Heavy AI Base

Prefer a **single shared heavy AI base** for large, stable, high-reuse dependencies.

Examples:

- `torch`
- CUDA-related Python runtime wheels
- other very large core AI dependencies that would be painful to redownload and reinstall per project

Do **not** design multiple shared base environments that each duplicate `torch + CUDA`.

### Layer 3: Project-Level Environments

Each repository or tool area should keep its own lightweight, isolated environment for project-specific dependencies.

Examples:

- `docling`
- `mineru`
- parser-specific SDKs
- project-specific Python libraries

Project environments should reuse the workstation's system layer and, where appropriate, the shared heavy AI base strategy. They should avoid re-solving heavyweight dependencies from scratch unless there is a clear reason.

## Environment Decision Rule

Before installing anything, classify it as one of:

1. **System-level reusable host infrastructure**
2. **Shared heavy AI base dependency**
3. **Project-private dependency**

Prefer the highest reusable layer that does **not** create version-conflict risk.

## Directory Layout Preference

Project work areas should live directly under the repository root when practical.

Example:

- `docling/`

Avoid adding an extra wrapper directory like `exploration/` unless there is a clear structural benefit.

## Package Mirror Policy

In this WSL environment, prefer Chinese mainland mirrors for large package downloads when practical.

- `pip` / `uv`: prefer a domestic PyPI mirror
- `conda` / `micromamba`: prefer domestic Anaconda mirrors that actually cover the required channels
- Mixed domestic mirrors are acceptable if a single mirror does not fully cover channels like `pytorch` or `nvidia`

If a heavy install fails midway:

1. Stop the unfinished install process
2. Clear partial environments and download caches
3. Validate mirror configuration with a dry-run
4. Only then retry the real install

## Activation Policy

Do not auto-activate project environments from shell startup files.

Prefer explicit activation through project scripts or one-off commands so new shells stay predictable.

## Shared Artifact Policy

Reusable model downloads and large caches should live outside the repository unless there is a strong reason not to.

Prefer shared cache roots such as:

- `~/.cache/docling`
- `~/.cache/convert-pdf`
