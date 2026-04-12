# convert-pdf

这个仓库用于把芯片手册、技术参考手册、应用手册等 PDF 转换为适合 AI 查阅、检索、引用和人工核对的资产。

当前主线不是“只把 PDF 转成 Markdown”，而是：

```text
PDF -> Docling JSON -> Markdown/HTML -> chunks/sections -> table sidecars -> alerts
```

完整架构说明见：

- [Docling Embedded Manual Processing Architecture](docs/architecture/2026-04-12-docling-embedded-manual-processing.md)
- [RAG For Embedded Manual Lookup](docs/architecture/2026-04-12-rag-for-embedded-manuals.md)

## 当前目标

面向嵌入式开发，处理后的手册需要支持：

- 快速定位寄存器、位定义、复位值、地址偏移
- 查找 GPIO/AF/pin matrix、外设信号、时序和电气参数
- 从 AI 回答回溯到手册页码和原始 PDF
- 对表格、图、公式和解析失败点做显式告警
- 后续可接入 RAG 或其他检索框架，但不在第一阶段绑定具体框架

## 核心设计

当前最佳实践：

- 原始 PDF 是最终权威来源
- `document.json` 是 Docling canonical source
- `document.md` 是 AI/人工阅读副本
- `document.html` 用于人工核对宽表和图片
- `chunks.jsonl` 是检索级索引
- `sections.jsonl` 是章节导航索引
- `tables/*.csv` 和 `tables/*.html` 用于表格核对
- `alerts.json` 用于暴露解析质量问题
- `_windows/` 只在显式开启缓存时使用

## 环境启动

从仓库根目录执行：

```sh
./scripts/bootstrap_ai_base.sh
./scripts/bootstrap_docling_env.sh
./scripts/verify_ai_stack.sh
```

项目环境位于：

```text
docling/.venv
```

共享重型 AI base 位于：

```text
/home/qcgg/.mamba/envs/ai-base-cu124-stable
```

不要把项目私有依赖安装进系统 Python。

## 输入目录

建议把 PDF 放在：

```text
manuals/raw/<vendor>/<chip>/<manual>.pdf
```

当前样本包括：

```text
manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf
manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf
manuals/raw/st/stm32h7/stm32h743vi.pdf
```

## 默认转换命令

数字版 datasheet/manual 优先关闭 OCR：

```sh
docling/.venv/bin/python -m docling_batch convert \
  --input manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf \
  --output manuals/processed \
  --device cuda \
  --no-ocr
```

默认行为：

- 整本处理
- 不启用窗口缓存
- 保留图片 sidecars
- 生成 JSON/Markdown/HTML/chunks/sections/tables/alerts

## 超大文档可选缓存

缓存默认关闭。只有超大文档、易中断任务、或需要反复实验时才开启：

```sh
docling/.venv/bin/python -m docling_batch convert \
  --input manuals/raw/espressif/esp32s3/esp32-s3_technical_reference_manual_en.pdf \
  --output manuals/processed \
  --device cuda \
  --no-ocr \
  --enable-window-cache \
  --cache-window-size 250
```

缓存不是首轮加速功能。它的作用是让长文档失败后能复用已完成页窗，避免整本从头再跑。

## OCR

数字版芯片手册默认使用 `--no-ocr`。

扫描件或图片化 PDF 再启用 OCR：

```sh
docling/.venv/bin/python -m docling_batch convert \
  --input manuals/raw/vendor/chip/scanned_manual.pdf \
  --output manuals/processed \
  --device cuda \
  --ocr-engine rapidocr \
  --force-full-page-ocr
```

## 输出结构

每份文档输出到：

```text
manuals/processed/<doc_id>/
```

主要文件：

```text
document.json
document.md
document.html
manifest.json
sections.jsonl
chunks.jsonl
alerts.json
artifacts/
tables/
_windows/
```

批处理运行摘要：

```text
manuals/processed/_runs/<timestamp>.json
```

## AI 使用方式

后续让 AI 使用某份处理后的手册时，优先给它这个目录：

```text
manuals/processed/<doc_id>
```

AI 应按以下顺序工作：

1. 先读 `manifest.json`，确认状态、页数、表格数、告警数和原始 PDF 路径。
2. 如果 `alert_count > 0`，先读 `alerts.json`，了解哪些页面/表格需要谨慎。
3. 用 `sections.jsonl` 找章节和页码范围。
4. 用 `chunks.jsonl` 检索具体段落和 `citation`。
5. 用 `document.md` 阅读上下文。
6. 遇到表格值时打开 `tables/*.csv` 或 `tables/*.html` 核对。
7. 遇到图、时序图、寄存器位图时看 `artifacts/` 和原始 PDF。
8. 对寄存器、电气参数、时序限制等关键结论，必须回到页码引用或原始 PDF 做交叉验证。

## 已验证样本

### ESP32-S3 datasheet

```text
manuals/processed/esp32-s3-datasheet-en
```

- 87 页
- 71 张表
- 309 chunks
- 141 sections
- 1 条告警：`Table 2-9. Peripheral Pin Assignment` 表体退化为图片

### STM32H743VI datasheet

```text
manuals/processed/stm32h743vi
```

- 357 页
- 329 张表
- 1324 chunks
- 242 sections
- 当前告警数为 0

### ESP32-S3 Technical Reference Manual

```text
manuals/processed/esp32-s3-technical-reference-manual-en
```

- 1531 页
- 667 张表
- 3775 chunks
- 1379 sections
- 9 条 `empty_table_sidecar` 告警
- 第 501-750 页窗口是明显性能热点

## Docling 当前评估

适合作为默认本地主线：

- 对数字版 datasheet/TRM 可完整跑通
- 能生成 JSON/Markdown/HTML 和检索索引
- 多数普通表格、寄存器摘要、电气参数表可用
- 能保留图片和表格 sidecars
- 便于后续接入 RAG，但不强绑定任何 RAG 框架

已知弱点：

- 超宽 pin matrix / AF matrix 可能退化成图片
- 部分 figure 可能被识别成 table
- 部分 table sidecar 可能为空
- 部分 caption 无法安全恢复
- 公式/MathML 可能解析失败
- 超大 TRM 的局部窗口可能非常慢

当前策略：

- 继续把 Docling 作为默认本地主线
- 不继续堆复杂 heuristic 或 VLM 补丁
- 用 `alerts.json` 记录边界问题
- 后续用告警页和慢窗口页对比 Marker、MinerU、OpenDataLoader PDF 等工具

## 相关文档

- [Docling Embedded Manual Processing Architecture](docs/architecture/2026-04-12-docling-embedded-manual-processing.md)
- [AI workstation design audit](docs/architecture/2026-04-12-ai-workstation-design-audit.md)
- [AI workstation execution plan](docs/architecture/2026-04-12-ai-workstation-execution-plan.md)
- [Global workstation reference](docs/architecture/global-workstation-reference.md)
