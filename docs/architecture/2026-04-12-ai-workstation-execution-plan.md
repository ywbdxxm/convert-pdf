# AI Workstation Execution Plan

Date: 2026-04-12

## Objective

Execute the audited workstation design in a way that is reproducible and stable.

## Phase 1: Persist Design

- write the design audit into repository docs
- write global workstation rules into `~/.codex/AGENTS.md`
- update planning files to reflect the real current state

## Phase 2: Materialize Bootstrap Tooling

Add repository scripts for:

- shared AI base creation
- Docling project overlay creation
- end-to-end verification

## Phase 3: Build Shared Heavy AI Base

Create:

- `~/.mamba/envs/ai-base-cu124-stable`

Command shape:

```sh
micromamba create -y -n ai-base-cu124-stable --channel-priority flexible \
  python=3.12 pytorch::pytorch pytorch::torchvision pytorch::torchaudio pytorch-cuda=12.4
```

## Phase 4: Build Docling Overlay

Create:

- `docling/.venv`

Approach:

- use the shared AI base Python to create the venv
- enable `--system-site-packages`
- install only Docling and project-private packages into the overlay

## Phase 5: Verify

Check:

1. `nvidia-smi`
2. Docker GPU runtime
3. shared AI base `torch.cuda.is_available()`
4. Docling import inside `docling/.venv`

## Acceptance Criteria

- shared heavy AI base exists and imports torch
- CUDA is visible from shared AI base
- project overlay exists under `docling/.venv`
- Docling imports from the project overlay
- verification script passes end to end
