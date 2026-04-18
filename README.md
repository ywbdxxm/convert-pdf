# convert-pdf

把芯片数据手册、TRM、应用笔记等 PDF 转成适合 agent（Claude Code / Codex）直接查阅、定位、引用、回 PDF 核验的结构化产物。

> 定位：AI 时代嵌入式开发的**手册基础设施**，不是通用 PDF→Markdown 工具，也不是 RAG 应用壳。

## 为什么这个项目有价值

嵌入式开发里真正耗时的不是"读文档"，是：

- 在几百到几千页手册里快速定位正确章节
- 在表格、图、寄存器摘要、时序图之间来回切换
- 判断哪些页面可以直接用、哪些必须回 PDF 核验
- 让 agent 参与时仍然保留证据链

目标不是让 AI "总结 PDF"，是让 AI 在工程上可用——能查寄存器字段、pin mux、电气参数、外设摘要，并能把每个结论挂回具体页、具体表、具体图。

## 当前产线

**只保留 `docling_bundle` 这一条主线**（2026-04-18 起）。`opendataloader_hybrid` 已从活跃路线移除。

```
manuals/
  raw/                            # 原始 PDF（权威来源）
    espressif/esp32s3/*.pdf
  processed/
    docling_bundle/<doc_id>/      # 最终面向 agent 的 bundle
tmp/
  docling_bundle-cache/            # 窗口缓存（可选）
```

## Bundle Schema（`manuals/processed/docling_bundle/<doc_id>/`）

| 文件 | 用途 |
|------|------|
| `README.md` | 单入口；摘要、告警、阅读顺序 |
| `manifest.json` | 机器入口；紧凑元数据 |
| `alerts.json` | 质量告警（不可信页/表格） |
| `toc.json` | 层级目录树 |
| `pages.index.jsonl` | 页码→内容反向索引 |
| `sections.jsonl` | 章节索引（带 `heading_level` / `suspicious`） |
| `chunks.jsonl` | 段级分块（Docling `HybridChunker` 输出） |
| `tables.index.jsonl` | 表格索引（caption / label / csv 路径） |
| `tables/*.csv` | 每张表的 CSV sidecar |
| `document.md` | 主阅读层 Markdown |
| `document.json` | Docling 原生 JSON 全量 |
| `document.html` | 宽表/视觉验证备用视图 |
| `assets/` | 提取到的所有图片证据 |

## 运行

```sh
docling/.venv/bin/python -m docling_bundle convert \
  --input manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf \
  --output manuals/processed \
  --device cuda \
  --no-ocr
```

默认不开 OCR；只在扫描件或图片密集时开。窗口缓存 `--enable-window-cache` 是可选容错，不是加速选项。

## 消费流程（agent）

1. 打开 `README.md`，看摘要和 `alert_count`
2. `alert_count > 0` 时先读 `alerts.json`
3. 要章节导航用 `toc.json`
4. 要按页查内容用 `pages.index.jsonl`
5. 查表用 `tables.index.jsonl` 定位，读对应 `tables/*.csv` 核值
6. 读 `document.md` 做上下文阅读
7. 任何结论以回 `manuals/raw/<...>.pdf` 对应页为最终权威

## 已知缺口与路线

详见：
- `docs/architecture.md` — 设计原则、产出契约、质量维度
- `task_plan.md` — 分阶段改进计划（当前 Phase 39：TOC 去噪）
- `findings.md` — 每次重跑的观察记录

评价标准：**Claude Code / Codex 直接调用这个 bundle 做嵌入式开发时的真实体验**。一切优化以降低"从问题到可信答案"的步数为准。
