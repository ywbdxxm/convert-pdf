# Findings & Decisions

## Current Focus
- 当前主线已经从环境建设切到 `Docling Batch Program Design`。
- 现在的问题不再是“这台机器能不能跑 `Docling`”，而是“如何把多份嵌入式手册批量转成适合 AI 检索、引用和工程开发的资产”。

## Current State Snapshot
- 系统环境：
  - `Ubuntu 24.04.4 LTS` on `WSL2`
  - GPU: `RTX 4060 Laptop GPU`
  - `nvidia-smi` 正常
  - WSL CUDA bridge 存在：`/usr/lib/wsl/lib/libcuda.so*`
- 系统层已完成：
  - `docker`
  - `nvidia-container-toolkit`
  - `ninja-build`
  - `tesseract` 及基础开发包
  - Docker daemon 的代理配置与 `nvidia` runtime 配置
- 共享重型 AI base 已落地：
  - 路径：`/home/qcgg/.mamba/envs/ai-base-cu124-stable`
  - 已验证 `torch 2.5.1` 可见 GPU
- 项目层 `Docling` overlay 已落地：
  - 路径：`docling/.venv`
  - `docling 2.86.0` 可正常导入
  - overlay 中的 `torch` 来自共享 base，而不是项目层重复安装
- 镜像配置已修正并验证：
  - `pip`: `/home/qcgg/.config/pip/pip.conf`
  - `uv`: `/home/qcgg/.config/uv/uv.toml`
  - `conda/micromamba`: `/home/qcgg/.condarc`
- 关键文档与脚本已补齐：
  - `docs/architecture/2026-04-12-ai-workstation-design-audit.md`
  - `docs/architecture/2026-04-12-ai-workstation-execution-plan.md`
  - `docs/architecture/global-workstation-reference.md`
  - `scripts/bootstrap_ai_base.sh`
  - `scripts/bootstrap_docling_env.sh`
  - `scripts/verify_ai_stack.sh`
- 当前代码面现状：
  - 第一版 `Docling` 批处理程序已经落地到 `docling_batch/`
  - 当前仓库同时包含：
    - 环境 bootstrap / verify 脚本
    - `docling_batch` Python 包
    - `tests/` 单元测试
  - 批处理程序当前已能输出 `Docling JSON + Markdown + manifest + sections.jsonl + chunks.jsonl + run summary`

## Parsing Tool Conclusions
### Default local path
- 默认基线仍是 `Docling`。
- 原因：
  - 原生支持 Markdown / HTML / JSON 导出
  - 关注阅读顺序、表格、公式、OCR 等 PDF 关键痛点
  - Python API 直接，适合做批处理程序
  - `DocumentConverter` + `convert_all(...)` 很适合多文件转换与错误汇总

### Strong alternatives
- `Marker`：
  - 复杂表格、公式、版面保真要求更高时的优先增强方案
  - 适合进入后续 A/B 测试
- `MinerU`：
  - 扫描件、中文、多语言 OCR、复杂布局时更值得投入
  - 适合做第二条高保真备用管线
- `OpenDataLoader PDF`：
  - 值得认真测试的强候选解析器
  - 优点是本地 deterministic mode + 可选 hybrid mode + bounding boxes
  - 代价是 `Java + Python` 混合栈更重
- `PyMuPDF4LLM`：
  - 轻量 baseline 或快速 PoC 合适
  - 不是当前高保真主路线

### Cloud / API options
- `Mathpix`：学术/STEM 文档、复杂公式和双栏论文仍然很强。
- `Mistral OCR`：托管 API 路线里，OCR 到 Markdown 的链路很直接。
- `Azure Document Intelligence`：更偏企业级结构化抽取，不一定是最自然的 Markdown。
- `LlamaParse`：如果工作流本来就围绕 LlamaIndex / RAG，集成会更顺手。
- 当前判断：
  - 云端方案在扫描件、复杂视觉理解上可能上限更高
  - 但对“长期批量处理嵌入式手册”的默认工作流，本地方案仍更稳、更便宜、更可复现

## Embedded Manual Workflow Recommendation
- 最稳的协作结构不是单一产物，而是三层：
  - 原始 PDF：最终权威来源
  - `Markdown + JSON`：日常检索和引用层
  - 页级回查能力：处理表格、脚注、图、页码争议时兜底
- 建议的目录形态：
  - `manuals/raw/`
  - `manuals/md/`
  - `manuals/json/`
  - `manuals/index/`
  - `manuals/notes/`
- 当前仓库里已先落地最小目录骨架：
  - `manuals/raw/`
  - `manuals/processed/`
  - `manuals/raw/st/`
  - `manuals/raw/ti/`
  - `manuals/raw/nxp/`
  - `manuals/raw/adi/`
  - `manuals/raw/infineon/`
  - `manuals/raw/microchip/`
  - `manuals/raw/other/`
- 对嵌入式开发，真正高价值的不是“整本能读”，而是这些可稳定引用的资产：
  - 寄存器地址、位定义、复位值
  - 中断号与中断源
  - 时钟树与分频约束
  - GPIO alternate function 表
  - 初始化顺序与依赖约束
  - 时序、电气与工作条件限制

## Batch Program Direction
- 实现语言应保持为 `Python`。
- 第一版批处理程序建议基于 `DocumentConverter` 和 `convert_all(...)`。
- 第一版至少应输出：
  - `.md`
  - `.json`
  - 每次运行的成功/失败汇总
- 用户已将第一版范围收敛为：
  - `Markdown + JSON + manifest + 章节/页码级索引`
  - 第一阶段目标是“可查阅、可引用、可回溯”
  - 寄存器表、AF 表、时序约束等深结构化资产留到后续阶段
- 第一版功能建议包括：
  - 递归扫描输入目录
  - 每个 PDF 独立状态记录
  - 可选 `--ocr`
  - 可选 `--force-full-page-ocr`
  - 局部失败不阻断整批任务
  - 产出后续索引所需的文档级 metadata
- 当前设计建议：
  - `chunks` 不应采用纯固定长度切分
  - 更合适的是“章节优先，但设置最大长度上限”的混合切分
  - 目标是在保留章节语义和页码可回溯性的前提下，避免单个 chunk 过大，不利于后续检索和问答
- 当前真正待设计的是：
  - 多份手册应如何建立索引
  - 哪些内容保留原始 Markdown
  - 哪些内容应提升为结构化摘录或知识资产

## Docling Docs-Derived Best Practice
- 这是我基于 Docling 官方文档、官方 examples 和官方 RAG recipes 收敛出的当前最佳实践。
- 关键结论不是“直接把 PDF 转成一个 Markdown 文件”，而是：
  - 以 `DoclingDocument JSON` 作为权威结构化中间层
  - 以 `Markdown` 作为人类查阅层
  - 以 Docling 原生 chunkers 作为 RAG / embedding 层

### 1. Canonical artifact should be Docling JSON
- Docling 官方 batch example 明确把现代导出方式作为推荐路径，`USE_V2 = True` 并使用 `save_as_json` / `save_as_markdown` / `save_as_html` 等导出。
- LlamaIndex 示例里，`DoclingReader(export_type=JSON)` 配合 `DoclingNodeParser()`，说明官方集成本身也倾向保留 Docling 原生格式，再下游做 chunking / indexing。
- 对我们这类芯片手册项目，最佳实践应是：
  - 原始 PDF 保留
  - `Docling JSON` 作为权威中间表示
  - `Markdown` 作为日常阅读副产物
- 这意味着后续任何 chunk、索引、摘录，都应尽量从 `Docling JSON` 派生，而不是从 Markdown 反推。

### 2. For RAG, prefer native Docling chunking over Markdown-only splitting
- Docling `Chunking` 概念文档明确区分两条路线：
  - 先导出 Markdown，再自行切分
  - 直接在 `DoclingDocument` 上使用原生 chunkers
- 文档还明确说明 Docling 与 LlamaIndex 等框架的集成，是通过 `BaseChunker` 接口完成的。
- Haystack 示例也把 `ExportType.DOC_CHUNKS` 设为默认，而 `ExportType.MARKDOWN` 只是另一种模式。
- 对我们的嵌入式手册场景，最佳实践应是：
  - 不把“纯 Markdown 切块”作为主 RAG 路线
  - 主索引从 `DoclingDocument` 原生 chunking 得到
  - Markdown 主要保留给人工查阅和 diff

### 3. Default chunker should be HybridChunker aligned to the embedding tokenizer
- Docling 官方文档明确指出：在 RAG / retrieval 场景里，chunker 和 embedding model 应使用同一 tokenizer。
- `HybridChunker` 的官方定义是：先做基于文档结构的 hierarchical chunking，再按 tokenizer 做超长切分和可选的同 heading/caption 邻块合并。
- 这与我们前面讨论的“章节优先，但设置最大长度上限”本质一致。
- 对我们项目，最佳实践应是：
  - 默认 chunker 用 `HybridChunker`
  - tokenizer 与后续 embedding 模型严格对齐
  - `max_tokens` 可以显式设定；若不设，则由 tokenizer 推导
- 一个对我们后续程序设计很重要的点：
  - `BaseChunker` 除了 `chunk()`，还有 `contextualize(chunk)` 接口
  - 这个接口返回带 heading / caption / metadata 上下文的文本，官方明确说明它通常用于喂 embedding model 或 generation model
- 因此我们自己的 chunk 索引里，最佳实践不是只存一个 `text`，而是同时保留：
  - 原始 `chunk.text`
  - `chunker.contextualize(chunk)` 生成的 `contextualized_text`

### 4. Table-heavy manuals need special handling
- `HybridChunker` 文档专门说明了表格分块时的 `repeat_table_header=True` 默认行为，这会在跨块表格前重复表头，帮助保持上下文。
- `Advanced chunking & serialization` 示例展示了：
  - 默认表格序列化策略
  - 可切换到 `MarkdownTableSerializer`
- `Table export` 示例又展示了将表格单独导出为 CSV / HTML。
- 我的结论是：
  - 对芯片手册这类“寄存器表 / 参数表 / AF 表很多”的场景，主 chunk 流程应启用 Docling 原生表格 chunking
  - 对可读性更强的文本索引，可优先尝试 Markdown table 序列化
  - 同时保留表格 sidecar 导出（如 CSV / HTML）会更稳
- 这里最后一条是我基于官方 examples 做的工程推断：因为 Docling 同时提供了表格 chunking 定制和单独表格导出，两者结合最适合 datasheet 这类表格高价值文档。

### 5. Pictures and page images should be optional sidecars, not primary text
- Figure export 和 Visual grounding 示例都说明：
  - 可以开启 `generate_page_images` / `generate_picture_images`
  - 可以按页保存图片，也可以将图片以引用方式写入 Markdown / HTML
  - Visual grounding 的做法是把 `Docling JSON` 按 `binary_hash` 存起来，再将检索到的 chunk 反查回页图和 bbox
- 对我们项目，这意味着：
  - 第一版不需要把图片内容硬塞进主 Markdown
  - 但应保留可选的 page-image sidecar 能力
  - 这样后续遇到引脚图、框图、时序图、流程图时，可以做人工或 agent 回查
- 如果后面我们确实需要更强的图示理解，再考虑 picture description / visual grounding 管线。

### 6. OCR should be conditional, not always-on
- Force full page OCR 示例明确说明：
  - `force_full_page_ocr=True` 会让整页纯 OCR，通常比混合检测更慢
  - 适合扫描件或布局抽取不可靠的 PDF
- GPU support 页面明确提到当前已知可工作的 GPU OCR 方案是 `RapidOCR` 的 torch backend。
- 对我们项目，最佳实践应是：
  - 默认数字版 datasheet / app note：不开 `force_full_page_ocr`
  - 对扫描件、老旧 PDF、图片化章节：按文档或按运行参数启用 OCR
  - 真要上 GPU OCR，再优先评估 `RapidOCR(backend="torch")`

### 7. Batch processing should follow the official convert_all pattern
- 官方 `batch_convert` 示例使用：
  - `DocumentConverter(...)`
  - `convert_all(input_doc_paths, raises_on_error=False)`
  - 按 `ConversionStatus` 处理 `SUCCESS / PARTIAL_SUCCESS / FAILURE`
- 对我们项目，最佳实践应是：
  - 整批任务不因单文件失败而整体终止
  - 每个 PDF 记录状态、错误、耗时和输出位置
  - 最终生成一个 run-level summary / manifest

### 8. Framework-specific RAG integrations should stay downstream
- 官方 examples 展示了 Haystack、LlamaIndex、LangChain、OpenSearch、Milvus、Weaviate、Qdrant、visual grounding 等多条集成路线。
- 这些示例更像“下游消费方式”，不是我们第一版批处理程序应耦合进去的核心产物。
- 所以对我们仓库，最佳实践应是：
  - 第一版先产出框架无关的 durable artifacts
  - 如果后续接 LlamaIndex / LangChain，再让它们消费我们的 `Docling JSON + native chunks`
  - 不要让第一版输出格式被某一个框架绑定

### Practical recommendation for this repository
- 结合 Docling 官方文档和我们的嵌入式目标，我现在的最终建议是：
  - `PDF -> DoclingDocument JSON` 作为 canonical source
  - 同时导出 `Markdown` 供人工阅读
  - 用 `HybridChunker` 从 `DoclingDocument` 直接生成 chunk
  - chunk 中同时保存 `text` 与 `contextualized_text`
  - 对表格保留更强 sidecar 导出能力
  - 对页图/图示保留可选 visual-grounding sidecar
  - OCR 做成按文档/按参数启用的模式，而不是默认总开
- 这套做法比“只导出 Markdown 再自己切块”更贴近 Docling 官方 RAG 路线，也更适合后面让我做带引用、可回溯的嵌入式开发辅助。

## Current Implementation Result
- 已实现的主入口：
  - `docling/.venv/bin/python -m docling_batch convert --input ... --output ... --device cuda`
- 当前实现的核心行为：
  - 递归发现 PDF
  - 用 Docling `convert_all(..., raises_on_error=False)` 批处理
  - 导出 `document.json`
  - 导出 `document.md`
  - 用 `HybridChunker` 直接从 `DoclingDocument` 生成原生 chunk
  - 保存 `contextualized_text`
  - 汇总 `sections.jsonl`
  - 写入每文档 `manifest.json`
  - 写入批处理级 `run summary`
- 已验证的 smoke 路径：
  - `--device cuda --no-ocr` 可在最小 PDF 上成功落盘全部输出
- 已观察到的真实 GPU/OCR 行为：
  - Docling 当前环境触发 OCR 时会实际走 `RapidOCR` 的 `torch` backend
  - 日志中已确认使用 `GPU device 0`
  - 首次 OCR 运行会下载 RapidOCR 模型，因此 OCR 必须保持显式、可控，而不是默认强制开启

## Current PDF Processing Pipeline
- 当前处理流程可以概括为：
  - `CLI 参数 -> RuntimeConfig -> PDF 发现 -> 可选页窗切分 -> Docling 转换 -> 文档合并 -> Markdown/JSON 导出 -> native chunking -> sections/chunks 索引 -> run summary`
- 更细一点：
  1. `docling_batch.cli` 解析输入目录、GPU/OCR、图片模式、chunk 上限、页窗大小等参数。
  2. `RuntimeConfig` 固化本次运行的全部处理配置。
  3. `discover_pdf_paths()` 递归发现输入中的 PDF。
  4. 对每个 PDF：
     - 若未启用页窗：整本走一次 `DocumentConverter.convert_all(...)`
     - 若启用页窗：先计算 `(start, end)` 页段，再按每个页窗调用 `convert_all(..., page_range=...)`
  5. 若存在多个页窗结果，则通过 `DoclingDocument.concatenate(...)` 合并为单个逻辑文档。
  6. 从合并后的文档导出：
     - `document.json`
     - `document.md`
  7. 对同一个合并文档使用 `HybridChunker` 生成 native chunks。
  8. 对每个 chunk 生成：
     - `text`
     - `contextualized_text`
     - `heading_path`
     - `page_start/page_end`
     - `citation`
  9. 再把 chunks 聚合为 `sections.jsonl`。
  10. 最终写入每文档 `manifest.json` 和整批 `_runs/*.json`。
- 当前这条链路里，真正的 canonical source 仍然是：
  - 合并后的 `DoclingDocument JSON`
- Markdown、sections、chunks 都是从这个 canonical source 派生出来的。

## How I Actually Use The Final Artifacts
- 对后续嵌入式开发，我不会把所有产物等权看待。
- 当前最合理的使用优先级是：
  1. `chunks.jsonl`
  2. `sections.jsonl`
  3. `document.md`
  4. 原始 PDF / 页图 / 图片 sidecar
  5. `document.json`
- 其中：
  - `chunks.jsonl` 是我最常用的“检索和引用层”
  - `sections.jsonl` 是我快速找主题位置的“导航层”
  - `document.md` 是我需要连续阅读上下文时的“阅读层”
  - 原始 PDF / 页图 / 图片 sidecar 是我遇到表格、图、脚注争议时的“证据层”
  - `document.json` 是最完整的 canonical source，更适合程序化派生，不是我日常第一眼去读的层

## What A Chunk Actually Is
- `chunk` 不是“随便切的一段文本”。
- 在当前实现里，`chunk` 是：
  - 从 `DoclingDocument` 原生结构上切出来的一个检索单元
  - 尽量保持章节语义
  - 同时受到 token 长度上限约束
- 它至少带这些信息：
  - `text`
  - `contextualized_text`
  - `heading_path`
  - `page_start/page_end`
  - `citation`
- 对我后续查手册来说，chunk 的作用是：
  - 先把“可能相关的证据片段”尽量缩到一个可读、可引用的小范围
  - 而不是每次都去读整章或整本 PDF

## Is document.md With Images Necessary
- 结论不是“完全没必要”，也不是“它应该成为主入口”。
- 更准确的定位是：
  - `document.md` 不是主检索层
  - 但它是非常有价值的阅读副本
- 我会不会看它：
  - 会
  - 但通常不是第一步
- 典型工作流是：
  - 先查 `chunks.jsonl`
  - 再看 `sections.jsonl`
  - 如果需要连续上下文，再打开 `document.md`
  - 如果 chunk 或 markdown 里涉及图、复杂表、脚注争议，再回到原始 PDF 或图片 sidecar
- 所以图片在 `document.md` 中有没有必要：
  - **有必要，但只对高价值图片有必要**
  - 不应该无图
  - 也不应该把二维码、页脚条、页码装饰这类噪声图片塞进去
- 还有一个很重要的现实约束：
  - `document.md` 里的图片即使保留了，也常常不是最清晰、最权威的图源
  - 对框图、时序图、复杂表格，Markdown 图片更适合当“快速线索”，不适合作为最终判定依据
  - 真到需要精确读图时，我更应回到原始 PDF、页图 sidecar，或更高分辨率的定向导出图

## What You Need To Send Me Later
- 是的，后续如果你让我做嵌入式开发，通常你直接给我产物路径就可以。
- 最实用的最小输入通常是：
  - 原始 PDF 路径
  - 对应处理结果目录路径，例如 `manuals/processed/<doc_id>/`
  - 你想解决的问题，例如“看 boot strap pin”“核对 ADC timing”“写 I2C 初始化”
- 如果你已经知道相关章节或页码，再补这些会更快：
  - `section` 名称
  - 页码范围
  - 芯片 revision
- 对我来说，最理想的协作输入是：
  - `manuals/raw/...pdf`
  - `manuals/processed/<doc_id>/`
  - 明确的问题描述

## Relationship To RAG
- 我当然知道 RAG。
- 当前我们做的事，不等于完整的 RAG 系统；更准确地说，当前做的是：
  - **RAG 的上游语料准备层 / parsing layer / evidence packaging layer**
- 一个完整 RAG 系统通常还包括：
  - embedding
  - 向量索引或检索引擎
  - query orchestration
  - reranking / answer synthesis
- 当前这套产物主要解决的是：
  - PDF 解析质量
  - chunk 质量
  - page-aware citation
  - 表格/图片/章节结构保留
- 这些问题恰恰是很多成熟 RAG 软件本身不替你解决的。
- 所以当前工作和成熟 RAG 软件不是替代关系，而是上下游关系：
  - 我们现在做的是“把脏 PDF 变成高质量可检索证据”
  - 成熟 RAG 软件是“拿这些证据去做检索与问答系统”
- 为什么现在不直接只用成熟 RAG 软件：
  - 因为对嵌入式手册场景，真正的瓶颈往往不是向量库，而是 PDF 解析和证据质量
  - 如果上游 chunk、页码、表格、图都不可靠，RAG 系统只会更快地检索到不可靠内容
  - 也就是说，这里典型是 `garbage in, garbage out`
- 但这不代表以后不用 RAG 软件：
  - 等当前这套产物形态稳定后，完全可以把 `chunks.jsonl` / `sections.jsonl` / `document.json` 接进成熟 RAG 软件
  - 那时你得到的是“高质量手册语料 + 成熟检索框架”的组合，而不是二选一

## What Docling Official RAG Examples Actually Do
- Docling 官方 examples 里的 RAG 路线，本质上都是同一个模式：
  1. 用 Docling 读入 PDF
  2. 选择一种导出形式：
     - `Markdown`
     - 或 `DOC_CHUNKS` / `JSON`
  3. 做 node/chunk 切分
  4. 做 embedding
  5. 写入向量库 / 检索引擎
  6. 用 query + retriever + LLM 形成完整 RAG 链

### Haystack example
- 官方 `RAG with Haystack` 示例用的是：
  - `docling-haystack`
  - `MilvusDocumentStore`
  - `SentenceTransformersDocumentEmbedder`
  - `MilvusEmbeddingRetriever`
  - `HuggingFaceAPIGenerator`
- 它提供两条 ingestion 路：
  - `ExportType.MARKDOWN`
  - `ExportType.DOC_CHUNKS`（官方默认）
- 在 `DOC_CHUNKS` 模式下，它直接给 `DoclingConverter` 传：
  - `chunker=HybridChunker(tokenizer=EMBED_MODEL_ID)`
- 也就是说，官方更偏向：
  - 直接用 Docling native chunks 进向量库
  - 而不是先转 Markdown 再自己乱切
- 官方还特别强调一点：
  - 这种模式能保留 document-native grounding
  - 检索结果里还能看到页码、bbox 之类的 grounded metadata

### LangChain example
- 官方 `RAG with LangChain` 示例的结构和 Haystack 本质一样：
  - `DoclingLoader`
  - `HybridChunker(tokenizer=tokenizer)`
  - `Milvus.from_documents(...)`
  - `retriever = vectorstore.as_retriever(...)`
  - 再接 retrieval chain
- 它同样体现了一个关键点：
  - 在 LangChain 里，Docling 主要负责“高质量文档加载 + chunking”
  - LangChain 负责“向量库 + retriever + LLM chain”

### LlamaIndex example
- 官方 `RAG with LlamaIndex` 示例给了两条路：
  1. Markdown 路：
     - `DoclingReader()` 默认导出 Markdown
     - `MarkdownNodeParser()`
  2. JSON / Docling-native 路：
     - `DoclingReader(export_type=DoclingReader.ExportType.JSON)`
     - `DoclingNodeParser()`
- 这说明官方自己也承认：
  - `Markdown` 路是更简单、更通用的
  - `JSON + DoclingNodeParser` 路是更 Docling-native、更保结构的
- 这和我们当前坚持 `document.json` 作为 canonical source 的方向一致

### Visual grounding example
- 官方 `Visual grounding` 例子做得更进一步：
  - 先把每个 `DoclingDocument` 存成 `binary_hash.json`
  - 检索时不只拿文本 chunk
  - 还通过 `binary_hash` 再回查完整 `DoclingDocument`
  - 然后拿到页图、bbox、原始位置去做 grounded presentation
- 这条路说明：
  - 在官方眼里，好的 RAG 不只是“返回文本”
  - 还应该能回到原始文档上的具体位置
- 这也是为什么我一直强调：
  - `document.json` 和原始 PDF 都必须保留

### Hybrid chunking example
- 官方 `Hybrid chunking` 示例最重要的点不是怎么打印 chunk，而是它明确展示了：
  - `chunk.text`
  - `chunker.contextualize(chunk)`
- 也就是说，官方建议 embedding / generation 时，不一定直接喂裸 `chunk.text`
  - 很多时候应喂带 heading/context 的 `contextualized_text`
- 这就是我们当前在 `chunks.jsonl` 里保留 `contextualized_text` 的根本原因

### Advanced chunking & serialization example
- 官方这里展示了：
  - 可以自定义 serializer provider
  - 比如用 `MarkdownTableSerializer()`
- 这说明 Docling 官方并不是只给一个固定 chunking 方案
  - 它允许你针对表格、序列化方式做定制
- 对我们这类芯片手册项目，这意味着：
  - 真正成熟的方案，最终很可能是“Docling native chunking + 针对表格的定制序列化”

## Difference Between Their RAG Examples And Our Current State
- 官方 examples 已经是完整或半完整的 RAG demo：
  - 有 embedding
  - 有 vector store
  - 有 retriever
  - 有 query/answer chain
- 我们当前还停在上游证据层：
  - 重点是高质量解析
  - 高质量 chunk
  - 引用与页码
  - 图片和表格保留
- 所以两者差异不在“方向不同”，而在“我们目前只做到 RAG ingestion 前半段”

## What This Means For Us
- 官方 examples 其实进一步印证了我们当前路线没走偏：
  - 官方默认偏 `DOC_CHUNKS`
  - 官方强调 `HybridChunker`
  - 官方强调 grounded metadata
  - 官方有 `JSON + DoclingNodeParser` 路线
- 如果后面要真正接成熟 RAG 软件，最自然的升级顺序是：
  1. 先把当前 PDF parsing / chunk / image filtering / large PDF windowing 做稳
  2. 再选择一个成熟框架：
     - Haystack
     - LangChain
     - LlamaIndex
     - 或直接接 Milvus / Qdrant / Azure AI Search / OpenSearch
  3. 把当前 `document.json` / `chunks.jsonl` 变成其 ingestion 输入

## Final Best Practice For Embedded Manual Use
- 如果目标被严格收敛为：
  - “让我后续做嵌入式开发时，能更准确、更方便、更迅速地查阅参考手册”
- 那当前最合理的完整最佳实践就是：
  1. 保留原始 PDF 作为最终权威来源
  2. 用 Docling 生成 `document.json` 作为 canonical source
  3. 同时导出 `document.md` 作为阅读副本，但不把它当唯一真相
  4. 用 `HybridChunker` 直接在 `DoclingDocument` 上生成 native chunks
  5. 保留 `contextualized_text + page range + citation`
  6. 用 `sections.jsonl` 做导航层，用 `chunks.jsonl` 做主检索层
  7. 对图像采用“高价值图保留、低价值图过滤、原 PDF 作为终局证据”的策略
  8. 对超大 PDF 优先程序内部分窗，而不是手工拆书签
  9. OCR 按需启用，不默认总开
  10. 当这套上游证据层稳定后，再接成熟 RAG 框架，而不是反过来

## Real Sample Test: ESP32-S3 Datasheet
- 已对真实样本执行：
  - `manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf`
  - 运行参数：`--device cuda --no-ocr`
- 结果：
  - 处理成功
  - `page_count = 87`
  - 输出目录：`manuals/processed/esp32-s3-datasheet-en/`
  - 生成了：
    - `document.json`
    - `document.md`
    - `manifest.json`
    - `sections.jsonl`
    - `chunks.jsonl`
    - `_runs/20260412T063932Z.json`
- 当前样本的索引规模：
  - `sections.jsonl`: 145 条
  - `chunks.jsonl`: 444 条
- 正向观察：
  - 主体章节抽取基本有效，例如 `Product Overview`、`CPU and Memory`、`4.1.3.5 Power Management Unit (PMU)` 等都形成了可引用 section/chunk
  - `manifest.json` 中记录了原文件路径、sha256、页数、GPU 设备选择和输出路径
  - `chunks.jsonl` 中已经包含 `heading_path`、`page_start/page_end`、`contextualized_text`、`citation`
- 当前暴露出的优化点：
  - `Contents`、`List of Tables`、`List of Figures` 这类目录/索引页进入了 chunks，后续应考虑增加过滤策略
  - `Note:`、`Cont'd from previous page`、`CPU Clock` 这类 heading 有时被单独提升为 section，说明还需要做一层后处理归并/去噪
  - 运行时出现过一次 tokenizer 长度 warning：`799 > 512`
  - 这说明当前应为 `HybridChunker` 增加更明确的默认 `max_chunk_tokens`，避免后续 embedding 阶段出现超长 chunk

## Large PDF Handling Recommendation
- 基于第一性原理和当前 Docling 路线，我的默认建议是：
  - **不要先按书签拆 PDF**
  - 优先保留整本手册作为单个 canonical document 处理
- 原因：
  - revision、章节层级、交叉引用、页码语义会更完整
  - 我们已经用 `sections.jsonl` 和 `chunks.jsonl` 去解决“大文档难查阅”的问题
  - 先拆 PDF 往往会让引用链断掉，后续回查原文更麻烦
- 只有在这些场景下，拆分才更合理：
  - 一个 PDF 实际上拼了多本不同手册或不同器件资料
  - 超大扫描件/OCR 文档导致速度、显存或稳定性明显恶化
  - 附录、封装图库、法务页等大段内容长期无用，且确实干扰处理
- 更稳的策略是：
  - 先整本转换
  - 再用章节级/chunk 级索引做后续检索
  - 只有当真实样本显示整本处理效果或成本不可接受时，再增加“按书签/页段拆分”的预处理步骤
- 当前实现已经开始向这个方向收敛：
  - 新增了 `--page-window-size`
  - 程序可在内部对单个 PDF 按页窗调用 Docling
  - 各窗口结果会尝试通过 `DoclingDocument.concatenate(...)` 合并回单个逻辑文档
  - `manifest.json` 会记录窗口数量和每个窗口的页段状态
- 当前阶段的诚实结论：
  - 行为正确性已经通过单元测试锁住
  - 真实样本上的长时间窗口化 smoke 仍偏慢，后续还需要继续做性能量化与进一步优化
- 一个关键澄清：
  - **分页窗处理的目标首先是“降低单次处理风险、降低内存/失败面”，不是“让中等 PDF 更快”**
  - 对 80~100 页这类文档，单次整本处理通常更快
  - 对 5000+ 页这类文档，整本处理可能直接变得不稳或不可完成，这时分窗的价值才会体现出来
- 当前为什么“加了分窗反而看起来跑不完”：
  - 当前实现会对每个页窗单独调用一次 Docling 转换
  - 每个窗口都要重复支付一次 pipeline 启动/推理调度开销
  - 当前输出是全部窗口结束后再统一写文件，因此处理中间不会逐步落盘，容易让人感觉“没有进展”
  - 当前版本是“稳态优先的朴素分窗实现”，还不是“吞吐最优实现”

## Image Noise Filtering Direction
- 当前我们已经确认：并不是所有图片都值得进 Markdown。
- 典型噪声包括：
  - 二维码
  - 页脚反馈条
  - 页码角标附近的小条带图
- 从 ESP32-S3 样本的图片元数据看，这类噪声通常具备：
  - 无 caption
  - 面积很小
  - 位于页脚或边角
  - 有时长宽比极端
- 当前结论：
  - “图片 sidecar + Markdown 引用”方向是对的，比纯占位符更适合手册查阅
  - 但后续必须补一层图片过滤，不能把所有图片无差别放进 Markdown
- 当前实现已新增第一轮启发式图片过滤：
  - 无 caption 且面积很小的图会被直接丢弃
  - 页脚/页眉附近的小图也更容易被过滤
- 在 ESP32-S3 样本上，第一页二维码已被成功移除，而功能框图仍被保留
- 但用户这次指出了一个很重要的细节：
  - 二维码这类图片噪声，当前已经不再作为图片出现在 `document.md`
  - 但 `Submit Documentation Feedback` 这类页脚噪声，当前往往不是图片残留，而是被 Docling 当成普通文本/链接抽取进了正文
- 这意味着后续噪声治理需要分成两类：
  - 图片噪声过滤
  - 页脚/页眉文本噪声过滤
- 还发现了一个实现问题：
  - 当前版本在 `document.md` 中写入了图片引用路径
  - 但本次实际输出目录里没有对应 `artifacts/` 目录
  - 这说明当前“Markdown 图片引用”和“sidecar 图片真正落盘”之间还不够一致
  - 后续需要把“保留哪些图片”和“最终真正写哪些图片文件”统一起来，而不是只改 Markdown 引用
- 基于用户这次反馈，当前图片策略需要进一步收敛：
  - 对“让我后续更准确查阅参考手册”这个目标来说，**误删重要图片的代价高于保留一些噪声图的代价**
  - 因此 `document.md` 作为重要阅读副本时，更合理的默认策略应是：
    - **Docling 识别到的图片默认全部保留到 Markdown**
    - 使用更清晰的引用式 sidecar 图片
    - 不在源生成阶段做激进图片过滤
  - 图片过滤若要做，应放到后续更高层的阅读 UI / 下游消费层，而不是先动 canonical reading artifact
- 同时有一个必须修复的工程问题：
  - 当前 Markdown 里的图片引用路径写成了相对 `document.md` 的嵌套路径
  - 这导致 `artifacts/` 被写在 `manuals/processed/<doc_id>/manuals/processed/<doc_id>/artifacts/`
  - 后续必须改成真正相对 `document.md` 的短路径，例如 `artifacts/<filename>`

## Current Image / Markdown Best Practice
- 针对你当前目标，重新收敛后的最佳实践是：
  - `document.md` 继续保留图片引用
  - 默认保留 Docling 识别出的全部图片
  - 图片使用 sidecar 引用，不内嵌 base64
  - 提高清晰度，例如 `image_scale=2.0` 或更高
  - 不把页码装饰图、二维码这类对象在源生成阶段硬删掉，除非后续有非常可靠的语义级过滤
- 原因：
  - `document.md` 对我后续查阅确实很重要
  - 图像漏掉一张关键框图/时序图，损失比多留一张二维码更大
  - 图片噪声虽然烦，但原始阅读副本更应偏完整，而不是偏激进清洗
- 当前实现已经与这个方向对齐：
  - 默认 `image_filter = off`
  - `document.md` 中默认保留 Docling 识别到的图片引用
  - sidecar 图片路径已修正为真正相对 `document.md` 的 `artifacts/<filename>`
  - 实际输出目录现在是：
    - `manuals/processed/<doc_id>/artifacts/`
    - 而不再是之前错误的嵌套路径

## Page Number Clarification
- 页码本身不是无用信息。
- 需要区分两件事：
  - **页码元数据 / citation / page_start-page_end**
    - 非常重要
  - **页脚里被抽成正文噪声的页码文本**
    - 基本无价值
- 所以应该保留的是：
  - 页码语义
  - 页码元数据
- 不应该保留的是：
  - 页脚版式噪声

## Current Large-PDF Default Behavior
- 当前默认配置下：
  - `page_window_size = 250`
  - `page_window_min_pages = 500`
- 这意味着：
  - 像 `87` 页的 datasheet，不会误走分窗路径
  - 像未来 `5000+` 页的超大 PDF，才会触发程序内部分窗
- 这更符合“中小文档快，大文档稳”的目标

## Workstation Architecture Conclusions
- 当前长期分层已经收敛为：
  - Host OS
  - WSL system layer
  - Docker / NVIDIA runtime layer
  - shared heavy AI base
  - project overlay environment
  - project data / artifacts
- 依赖分类规则已经明确：
  - 系统级可复用基础设施
  - 共享重型 AI 依赖
  - 项目私有依赖
- 当前仓库与全局规则都偏向：
  - 系统层只放跨项目基础设施
  - 重型 `torch + CUDA` 只保留一个共享 base
  - 项目层用轻量 overlay 复用共享 base
  - 大缓存、模型和产物尽量放仓库外
  - 不在 shell 启动文件里自动激活项目环境

## Environment Implementation Findings
- `uv + PyPI CUDA wheels + pypi.nvidia.com` 这条共享 base 路线在当前网络条件下不够稳。
- 因此共享重型 AI base 改为 `micromamba` 管理。
- 在 `venv --system-site-packages` overlay 方案里：
  - `uv pip install` 没有正确复用继承来的 `torch`
  - 它会重新解析并尝试下载一整套新的 `torch + CUDA` 依赖
- `pip install` 在同一 overlay 场景里能正确识别共享 `torch`。
- 因此当前可工作的组合是：
  - 共享重型 base：`micromamba`
  - 项目 overlay：`venv --system-site-packages`
  - overlay 安装器：`pip`
- 当前没有安装完整 CUDA toolkit / `nvcc`，这是有意选择：
  - 当前负载只需要运行时 GPU 支持
  - 还没有需要自定义 CUDA 编译的场景

## Key Decisions
| Decision | Current conclusion |
|----------|--------------------|
| 默认本地解析器 | `Docling` |
| 高保真增强方案 | `Marker` |
| 扫描件 / 多语言备选 | `MinerU` |
| 共享重型 AI base 管理器 | `micromamba` |
| 项目 overlay 安装策略 | `venv --system-site-packages` + `pip` |
| 仓库内项目目录布局 | 直接放根目录，如 `docling/` |
| 大模型与缓存位置 | 尽量放仓库外 |
| 全局工作站长文档 | `/home/qcgg/.codex/docs/ai-workstation-architecture.md` |

## Active Open Questions
- 多手册索引应按 `vendor / chip / peripheral / chapter` 建，还是先做更扁平的 chunk 索引？
- 哪些内容应保留为接近原文的 Markdown，哪些内容应提升为结构化摘录？
- 为了支撑“写代码前先引用手册”这一工作流，最小可用数据 schema 应该长什么样？
- 何时应该把 `Marker`、`MinerU` 或 `OpenDataLoader PDF` 正式拉进同一批样本做 A/B？

## Historical Notes Worth Keeping
- 早期 `uv` 方案留下的共享 base 路径和半成品环境已经作废；当前唯一权威共享 base 是 `/home/qcgg/.mamba/envs/ai-base-cu124-stable`。
- 早期沙箱 `fetch` 网络问题已被诊断并改善到“日常可用”状态，但它已经不是当前主线阻塞项。

## References
- Marker: https://github.com/datalab-to/marker
- Docling: https://www.docling.ai/
- MinerU: https://github.com/opendatalab/MinerU
- PyMuPDF4LLM: https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html
- OpenDataLoader PDF: https://github.com/opendataloader-project/opendataloader-pdf
- Mathpix: https://mathpix.com/pdf-to-markdown
- Mistral OCR: https://docs.mistral.ai/capabilities/document_ai/basic_ocr/
- Azure Document Intelligence Markdown: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/markdown-elements?view=doc-intel-4.0.0
- LlamaParse: https://docs.llamaindex.ai/
