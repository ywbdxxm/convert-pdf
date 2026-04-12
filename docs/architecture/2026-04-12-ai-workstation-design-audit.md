# AI Workstation Design Audit

Date: 2026-04-12

## Goal

Audit the current WSL-based AI workstation design for the `convert-pdf` repository, identify gaps, and lock a stable architecture that supports:

- embedded datasheet / app note parsing
- local PDF to Markdown conversion
- OCR / VLM experimentation
- future Python and AI project reuse

## Verified Current State

### Host / WSL / GPU

- Windows host is already exposing GPU into WSL
- WSL distribution: `Ubuntu 24.04.4 LTS`
- GPU path is working in WSL via `/usr/lib/wsl/lib/libcuda.so*`
- `nvidia-smi` works and reports `RTX 4060 Laptop GPU`, driver `595.79`

### Container Runtime

- Docker is installed and working
- NVIDIA container runtime is installed and registered in Docker
- GPU containers work
- Docker daemon proxy is configured

### Native Tooling

- `python3`, `pip`, `uv`, `git`, `curl`, `wget`
- build tools including `build-essential`, `cmake`, `ninja-build`
- OCR stack including `tesseract`

### Python Package Routing

- `pip` is configured to use the Tsinghua mirror
- `uv` is configured to use the Tsinghua mirror
- `micromamba` is installed
- `.condarc` is configured to use domestic mirrors for `conda-forge`, `pytorch`, and `nvidia`

## Gaps Found

### 1. Global Policy Was Not Actually Persisted

The global file [AGENTS.md](/home/qcgg/.codex/AGENTS.md) existed but was empty. That meant future sessions would not inherit the workstation rules the repository was already depending on.

### 2. Referenced Design Documents Were Missing

`task_plan.md` referenced design and plan documents under `docs/superpowers/...`, but those files do not currently exist in the repository. The design was mostly present in planning files and conversation state, not in stable repo docs.

### 3. Project Layer Was Not Materialized

The repository-level `docling/` directory existed but was empty. The architecture described project isolation, but there was no bootstrap path, no requirements file, and no verification entrypoint.

### 4. Shared Heavy AI Base Reuse Mechanism Was Not Defined

The design said "shared heavy AI base + project-level isolation", but it did not define how the project environment would reuse the shared base without reinstalling heavy packages.

### 5. Model Artifact Policy Was Missing

The design covered Python packages, but not reusable model artifacts and cache locations. For tools like Docling, this matters because model downloads can become large and should not live inside repositories by default.

### 6. Activation Policy Was Missing

The workstation design did not explicitly say how environments should be activated. Without a policy, it is easy to drift into shell auto-activation and hard-to-debug terminal behavior.

### 7. Verification Matrix Was Incomplete

There were spot checks, but no single repeatable verification flow covering:

- WSL GPU
- Docker GPU runtime
- shared AI base torch + CUDA
- Docling project overlay import path

## Final Architecture

### Layer 0: Windows Host

Responsibilities:

- NVIDIA Windows driver
- WSL integration
- host-side proxy tooling

This layer is a prerequisite but not a place for project tooling.

### Layer 1: WSL System Layer

Responsibilities:

- Docker
- NVIDIA container runtime
- WSL CUDA bridge
- native build tools
- OCR binaries

This layer should stay stable and reusable across all projects.

### Layer 2: Shared Heavy AI Base

Responsibilities:

- `python=3.12`
- `pytorch`
- `torchvision`
- `torchaudio`
- `pytorch-cuda=12.4`

Management tool:

- `micromamba`

Reason:

- better fit than `uv` for a heavy binary GPU base in this network environment

Proposed stable location:

- `~/.mamba/envs/ai-base-cu124-stable`

### Layer 3: Project Overlay Environment

Responsibilities:

- project-specific Python packages such as `docling`
- thin incremental dependencies
- local verification scripts

Management approach:

- create a project venv from the shared AI base Python
- use `--system-site-packages` so the project overlay can see the heavy shared packages
- install only project-private dependencies into the overlay, using `pip` so inherited shared packages are respected during resolution

This keeps the project isolated enough for day-to-day work while avoiding a second heavy torch download.

### Layer 4: Project Data And Outputs

Responsibilities:

- raw manuals
- converted Markdown / JSON outputs
- indexes and notes
- benchmark outputs

Suggested repository layout:

- `docling/`
- `samples/`
- `outputs/`
- `benchmarks/`
- `docs/architecture/`

### Shared Artifact Cache

Reusable model artifacts should stay outside repositories.

Suggested cache roots:

- `~/.cache/docling`
- `~/.cache/convert-pdf`

## Update Policy

- treat `ai-base-cu124-stable` as a stable baseline, not a rolling target
- do not update the heavy shared base casually
- update the shared base only when a project truly needs a newer torch / CUDA combination
- keep project overlays free to evolve faster than the base

## Activation Policy

- do not auto-source project environments from `.zshrc`, `.bashrc`, or VS Code shell hooks
- activate environments explicitly through scripts or manual commands
- prefer commands that make the active layer obvious

## Fallback Paths

### If Shared Overlay Reuse Fails

Fallback to a project-local `micromamba` environment based on the same shared baseline. This may duplicate some metadata or hardlinks, but it is still better than returning to a full `uv + CUDA wheel` reinstall path.

### If GPU Is Unavailable

Keep a CPU-only Docling path available for basic parsing and debugging. GPU is an optimization, not a hard prerequisite for repository progress.

## Recommended Next Actions

1. Materialize the missing design and execution docs
2. Persist global workstation rules in `~/.codex/AGENTS.md`
3. Add bootstrap scripts for shared AI base, project overlay, and verification
4. Create the shared AI base with `micromamba`
5. Create the `docling` overlay environment and install Docling there
6. Verify imports and GPU access end to end
