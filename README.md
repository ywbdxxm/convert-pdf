# convert-pdf

本仓库用于探索“如何让 AI 可靠查阅芯片手册”。当前方向已经从自研 PDF/RAG 管线调整为：

```text
优先试用成熟本地/免费工具 -> 用真实芯片手册验证 -> 只在证明有缺口时写最小适配
```

## 当前原则

- 不重复造轮子，不继续扩展自研 RAG/search/index。
- `docling_batch/` 冻结为历史 baseline，不再新增功能。
- 优先本地、免费、自托管；默认不使用付费远程 API。
- 原始 PDF 永远是寄存器、电气参数、时序限制、pin mux 的最终权威来源。
- 工具好坏只看真实手册问题上的结果，不看架构想象。

## 当前硬件环境

- WSL2 / Ubuntu
- RTX 4060 Laptop GPU
- Docker + NVIDIA runtime 可用
- 共享 AI base：`/home/qcgg/.mamba/envs/ai-base-cu124-stable`
- 当前 Docling overlay：`docling/.venv`

环境脚本保留：

```sh
./scripts/bootstrap_ai_base.sh
./scripts/bootstrap_docling_env.sh
./scripts/verify_ai_stack.sh
```

## 候选路线

### 第一优先：解析器对比

1. `OpenDataLoader PDF`
   - 本地优先，输出 Markdown / JSON / HTML。
   - JSON 包含 page number / bounding box，适合做源定位验证。
   - 先测 local mode，再考虑 hybrid mode。

2. `Docling` 官方集成
   - 不再以 `docling_batch` 为唯一用法。
   - 优先试 `LlamaIndex + DoclingReader/DoclingNodeParser`。
   - 再试 `LangChain + DoclingLoader`。

3. `PyMuPDF4LLM`
   - 作为快速数字 PDF baseline。

4. `Marker` / `MinerU`
   - 在 OpenDataLoader 与 Docling 集成不足时再试。

### 第二优先：本地文档问答应用

1. `AnythingLLM`
   - 本地/offline 友好，适合快速验证“上传文档后能不能用”。

2. `Dify`
   - 自托管 Docker Compose，适合后续做 Knowledge / workflow。
   - 先喂解析器输出的 Markdown，不优先测试其原生 PDF 解析。

3. `Kotaemon`
   - 文档 QA UI，支持 local LLM、citations、PDF preview、Docling loader。

4. `Open WebUI + Docling Serve`
   - 作为后续 UI 集成候选。

## 暂缓或排除

- `RAGFlow`：当前太重，暂缓。
- `Unstructured`：当前不走付费/远程 API 路线，暂不测。
- `LlamaParse` / `Mistral OCR` / `Azure Document Intelligence` / `Mathpix`：默认排除，除非之后明确接受付费远程 API。
- 自研 `manual_eval` 框架：已停止，不继续。

## 当前样本

```text
manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf
manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf
manuals/raw/st/stm32h7/stm32h743vi.pdf
```

## 固定测试问题

- ESP32-S3 datasheet：定位 `Table 2-9. Peripheral Pin Assignment`。
- ESP32-S3 datasheet：查一个 GPIO/pin mux 事实并回到页码。
- ESP32-S3 datasheet：查一个电气参数表值并回到页码。
- STM32H743VI datasheet：检查一个表格密集章节。
- ESP32-S3 TRM：查 I2C 或 UART register summary。
- ESP32-S3 TRM：检查公式/图/时序图密集页面。

## 判断标准

每个工具都按这些问题打分：

- 能否本地免费运行
- 安装和运行成本
- 表格结构是否可靠
- 是否保留页码
- 是否有 bounding box / source metadata
- 是否方便回到原始 PDF
- 是否能处理图和时序图
- 是否减少自研代码

## 重要文档

- [Local-Free Manual Tooling Plan](docs/architecture/2026-04-13-external-first-manual-tooling-plan.md)
- [Docling Embedded Manual Processing Architecture](docs/architecture/2026-04-12-docling-embedded-manual-processing.md)
- [RAG For Embedded Manual Lookup](docs/architecture/2026-04-12-rag-for-embedded-manuals.md)
- [AI Workstation Design Audit](docs/architecture/2026-04-12-ai-workstation-design-audit.md)
- [AI Workstation Execution Plan](docs/architecture/2026-04-12-ai-workstation-execution-plan.md)

## 下一步

不要写新框架代码。下一步只做一个小实验：

```text
OpenDataLoader PDF local mode
-> ESP32-S3 datasheet
-> 检查 Table 2-9 的 JSON/Markdown/HTML 输出
-> 和当前 Docling baseline + 原始 PDF 对比
```
