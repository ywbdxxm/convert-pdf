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

## ESP32-S3 Accuracy Audit
- 我对 `manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf` 和当前产物做了针对性对照，抽查了：
  - 第 1 页：封面信息
  - 第 2 页：图文混排页
  - 第 27 页：大表格页
  - 第 64 页：典型正文 + 表格 + 页脚噪声页
- 当前结论：
  - **标题与正文连续文本：整体表现良好**
  - **图像保留：当前方向正确，阅读副本价值明显提升**
  - **大表格页：仍明显不理想**
  - **页脚文本噪声：阅读层仍存在，但检索层已做过滤**

### 1. 标题与正文
- 第 1 页和第 2 页对照结果显示：
  - 标题层级基本正确
  - 正文主叙述基本保住
  - 产品概述、功能描述等连续文本已足够用于后续查阅
- 对后续嵌入式开发，这一层已经可用。

### 2. 图像
- 第 2 页功能框图在 `document.md` 中已被保留，方向正确。
- 这比之前只留 `<!-- image -->` 占位符明显更适合后续查阅。
- 图像路径现在也已修正为相对 `artifacts/`，这点已经工程上闭环。

### 3. 大表格页
- 第 27 页 `Table 2-9. Peripheral Pin Assignment` 目前仍然偏弱：
  - 原 PDF 是一个大型矩阵表
  - 当前 `document.md` 中更多表现为图片 + 很短的尾注文本
  - 这不够支持后续直接从 Markdown 里精确读 pin matrix
- 这说明当前对“非常复杂的宽表/矩阵表”，Docling 这条默认主线仍有局限。
- 对这类页面，后续最值得补的是：
  - 表格 sidecar 导出
  - 或对宽表做更专门的保留/对照策略

### 4. 页脚噪声
- 第 64 页对照结果显示：
  - `document.md` 中仍保留 `Submit Documentation Feedback`
  - 这与原 PDF 页脚一致
- 当前这不是 bug，而是当前“阅读层尽量完整”的设计结果。
- 同时，检索层已经对这类噪声做了过滤：
  - `chunks.jsonl` / `sections.jsonl` 中不再保留它
- 这说明我们当前已经实现：
  - 阅读层偏完整
  - 检索层偏干净

## Current Docling Assessment
- 如果问题是“当前 Docling 对这类 ESP32 datasheet 到底怎么样”，我的结论是：
  - **做主线基础方案是合格的**
  - 尤其在：
    - 标题
    - 连续正文
    - 页码 grounding
    - 图像保留
    - canonical JSON
  - 上表现已经足够支撑后续查阅型工作流
- 但它当前仍然不是“所有页面都高保真”：
  - 最大短板仍在宽表/复杂矩阵表
  - 以及阅读层里的页脚 boilerplate

## Highest-Value Next Optimizations
- 基于这次真实对照，后续最值得做的优化顺序是：
  1. 大表格 / 宽矩阵表的 sidecar 保留策略
  2. 超大 PDF 性能量化与窗口策略优化
  3. 如有必要，再评估是否引入第二条高保真补充管线（如 Marker / MinerU）专门处理复杂表格页面

## Table Optimization Strategies
- 针对宽表/矩阵表，最合理的优化不是只盯着 `document.md` 本身，而是做“多层表格保留”。
- 当前最可行的策略分为 4 层：

### 1. Markdown inline table
- 适用于：
  - 行列不多
  - 宽度适中
  - 单页内可读
- 优点：
  - 直接可读
  - 对检索友好
- 缺点：
  - 对 pin matrix、AF table、宽时序表通常不够稳

### 2. Table sidecar as HTML / CSV
- 这是当前最值得优先补的策略。
- 官方 `export_tables` 示例明确支持：
  - `table.export_to_dataframe(...)`
  - 导出 CSV / HTML
- 对我们项目，建议是：
  - 每张检测到的表都导出 sidecar：
    - `tables/<table_id>.html`
    - `tables/<table_id>.csv`
  - `document.md` 中保留表格出现位置和对 sidecar 的引用
- 这样即使 Markdown 本体不够理想，表格也还有独立、高可读的保底版本。

### 3. Table image sidecar
- 对非常宽、非常复杂、排版依赖强的表，可以进一步保留：
  - 表格截图
  - 或表格区域图片
- 这对 pin matrix / AF matrix / 信号映射表很有价值。
- 因为这类表哪怕 CSV/HTML 导出来了，也可能仍然缺少某些视觉结构感。

### 4. Structured table extraction later
- 更后续的阶段，可以针对高价值表做结构化抽取：
  - pin assignment schema
  - AF table schema
  - register bitfield schema
  - timing parameter schema
- 但这已经不是当前第一阶段主线，应该建立在前 3 层稳定之后。

## Recommended Table Best Practice
- 对当前项目，我建议最终采用：
  - Markdown 中保留表格位置和简要可读内容
  - 同时导出 HTML/CSV sidecar
  - 对特别宽的表，再保留图片 sidecar
- 这样后续我做嵌入式开发时的工作流会是：
  - 先从 `chunks.jsonl` 定位到表所在 section/page
  - 再看 `document.md` 获取上下文
  - 如需精确读表，优先打开 table sidecar
  - 最后必要时回原始 PDF

## Current Table Sidecar Result
- 当前这条策略已经实际落地：
  - 每张 Docling 识别到的表都会导出：
    - `tables/table_XXXX.csv`
    - `tables/table_XXXX.html`
  - `manifest.json` 中会记录：
    - `table_count`
    - 每张表的 `table_id`
    - 页码范围
    - `csv_path`
    - `html_path`
- 在 ESP32-S3 当前样本上：
  - 已实际导出 `71` 张表的 sidecar
  - 这明显提升了“宽表/矩阵表可精读性”的保底能力
- 当前又进一步打通了检索层和表格 sidecar 的关系：
  - `chunks.jsonl` 中与某张表页码重叠的 chunk，会附带 `tables` 字段
  - `sections.jsonl` 中与某张表页码重叠的 section，也会附带 `tables` 字段
- 这意味着后续我查到某个 chunk/section 时，已经能直接知道相关 table sidecar 在哪，而不是只能靠页码再手工跳转

## What Docling Features We Are Using Right Now
- 当前代码里实际用到的 Docling 核心能力包括：
  - `DocumentConverter`
  - `PdfFormatOption`
  - `ThreadedStandardPdfPipeline`
  - `ThreadedPdfPipelineOptions`
  - `convert_all(..., raises_on_error=False, page_range=...)`
  - `DoclingDocument.concatenate(...)`
  - `save_as_json(...)`
  - `save_as_markdown(...)`
  - `HybridChunker`
  - `chunker.contextualize(chunk)`
  - `PdfPipelineOptions`
  - `AcceleratorOptions`
  - `RapidOcrOptions` / `TesseractCliOcrOptions`
- 当前真正还没有用到的 Docling 路线包括：
  - `VlmPipeline`
  - `VlmConvertOptions`
  - `VlmPipelineOptions`
  - 远程 VLM / vLLM API runtime

## GPU Optimization Judgement
- 结合官方文档，当前更适合我们的 GPU 优化路线是：
  - `ThreadedStandardPdfPipeline + ThreadedPdfPipelineOptions`
- 这是官方 `gpu_standard_pipeline` 示例的路线。
- 它适合：
  - 标准 PDF 解析主线
  - 本地 GPU
  - 强调吞吐和稳态
- 这比当前直接考虑 `gpu_vlm_pipeline` 更适合作为下一步优化。
- 当前实现已经切换到这条路线：
  - GPU 下默认使用 `ThreadedPdfPipelineOptions`
  - 默认 GPU batch 配置为：
    - `layout_batch_size = 32`
    - `ocr_batch_size = 4`
    - `table_batch_size = 4`
- 这意味着当前真正可用的 GPU 优化点包括：
  - `AcceleratorOptions(device="cuda")`
  - `RapidOCR(backend="torch")` 在 OCR 路径上的 GPU 加速
  - `ThreadedStandardPdfPipeline` 在标准 PDF 解析主线上的吞吐优化

## Current Large-PDF Usability Improvements
- 当前已经新增窗口级进度输出：
  - 例如 `[esp32-s3-datasheet-en] window 1/1 pages 1-87`
- 这让后续处理超大 PDF 时，不再像之前那样“长时间无输出”。
- 另外，当前已对 HuggingFace tokenizer 的 `model_max_length` 做了运行时放宽：
  - 目的是避免在 Docling native chunking 的计数/切分过程中产生误导性的长度 warning
- 在 ESP32-S3 真实样本上，本轮验证后：
  - 进度输出已正常出现
  - 之前的 `Token indices sequence length ...` warning 已不再出现

## Tokenizer Length Clarification
- `tokenizer 长度` 在我们当前上下文里，不是指 PDF 页数，也不是指原文会被截断的长度。
- 它更准确地指：
  - 用于 `HybridChunker` 计数和切分的 tokenizer 的 `model_max_length`
  - 以及一个 chunk 在 tokenizer 看来会被切成多少 token
- 调整这个值当前主要影响：
  - chunk 计数/切分时是否触发 HuggingFace 的长度 warning
  - `HybridChunker` 内部对“这段文本会不会太长”的判断过程是否顺畅
- 它当前**不直接改变**：
  - 原始 PDF 内容
  - `document.json`
  - `document.md`
- 在我们这套实现里，真正决定 chunk 大小的主参数仍然是：
  - `max_chunk_tokens`
- 运行时放宽 `model_max_length` 更像是：
  - 让 tokenizer 不要因为自己的默认上限太小而在计数阶段报误导性 warning

## HF Hub Warning Clarification
- `Warning: You are sending unauthenticated requests to the HF Hub...` 的意思是：
  - 当前有组件会从 HuggingFace Hub 下载模型或 tokenizer 资产
  - 你现在是匿名访问
  - 匿名访问通常仍然能用，但速率限制和下载体验会更差
- 对当前 Docling 使用的实际影响是：
  - **首次下载** 可能更慢
  - 更容易碰到限流
  - 已下载并缓存后，后续运行影响会明显下降
- 它通常**不意味着**：
  - Docling 不能工作
  - 当前解析逻辑有错误
- 在我们当前链路里，这个 warning 最常见的来源是：
  - `HybridChunker` 默认用的 HuggingFace tokenizer/模型标识
- 当前更合理的配置方式是：
  - 不把 token 写进仓库文件
  - 优先用 `hf auth login`
  - 或在本地 shell / 用户环境里设置 `HF_TOKEN`
- 当前这台机器上已实际完成本机 Hugging Face 认证：
  - 使用官方登录流程写入了用户级 token 缓存
  - `whoami` 已返回当前账号
  - 单独加载 `sentence-transformers/all-MiniLM-L6-v2` tokenizer 时已不再出现匿名访问提示
- 这意味着当前认证已经是：
  - **WSL 当前用户级全局认证**
  - 而不是某个单独 venv 私有认证
- 关键凭据位置是：
  - `~/.cache/huggingface/token`
  - `~/.cache/huggingface/stored_tokens`

## What gpu_vlm_pipeline Is For
- 官方 `gpu_vlm_pipeline` 示例并不是“把当前标准流水线换成更快版本”那么简单。
- 它做的是：
  - 使用 `VlmPipeline`
  - 使用 `VlmConvertOptions.from_preset("granite_docling", ...)`
  - 通过 vLLM API runtime 跑远程/本地 VLM 推理
- 这条路线更像：
  - 用 VLM 做页面理解和转换
  - 适合视觉理解更复杂、需要 VLM 参与的场景
- 它可能带来的提升主要是：
  - 某些复杂视觉页面的理解上限
  - VLM 推理吞吐（前提是 vLLM / 远程服务配置得好）
- 但它也带来明显代价：
  - 依赖 `vllm`
  - 依赖远程 API 或额外模型服务
  - 复杂度显著上升
  - 稳态和可控性不如先把标准流水线打磨好
- 对我们当前这条“芯片手册标准主线”，它不是第一优先优化项。

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

## Current Text Noise Strategy
- 当前已经明确分层：
  - `document.md`：尽量完整保留原始阅读信息，不做激进文本过滤
  - `chunks.jsonl` / `sections.jsonl`：做面向检索的文本噪声过滤
- 当前索引层已过滤的典型噪声包括：
  - `Submit Documentation Feedback`
  - 纯页码文本
  - 目录页 / 表目录 / 图目录 / 续页标题等已知噪声 section
- 在 ESP32-S3 样本上，当前状态已经变成：
  - `document.md` 仍保留这类页脚文本
  - 但 `chunks.jsonl` / `sections.jsonl` 已不再包含这类噪声

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

## New Implementation Findings
### Reading layer now links table sidecars directly
- `document.md` 不再只保留表格内联 Markdown。
- 当前实现会在每张成功匹配回原文位置的表格后追加：
  - `Table sidecars: [HTML](...) | [CSV](...) | table_id`
- 这意味着阅读层、manifest、sections/chunks 三层现在都能引用到同一张表。
- 匹配策略不是按页码盲插，而是按 `TableItem.export_to_markdown(doc=doc)` 的顺序去原始 `document.md` 中精确定位。
- 若未来某张表无法精确回插，逻辑会退化到 `Table Sidecars Appendix`，而不是静默丢失链接。

### Table manifest now carries table semantics
- `manifest.json` 的每个表格记录新增：
  - `label`
  - `caption`
- 对真实样本，这已经能区分：
  - `document_index`
  - 正常业务表格 `table`
- 像 `Table 1-1. ESP32-S3 Series Comparison` 这类表题，现在已在 manifest 中可直接访问。

### Large-PDF window processing is now resumable
- 每份文档目录下新增 `_windows/` 缓存目录。
- 每个页窗会落两个文件：
  - `window_XXXX_p000001-000250.document.json`
  - `window_XXXX_p000001-000250.meta.json`
- cache meta 会记录：
  - 页窗范围
  - 源 PDF `sha256`
  - 转换状态
  - 错误列表
  - 对应页窗 `DoclingDocument JSON`
- 当源 PDF hash 不变时，后续复跑会直接复用窗口缓存，不再重跑该页窗。

### ESP32-S3 sample re-check after these changes
- 输入：`manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf`
- 输出：`manuals/processed/esp32-s3-datasheet-en`
- 已确认：
  - `document.md` 中 `Table 1-1`、`Table 5-1` 等表后存在 sidecar 链接
  - 当前样本没有触发 `Table Sidecars Appendix`
  - `_windows/window_0001_p000001-000087.*` 已落盘
  - 第二次复跑明确打印 `reuse cached window 1/1 pages 1-87`

## Architecture Gap Review
### Current cache mechanism is useful but not yet complete
- 当前缓存是“页窗级 canonical cache”：
  - 每个窗口保存 `DoclingDocument JSON`
  - meta 中保存窗口范围、状态、错误和 `source_pdf_sha256`
- 这已经足够避免大 PDF 因中断而整本重跑。
- 但现在仍有一个重要缺口：
  - 缓存 key 只看源 PDF hash 和页窗范围
  - 还没有纳入 `docling version / OCR flags / image settings / pipeline signature`
- 这意味着：
  - 如果后续你改变了解析参数，当前缓存仍可能被误复用
  - 从工程严谨性上，这一层还应该升级为“conversion signature cache”

### Best-practice mainline still matches our current direction
- 结合 Docling 官方 `chunking`、`batch convert`、`table export`、`figure export`、`visual grounding`、`full page OCR` 示例，当前主线仍然应该是：
  - 原始 PDF 保留
  - `DoclingDocument JSON` 作为 canonical source
  - `document.md` 作为阅读层
  - 原生 `HybridChunker` 作为检索层
  - 表格 sidecar 作为高价值补强层
- 这条主线没有问题，不需要推翻重来。

### The highest-value missing layer is visual grounding, not generic RAG software
- 第一性原理看，你真正缺的不是“再套一层成熟 RAG 软件”。
- 真正缺的是：
  - 关键图/表/页的稳定回查能力
  - 当文本解析失败时，能迅速退回页图/框图/时序图原貌
- Docling 官方 `visual grounding` 与 `figure export` 路线正好对应这个需求。
- 因此当前架构里最值得补的不是换框架，而是补：
  - `generate_page_images`
  - page / bbox / artifact 对应索引
  - `figures.jsonl` 或 picture manifest

### Current outputs are still weak on hard visual/table pages
- 当前 ESP32-S3 样本里，`Table 2-9. Peripheral Pin Assignment` 已出现典型问题：
  - 表题保住了
  - 但表本体退化成图片占位
  - 这类宽矩阵表没有变成结构化表格 sidecar
- 这说明：
  - 当前标准主线对“超宽 GPIO/AF/Peripheral matrix 表”仍不够稳
  - 未来需要一条“疑难页二级补救”路线
- 最合理的形态不是整本都走 VLM，而是：
  - 主线继续走标准 Docling
  - 自动识别失败页/可疑页
  - 对这些页再走 VLM 或第二解析器补救

### Reading layer still has fidelity annoyances
- `document.md` 当前仍存在：
  - `Submit Documentation Feedback` 这类页脚噪声
  - `Table 5-9 - cont'd from previous page` 这类续页噪声
  - `T able` / `As- sign` 这类断词和断行问题
- 在 ESP32-S3 样本里，当前统计到：
  - `submit documentation feedback` 仍有 `1` 处
  - `T able` 断词有 `26` 处
  - `71` 张表里有 `17` 张 caption 为空，其中 `11` 张不是目录表
- 这些不会推翻当前架构，但说明：
  - `document.md` 更适合作为“完整阅读副本”
  - 而不是“唯一高质量阅读层”
- 一个更稳的后续方向是：
  - 保留当前完整 `document.md`
  - 额外生成一个轻清洗的 `document.clean.md` 或 `document.html`

### Practical next improvements
- 为窗口缓存补 `conversion signature`
- 增加 `document.html` 导出，方便人工核对宽表和图片
- 增加 `page_images/` 与 visual-grounding 元数据
- 增加 `figures.jsonl` / picture manifest
- 为“表题存在但表体退化为图片”的页建立自动告警
- 对疑难页做二级补救，而不是整本文档切到 VLM

### 2026-04-12: Conversion Signature Cache Landed
- 当前窗口缓存不再只看 `source_pdf_sha256`。
- 现在还会校验 `conversion_signature`，其内容覆盖：
  - `docling_version`
  - `ThreadedStandardPdfPipeline`
  - `device`
  - `enable_ocr / ocr_engine / force_full_page_ocr`
  - `generate_picture_images / generate_page_images / image_scale`
- 这解决了之前最明显的缓存严谨性问题：
  - 同一份 PDF 只要解析参数变了，旧窗口缓存就会失效
  - `manifest.json` 里现在也会记录 `conversion_signature`

### 2026-04-12: document.html Landed
- 当前每份文档除了：
  - `document.json`
  - `document.md`
- 还会额外导出：
  - `document.html`
- 这一层的定位不是给检索用，而是给人工核对用：
  - 宽表
  - 图片
  - 页面阅读流
- 当前实现保持保守：
  - 直接导出 Docling 原生 HTML
  - 不额外改写 HTML 内容
  - `manifest.json` 中记录 `document_html` 路径

### 2026-04-12: Image-Fallback Table Alert Landed
- 当前新增 `alerts.json`。
- 首个告警规则是：
  - 如果 `document.md` 中出现 `Table ...` 表题
  - 后面直接跟 `![Image](...)`
  - 且没有结构化 Markdown 表格或 `Table sidecars`
  - 则记录 `table_caption_followed_by_image_without_sidecar`
- 这个规则专门服务于 `Table 2-9. Peripheral Pin Assignment` 这种情况。
- 这不是尝试“修复” Docling，而是承认并显式标注标准管线的局限：
  - 后续可用这些 alert 去做人工回查
  - 或者用于和 `Marker` / `MinerU` 等其他工具做 A/B 对比

### 2026-04-12: ESP32-S3 And STM32H743VI Re-validation
- 当前两份样本都已在新链路下复验：
  - `esp32-s3_datasheet_en.pdf`，87 页
  - `stm32h743vi.pdf`，357 页
- 两者都已确认：
  - `document.html` 正常生成
  - `manifest.json` 中有 `conversion_signature`
  - 复跑时能命中 `_windows` 缓存
- `ESP32-S3` 结果：
  - `table_count = 71`
  - `alert_count = 1`
  - 这 1 条 alert 是真实有效告警：
    - 第 27 页
    - `Table 2-9. Peripheral Pin Assignment`
    - 表题存在，但表体退化为图片
- `STM32H743VI` 结果：
  - `table_count = 329`
  - `alert_count = 0`
  - 当前规则下未发现图片退化表格误报
  - 首轮转换中出现 `Could not parse formula with MathML` warning，但最终文档状态为 `success`

### Current judgment on ultra-wide matrix tables
- 现在可以更明确地下结论：
  - `Table 2-9` 这类超宽外设/AF 矩阵表，主要是 Docling 标准解析管线的能力边界
  - 不是我们后处理还差一点点就能稳定救回来的问题
- 如果继续深挖，通常就会走向：
  - VLM
  - 第二解析器
  - 更复杂的页级补救逻辑
- 这些路线不能保证准确性，还会显著抬高复杂度和不确定性。
- 因此当前项目的正确策略是：
  - 承认这是标准 Docling 主线的局限
  - 用 `alerts.json` 显式标记
  - 后续再和其他工具做针对性 A/B，而不是现在无限制优化

### 2026-04-12: Caption Recovery Still Had Deterministic Headroom
- 对当前两份样本进一步检查后确认：
  - 空 `caption` 并不总是意味着 Docling 完全没给出表题
  - 有一部分表题实际上存在于：
    - `table.export_to_markdown()` 的单列表头行
    - 或 `table.export_to_html()` 的首个 `<th>/<td>`
- 这类情况可以做低风险恢复，不需要猜测，也不需要引入 VLM。
- 因此当前 caption 提取策略已补强为：
  - 先取 markdown 的纯文本标题行
  - 若拿不到，再从 HTML 首行中提取符合 `Table N.` 形式的标题

### 2026-04-12: 500-Page Window Threshold Was Too Conservative
- 继续检查两份样本后确认：
  - `87` 页的 ESP32-S3 不需要分窗
  - `357` 页的 STM32H743VI 已经足够大，首轮如果不分窗，会失去缓存收益
- 因此默认 `page_window_min_pages` 从 `500` 下调到 `300`。
- 这个调整的特点是：
  - 对小文档没有影响
  - 对 300+ 页数据手册，能更早获得：
    - 中断恢复
    - 局部重跑
    - 更稳的长任务执行

### 2026-04-12: Caption Backfill From Markdown Context Landed
- 继续深挖空 `caption` 后确认：
  - 有不少表的标题不在 table 自身导出内容里
  - 但它们在 `document.md` 中、而且和 `Table sidecars` 的位置关系是稳定的
- 因此当前新增一层保守回填：
  - 对 `caption == ''` 的表
  - 依据 `Table sidecars` 的实际落点
  - 向上回溯最近合法的 `Table N.` 标题
- 这一步不需要猜测，不依赖 VLM，也不改变 `document.md` 原文，只补强 manifest/table metadata。

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
