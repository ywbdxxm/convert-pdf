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

### 2026-04-12: Large-PDF Windowing Started
- 已新增 `--page-window-size` 参数，默认值为 `250`
- 当前实现支持：
  - 对单个 PDF 计算页窗范围
  - 分页窗调用 Docling `convert_all(..., page_range=...)`
  - 将窗口级 `DoclingDocument` 用 `DoclingDocument.concatenate(...)` 合并
  - 在 `manifest.json` 中记录 `page_window_size`、`window_count` 和各窗口状态
- 已完成相关单元测试：
  - 页窗切分
  - 窗口状态聚合
  - CLI 默认值
- 真实样本上的强制多窗口 smoke 已开始尝试，但当前阶段仍偏慢；这一点需要在下一轮继续量化与优化
- 同时已将 `manuals/processed/` 调整为仅保留 `.gitkeep`，不再跟踪真实生成产物，避免大文档处理结果污染 git 历史
- 当前已补充结论说明：
  - 分窗的首要目标是稳态和容错，不是让中等 PDF 更快
  - 目前实现属于“朴素分窗”，会让中等规模 PDF 看起来比整本处理更慢
  - 这不代表方向错了，而是说明下一轮要继续做吞吐优化和更好的进度可见性

### 2026-04-12: Image Noise Issue Confirmed
- 用户指出二维码、页脚反馈条这类图片进入 Markdown 没有价值
- 已从 ESP32-S3 样本的 Docling 图片元数据确认这类噪声存在
- 当前判断：
  - “引用式图片 sidecar”方向仍然正确
  - 但必须增加图片过滤，不能无差别保留所有图片

### 2026-04-12: End-To-End Pipeline Explained
- 已将“当前处理一份 PDF 的全过程”写回 findings
- 当前统一口径为：
  - `CLI -> RuntimeConfig -> PDF 发现 -> 可选页窗切分 -> Docling 转换 -> 文档合并 -> JSON/Markdown 导出 -> native chunking -> sections/chunks 索引 -> run summary`
- 这样后续讨论性能、图片过滤、OCR 或大 PDF 优化时，默认都指向同一条实际代码路径

### 2026-04-12: Artifact Usage Model Clarified
- 已把“chunk 是什么”“我后续如何查阅最终产物”“document.md 中图片的定位”写回 findings
- 当前统一结论：
  - `chunks.jsonl` 是主检索层
  - `sections.jsonl` 是导航层
  - `document.md` 是阅读层
  - 原始 PDF / 图片 sidecar 是证据层
  - `document.json` 是 canonical source，但不是我日常第一眼去读的层

### 2026-04-12: RAG Positioning Clarified
- 已补充说明当前工作与完整 RAG 系统的关系
- 当前统一结论：
  - 我们现在做的是 RAG 上游的 parsing / evidence packaging
  - 不是完整的 embedding + retrieval + answer system
  - 当前产物未来完全可以接入成熟 RAG 软件

### 2026-04-12: Official Docling RAG Examples Re-Checked
- 已重新核对 Docling 官方 examples 中与 RAG 最相关的几条路线：
  - Haystack
  - LangChain
  - LlamaIndex
  - Visual grounding
  - Hybrid chunking
  - Advanced chunking & serialization
- 当前进一步确认：
  - 官方默认更偏向 `DOC_CHUNKS` / native chunking，而不是纯 Markdown 切块
  - 官方非常强调 grounded metadata、`contextualized_text` 和 Docling-native JSON 路线
  - 我们当前路线与官方 ingestion 方向一致，只是还没接 embedding/vector store/retriever 这一段

### 2026-04-12: Final Embedded-Manual Best Practice Summarized
- 已把“基于第一性原理、面向后续嵌入式开发”的完整最佳实践写回 findings
- 当前统一口径：
  - 原始 PDF 是最终证据
  - `document.json` 是 canonical source
  - `chunks.jsonl` 是主检索层
  - `sections.jsonl` 是导航层
  - `document.md` 是阅读层
  - 图片采取“高价值保留、低价值过滤”的策略
  - 超大 PDF 优先内部分窗
- 成熟 RAG 框架应作为下游接入，而不是替代这层上游证据准备

### 2026-04-12: Auto Window Threshold And Image Filtering Landed
- 已新增：
  - `--page-window-min-pages`，默认 `500`
  - `--image-filter {off,heuristic}`，默认 `heuristic`
- 当前默认行为已经收敛为：
  - 小文档整本处理
  - 大文档才启用内部分窗
  - Markdown 图片先做一轮启发式噪声过滤
- 已重新跑 ESP32-S3 真实样本验证：
  - `window_count = 1`
  - 第一页二维码已被移除
  - 功能框图仍保留
- 进一步检查发现：
  - 当前 `document.md` 中仍写有图片引用
  - 但本次实际输出目录未见对应 `artifacts/`
  - 说明当前图片过滤逻辑主要控制的是 Markdown 引用，不是最终 sidecar 文件全集

### 2026-04-12: Image Strategy Reconsidered
- 用户指出 `document.md` 对后续查阅非常重要，希望不要激进删图
- 当前结论已经改为：
  - 默认保留 Docling 识别到的全部图片进 `document.md`
  - 重点改为修复图片引用路径和提升清晰度
  - 图片过滤若要继续做，应转移到更高层消费/UI，而不是当前源生成阶段

### 2026-04-12: Image Path Strategy Implemented
- 已将默认图片策略改为：
  - `image_filter = off`
  - `image_scale = 2.0`
  - `document.md` 默认保留 Docling 识别到的图片引用
- 已修复图片路径：
  - Markdown 中的图片现在引用 `artifacts/<filename>`
  - sidecar 图片真实落在 `manuals/processed/<doc_id>/artifacts/`
- 已重新跑 ESP32-S3 样本验证：
  - `document.md` 中图片引用为相对路径
  - `artifacts/` 目录真实存在
  - 图片与 Markdown 引用闭环已打通

### 2026-04-12: Retrieval-Layer Text Noise Filtering Added
- 已新增索引层文本噪声过滤：
  - `Submit Documentation Feedback`
  - 纯页码文本
  - 原有目录/续页类噪声 section
- 当前策略保持为：
  - `document.md` 尽量完整，不激进清洗
  - `chunks.jsonl` / `sections.jsonl` 做检索层清洗
- 重新跑 ESP32-S3 样本后确认：
  - `document.md` 中页脚文本仍存在
  - `chunks.jsonl` / `sections.jsonl` 中已无这类噪声

### 2026-04-12: Docling Feature Usage And GPU Direction Clarified
- 已补充说明当前实际用到的 Docling API 与未用到的路线
- 当前统一结论：
  - 标准主线当前用的是 `DocumentConverter + standard PDF pipeline + HybridChunker`
  - 下一步更适合优先尝试官方 `gpu_standard_pipeline` 路线
  - 官方 `gpu_vlm_pipeline` 更像 VLM 页面理解路线，不是当前最该优先上的性能优化

### 2026-04-12: GPU Standard Pipeline Adopted
- 当前实现已切到官方 `gpu_standard_pipeline` 对应路线：
  - `ThreadedStandardPdfPipeline`
  - `ThreadedPdfPipelineOptions`
- 默认 GPU batch 配置当前为：
  - `layout_batch_size = 32`
  - `ocr_batch_size = 4`
  - `table_batch_size = 4`
- 这样当前主线已经不只是“开 CUDA”，而是开始利用官方推荐的 threaded standard pipeline 做吞吐优化

### 2026-04-12: Progress Visibility And Tokenizer Warning Improved
- 已新增窗口级进度输出：
  - 真实样本运行时会输出类似 `[esp32-s3-datasheet-en] window 1/1 pages 1-87`
- 已对 HuggingFace tokenizer 的 `model_max_length` 做运行时放宽
- 重新跑 ESP32-S3 样本后确认：
  - 进度日志正常出现
  - 先前的 `Token indices sequence length ...` warning 已消失

### 2026-04-12: Tokenizer And HF Warning Meaning Clarified
- 已把两个容易误解的点写回 findings：
  - `tokenizer length` 主要影响 chunk 计数/切分阶段，不直接改动原文内容
  - `HF Hub unauthenticated` warning 主要影响首次下载速度和限流，不等于 Docling 失效
- 已补充当前建议：
  - `HF_TOKEN` 不写进仓库
  - 优先使用 `hf auth login` 或本地环境变量配置

### 2026-04-12: Hugging Face Auth Configured
- 已使用官方 Hugging Face 登录流程完成本机认证
- 已验证：
  - `whoami` 返回当前账号
  - 单独加载 Hugging Face tokenizer 成功
  - 当前 Docling 使用链不再需要匿名访问 Hugging Face Hub
- 已进一步确认：
  - token 已写入 `~/.cache/huggingface/`
  - 当前认证是 WSL 用户级全局可复用，不局限于 `docling/.venv`
- 新发现：
  - `Submit Documentation Feedback` 这一类内容当前仍会出现在 `document.md`
  - 但它是文本/链接噪声，不是图片过滤失效

### 2026-04-12: ESP32-S3 Quality Audit Completed
- 已对当前 ESP32-S3 样本产物与原始 PDF 做针对性对照
- 抽查页：
  - 第 1 页（封面）
  - 第 2 页（图文混排）
  - 第 27 页（宽表）
  - 第 64 页（正文 + 表格 + 页脚噪声）
- 当前审计结论：
  - 标题和连续正文表现良好
  - 图像保留方向正确
  - 宽表/矩阵表仍然是当前主线短板
  - 阅读层页脚噪声仍在，但检索层已清理

### 2026-04-12: Table Optimization Strategy Summarized
- 已把“怎么优化表格”的分层策略写回 findings
- 当前统一方向：
  - `document.md` 不是唯一表格承载层
  - 对宽表/矩阵表应增加 HTML/CSV sidecar
  - 必要时再保留表格图片 sidecar
  - 结构化表格抽取留到更后续阶段

### 2026-04-12: Table Sidecars Landed
- 已新增表格 sidecar 导出：
  - `tables/table_XXXX.csv`
  - `tables/table_XXXX.html`
- `manifest.json` 中已写入：
  - `table_count`
  - 各表 `table_id`
  - 页码范围
  - sidecar 路径
- 重新跑 ESP32-S3 样本验证：
  - 当前共导出 `71` 张表
  - 真实 sidecar 文件已落盘
  - 先前表格导出 deprecated warning 已修复

### 2026-04-12: Table References Linked Into Retrieval Layer
- 已将 table sidecar 与检索层打通：
  - `chunks.jsonl` 中相关 chunk 会携带 `tables`
  - `sections.jsonl` 中相关 section 会携带 `tables`
- 重新跑 ESP32-S3 样本后确认：
  - table sidecar 仍正常导出
  - 检索层已能直接给出对应 `tables/table_XXXX.(csv|html)` 引用

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
2026-04-12 继续推进：补了 document.md 表格 sidecar 注入的失败测试，下一步实现注入逻辑并补大 PDF 窗口缓存/恢复测试。
2026-04-12 继续推进：补了大 PDF 窗口缓存/恢复的失败测试，目标是支持窗口级 checkpoint 和重跑恢复。
2026-04-12 已实现表格 sidecar 注入和窗口缓存/恢复主逻辑，正在跑新增与受影响测试。
2026-04-12 修正了表格测试桩的 markdown 导出行为，继续复测表格注入与窗口缓存链路。
2026-04-12 已完成真实样本验证：ESP32-S3 文档表格 sidecar 已注入 document.md，_windows 缓存落盘，第二次复跑命中缓存；全量 28 项测试通过。
2026-04-12 已完成架构缺口复盘：重新对照 Docling 官方 chunking / batch / table / figure / visual grounding / OCR 文档，确认主线不变，但需要补 conversion signature cache、page images / visual grounding、figure metadata 和疑难页二级补救。
2026-04-12 开始实现 conversion signature cache：缓存现在会区分解析参数，避免配置变化时误复用窗口结果。
2026-04-12 已接入 document.html 导出，并把路径写入 manifest，作为更适合人工核对宽表/图片的阅读副产物。
2026-04-12 已增加 markdown 告警检测：对“表题后跟图片且无结构化 sidecar”的情况输出 alerts.json，显式标注标准 Docling 管线的局限。
2026-04-12 修正 alerts 检测器：现在能识别 `## Table ...` 这类 heading 形式的表题，不再漏报图片退化表格。
2026-04-12 收紧 alerts 表题规则：现在只匹配真正的 `Table <编号>. ...` caption，避免把正文句子误报为图片退化表格。
2026-04-12 已完成 ESP32-S3 与 STM32H743VI 样本复验：两者均可从窗口缓存复跑；ESP32-S3 识别出 1 条真实图片退化表格告警，STM32H743VI 在当前规则下无图片退化表格误报。
2026-04-12 开始实现 caption 恢复增强：对首行即表题、或 HTML 单列表头即表题的情况补回 manifest caption。
2026-04-12 下调默认分窗阈值到 300 页，使 357 页级数据手册也能获得窗口缓存与更稳的首轮执行。
2026-04-12 增加基于 document.md 上下文的 caption 回填：对 sidecar 已定位但 caption 为空的表，向上回溯最近合法表题补回 manifest caption。
2026-04-12 已完成确定性优化复验：STM32H743VI 默认改为双窗口缓存；caption 回填后 ESP32-S3 可稳定补回 4 条，STM32H743VI 可稳定补回 77 条。
2026-04-12 调整默认策略：缓存/分窗不再服务于中型一次性文档，默认仅在 1000+ 页文档上触发。
2026-04-12 修正分窗默认策略相关测试：1001 页以上默认分窗，缓存复用测试也同步到新阈值。
2026-04-12 修正 roundtrip 缓存测试期望值，使其与 1001 页默认分窗阈值测试数据一致。
2026-04-12 将缓存机制改为显式 opt-in：默认整本处理，不启用缓存；通过 --enable-window-cache 和 --cache-window-size 控制。
2026-04-12 TRM 完整转换后发现空表格 sidecar；新增 empty_table_sidecar 告警，避免 manifest 中存在不可用表文件时静默通过。
2026-04-12 完成 ESP32-S3 TRM 全量转换：1531 页、7 窗口、667 表、3775 chunks、1379 sections；新增 empty_table_sidecar 告警后捕获 9 个空/不可用表格 sidecar。
2026-04-12 完成 Docling 嵌入式手册处理架构文档收口：新增完整 architecture doc，并同步更新 README 与 AGENTS，明确产物、AI 使用流程、配置方式和 Docling 边界。
2026-04-12 Docling feature branch completed: fast-forward merged `feat/docling-batch-processor` into `main`, verified 39 tests on merged main, and pushed `origin/main` to 7230785.
