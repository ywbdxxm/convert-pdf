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
