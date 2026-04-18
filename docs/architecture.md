# docling_bundle Architecture

日期：2026-04-19（Phase 60 完成 — 完整 TRM 验证 + 最终产物落盘）

## 1. 目标

把一份芯片手册 PDF 转成一个**自包含目录**，让 agent 可以：

1. 在单一入口（`README.md`）立刻知道：页数、表数、告警数、章节大纲、表格分布、阅读顺序
2. 在固定路径上做程序化访问（manifest / toc / pages index / sections / chunks / tables index / cross_refs / assets_index）
3. 按页、按章、按表三种维度交叉跳转
4. 对任何怀疑点，能立刻回到原 PDF 的确切页——尤其当 `alerts.json` 告知"转换结果不可信"时

**不做**的事：全文检索 / RAG / 模型推理 / 语义问答 / MCP server。这些是更上层应用的职责，本项目只负责把 PDF 压缩成可信、结构化、可导航的证据层。

## 2. 分层

```
PDF (权威真相)
  │
  ▼
Docling pipeline (CUDA, HybridChunker)         ← docling_bundle/converter.py
  │
  ▼
canonical document.{json,md,html}              ← Docling 原生解析结果
  │
  ▼
navigation layer                                ← docling_bundle/indexing.py
  - toc.json           (hierarchical headings + is_chapter + suspicious)
  - sections.jsonl     (leaf + navigational-parent, is_chapter + heading_level + table_ids)
  - pages.index.jsonl  (page → chunk/table/asset/alert reverse index)
  - chunks.jsonl       (HybridChunker output + full heading lineage + citation)
  │
  ▼
evidence layer                                  ← tables.py / images.py / assets_index.py / cross_refs.py
  - tables.index.jsonl + tables/*.csv
  - assets.index.jsonl + assets/*.png
  - cross_refs.jsonl   (section / table / figure with resolved target_page + target_id)
  │
  ▼
quality layer                                   ← docling_bundle/alerts.py
  - alerts.json        (structural warnings + page refs + csv_path / image_path)
  │
  ▼
entry layer                                     ← docling_bundle/reading_bundle.py
  - README.md          (agent/human single entry with alerts inlined)
  - manifest.json      (machine single entry with canonical counts + file paths)
```

## 3. 设计原则

1. **原始 PDF 是最终权威。** 任何结构化产物都只是索引，不是 source of truth。
2. **单入口 + 机器入口双轨。** `README.md` 给 agent / 人，`manifest.json` 给程序。不做"index of indexes"。
3. **不可变 dataclass + 纯函数。** Paths / RuntimeConfig 是 frozen；indexing / tables / alerts / cross_refs 都是无副作用计算。
4. **处理不好就暴露，不试图修复。** 对应 `开发要求.md` 规则 4 / 5：谨慎使用启发式；处理不好的表 / 图 / 页面直接在 `alerts.json` 留痕，告诉 agent 回原 PDF。代表：`table_without_caption` / `table_caption_followed_by_image_without_sidecar`。
5. **静默失败是最大反模式。** 任何内容被丢弃或不可信，必须在 alerts / 计数里可见。Phase 60 修的 footer-strip bug 就是这条原则的具体应用（之前是整块 chunk 被拒，agent 查不到，也没告警）。
6. **不改 assets 文件名。** Docling 的 `document.json` / `document.html` 内部引用用 hash 文件名，改名会断链。通过 `assets.index.jsonl` 补语义。
7. **Bundle 内不写 runtime 状态。** 窗口缓存放在 `tmp/docling_bundle-cache/`，不污染产物目录。

## 4. 产物契约

### `manifest.json`（机器入口）

```json
{
  "doc_id": "esp32-s3-datasheet-en",
  "title": "esp32-s3_datasheet_en",
  "source_pdf_path": "<absolute path>",
  "source_filename": "esp32-s3_datasheet_en.pdf",
  "page_count": 87,
  "status": "success",
  "errors": [],
  "document_json": "document.json",
  "document_markdown": "document.md",
  "document_html": "document.html",
  "readme": "README.md",
  "alerts_path": "alerts.json",
  "sections_index": "sections.jsonl",
  "chunks_index": "chunks.jsonl",
  "tables_index": "tables.index.jsonl",
  "tables_dir": "tables",
  "toc": "toc.json",
  "pages_index": "pages.index.jsonl",
  "cross_refs": "cross_refs.jsonl",
  "assets_index": "assets.index.jsonl",
  "table_count": 71,
  "chunk_count": 339,
  "section_count": 145,
  "alert_count": 3
}
```

### `toc.json`

```json
{"heading": "2.1 Pin Layout", "level": 2, "page": 15, "is_chapter": false}
{"heading": "1 ESP32-S3 Series Comparison", "level": 1, "page": 13, "is_chapter": true}
```

- `level` 从数字前缀推断：`1` / `1.2` / `A.1.3` → 1 / 2 / 3；无前缀默认 1
- `is_chapter=true` 仅对编号 level-1 heading；`jq 'select(.is_chapter)'` 一键取完整章节目录
- 过滤：`NOISY_SECTION_IDS`（Contents / List of Tables / List of T ables / List of Figures / Cont'd from previous page）；`NOISY_TOC_HEADINGS`（Note: 等）；重复 >3 次的非编号 heading；被误识为 heading 的表格 caption；Unicode 项目符号开头的 heading
- `suspicious=true` 当对应 section 被 `flag_suspicious_sections` 标异常（span 超总页数 30%）

### `sections.jsonl`

```json
{"section_id": "4.2.1.1 UART Controller", "heading_path": ["4 Functional Description","4.2 Peripherals","4.2.1 Connectivity Interface","4.2.1.1 UART Controller"], "heading_level": 4, "is_chapter": false, "page_start": 51, "page_end": 51, "chunk_count": 3, "chunk_ids": [...], "text_preview": "...", "table_ids": [...]}
{"section_id": "4 Functional Description", "heading_path": ["4 Functional Description"], "heading_level": 1, "is_chapter": true, "page_start": 36, "page_end": 63, "chunk_count": 0, "chunk_ids": [], "text_preview": "", "table_ids": [...]}
```

两类记录：

- **Leaf section**（直接挂 chunks）：`chunk_count > 0`，`chunk_ids` 非空
- **Navigational parent**（chapter / 中间分组 heading，本身无 direct chunk）：`chunk_count = 0`，`chunk_ids = []`；通过 `augment_sections_with_navigational_parents` 为每个 TOC 入口（只要有 chunk 的 `heading_path` 引用过它）补一条记录，保证 `jq 'select(.is_chapter)'` 有真正的章节条目返回

约束：
- Leaf 与 parent 的 `chunk_ids` 不重叠（chunks 互斥分组不破）
- Parent 的 `page_end` 取所有 descendant chunk 的最大 `page_end`
- Suspicious heading 不建 nav parent（防止 ghost span 复活）
- 不为"chunk.heading_path 里从未出现"的 TOC 入口建 parent（避免虚构）

### `chunks.jsonl`

```json
{
  "doc_id": "...", "chunk_id": "...:0005", "chunk_index": 5,
  "section_id": "4.1.3.5 Power Management Unit (PMU)",
  "heading_path": ["4 Functional Description", "4.1 System", "4.1.3 System Components", "4.1.3.5 Power Management Unit (PMU)"],
  "page_start": 42, "page_end": 43,
  "text": "ESP32-S3 has an advanced Power Management Unit (PMU)...",
  "contextualized_text": "4 Functional Description\n4.1 System\n...\n4.1.3.5 Power Management Unit (PMU)\nESP32-S3 has an advanced Power Management Unit (PMU)...",
  "doc_item_count": 1,
  "table_like": false,
  "table_ids": [],
  "citation": "esp32-s3-datasheet-en p.42-43"
}
```

- `heading_path` 完整祖先链（Phase 56a）：数字 heading 权威决定 level；非数字 heading 挂在最深数字祖先之下
- `text` 经过清洗：`clean_ocr_text` 反转 Docling 的 `T able` → `Table` OCR 断词；`.lstrip()` 去掉表格序列化前导 `\n`；`_strip_noisy_text_phrases` 剥离"Submit Documentation Feedback"页脚（Phase 60）
- `section_id = heading_path[-1]`（叶节点）
- `citation` 是 `doc_id p.X` 或 `doc_id p.X-Y`

### `pages.index.jsonl`

```json
{"page": 27, "chunk_ids": ["...:0100"], "table_ids": [], "asset_ids": ["...:asset:0025"], "alert_kinds": ["table_caption_followed_by_image_without_sidecar"]}
```

覆盖 1..N 每页。`alert_kinds` 是该页所有 alert 的 `kind` 列表（可空）。

### `tables.index.jsonl`

```json
{
  "table_id": "...:table:0009", "page_start": 17, "page_end": 17,
  "csv_path": "tables/table_0009.csv",
  "label": "table",
  "caption": "Table 2-1. Pin Overview (cont'd)",
  "kind": "pinout",
  "is_toc": false,
  "rows": 18,
  "columns": ["Pin No.", "Pin Name", "Pin Type", ...],
  "continuation_of": "...:table:0008"
}
```

- `kind`：`pinout` / `strap` / `register` / `electrical` / `timing` / `revision` / `document_index` / `generic`。CSV header 启发式推断；`generic` 是安全兜底（不强行分类）
- `rows`：**data rows 数**（Phase 59e）— Docling `num_rows` 包含 header 行，我们减去 `column_header=True` 的 row 数
- `continuation_of`：续页表指向父表；caption 统一 `<base> (cont'd)` 格式；续页判定要求 **page adjacency** + column 相似或显式 cont'd 标记 + 数字匹配（三重约束）
- `is_toc=true`：目录页表格（label=document_index）；`columns=[]`（避免暴露 `[0,1,2,...]` pandas 默认索引）；CSV 以 `header=False` 写入
- caption 经过 `backfill_table_captions_from_markdown` 从 markdown 上下文补回；无法确定时留空 + 触发 `table_without_caption` alert

### `cross_refs.jsonl`

```json
{"kind": "section", "target": "4.1.3.5", "source_page": 2, "raw": "see Section 4.1.3.5", "target_page": 42, "target_id": "4.1.3.5 Power Management Unit (PMU)", "source_chunk_id": "...:0005"}
{"kind": "table", "target": "2-5", "source_page": 23, "raw": "As shown in Table 2-5", "target_page": 25, "target_id": "...:table:0016", "source_chunk_id": "...:0099"}
{"kind": "figure", "target": "2-2", "source_page": 15, "raw": "shown in Figure 2-2", "target_page": 30}
```

- 前缀锚定 `see|refer to|shown in|as shown in`，避开表 caption 自指假阳性
- 识别 Docling 的 `T able` OCR 断词（`T\s+able`）
- **Section** 在 `toc.json` resolve；`target_id = toc heading` 文本（= `sections.jsonl.section_id`）
- **Table** 在 `tables.index.jsonl` resolve；`target_id = table_id`
- **Figure** 通过 `build_figure_page_map(doc)` 从 Docling `label=caption` 的 text 解析（Phase 58b）；无 figure 全局 id，不填 `target_id`
- `source_chunk_id` 尽力匹配到 source_page 上 raw 文本出现的首个 chunk

### `assets.index.jsonl`

```json
{"asset_id": "...:asset:0025", "path": "assets/image_000025_<hash>.png", "page": 27, "md_line": 802, "size_bytes": 737382}
```

- 文件名保留 Docling 原始 hash（防断链）
- 缺失文件 `missing: true`；不静默跳过
- 与 `pages.index.jsonl` 的 `asset_ids` 交叉引用
- 不猜 caption（`assets_index.py` docstring 明示：6 个 `pictures[].captions` 有结构化 caption 但其余靠散文易误判，保持"只记录可观察事实"）

### `alerts.json`

结构化质量告警。当前 kinds：

| kind | 含义 | payload |
|---|---|---|
| `table_caption_followed_by_image_without_sidecar` | 该表被 Docling 识别成了图片，CSV 不可用 | `page`, `caption`, `image_path` |
| `empty_table_sidecar` | CSV 导出为空 | `table_id`, `page_*`, `caption`, `csv_path`, `empty_csv` |
| `table_without_caption` | 非 TOC 表 caption 缺失 | `table_id`, `page_*`, `csv_path`, `detail` |

所有告警都带页码；README 的 `## Alerts` 段直接把每条渲染成一行可 jump 的说明。

### `document.md` / `document.html` / `document.json`

Docling 原生解析输出，不二次语义处理。Markdown 经过：
- 独立页码行清理 / `T able` OCR 断词清理（`_clean_markdown_ocr_artifacts`）
- `## Cont'd from previous page` 等 h2 清理
- 独立的 `Cont'd on next page` / `Table X-Y - cont'd from previous page` 段落清理（行锚定，inline 散文保留）
- `Table sidecar: [CSV](...)` 链接注入（每张表跟一条指向 CSV 的 sidecar）

## 5. 代码模块边界

| 模块 | 行数 | 职责 |
|---|---|---|
| `docling_bundle/converter.py` | 662 | pipeline 编排 + Docling 调用 + 窗口/缓存 + bundle 写入顺序 |
| `docling_bundle/indexing.py` | 828 | chunk / section / toc / pages_index / lineage / nav parents / 异常检测 |
| `docling_bundle/tables.py` | 538 | 表格导出 / caption 回填 / 续页链路 / CSV 写入 / markdown sidecar 注入 |
| `docling_bundle/cross_refs.py` | 251 | 交叉引用抽取 + section/table/figure resolve + target_id |
| `docling_bundle/reading_bundle.py` | 158 | README 生成（章节大纲 / 表格 kind 分布 / cross-ref 摘要 / alerts） |
| `docling_bundle/alerts.py` | 140 | markdown + sidecar + missing-caption 告警 |
| `docling_bundle/cli.py` | 116 | CLI 入口 |
| `docling_bundle/images.py` | 94 | 图片引用过滤 / artifact 目录解析 |
| `docling_bundle/assets_index.py` | 70 | 图片清单构建 |
| `docling_bundle/patterns.py` | 64 | 共享正则 + OCR 清洗 / heading normalize helper |
| `docling_bundle/config.py` | 42 | Docling pipeline 参数 |
| `docling_bundle/paths.py` | 42 | DocumentPaths frozen dataclass |
| `docling_bundle/models.py` | 24 | RuntimeConfig frozen dataclass |

**核心函数**（indexing.py）：

- `build_chunk_records` — 从 HybridChunker 输出构建 chunks.jsonl 记录；drop TOC 区 chunks（`TOC_DROP_SECTION_IDS`）；lineage promotion 让 chunks reparent 到真实父 section（Phase 58a）；footer phrase 剥离（Phase 60）
- `build_section_records` — 按 section_id 聚合 chunks；orphan chunks 按 doc 顺序 reparent 到最近真实 section，不扩张 parent page range（Phase 54）
- `augment_sections_with_navigational_parents` — 为所有 TOC 条目且在 chunk.heading_path 出现过的 heading 补 nav parent 记录（Phase 59a）
- `build_doc_item_lineages` — 按 doc 顺序遍历，构建 heading 祖先栈，`self_ref` 作为稳定查找 key（Phase 56a）
- `build_toc` — 两-pass 过滤（noisy names / repeat drop）+ `is_chapter` / `suspicious` 标记
- `flag_suspicious_sections` — 跨页 >30% 总页数 flag 为 suspicious
- `compute_dropped_repeat_labels` — 重复 >TOC_REPEAT_DROP_THRESHOLD 次的无编号 heading 被共享 helper 过滤（两层一致，防止 ghost section 溜号）

**测试**：242 个单元测试全绿，覆盖 indexing / tables / alerts / cross_refs / assets_index / markdown_cleanup / cli / paths / config / workflow / reading_bundle。正常 + 边界 + cross-vendor 场景全覆盖。

## 6. 基线实测

### ESP32-S3 Datasheet（87 页）

| 维度 | 状态 |
|---|---|
| 章节导航 | ✅ 7 个 `is_chapter=true` 入口；`toc.json` 150 entries / `sections.jsonl` 145 records（含 9 nav parents） |
| 按页反查 | ✅ `pages.index.jsonl` 覆盖 87/87 页，含 chunk / table / asset / alert 四维 |
| Chunks 覆盖 | ✅ 339 条；heading_path 深度分布 d1/d2/d3/d4/d5 = 19/107/101/100/12 |
| 表格 caption 覆盖 | ✅ 63/65 非 TOC 表有 caption（97%），剩 2 张以 `table_without_caption` alert 回原 PDF |
| 表格语义分类 | ✅ pinout=13 / electrical=27 / strap=1 / revision=4 / generic=20 / document_index=6 |
| 表格 rows 精度 | ✅ 71/71 与 CSV 数据行精确对齐（减 header 行） |
| 续页表 | ✅ 13 条 `(cont'd)`，`continuation_of` 指向父表 |
| 交叉引用 | ✅ 47 条全 resolved (100%)；43 带 `target_id`（section + table）；4 figure resolved via Docling caption |
| 图片 | ✅ 85 asset，零 missing |
| 告警可行动 | ✅ 3 alert，均含页码 + fallback 信息 |
| Integrity | ✅ 0 dangling refs / 0 duplicate section_id / 0 bad page range |

### ESP32-S3 TRM（1531 页，~24min CUDA）

| 维度 | 状态 |
|---|---|
| pages.index 覆盖 | 1531/1531（Phase 60 footer-strip 修复后） |
| Chunks | 3793 条 |
| Sections | 1663 条（含 73 nav parents） |
| Tables | 667（含 6 TOC + 371 `table_without_caption` alert，TRM 大量寄存器表无标"Table X-Y"caption，回原 PDF） |
| Cross_refs | 47/47 resolved；figure 通过 Docling caption resolve |
| Assets | 1448 张 |
| Alerts | 380（371 table_without_caption + 9 empty_table_sidecar），全部带页码契约 |

**规模比**：TRM 约是 datasheet 的 17 倍页、11 倍 chunks，处理时间线性可接受。

## 7. 已知缺口（选择不修）

按 `开发要求.md` 规则 4 / 5，以下是**明知但选择不修**的缺口，处理方式都是让 agent 回原 PDF：

- **Figure 无全局 id**：`cross_refs.jsonl` figure 引用的 `target_page` 已 resolve（Phase 58b），但无稳定 id 可作 `target_id`。Docling 结构性缺口。
- **`table_without_caption` 表**：Docling OCR / layout 层失败，已通过 alert 契约回原 PDF（开发要求 规则 5）。
- **Docling HybridChunker attribution 偶发错误**：例：datasheet `Table 1-1` 被归到 `1.1 Nomenclature` 而非 `1.2 Comparison`；bundle 层修复会引入重归属启发式，过拟合风险高。
- **TRM 的 `is_chapter=True` 噪声**：TRM 用 `1. Internal ROM 0`、`7 . 1. 1 Overview` 这类编号，`is_chapter_heading` 会误命中。跨 vendor 约束决定不收紧判据（会破坏 datasheet `1 ESP32-S3 Series Comparison`）。
- **p.78 字体解码偶发污染**：Docling 层问题，不在本项目层修。

## 8. 决策精选（按时间倒序）

- **只保留 docling_bundle**（2026-04-18）：用户显式裁剪，OpenDataLoader 分支归档
- **不做 RAG / MCP / 全文检索**：基础设施层职责外
- **不追 bundle 体积最小**：证据完整性优先；`assets/` 主导体积，框图 / 时序图最值得保留
- **启发式必须有 alert 兜底**：silent failure 是最大反模式（Phase 60 修的 footer-strip bug 是这条的实例）
- **两层过滤规则原文级别统一**：TOC 过滤 + sections 过滤 + lineage 过滤共享 helper（Phase 51 / 53 / 54 教训）
- **TRM 验证纳入正式 baseline**（2026-04-19）：产物落盘到 `manuals/processed/docling_bundle/esp32-s3-technical-reference-manual-en/`

完整决策历史在 `task_plan.md` 的 `Decisions Made` 段；实测观察在 `findings.md`；会话日志在 `progress.md`；项目整体评估在 `PROJECT_REPORT.md`。
