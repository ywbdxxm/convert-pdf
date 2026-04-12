# Progress Log

## Current Status
- 当前阶段：`Docling Batch Program Design`
- 当前主线：
  - 环境建设已经完成
  - `Docling` 与共享 GPU Python 基础栈已经打通
  - 下一步重点是多 PDF 批处理产物形态、索引结构和结构化摘录策略
- 当前工作区状态：
  - 工作区当前存在未提交的 planning files 更新
  - 本次已对 `progress.md` 和 `findings.md` 做压缩整理，只保留 durable context
  - 当前仓库尚无批处理程序代码，只有环境与验证脚本，适合直接为第一版建立新的程序入口和测试夹具

## Milestones
### 2026-04-11: Research Baseline Established
- 创建 `task_plan.md`、`findings.md`、`progress.md`
- 完成 PDF -> Markdown 工具调研框架
- 对比 `Docling`、`Marker`、`MinerU`、`PyMuPDF4LLM` 以及主要云 API
- 初步结论收敛为：
  - 默认基线：`Docling`
  - 高保真增强：`Marker`
  - 扫描件 / 多语言补充：`MinerU`
- 同步刷新仓库 `README.md` 与 `.gitignore`

### 2026-04-11 Late: Scope Narrowed To Embedded Manuals
- 场景收敛到嵌入式 `datasheet / app note`
- 明确“原始 PDF + Markdown/JSON + 页级回查”三层工作流
- 深入确认 `Docling` 适合做本地 Python 批处理主线
- 记录系统层与项目层的职责边界，并写入仓库级 `AGENTS.md`

### 2026-04-12 Early: Heavy AI Dependency Strategy Corrected
- 长时间 `uv + CUDA wheels` 安装暴露出网络 / TLS / 重复下载问题
- 明确不能把“每个项目都重装一套 `torch + CUDA`”作为长期方案
- 任务范围从“当前项目环境”提升为“长期 AI 工作站架构”
- 新增共享 `AI base` 设计与批处理程序设计两个阶段

### 2026-04-12 Morning: Mirror Reset And Architecture Audit
- 清理失败的下载缓存和半成品环境
- 统一并验证 `pip` / `uv` / `micromamba` 国内镜像配置
- 完整审计当前工作站设计与仓库落盘情况
- 新增并补齐：
  - `docs/architecture/2026-04-12-ai-workstation-design-audit.md`
  - `docs/architecture/2026-04-12-ai-workstation-execution-plan.md`
  - `scripts/bootstrap_ai_base.sh`
  - `scripts/bootstrap_docling_env.sh`
  - `scripts/verify_ai_stack.sh`

### 2026-04-12 Noon: Environment Milestone Closed
- 建立共享重型 AI base：`/home/qcgg/.mamba/envs/ai-base-cu124-stable`
- 验证共享 base 中 `torch 2.5.1` 可访问 GPU
- 发现 `uv` 在 overlay 场景不会正确复用共享 `torch`
- 切换为 `pip` 作为 overlay 安装器
- 重建 `docling/.venv`，成功安装 `docling 2.86.0`
- 完成 WSL GPU、Docker GPU runtime、共享 base、`Docling` overlay 整体验证
- 当前阶段正式切换到 `Docling Batch Program Design`

### 2026-04-12: Cross-Project Workstation Reference Added
- 新增全局工作站文档：
  - `/home/qcgg/.codex/docs/ai-workstation-architecture.md`
- 更新全局入口：
  - `/home/qcgg/.codex/AGENTS.md`
- 在仓库内补充短指针文档：
  - `docs/architecture/global-workstation-reference.md`

### 2026-04-12: Planning Files Condensed
- 将 `findings.md` 从长篇研究/调试堆栈整理为“当前状态 + 关键结论 + 未决问题”
- 将 `progress.md` 从逐条会话流水整理为“关键里程碑 + 当前状态 + 后续工作”
- 保留了会影响后续设计的 durable context，移除了重复叙述、失效中间状态和低信噪比调试细节

### 2026-04-12: Batch Program Design Discovery Started
- 完成 session catchup，并重新读取 `task_plan.md`、`findings.md`、`progress.md`
- 检查仓库文件结构、最近提交、`docling/` 目录和现有脚本
- 确认当前没有批处理程序本体，不存在必须兼容的旧实现
- 当前进入批处理程序设计澄清阶段，下一步是收敛第一版输出形态和索引目标

### 2026-04-12: First-Version Scope Selected
- 用户已选择第一版做 A 路线
- 当前收敛范围为：
  - `Markdown + JSON + manifest + 章节/页码级索引`
  - 目标是让后续 AI 查阅、引用和回溯更可靠
  - 寄存器/AF/时序等深结构化抽取延后

### 2026-04-12: Chunking Recommendation Added
- 已给出当前推荐的 chunk 策略
- 推荐采用“章节优先，但设置最大长度上限”的混合切分
- 原因是它比“纯章节切分”更利于后续检索，也比“纯固定长度切分”更能保留手册语义和引用边界

### 2026-04-12: Docling Official RAG Guidance Reviewed
- 已重新阅读 Docling 官方文档中与本项目最相关的部分：
  - batch conversion
  - serialization
  - chunking
  - hybrid chunking
  - advanced chunking and serialization
  - RAG integrations
  - visual grounding
  - GPU / OCR usage
- 当前结论进一步收敛为：
  - `Docling JSON` 应作为 canonical source
  - `Markdown` 主要作为人工查阅层
  - RAG 主索引应来自 Docling 原生 chunking，而不是纯 Markdown 切块
  - 默认 chunker 应优先 `HybridChunker`
  - chunk 索引中应保留 `contextualized_text`

### 2026-04-12: Implementation Spec And Plan Written
- 已将认可后的设计落盘到：
  - `docs/superpowers/specs/2026-04-12-docling-batch-design.md`
  - `docs/superpowers/plans/2026-04-12-docling-batch-implementation.md`
- 已切换到功能分支：
  - `feat/docling-batch-processor`
- 当前开始进入 TDD 实现阶段

### 2026-04-12: First Batch Processor Implementation Landed
- 已新增 `docling_batch/` 包与 `tests/`
- 已实现：
  - CLI 参数解析
  - GPU/OCR pipeline 配置
  - PDF 递归发现
  - `Docling JSON` / `Markdown` 导出
  - `HybridChunker` 原生 chunking
  - `contextualized_text` 写入
  - `sections.jsonl` / `chunks.jsonl` / `manifest.json` / run summary 产出
- 已完成单元测试：
  - `docling/.venv/bin/python -m unittest discover -s tests -v`
- 已完成 smoke test：
  - `docling/.venv/bin/python -m docling_batch convert --input /tmp/docling-batch-input --output /tmp/docling-batch-output --device cuda --no-ocr`
  - 成功生成 `document.json`、`document.md`、`manifest.json`、`sections.jsonl`、`chunks.jsonl` 和 `_runs/*.json`

### 2026-04-12: Manuals Directory Skeleton Added
- 已创建并落盘最小 PDF 目录骨架：
  - `manuals/raw/`
  - `manuals/processed/`
  - 厂商子目录：`st`、`ti`、`nxp`、`adi`、`infineon`、`microchip`、`other`
- 已补 `.gitkeep`，保证这些空目录能被 git 跟踪
- 同时记录了“大 PDF 是否需要先按书签拆分”的当前建议：
  - 默认不拆，先整本处理
  - 仅在多文档拼接、超大扫描件或明确无用附录干扰时再考虑预拆分

### 2026-04-12: Real ESP32-S3 Sample Tested
- 已对用户提供的真实样本执行：
  - `manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf`
- 实际命令：
  - `docling/.venv/bin/python -m docling_batch convert --input ... --output manuals/processed --device cuda --no-ocr`
- 实际结果：
  - `processed=1 success=1 partial=0 failure=0`
  - 输出目录：`manuals/processed/esp32-s3-datasheet-en/`
  - `page_count = 87`
  - `sections.jsonl = 145` 条
  - `chunks.jsonl = 444` 条
- 当前确认：
  - 主体章节和多数技术内容已可被章节级与 chunk 级索引覆盖
  - 目录页、表目录、续页标题等噪声仍进入索引，属于下一轮优化项
  - 当前 tokenizer 还出现过一次超长 warning，后续应加默认 `max_chunk_tokens`

## Verification Summary
| Area | Result | Status |
|------|--------|--------|
| WSL GPU | `nvidia-smi` 正常识别 `RTX 4060 Laptop GPU` | ✓ |
| Docker GPU runtime | GPU 容器可正常执行 `nvidia-smi` | ✓ |
| Shared AI base | `torch 2.5.1` 可见 CUDA 与当前 GPU | ✓ |
| Docling overlay | `docling 2.86.0` 可正常导入 | ✓ |
| Overlay reuse | `docling/.venv` 中的 `torch` 来自共享 base | ✓ |
| Mirror configuration | `pip` / `uv` / `micromamba` 配置已修正并做过可用性验证 | ✓ |
| Architecture docs | 审计文档、执行计划、全局引用文档已落盘 | ✓ |

## Resolved Blockers
- `uv + pypi.nvidia.com` 路线不适合作为共享重型 AI base 的稳态方案。
- `uv` 在 `venv --system-site-packages` overlay 中不会正确复用共享 `torch`。
- 早期缺失的架构文档、全局规则入口和项目层落盘内容已经补齐。
- 早期沙箱 `fetch` 网络问题已不再构成当前主线阻塞。

## Current Assets
- 共享重型 AI base：`/home/qcgg/.mamba/envs/ai-base-cu124-stable`
- 项目环境：`docling/.venv`
- 工作站长文档：`/home/qcgg/.codex/docs/ai-workstation-architecture.md`
- 仓库架构文档：
  - `docs/architecture/2026-04-12-ai-workstation-design-audit.md`
  - `docs/architecture/2026-04-12-ai-workstation-execution-plan.md`
  - `docs/architecture/global-workstation-reference.md`
- 执行脚本：
  - `scripts/bootstrap_ai_base.sh`
  - `scripts/bootstrap_docling_env.sh`
  - `scripts/verify_ai_stack.sh`

## Remaining Work
- 设计多 PDF 批处理程序的输出 schema
- 设计手册索引结构与命名规则
- 决定哪些内容保留原文，哪些内容提升为结构化摘录
- 准备后续 `Docling` 与 `Marker` / `MinerU` / `OpenDataLoader PDF` 的 A/B 测试样本与准则
