# convert-pdf

当前主线只做一件事：

```text
比较 Docling 和 OpenDataLoader PDF，看看谁更适合把芯片手册转换成可供 Codex 直接检索的结构化文件夹
```

## 当前进展

- `OpenDataLoader PDF hybrid` 已经完成 `ESP32-S3 datasheet` 和 `ESP32-S3 TRM` 的真实跑数与 Codex-facing bundle 打包。
- `docling_bundle`（原 `docling_batch`）已完成输出结构重构，并在同一组样本上重新跑通。
- 两条产线当前都能产出独立可读的最终目录：
  - `manuals/processed/opendataloader_hybrid/<doc_id>/`
  - `manuals/processed/docling_bundle/<doc_id>/`

## 当前判断

- 如果看“提取证据能力”，当前更强的是 `OpenDataLoader PDF hybrid`。
  - 更快
  - 更不持续吃 GPU
  - 页级 bbox / element metadata 更强
  - 结构化 table 覆盖更高
- 如果看“直接给 Codex 查阅和验证”，当前更顺手的是 `docling_bundle`。
  - `document.md` / `pages/` 更平静
  - table sidecar 链接更直接
  - `quality-summary.md` / `alerts.json` 更像成熟工作流
- 对超大 TRM，`OpenDataLoader hybrid` 当前必须带 `--hybrid-fallback` 才够稳。

## 当前目录

```text
docling/                     # Docling Python overlay env
docling_bundle/              # Docling bundle builder package
opendataloader/              # OpenDataLoader Python overlay env
opendataloader_hybrid/       # OpenDataLoader bundle builder package
manuals/raw/                 # 原始 PDF
manuals/processed/
  docling_bundle/<doc_id>/   # Docling 最终 bundle
  opendataloader_hybrid/<doc_id>/  # OpenDataLoader 最终 bundle
tmp/opendataloader_hybrid-native/  # OpenDataLoader staging/native 中间落盘
```

## 当前架构

```text
PDF -> parser -> Markdown / JSON / HTML / images / tables -> Codex 直接读文件夹 -> 原始 PDF 核验
```

不是主线的东西：

- 不继续扩展 `docling_bundle`
- 不写新的 RAG/search/index 框架
- 不优先测 UI/RAG 软件
- 不优先测其它 parser

## 当前只测 4 条主线

1. `docling_bundle`
   - 当前更强的阅读/验证 bundle

2. `OpenDataLoader PDF hybrid`
   - 当前更强的提取/证据 bundle

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
1. 继续把 docling_bundle 更成熟的阅读层优点有选择地移植到 OpenDataLoader bundle
2. 继续做同页/同任务 A/B 验证，而不是再扩工具面
3. 等路线最终稳定后，再决定是否继续精简或重命名剩余历史文档
```

## 文档

- [Docs Index](docs/README.md)
- [Parser Status And Next Steps](docs/architecture/2026-04-15-parser-status-and-next-steps.md)
- [Parser Optimization Roadmap](docs/superpowers/plans/2026-04-15-parser-optimization-roadmap.md)
- [Docling Embedded Manual Processing Architecture](docs/architecture/2026-04-12-docling-embedded-manual-processing.md)
