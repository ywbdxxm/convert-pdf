# Docling Workspace

This directory is the project-level Docling overlay for `convert-pdf`.

## Purpose

- keep Docling-specific Python dependencies isolated from other projects
- reuse the shared heavy AI base for `torch + CUDA`
- avoid reinstalling the heavy GPU stack per project
- respect inherited shared packages during install, so heavy torch dependencies stay in the shared base

## Expected Layout

- `.venv/`
  - project overlay venv created from the shared AI base Python
- `requirements.txt`
  - project-private dependencies

## Bootstrap

From the repository root:

```sh
./scripts/bootstrap_ai_base.sh
./scripts/bootstrap_docling_env.sh
```

## Verification

```sh
./scripts/verify_ai_stack.sh
```

## Activation

Activate only when needed:

```sh
source docling/.venv/bin/activate
```

Do not auto-activate this environment from shell startup files.
