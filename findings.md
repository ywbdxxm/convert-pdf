# Findings & Decisions

## Requirements
- 用户要为当前 PDF 处理项目调研“PDF 转 Markdown 供大模型查阅”的可用工具。
- 需要关注“当前可用”“最好用”的工具，而不是历史方案。
- 需要给出带场景区分的推荐，而不是单一答案。
- 需要把研究过程和结论记录到仓库，并后续用 git 管理。

## Research Findings
- `Marker`（`datalab-to/marker`）是目前非常活跃的开源方案，官方定位是将文档快速准确地转为 Markdown、JSON、chunks 和 HTML，强调表格、公式、代码块、图片提取，以及可选 LLM 增强模式。
- `Docling` 官方站点明确支持 `DocumentConverter().convert(...).document.export_to_markdown()`，并把 Markdown 导出作为面向 AI/RAG ingestion 的一等能力。
- `MinerU` 官方仓库定位是 “LLM-ready markdown/JSON”，重点强调复杂版面、公式转 LaTeX、表格转 HTML、109 语言 OCR、扫描件支持和多种部署方式。
- `PyMuPDF4LLM` 是轻量级路线，官方文档强调 Markdown/JSON/TXT 输出、版面分析、多栏支持、自动 OCR，以及 LlamaIndex/LangChain 集成。
- 初步判断：开源本地方案里，`Marker`/`Docling`/`MinerU` 更适合高保真解析；`PyMuPDF4LLM` 更适合追求轻量、低依赖和快速接入。
- `Mathpix` 是偏商业/科研文档路线的强项，官方明确把 PDF→Markdown 作为核心能力，突出数学公式、双栏论文、复杂表格与 STEM 文档。
- `Mistral OCR` 官方文档说明其 OCR 结果以结构化内容返回，页级结果直接带 `markdown` 字段，并支持把表格输出为 `markdown` 或 `html`。
- `Azure Document Intelligence` 的 Layout API 官方支持 `outputContentFormat=markdown`，可输出段落、标题、表格、图片、选择标记、公式、条码等语义化 Markdown 元素。
- `LlamaParse` 官方文档明确支持 `result_type="markdown"`，且定位就是为检索和上下文增强解析文件，工程接入 RAG 较顺手。
- 初步判断：云 API 路线里，`Mathpix` 偏学术/STEM，`Mistral OCR` 偏通用 OCR+Markdown，`Azure Document Intelligence` 偏企业级文档处理，`LlamaParse` 偏 LlamaIndex/RAG 工作流集成。

## Candidate Snapshot
| Tool | Type | Officially highlighted strengths | Main caveat | Best fit |
|------|------|----------------------------------|-------------|----------|
| Marker | Open-source local / API | Markdown/JSON/chunks/HTML；表格、公式、图片、去页眉页脚；可加 `--use_llm` 提升准确率 | GPL 代码 + 模型许可限制，栈较重 | 追求高保真通用解析 |
| Docling | Open-source local | Markdown/HTML/JSON；阅读顺序、表格、公式、OCR、chunking、RAG integrations、本地执行 | 对“极致精度”没有像 Marker 那样公开强调 benchmark | 默认工程集成首选 |
| MinerU | Open-source local / offline | 复杂布局、跨页表格、公式转 LaTeX、109 语言 OCR、扫描件/手写、多种 SDK/CLI/REST | AGPL-3.0；复杂度和部署重量更高 | 扫描件、多语言、复杂学术/中文文档 |
| PyMuPDF4LLM | Open-source local | `to_markdown()` 直接导出、自动/强制 OCR、语言包可配、LlamaIndex/LangChain 集成 | 对复杂表格/公式的高保真能力不如前三者完整 | 轻量基线和快速 PoC |
| Mathpix | Commercial / API / on-prem | 科研论文、双栏、公式、含公式表格、Markdown 导出 | 商业付费路线 | 学术/STEM 文档最佳 |
| Mistral OCR | Commercial API | 页级 `markdown` 主输出、多栏/表格、结构化返回、可选表格 Markdown/HTML | 托管 API，需上传文档 | 托管 API 通用方案 |
| Azure Document Intelligence | Commercial API | `outputContentFormat=markdown`、语义元素丰富、公式 LaTeX、企业文档结构化强 | Markdown 更偏“结构化布局表达”，不一定最自然 | 企业文档/合规/微软生态 |
| LlamaParse | Commercial API / self-host | 130+ 格式、agentic OCR、Markdown 输出、RAG/LlamaIndex 工作流顺滑 | 更偏平台化服务而非单点 Markdown 工具 | 已使用 LlamaIndex/LlamaCloud 的团队 |

## Preliminary Recommendation
- 如果这个仓库要先选一个默认开源方案，我建议先集成 `Docling`。
- 如果目标是“能打复杂 PDF、追求高精度 Markdown”，优先试 `Marker`，尤其是复杂表格和公式多的文档。
- 如果样本里扫描件、中文、多语言、跨页表格特别多，再补 `MinerU` 做第二条高保真管线。
- 如果只想先跑通工程链路和做 baseline，`PyMuPDF4LLM` 最省事。
- 如果文档以论文/教材/公式为主，商业方案里 `Mathpix` 仍然很强。
- 如果你更想直接接 API 而不是维护本地模型，`Mistral OCR` 是当前很顺手的 Markdown 输出型 API。

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 调研优先看官方来源 | 避免二手比较文章过时或失真 |
| 以 LLM/RAG 实用性为核心评估维度 | 用户目标是“供大模型查阅”，不是单纯视觉复刻 |
| 把候选工具分为开源本地与云 API 两类 | 实际选型受成本、隐私、吞吐和部署约束影响很大 |
| 默认推荐 Docling，精度推荐 Marker，复杂扫描推荐 MinerU | 这是基于官方能力声明后的工程化选型推断 |
| `fetch` 失败的根因优先按“工具运行环境无法访问代理”解释 | 单条 `fetch`、沙箱 `curl`、提权 `curl` 三组证据一致 |
| README 使用“项目方向 + 当前阶段 + 选型路线”结构 | 比泛泛介绍 PDF 工具更贴近当前仓库状态 |
| `.gitignore` 保留，但收敛为最小必要集合 | 用户明确不想删掉它，同时仓库还处于早期阶段 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| 当前仓库几乎为空，仅剩 `.git` 与 `.codex` | 先建立规划文件和研究记录，再继续调研 |
| 当前会话中 `fetch` 工具失败，而用户自有 WSL 终端网络正常 | 正在做环境差异诊断 |
| 原 README 过于泛化，和当前阶段不匹配 | 重写为“PDF 处理项目，当前先做 PDF 转 Markdown” |

## Resources
- Marker GitHub: https://github.com/datalab-to/marker
- Docling 官网: https://www.docling.ai/
- MinerU GitHub: https://github.com/opendatalab/MinerU
- PyMuPDF4LLM 文档: https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/index.html
- Mathpix PDF to Markdown: https://mathpix.com/pdf-to-markdown
- Mathpix OCR API docs: https://docs.mathpix.com/
- Mistral OCR docs: https://docs.mistral.ai/capabilities/document_ai/basic_ocr/
- Azure Document Intelligence Markdown docs: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/markdown-elements?view=doc-intel-4.0.0
- LlamaParse docs: https://docs.llamaindex.ai/en/v0.10.33/module_guides/loading/connector/llama_parse/

## Visual/Browser Findings
- Marker README 写明支持 PDF/图片/PPTX/DOCX/XLSX/HTML/EPUB，输出 Markdown/JSON/chunks/HTML，可选 `--use_llm` 提升表格、行内公式和表单提取准确率。
- Docling 官网首页直接给出 Python 示例，调用 `doc.export_to_markdown()` 导出 Markdown，并强调表格、公式、阅读顺序、OCR 以及面向 AI/RAG 的导出。
- MinerU README 说明它支持复杂布局、表格、公式、跨页表格、扫描件和 109 语言 OCR，也明确列出一些局限，例如极复杂布局、特殊列表、代码块和复杂表格仍可能有误差。
- PyMuPDF4LLM 文档显示其能自动对无可选文本页面触发 OCR，这对混合型 PDF 很实用，也说明其定位偏轻量与工程集成友好。
- Mathpix 页面强调其 PDF→Markdown 针对 scientific documents 做了专项优化，尤其是高难公式、双栏论文和带公式的表格。
- Mistral OCR 文档的返回结构里每页直接包含 `markdown` 主输出字段，对“转成 Markdown 给大模型吃”非常直接。
- Azure 文档说明其 Markdown 输出保留层级和元素语义，这意味着它更偏“结构化企业文档抽取”，而不是纯文本 OCR。
- LlamaParse 文档示例直接把 `result_type` 设为 `markdown`，说明其默认使用方式就是面向解析后检索/RAG 管线。

## Fetch Tool Diagnosis
- 单独调用 `fetch` 请求 `https://example.com` 也失败，说明不是某个站点特例。
- 沙箱内直接执行 `curl -I https://example.com` 失败，并明确报错尝试连接 `127.0.0.1:7897`。
- 当前环境存在 `HTTP_PROXY`、`HTTPS_PROXY`、`http_proxy`、`https_proxy`，全部指向 `http://127.0.0.1:7897`。
- 提权后执行同一条 `curl -I https://example.com` 成功，返回 `HTTP/1.1 200 Connection established` 和后续 `HTTP/2 200`。
- 这说明“普通 WSL/提权环境”能访问你的 Clash 代理，但“我的沙箱环境”不能访问同一个 `127.0.0.1:7897`。
- 在沙箱内去掉代理后，`curl` 报 `Could not resolve host: example.com`，说明沙箱本身没有直接外网 DNS/网络能力，依赖代理才能出网。
- 在沙箱内显式把代理改成 `/etc/resolv.conf` 中的 `10.255.255.254:7897` 也无法连通，因此不只是 `localhost` 字面量问题，更像是沙箱与宿主网络命名空间隔离。
- 对 `fetch` 工具本身再次复现，错误为 `Failed to fetch robots.txt https://example.com/robots.txt due to a connection issue`；这与代理不可达导致首个联网动作失败高度一致。
- 已按 A 方案修改 `~/.codex/config.toml`：
  - 设置 `sandbox_mode = "workspace-write"`
  - 设置 `approval_policy = "on-request"`
  - 设置 `sandbox_workspace_write.network_access = true`
  - 为 `mcp_servers.fetch` 增加 `env_vars = ["HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy"]`
- 当前改动只会影响后续新启动的 Codex 会话；现有会话里的 `fetch` MCP 进程不会自动热重载。
- 在新会话中，沙箱内 `curl -I https://example.com` 和 `curl -I https://raw.githubusercontent.com` 都成功，说明沙箱网络已经恢复正常。
- `fetch` 现已成功抓取以下真实目标：
  - `https://developers.openai.com/codex/concepts/sandboxing`
  - `https://www.docling.ai/`
  - `https://github.com/datalab-to/marker`
  - `https://raw.githubusercontent.com/datalab-to/marker/master/README.md`
- `fetch` 仍然会对 `https://example.com` 和 `https://example.com/robots.txt` 报 `Failed to fetch robots.txt ... due to a connection issue`。
- 当前结论：`fetch` MCP 已达到“日常可用”状态，至少对文档站点、GitHub 页面和 raw 文本可正常使用；但不能视为对所有站点都完全无异常。

---
*Update this file after every 2 view/browser/search operations*
