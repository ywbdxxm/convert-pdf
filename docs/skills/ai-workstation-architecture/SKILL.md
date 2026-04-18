---
name: ai-workstation-architecture
description: Use when configuring, installing, debugging, or verifying an AI Python environment on any Linux / WSL / GPU workstation — venv / uv / micromamba / conda / pip, PyTorch / CUDA / NVIDIA driver, Docker / NVIDIA Container Toolkit, mirror config, model cache layout, shell init / activation — before running any install, activate, or config edit that might cross layer boundaries.
---

# AI Workstation Architecture

## Overview

Any AI-capable Linux / WSL workstation with a GPU should follow a **layered architecture**: every tool, package, and cache belongs to **exactly one** of six layers. Mixing layers — installing `torch` into system Python, duplicating heavy bases per project, auto-activating venvs from `~/.bashrc` — is the dominant failure mode, and every pitfall in this skill has been observed in practice. **Reuse shared heavy infrastructure. Keep project overlays thin. Verify before assuming.**

**This skill is machine-portable.** The architecture, hard rules, and pitfalls apply to any host. What varies per host: the exact base-env name, the overlay path, the installed tool / driver / package versions. Re-anchor those on entry — never trust a memory or an old planning note without verifying against the live filesystem. **Default network posture: domestic (mainland-China) mirrors for every channel that supports one** (see Mirror Policy).

## Re-anchor On Entry (run first, before any install)

```bash
# GPU + driver (layer 0 / 1)
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || echo "no NVIDIA GPU visible"

# Container runtime (layer 1)
docker version --format '{{.Server.Version}}' 2>/dev/null || echo "docker: not installed"

# Candidate shared heavy bases (layer 2)
ls "${MAMBA_ROOT_PREFIX:-$HOME/.mamba}/envs/" 2>/dev/null
ls "${HOME}/miniconda3/envs/" "${HOME}/anaconda3/envs/" 2>/dev/null

# Base python + torch + CUDA (replace <BASE_ENV> with the env path you pick)
# <BASE_ENV>/bin/python -c 'import sys,torch;print(sys.version.split()[0], torch.__version__, torch.version.cuda, torch.cuda.is_available())'

# Mirror config — confirm domestic mirrors are already swapped in
cat ~/.config/pip/pip.conf 2>/dev/null
cat ~/.config/uv/uv.toml 2>/dev/null
cat ~/.condarc 2>/dev/null
echo "HF_ENDPOINT=${HF_ENDPOINT:-<unset — upstream HuggingFace>}"
cat /etc/docker/daemon.json 2>/dev/null | grep -i registry-mirror || echo "docker registry-mirrors: not set"

# Current project overlay (layer 3), if any
[ -f ./.venv/pyvenv.cfg ] && head -5 ./.venv/pyvenv.cfg
```

If any output surprises you, the assumption was stale. Trust the live filesystem, not memory.

## When to Use

**Triggers:**

- Any `pip install` / `uv add` / `uv pip install` / `micromamba install` / `conda install` about to run
- Creating / removing / activating a Python env (`python -m venv`, `uv init`, `uv venv`, `micromamba create`, `conda create`)
- Installing or diagnosing `torch`, `transformers`, `vllm`, `bitsandbytes`, `flash-attn`, `xformers`, `ollama`, or any other AI runtime
- GPU not detected (`torch.cuda.is_available() == False`, `nvidia-smi` weirdness, container can't see GPU)
- Docker failing to pull / network / proxy issues
- Deciding where model downloads / HF cache / weights should live
- User asks to "install Python X", "upgrade torch", "set up a new AI project", "fix CUDA", "change mirror"
- Editing `~/.bashrc` / `~/.profile` / `~/.zshrc` for env activation
- Anything invoked with `sudo pip` (hard-stop trigger)

**Use BEFORE:** any install that might pull heavy binary wheels; any venv creation for AI work; any retry of a failed heavy install.

**Do NOT use when:** writing application code inside an already-working venv — that's application-layer work, not env config.

## The Six Layers

| # | Layer | Scope | Tool | Example |
|---|---|---|---|---|
| 0 | **Host OS** | GPU driver, WSL integration, host-side proxy | Vendor tools | NVIDIA driver, WSL2 integration |
| 1 | **OS system** | Base Linux tooling, Docker, NVIDIA Container Toolkit, compilers, OCR binaries | `apt` / `dnf` / `pacman` / `brew` | `docker`, `nvidia-container-toolkit`, `tesseract`, `build-essential`, `cmake`, `ninja-build` |
| 2 | **Shared heavy AI base** | Stable, high-reuse GPU runtime | `micromamba` / `conda` | Env named by a convention that encodes the CUDA line (pattern like `ai-base-cu<NN>-stable`), containing `python`, `pytorch`, `torchvision`, `torchaudio`, `pytorch-cuda` |
| 3 | **Project overlay** | Project-specific Python deps on top of the shared base | `python -m venv --system-site-packages` + **`pip`** | `<project>/.venv` inheriting shared `torch` |
| 4 | **Project data / outputs** | Raw inputs, experiment results, derived artifacts | Repository + documented external paths | Project-scoped; never inside the shared base |
| 5 | **Shared caches / artifacts** | Large reusable model downloads and caches | Explicit cache roots outside repos | `~/.cache/<tool>`, `HF_HOME`, `TRANSFORMERS_CACHE` |

Rule of thumb: **if you can't name the layer, don't install it yet.**

## Tool-to-Layer Mapping

| Need | Tool | Why |
|---|---|---|
| OS binaries — compilers, Docker, NVIDIA Container Toolkit, OCR | `apt` / `dnf` / `pacman` / `brew` | System infrastructure; stable across all projects |
| Shared heavy GPU base (torch + CUDA) | `micromamba` or `conda` | Better than `uv` for `torch + CUDA` binary chains over network; avoids repeat hits on `pypi.nvidia.com` |
| Project overlay **inheriting** shared torch | `python -m venv --system-site-packages` + **`pip install`** | **Observed:** `uv pip install` in this pattern does NOT reuse inherited `torch` — it starts resolving a new PyPI CUDA stack. `pip` does reuse correctly. Architectural fact, not a CLI detail. |
| Project **without** shared-base inheritance (pure PyPI) | `uv init` / `uv venv` / `uv add` | Fast, lock-file native, correct when there's nothing heavy to inherit |
| System Python | Don't touch | Stays clean of project-private AI packages. No `sudo pip install`. Ever. |

## Hard Rules (non-negotiable)

1. **No project AI stacks in system Python.** No `sudo pip install torch`. Ever.
2. **No duplicate heavy bases** without a real compatibility boundary. If a project needs a different CUDA / torch version, create a **named sibling** (`ai-base-cu<NEW>-stable`), migrate, then remove the old one. Don't fork the base per project.
3. **No auto-activation from shell init.** Don't append `source .../bin/activate` to `~/.bashrc` / `~/.profile` / `~/.zshrc`. Always explicit.
4. **Never retry a failed heavy install without cleanup.** Kill the process, remove the partial env, clear the relevant cache (`pip cache purge`, `micromamba clean -a`), validate the mirror, THEN retry.
5. **`uv` ≠ `pip`** in overlay-reuse scenarios. Architecturally different tools, not interchangeable CLIs.
6. **Do not leave design decisions only in chat.** Write them into this skill or project docs.
7. **Model artifacts and large caches stay outside repos** unless they're a pinned deliverable. Point `HF_HOME` / `TRANSFORMERS_CACHE` at a shared cache root.
8. **Swap to domestic mirrors before the first heavy install.** Default entry point: **Cernet MirrorZ** (`mirrors.cernet.edu.cn`) for pip / uv / conda / pytorch / nvidia / apt / npm / cargo / go. Plus `hf-mirror.com` for HuggingFace and a separate Docker Hub registry mirror for image pulls. Configure the swaps **before** the install, not during a retry after a 40-minute timeout. Canonical config docs at `help.mirrors.cernet.edu.cn/<tool>/`. Only skip on explicit upstream request, stale-sync fallback, or air-gapped host.

## Typical Operations → Minimum Steps

Substitute `<BASE_ENV>` with the base env path discovered by the re-anchor commands (e.g. `$HOME/.mamba/envs/ai-base-cu<NN>-stable`).

| Task | Recipe |
|---|---|
| **New AI project needing torch** | `cd <project>; <BASE_ENV>/bin/python -m venv --system-site-packages .venv; source .venv/bin/activate; pip install <deps>` |
| **New pure-PyPI project** (no torch inheritance) | `uv init <project>; cd <project>; uv add <deps>` |
| **Install one more package into existing overlay** | `source <project>/.venv/bin/activate; pip install <pkg>` (use `pip`, **not** `uv pip install`) |
| **Verify GPU visible in overlay** | `source .venv/bin/activate; python -c 'import torch;print(torch.cuda.is_available(), torch.cuda.get_device_name() if torch.cuda.is_available() else "no gpu")'` |
| **Upgrade torch / CUDA** | Create sibling env (`micromamba create -n ai-base-cu<NEW>-stable …`), migrate projects, delete old env. Never mutate the stable base in place. |
| **Failed heavy install recovery** | Kill process → `rm -rf <partial env>` → `micromamba clean -a` or `pip cache purge` → validate mirror → retry |
| **Docker pull hanging on proxy** | Edit `/etc/systemd/system/docker.service.d/http-proxy.conf` → `systemctl daemon-reload && systemctl restart docker` |
| **GPU not visible in container** | Install `nvidia-container-toolkit`; `nvidia-ctk runtime configure --runtime=docker`; restart Docker |
| **Model cache blowing up repo** | `export HF_HOME=~/.cache/huggingface` before first download; if already downloaded, `mv` / `ln -s` to cache root |
| **Deactivate activated env** | `deactivate` (venv) / `micromamba deactivate` / `conda deactivate` |

## Mirror Policy

**Default: swap every swappable channel to its mainland-China mirror before the first install.** This is the user's operating network posture. Large downloads (torch, CUDA wheels, conda-forge, base images) are the choke point; mirror selection determines whether a heavy install takes 30 seconds or times out after an hour. If the skill loads and no swap has been done yet for a channel the project will use, **do the swap first**.

**Primary mirror: MirrorZ CERNET** — the CERNET university-alliance union mirror at `https://mirrors.cernet.edu.cn/`. It uses `mirrorz-302` intelligent routing that auto-selects the fastest university sub-mirror (Tsinghua / USTC / SJTU / SUSTech / …). The canonical configuration docs for every tool live at `https://help.mirrors.cernet.edu.cn/<tool>/` — **consult that page when wiring up a new channel instead of guessing URLs.**

**Mandatory swap recipe** (apply every row whose channel your work touches):

| Channel / tool | Mainland mirror (default = Cernet MirrorZ) | Where to configure |
|---|---|---|
| `pip` (PyPI) | `https://mirrors.cernet.edu.cn/pypi/web/simple/` | `~/.config/pip/pip.conf` — `[global] index-url = …` + `trusted-host = mirrors.cernet.edu.cn` |
| `uv` (PyPI) | same Cernet URL | `~/.config/uv/uv.toml` — `index-url = "…"` + `index-strategy = "first-index"` |
| `conda` / `micromamba` (incl. `conda-forge` / `pytorch` / `nvidia` / `bioconda` channels) | Cernet Anaconda mirror | `~/.condarc` — see `help.mirrors.cernet.edu.cn/anaconda/` for full channel block |
| HuggingFace (models + datasets) | `https://hf-mirror.com` (Cernet does NOT mirror HF) | `export HF_ENDPOINT=https://hf-mirror.com` before first `from_pretrained` / `snapshot_download` |
| Docker Hub image pulls (`docker pull foo:tag`) | Domestic image-registry mirror (e.g. `https://docker.m.daocloud.io`) — **note: Cernet's `docker-ce` path is the engine-install apt repo, NOT an image registry mirror** | `/etc/docker/daemon.json` → `"registry-mirrors": [...]`, then `systemctl restart docker` |
| Docker Engine install repo (`apt install docker-ce`) | Cernet | `help.mirrors.cernet.edu.cn/docker-ce/` |
| `apt` (Ubuntu / Debian) | Cernet | `help.mirrors.cernet.edu.cn/ubuntu/` or `/debian/` — script replaces `/etc/apt/sources.list` |
| `npm` | Cernet `https://mirrors.cernet.edu.cn/npm/` (or fall back to `https://registry.npmmirror.com`) | `npm config set registry …` |
| `cargo` (crates.io) | Cernet | `help.mirrors.cernet.edu.cn/crates.io-index/` → `~/.cargo/config.toml` |
| `go` modules | Cernet `goproxy` (or `https://goproxy.cn`) | `go env -w GOPROXY=<mirror>,direct` |

**Rule:** optimize for reliable coverage, not uniformity. Mixed mirrors (one per channel) are normal — Cernet covers most but **not** HuggingFace or the Docker Hub image registry, so those stay on their own domestic mirrors.

**Cernet caveats** (know these before assuming it'll work):

- **Sync lag.** The union mirror can trail individual university mirrors / upstream by hours to a day. If you need a package published upstream in the last 24 h, hit upstream directly or a specific university mirror (Tsinghua / USTC / SUSTech).
- **`pytorch-nightly` / `ignite-nightly` are NOT mirrored.** Use upstream for nightlies.
- **No HuggingFace mirror.** Keep `HF_ENDPOINT=https://hf-mirror.com`.
- **`docker-ce` path ≠ Docker Hub registry mirror.** The `docker-ce` mirror installs the Docker engine; it does NOT accelerate `docker pull python:3.13`. For image pulls, a separate `registry-mirrors` entry is still needed.

**Validate before assuming.** Tool config keys drift across versions (`uv`'s `default-index` worked in one version, was rejected by another). Check with `pip config list`, `uv --version && cat ~/.config/uv/uv.toml`, `cat ~/.condarc`, `cat /etc/docker/daemon.json`, `env | grep -E 'HF_ENDPOINT|HF_HUB_ENDPOINT'` **before** a heavy install. A misconfigured mirror fails silently into a slow upstream fetch.

**Before retrying a mirror-dependent install** that failed midway: stop the process, remove partial env + caches (`pip cache purge`, `micromamba clean -a`), confirm mirror responds (`curl -I <mirror-url>`), THEN retry. Note: `micromamba --dry-run` still populates caches — factor into cleanup.

**Exceptions to the Cernet-first default** (rare — requires explicit signal):

- Package is too new and hasn't synced yet → fall back to upstream or a specific university mirror
- User explicitly requests upstream (debugging mirror staleness, or package missing from mirror)
- Host is air-gapped / behind corporate Artifactory / Nexus — use the internal mirror instead
- Host is outside mainland network — check upstream latency first; domestic mirror may be slower from abroad

## Activation Policy

- **No auto-activation from shell init.** Explicit per shell.
- For scripts, prefer absolute interpreter paths: `<BASE_ENV>/bin/python script.py` — no activation needed.
- Deactivate explicitly: `deactivate` / `micromamba deactivate` / `conda deactivate`.

## Update Policy

- **Shared AI base is immutable-by-default.** Upgrade via sibling env, not in-place mutation.
- **Project overlays can evolve freely.** They're the right place for churn.
- **System Python never changes** for AI packages. OS updates are fine.

## Known Pitfalls (observed, not theoretical)

1. **Docker daemon proxy ≠ shell proxy.** `docker pull` times out while shell networking is fine — daemon doesn't inherit shell env. Fix: systemd drop-in for docker service, then `daemon-reload` + `restart`.
2. **Sandboxed / container networking ≠ host networking.** Agent-sandbox / container `curl` / `fetch` can fail while interactive terminal works. Don't assume symmetry.
3. **Heavy PyPI + `pypi.nvidia.com` is fragile.** TLS / timeout errors on large CUDA wheels — this is the main reason shared torch lives in mamba, not per-project PyPI.
4. **`uv` config key drift.** Config that worked in one `uv` version can be rejected by another. Validate against installed version.
5. **`micromamba --dry-run` still populates caches.** Repodata / solv caches get written. Clean after dry-runs if the goal is a full restart.
6. **Overlay installer choice matters.** `uv pip install` in a `--system-site-packages` venv does NOT reuse inherited `torch`; `pip install` does. Architecture, not CLI.
7. **Stale planning docs / chat transcripts get misread as current state.** Re-anchor with live filesystem commands before trusting them.

## Decision Checklist (before any install)

1. **Layer:** Which of the 6 layers does this belong to?
2. **Tool:** Which tool matches that layer?
3. **Reuse:** Can this reuse an existing shared base instead of reinstalling heavy deps?
4. **Inheritance:** If overlay, does it need `--system-site-packages`? If yes → use `pip`, never `uv pip install`.
5. **Cache:** Where will model downloads live? (Not inside the repo unless deliberate.)
6. **Activation:** Is activation explicit per shell? (No `.bashrc` edits.)
7. **Mirror:** Is every channel this install touches swapped to its domestic mirror? (pip / uv / conda / pytorch / nvidia / `HF_ENDPOINT` / docker registry / apt / …). If a channel is still on upstream, swap **before** the install, not after a timeout.
8. **Verification:** What one-liner proves the install worked? (`python -c 'import X;print(X.__version__)'`, `torch.cuda.is_available()`, etc.)

If you can't answer all eight, the design is not done.

## Red Flags — STOP and Re-check

- About to `sudo pip install …` → wrong layer; stop
- About to `pip install torch` **inside an overlay that already inherits shared torch** → you'll duplicate the heavy stack and break layer separation
- About to `uv pip install` in a `--system-site-packages` venv → uv won't see inherited torch; will refetch
- About to append `source .venv/bin/activate` to `~/.bashrc` → forbidden
- About to mutate the shared base in place → make a sibling env instead
- About to retry a failed heavy install without killing the process / clearing caches → 90% chance same failure
- About to `rm -rf` a cache / env directory → confirm it's scoped correctly (project `.venv` or cache root, never the shared base)
- Trusting a memory / old planning note about env state → run the re-anchor commands first

## Common Mistakes

| Mistake | Fix |
|---|---|
| Running `pip install` without an active venv or explicit interpreter path | Activate overlay first OR use absolute interpreter path |
| Using `uv pip install` in an inherited-site-packages venv | Use `pip install`; `uv` breaks the inheritance |
| Creating a second shared base for a single project's torch bump | Make a project-local overlay; only create a new shared base when multiple projects need the bump |
| `export HF_HOME=./models` (inside the repo) | Point `HF_HOME` at `~/.cache/huggingface` or an explicit external root |
| Mixing `conda install` and `pip install` in the same env | Pick one ecosystem per env |
| Editing `~/.bashrc` to auto-activate | Per-shell explicit activation |
| Assuming a memory or old planning note is current state | Run the re-anchor commands first |
| Skipping `nvidia-smi` before debugging CUDA | Always prove GPU at host / WSL layer before suspecting Python |
| Running `pip install torch` before swapping PyPI to a domestic mirror | Point `pip` + `uv` at `https://mirrors.cernet.edu.cn/pypi/web/simple/` first; a cold upstream torch wheel can take >30 min or time out |
| Calling `from_pretrained("…")` / `snapshot_download` with `HF_ENDPOINT` unset | `export HF_ENDPOINT=https://hf-mirror.com` **before** the first HF call (Cernet does not mirror HF) — can't redirect a download that's already started |
| Assuming Cernet's `docker-ce` path accelerates `docker pull` | It doesn't — `docker-ce` is the engine-install apt repo. For image pulls add a separate `"registry-mirrors"` entry in `/etc/docker/daemon.json` and `systemctl restart docker` |
| `apt update` crawling slow upstream | Swap `/etc/apt/sources.list` via `help.mirrors.cernet.edu.cn/ubuntu/` (or `/debian/`) before any large `apt install` |
| Picking a package that synced "yesterday upstream" and Cernet returns 404 | Cernet has sync lag — fall back to a specific university mirror (Tsinghua / USTC / SUSTech) or upstream for recent packages, then restore Cernet for routine use |
| Guessing mirror URLs for a new tool | Check `help.mirrors.cernet.edu.cn/<tool>/` first — it's the canonical config source |

## The Bottom Line

Three questions per install:

1. **Which layer?**
2. **Which tool?**
3. **What's the one-line verification?**

If you can't answer all three, stop and think. Reuse the shared heavy base instead of re-downloading torch per project. Keep overlays thin. Verify before assuming. The hard rules exist because each one was learned from a real failure.
