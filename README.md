# convert-pdf

当前主线只做一件事：

```text
比较 Docling 和 OpenDataLoader PDF，看看谁更适合把芯片手册转换成可供 Codex 直接检索的结构化文件夹
```

## 当前架构

```text
PDF -> parser -> Markdown / JSON / HTML / images / tables -> Codex 直接读文件夹 -> 原始 PDF 核验
```

不是主线的东西：

- 不继续扩展 `docling_batch`
- 不写新的 RAG/search/index 框架
- 不优先测 UI/RAG 软件
- 不优先测其它 parser

## 当前只测 4 条主线

1. `docling_batch` 现有输出
   - 冻结 baseline

2. `Docling` 原生输出
   - 区分 Docling 本身和 `docling_batch` 包装层

3. `OpenDataLoader PDF` local mode
   - 第一解析器候选

4. `OpenDataLoader PDF` hybrid mode
   - 当 local mode 的表格质量不够时再测

附加 metadata spot-check：

- `OpenDataLoader PDF + LangChain`
- `Docling + LlamaIndex / LangChain`

它们不是运行时主架构，只用于检查 consumer 会不会破坏 page / bbox / source metadata。

## 当前不测

- Dify
- AnythingLLM
- Kotaemon
- Open WebUI
- LiteParse
- PyMuPDF4LLM
- MarkItDown
- PaperFlow
- Marker
- MinerU
- PaddleOCR-VL
- HURIDOCS
- RAGFlow
- Unstructured
- 付费或远程 API 路线

## 固定样本

```text
manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf
manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf
manuals/raw/st/stm32h7/stm32h743vi.pdf
```

## 固定问题

- 定位 `Table 2-9. Peripheral Pin Assignment`
- 查一个 GPIO/pin mux 事实并回到页码
- 查一个电气参数表值并回到页码
- 检查 STM32H743VI 的表格密集章节
- 查 ESP32-S3 TRM 的 I2C/UART register summary
- 检查公式/图/时序图密集页面

## 当前下一步

```text
1. 用现有 docling_batch 输出做 baseline
2. 跑 Docling 原生输出
3. 跑 OpenDataLoader PDF local mode
4. 如表格不够好，再跑 OpenDataLoader PDF hybrid mode
5. 最后只做 OpenDataLoader LangChain 和 Docling LlamaIndex/LangChain metadata spot-check
```

## 文档

- [Docling / OpenDataLoader Mainline Plan](docs/architecture/2026-04-13-external-first-manual-tooling-plan.md)
- [Docling Embedded Manual Processing Architecture](docs/architecture/2026-04-12-docling-embedded-manual-processing.md)
- [RAG For Embedded Manual Lookup](docs/architecture/2026-04-12-rag-for-embedded-manuals.md)
