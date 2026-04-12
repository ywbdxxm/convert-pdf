# Task Plan: PDF / AI 工作站架构与 Docling 环境建设

## Goal
为这台机器设计并逐步落地一套长期可复用的 PDF / AI 工作站架构，覆盖 `WSL 系统层 -> Docker / 容器层 -> CUDA / GPU 层 -> 共享 AI base 层 -> 项目级环境层`，并在当前仓库中完成 `Docling` 探索环境建设。

## Current Phase
Docling Batch Program Implementation Verification

## Phases
### Phase 1: Research Refresh
- [x] 恢复上一轮 PDF 工具调研结论
- [x] 核对 `Docling`、`MinerU API`、`pdf-reader-mcp` 相关事实
- [x] 核对本机 WSL / GPU 当前状态
- **Status:** complete

### Phase 2: Environment Design
- [x] 给出本地 vs 云端 API 的现实取舍
- [x] 给出 WSL 全局 CUDA / Python / 容器基础环境设计
- [x] 给出 `Docling` 探索目录结构设计
- **Status:** complete

### Phase 3: User Approval
- [x] 向用户展示 2-3 个实现路径
- [x] 给出推荐方案和风险
- [x] 等待用户确认后再开始实施
- **Status:** complete

### Phase 4: Environment Implementation
- [x] 新建 `docling` 探索目录
- [x] 配置 WSL 全局 GPU / Python / 构建环境
- [x] 清理未完成的重型下载与缓存残留
- [x] 统一 `conda` / `uv` / `pip` 国内镜像配置
- [x] 在新镜像策略下重建共享 `AI base`
- [x] 建立项目级隔离环境与验证脚本
- **Status:** complete

### Phase 5: Verification & Documentation
- [x] 验证 GPU、Python、Docling、后续 OCR/VLM 基础可用
- [x] 补齐设计审计文档与执行脚本
- [x] 更新 README / findings / progress
- [x] 提交并推送
- **Status:** complete

### Phase 6: Shared AI Base Design
- [x] 总结当前 CUDA Python 依赖安装瓶颈
- [x] 设计共享 `AI base` 环境分层
- [x] 明确未来项目如何复用该基础环境
- **Status:** complete

### Phase 7: Workstation Architecture Design
- [x] 明确这台工作站未来的主负载类型
- [x] 设计 `Host -> WSL -> Docker -> AI base -> Project -> Data` 分层边界
- [x] 给出长期提效优先级与落地顺序
- **Status:** complete

### Phase 8: Docling Batch Program Design
- [x] 明确“给 AI/我自己查阅嵌入式手册”的最优产物形态
- [x] 设计多 PDF 批处理、文档索引和后续检索结构
- [x] 明确哪些信息应保留为原文、哪些应做结构化摘录
- **Status:** complete

## Key Questions
1. `Docling` 本地方案和 `MinerU API` 这类云端方案相比，实际效果差距会不会大到值得优先走云端？
2. 对嵌入式 datasheet / app note，什么场景本地方案更优，什么场景云端/远程增强更优？
3. 这台 `WSL2 + RTX 4060 Laptop GPU` 当前是否已经具备 CUDA 基础能力？
4. 为后续 `Docling + MinerU/OCR/VLM` 实验，WSL 全局环境最合理的打底范围是什么？
5. `Docling` 探索目录第一阶段应该只放环境和验证，还是顺带脚本骨架？
6. 为了后续基于手册做嵌入式开发，批处理程序应该输出什么层级的数据，才最利于查阅和复用？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 本阶段不写批处理程序，只配环境 | 用户已明确先做环境准备 |
| 环境目标覆盖 `Docling + MinerU/OCR/VLM` 基础 | 用户明确要求把后续 CUDA 基础一次打好 |
| 允许修改 WSL 全局环境 | 用户明确接受系统级改动 |
| 优先采用系统级 WSL GPU/NVIDIA 支持 | 用户希望后续所有项目都能直接复用这套基础设施 |
| Python AI 依赖按项目做合理隔离，不直接灌进系统 Python | 用户认可项目级隔离更稳，避免污染 Ubuntu 24.04 的系统 Python |
| 本次继续完成当前 GPU 项目环境安装 | 用户明确要求这次继续等待当前下载完成 |
| 后续补一个共享 `AI base` 通用环境方案 | 用户明确要求避免每个项目都重复下载这些超大 GPU 依赖 |
| 当前任务范围提升为长期工作站架构设计 | 用户明确愿意在初期投入时间，把底层基础设施设计好 |
| 先做设计评审，再开始实施 | `brainstorming` 规则要求先给方案并获批 |
| 共享重型 `AI base` 不再沿用 `uv + pypi.nvidia.com` 作为首条重建路径 | 该链路已出现真实 `tls handshake eof`，稳态不足 |
| `pip` / `uv` 统一使用清华 PyPI 镜像 | 国内可用性高，适合作为 Python 包默认源 |
| `conda-forge` 使用中科大镜像，`pytorch` / `nvidia` 使用教育网国内镜像 | 单一镜像未覆盖全部 GPU 相关 channel，混合国内镜像更稳 |
| 重建前必须先停掉未完成安装并清空残留缓存 | 避免“半完成环境 + 旧缓存”污染后续判断与重试 |
| 批处理程序第一版先做 `Markdown + JSON + manifest + 章节/页码级索引` | 用户已明确优先做适合 AI 查阅和可引用回溯的 A 路线，暂不提前做寄存器等深结构化抽取 |
| `Docling JSON` 作为批处理程序的 canonical source，`Markdown` 作为阅读副产物，RAG 主索引来自 Docling 原生 chunking | 这是基于 Docling 官方 chunking / serialization / RAG examples 收敛出的最稳妥路线 |
| 对超大 PDF 优先采用程序内部分页窗口处理，而不是要求用户手工拆 PDF | 这样可以保留统一文档身份、绝对页码和全局引用链，同时降低单次处理风险 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `nvidia-smi` 在无权限阶段失败 | 1 | 在 full access 下复测成功，确认为权限问题，不是 WSL GPU 桥接损坏 |
| `docker pull` 首次超时 | 1 | 已定位为 Docker daemon 未继承代理环境；通过 systemd drop-in 配置代理后恢复 |
| `uv add` 首次失败 | 1 | 已定位为 `uv` 试图安装当前目录自身包；改用 `--no-install-project` 重试 |
| CUDA 版 `torch` 安装在断网后失败退出 | 1 | 已定位为从 `pypi.nvidia.com` 拉取 `nvidia-cusolver-cu12` 时 `tls handshake eof`，当前项目环境仍未完成 |
| 共享 `AI base` 的 `uv pip install` 已结束但未完成环境落盘 | 1 | 原 `/home/qcgg/.venvs/ai-base-cu128-stable` 未形成可用环境，现已清理并转向 `micromamba` 路线 |
| `uv` 全局镜像配置写成了无效键 `default-index` | 1 | 已修正为当前 `uv` 版本支持的 `index-url`，并用 `uv pip install --dry-run` 验证 |
| `micromamba create` 持续下载但环境目录几乎未落盘 | 1 | 已停止进程、清空 `~/.mamba` 相关残留，并改为先 dry-run 验证镜像链路 |
| 规划文件引用的设计文档路径不存在 | 1 | 已补写新的架构审计与执行文档，并改用真实存在的 `docs/architecture/` 路径 |
| `uv` 在 overlay venv 中未复用共享 base 的 `torch` | 1 | 已确认 `pip` 能正确识别 `--system-site-packages` 继承依赖，并将 overlay 安装脚本切换为 `pip` |

## Notes
- 当前系统为 `Ubuntu 24.04.4 LTS / WSL2`
- 当前 GPU 已可见：`RTX 4060 Laptop GPU`，`nvidia-smi` 返回正常，驱动 `595.79`，CUDA `13.2`
- 当前存在 `/usr/lib/wsl/lib/libcuda.so*`，说明 WSL CUDA 桥接库存在
- 当前 `nvcc` 仍未安装；这是有意保留，当前阶段不需要完整 CUDA toolkit
- 当前已完成：`docker`、`nvidia-container-toolkit`、`ninja-build`、`tesseract` 基础包
- 当前已完成：Docker daemon NVIDIA runtime 配置与代理配置
- 当前已完成：`docling/` 目录与基础 README / requirements
- 当前共享重型 `AI base` 已创建完成：`/home/qcgg/.mamba/envs/ai-base-cu124-stable`
- 当前 `docling/.venv` 已创建完成，并成功复用共享 base 中的 `torch`
- 当前镜像配置文件已落盘：
  - `pip`: `/home/qcgg/.config/pip/pip.conf`
  - `uv`: `/home/qcgg/.config/uv/uv.toml`
  - `conda/micromamba`: `/home/qcgg/.condarc`
- 当前全局工作站规则已补入：
  - `/home/qcgg/.codex/AGENTS.md`
- 当前已验证：
  - `pip` 可通过国内镜像解析包版本
  - `uv` 修正后可通过国内镜像完成 dry-run 解析
  - `micromamba` 可在国内镜像配置下 dry-run 解析 `pytorch-cuda=12.4`
  - 共享 `AI base` 中 `torch 2.5.1` 可见 GPU
  - `docling 2.86.0` 可在 `docling/.venv` 中正常导入
  - `docling/.venv` 中的 `torch` 实际来自共享 base，而不是项目层重复安装
- 当前已补齐：
  - `docs/architecture/2026-04-12-ai-workstation-design-audit.md`
  - `docs/architecture/2026-04-12-ai-workstation-execution-plan.md`
- 当前已补齐可执行脚本：
  - `scripts/bootstrap_ai_base.sh`
  - `scripts/bootstrap_docling_env.sh`
  - `scripts/verify_ai_stack.sh`
