# Task Plan: PDF / AI 工作站架构与 Docling 环境建设

## Goal
为这台机器设计并逐步落地一套长期可复用的 PDF / AI 工作站架构，覆盖 `WSL 系统层 -> Docker / 容器层 -> CUDA / GPU 层 -> 共享 AI base 层 -> 项目级环境层`，并在当前仓库中完成 `Docling` 探索环境建设。

## Current Phase
Docling Batch Optimization Documentation

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

### Phase 9: Table References And Large PDF Resilience
- [x] 将表格 sidecar 更直接地挂回 `document.md`
- [x] 为表格 manifest 增加 `label/caption` 元数据
- [x] 为大 PDF 增加窗口级缓存和恢复
- [x] 用真实样本验证缓存复跑与表格引用
- **Status:** complete

### Phase 10: Architecture Gap Review
- [x] 重新核对 Docling 官方 chunking / batch / table / figure / visual grounding / OCR 文档
- [x] 对当前产物与原始 PDF 做一轮问题审计
- [x] 收敛“第一性原理下”的最佳实践与当前缺口
- **Status:** complete

### Phase 11: Incremental Hardening
- [x] 为窗口缓存补 conversion signature
- [x] 为阅读层增加 `document.html`
- [x] 增加疑似“表格退化成图片”告警
- [x] 用 `ESP32-S3` 和 `STM32H743VI` 样本验证
- **Status:** complete

### Phase 12: ESP32-S3 TRM Evaluation
- [x] 用 Docling 处理 `esp32-s3_technical_reference_manual_en.pdf`
- [x] 完整等待 1531 页转换结束
- [x] 评估输出规模、表格、告警、chunk/section 结果
- [x] 增加空 table sidecar 告警
- **Status:** complete

### Phase 13: Docling Architecture Documentation
- [x] 总结嵌入式开发场景下的 Docling 手册处理架构
- [x] 解释设计初衷、产物含义、AI 使用流程和配置方式
- [x] 总结 Docling 优缺点和当前样本评估结果
- [x] 更新 README 和 AGENTS 文档入口
- **Status:** complete

### Phase 14: RAG Best Practice Review
- [x] 解释 RAG 的第一性原理、用途和边界
- [x] 对比当前 Docling 产物与完整 RAG 系统的差距
- [x] 给出芯片手册转换成 AI 可理解查阅资产的最佳实践
- **Status:** complete

### Phase 15: RAG Documentation
- [x] 将 RAG 总结落入 `docs/architecture/` 独立文档
- [x] 明确后续轻量检索层需要在当前工程开发
- [x] 明确现成 RAG 软件应作为后续集成层而不是当前基础
- **Status:** complete

### Phase 16: RAG Scope Reality Check
- [x] 核对 Docling 官方定位是否本来就是 RAG ingest 组件而非完整应用
- [x] 调研是否已有开源 RAG 应用/框架可直接复用
- [x] 重新评估对当前“AI 查芯片手册”需求的实际提升和最小必要投入
- **Status:** complete

### Phase 17: Docling Complexity Reality Check
- [x] 量化当前 Docling 包装代码、测试和文档规模
- [x] 区分 Docling 解析能力边界与本项目工程化包装复杂度
- [x] 明确当前阶段应停止继续扩展 Docling 工程，转向试用现成 RAG/文档问答工具
- **Status:** complete

### Phase 18: Avoid NIH Tooling Review
- [x] 对照 Docling/Marker/MinerU/Unstructured/PyMuPDF4LLM/RAGFlow 现有能力
- [x] 标记当前自研代码中可能重复造轮子的部分
- [x] 明确当前实现只是实验基线，不是已证明的最佳路线
- **Status:** complete

### Phase 19: Refactor Replacement Analysis
- [x] 按 `docling_batch` 模块拆分职责
- [x] 对照现成工具能力，标记可替代、应保留、应冻结/删除的部分
- [x] 给出第一性原理下的重构方向和推荐路线
- **Status:** complete

### Phase 20: Output Schema Reality Check
- [x] 核对当前项目哪些部分是 Docling 原生 API，哪些是自定义包装
- [x] 重新判断 `manuals/processed/<doc_id>` 是否应该作为所有工具的强制输出结构
- [x] 明确多工具 A/B 下更合理的原始输出与最小归一化结构
- **Status:** complete

### Phase 21: Evaluation Framework Design
- [x] 设计基于 Docling 原生工具的 baseline runner
- [x] 设计多工具 raw output + minimal evidence normalization 框架
- [x] 明确哪些现成软件先接入，哪些暂缓
- [x] 等用户确认设计后再写实现计划
- **Status:** complete

### Phase 22: External-First Tooling Research
- [x] 暂停并记录 `manual_eval` 自研框架方向，不继续实现
- [x] 调研 Docling 官方/生态中已有的 RAG 和文档问答集成最佳实践
- [x] 调研成熟 PDF/RAG 工具软件，优先寻找可直接使用的方案
- [x] 形成外部工具优先的试用顺序和验收标准
- **Status:** complete

### Phase 23: Local-Free Tooling Plan Cleanup
- [x] 根据 WSL + RTX 4060、本地免费优先、不测 RAGFlow/Unstructured 的约束重排工具候选
- [x] 纳入 OpenDataLoader PDF、OpenDataLoader LangChain consumer、Dify、AnythingLLM、Kotaemon、Open WebUI、Docling 集成、Marker/MinerU/PyMuPDF4LLM 的试用顺序
- [x] 更新总计划文档
- [x] 压缩 `findings.md` / `progress.md`
- [x] 优化 `README.md`
- **Status:** complete

### Phase 24: Agentic File Retrieval Reframe
- [x] 确认核心方向是 PDF 转结构化文件后让 Codex/agent 直接检索，而非默认传统 RAG
- [x] 将 OpenDataLoader/Docling/LangChain/LlamaIndex 组合定位为文件资产和 metadata 验证路径
- [x] 将 Dify/AnythingLLM/Kotaemon/Open WebUI 降级为文件检索不足时的消费者/UI 候选
- **Status:** complete

### Phase 25: Agentic Tool Candidate Expansion
- [x] 继续探索适合 Agentic 文件检索的本地/免费 PDF 转换器和文件资产生成工具
- [x] 纳入 LiteParse、MarkItDown、PaperFlow、PaddleOCR-VL、HURIDOCS、Markdrop/pdfmd 等候选
- [x] 将当前 `docling_batch` 明确纳入冻结 baseline 对比
- **Status:** complete

### Phase 26: Optional Docling Batch Unfreeze Boundaries
- [x] 分析如果不冻结 `docling_batch`，哪些优化仍符合 Agentic 文件检索方向
- [x] 明确只允许 page slices、folder index、quality summary、hard-page images、native chunk comparison 等薄改动
- [x] 明确禁止继续在 `docling_batch` 中构建 RAG/search/table 修复/VLM/多工具框架
- **Status:** complete

### Phase 27: OpenDataLoader Docling Comparison Planning
- [x] 将下一轮范围收敛到 `docling_batch` baseline、Docling native、OpenDataLoader local、OpenDataLoader hybrid
- [x] 仅保留 OpenDataLoader LangChain 与 Docling LlamaIndex/LangChain 作为 metadata spot-check，其它 parser、consumer、UI/RAG app 全部暂缓
- [x] 明确比较重点是文件资产质量、metadata、页码、bbox、表格和原 PDF 回溯能力
- **Status:** complete

### Phase 28: Docling Batch Optimization Documentation
- [x] 记录 `docling_batch` 相对 Docling 原生输出的额外包装层
- [x] 记录允许解冻后可做的薄优化方向
- [x] 记录禁止继续做的方向，防止再次回到 NIH / 自研 RAG 路线
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
| `document.md` 中的表格不再只保留内联 Markdown，本轮开始在每张表后追加 `HTML/CSV sidecar` 链接 | 阅读层现在能直接跳转到更适合核对宽表/矩阵表的 sidecar 文件 |
| 大 PDF 优化优先做“窗口级缓存/恢复”，而不是先继续激进调 batch size | 对 5000+ 页手册，抗中断和避免整本重跑的收益高于小幅吞吐提升 |
| 当前主线继续以 `Docling JSON + Markdown + native chunking + table sidecars` 为核心，不切到全量 VLM 管线 | 这是准确性、可复现性、吞吐和工程复杂度之间最稳的主线 |
| 下一阶段最高价值增强不是更换主解析器，而是补 `visual grounding / page images / figure metadata` 和“疑难页二级补救” | 这更直接解决嵌入式手册中的时序图、框图、宽矩阵表问题 |
| 缓存机制默认关闭，仅作为显式可选的容错功能 | 这更符合“多数手册只处理一次”的真实工作流，避免普通单次转换承担额外复杂度和时间成本 |

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
- 当前已新增：
  - `document.md` 表格后置 `Table sidecars` 引用
  - `manifest.json` 的表格 `label/caption`
  - 每份文档 `_windows/` 窗口缓存，可复跑恢复
