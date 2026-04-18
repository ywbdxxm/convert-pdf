# docling_bundle Architecture

日期：2026-04-18（Phase 52 完成，用户宣告当前停止点）

## 1. 目标

把一份芯片手册 PDF 转成一个**自包含目录**，让 agent 可以：

1. 在单一入口（`README.md`）立刻知道：页数、表数、告警数、章节大纲、表格分布、阅读顺序
2. 在固定路径上做程序化访问（manifest / toc / pages index / sections / chunks / tables index / cross_refs / assets_index）
3. 按页、按章、按表三种维度交叉跳转
4. 对任何怀疑点，能立刻回到原 PDF 的确切页——尤其当 `alerts.json` 告知"转换结果不可信"时

**不做**的事：全文检索 / RAG / 模型推理 / 语义问答。这些是更上层应用的职责，这个项目只负责把 PDF 压缩成可信、结构化、可导航的证据层。

## 2. 分层

```
PDF (权威真相)
  │
  ▼
Docling pipeline (CUDA, HybridChunker)         ← docling_bundle/converter.py
  │
  ▼
canonical document.{json,md,html}              ← 原始解析结果（不二次处理）
  │
  ▼
navigation layer                                ← docling_bundle/indexing.py
  - toc.json           (hierarchical headings + is_chapter + suspicious)
  - sections.jsonl     (chunk-derived sections + heading_level + table_ids)
  - pages.index.jsonl  (page → chunk/table/asset/alert reverse index)
  - chunks.jsonl       (Docling HybridChunker output + citation + table_ids)
  │
  ▼
evidence layer                                  ← tables.py / images.py / assets_index.py
  - tables.index.jsonl + tables/*.csv
  - assets.index.jsonl + assets/*.png
  - cross_refs.jsonl   (section / table / figure with resolved page numbers)
  │
  ▼
quality layer                                   ← docling_bundle/alerts.py
  - alerts.json        (structural warnings + page refs + csv_path)
  │
  ▼
entry layer                                     ← docling_bundle/reading_bundle.py
  - README.md          (human/agent single entry with alerts inlined)
  - manifest.json      (machine single entry with canonical counts)
```

## 3. 设计原则

1. **原始 PDF 是最终权威。** 任何结构化产物都只是索引，不是 source of truth。
2. **单入口 + 机器入口双轨。** `README.md` 给 agent/人，`manifest.json` 给程序。没有第二个 "index of indexes"。
3. **不可变 dataclass + 纯函数。** Paths、RuntimeConfig 都是 frozen；indexing / tables / alerts 都是无副作用的计算。
4. **处理不好就暴露，不试图修复。** 对应 `开发要求.md` 规则 4/5：谨慎使用启发式，处理不好的表/图/页面直接在 alerts 里告诉 agent 去看原 PDF。代表：`table_without_caption` / `table_caption_followed_by_image_without_sidecar`。
5. **体积不算 KPI，可用性算。** `assets/` 主导 bundle 体积，但手册的框图/时序图是最贵的证据，不做激进剪枝。

## 4. 产物契约

### `toc.json`

```json
{"heading": "2.1 Pin Layout", "level": 2, "page": 15, "is_chapter": false}
{"heading": "1 Overview", "level": 1, "page": 13, "is_chapter": true}
```

- `level` 从数字前缀推断：`1` / `1.2` / `A.1.3` → 1 / 2 / 3；无前缀默认 1
- `is_chapter: true` 仅对编号 L1 heading；`jq 'select(.is_chapter)'` 一键取完整章节目录
- 过滤：`NOISY_SECTION_IDS`、`NOISY_TOC_HEADINGS`（`Note:` 等）、重复 >3 次非编号 heading、被误识为 heading 的表格 caption
- `suspicious: true` 当对应 section 被 `flag_suspicious_sections` 标异常

### `pages.index.jsonl`

```json
{"page": 27, "chunk_ids": ["...:0100"], "table_ids": [], "asset_ids": ["...:asset:0025"], "alert_kinds": ["table_caption_followed_by_image_without_sidecar"]}
```

覆盖任何在 chunk / table / asset / alert 中出现的页。

### `sections.jsonl`

```json
{"section_id": "2.1 Pin Layout", "heading_level": 2, "page_start": 15, "page_end": 16, "chunk_count": 3, "chunk_ids": [...], "table_ids": [...]}
```

- `suspicious: true` 当该 section 跨页 > 总页数 30%（启发式兜底）
- `NOISY_TOC_HEADINGS`（`Note:` 等）不会产生 section 记录——和 `toc.json` 的过滤保持一致，防止幽灵 section

### `tables.index.jsonl`

```json
{"table_id": "...:table:0009", "page_start": 17, "csv_path": "tables/table_0009.csv", "label": "table", "caption": "Table 2-1. Pin Overview (cont'd)", "kind": "pinout", "columns": ["Pin No.", ...], "continuation_of": "...:table:0008", "is_toc": false}
```

- `kind`：`pinout | strap | register | electrical | timing | revision | document_index | generic`（CSV header 启发式推断，`generic` 是安全兜底）
- `continuation_of`：续页表指向父表；caption 统一 `<base> (cont'd)` 格式
- 续页判定要求 **page adjacency**（同页或下一页）+ column 相似或显式 cont'd 标记 + 数字匹配
- `is_toc: true` 标目录页表格

### `cross_refs.jsonl`

```json
{"kind": "section", "target": "4.1.3.5", "source_page": 2, "target_page": 42, "raw": "see Section 4.1.3.5", "source_chunk_id": "...:0005"}
{"kind": "figure", "target": "3-1", "source_page": 30, "target_page": null, "raw": "see Figure 3-1"}
```

- 前缀锚定 `see|refer to|shown in|as shown in`，避开表格 caption 的 "Table X-Y." 假阳性
- 识别 Docling 的 `T able` OCR 断词
- Section 在 `toc.json` resolve、Table 在 `tables.index.jsonl` resolve、Figure 目前不 resolve（设计缺口，见 §7）

### `assets.index.jsonl`

```json
{"asset_id": "...:asset:0025", "path": "assets/image_000025_<hash>.png", "page": 27, "md_line": 802, "size_bytes": 737382}
```

- 不改文件名（避免 `document.json` / `document.html` 内部引用断链）
- 缺失文件显式 `missing: true`，不静默跳过
- 与 `pages.index.jsonl` 的 `asset_ids` 字段交叉引用

### `alerts.json`

结构化质量告警。当前 kinds：

| kind | 含义 | payload |
|---|---|---|
| `table_caption_followed_by_image_without_sidecar` | 该表被 Docling 识别成了图片，CSV 不可用 | `page`, `caption`, `image_path` |
| `empty_table_sidecar` | CSV 导出为空或缺失 | `table_id`, `page_*`, `caption`, `csv_path` |
| `table_without_caption` | 非 TOC 表 caption 缺失（Docling 漏识别），建议核原 PDF | `table_id`, `page_*`, `csv_path`, `detail` |

所有告警都带页码；README 的 `## Alerts` 段直接把每条渲染成一行可 jump 的说明。

## 5. 代码模块边界

| 模块 | 行数 | 职责 |
|---|---|---|
| `docling_bundle/converter.py` | 595 | pipeline 编排 + 窗口/缓存 + bundle 写入 |
| `docling_bundle/tables.py` | 493 | 表格导出 / caption 回填 / 续页链路 / Markdown sidecar 注入 |
| `docling_bundle/indexing.py` | 397 | chunk / section / toc / pages_index / 异常检测 |
| `docling_bundle/cross_refs.py` | 162 | 交叉引用抽取 + 页码 resolve |
| `docling_bundle/reading_bundle.py` | 158 | README 生成（章节大纲 / 表格分布 / cross-ref / alerts） |
| `docling_bundle/alerts.py` | 140 | Markdown + sidecar + 无 caption 告警启发式 |
| `docling_bundle/cli.py` | 116 | CLI 入口 |
| `docling_bundle/images.py` | 94 | 图片引用过滤、artifact 目录解析 |
| `docling_bundle/assets_index.py` | 70 | 图片清单构建 |
| `docling_bundle/config.py` | 42 | Docling pipeline 参数 |
| `docling_bundle/paths.py` | 42 | DocumentPaths frozen dataclass |
| `docling_bundle/models.py` | 24 | RuntimeConfig frozen dataclass |
| `docling_bundle/patterns.py` | 17 | 共享正则常量 |

测试：153 个单元测试全绿，覆盖 indexing / tables / alerts / cross_refs / assets_index / converter-workflow / bundle。端到端集成测试、CLI `main()`、错误路径测试仍缺（Phase 44 任务）。

## 6. 质量维度（ESP32-S3 datasheet 实测基线）

| 维度 | 状态 |
|---|---|
| 章节导航 | ✅ `toc.json` + `is_chapter=true` 一键取 7 个真实章节 |
| 按页反查 | ✅ `pages.index.jsonl` 覆盖 chunk / table / asset / alert |
| 表格 caption 覆盖 | ✅ 63/65 = 97%（剩 2 张有 `table_without_caption` alert 指回原 PDF） |
| 表格语义分类 | ✅ `kind` 分布：pinout=13 / electrical=27 / strap=1 / revision=4 / generic=20 |
| 续页表处理 | ✅ 13 条续页统一 `(cont'd)` 格式，`continuation_of` 指向父表 |
| 交叉引用索引 | ✅ 47 条，91% resolved（剩 4 条全是 Figure，结构性缺口） |
| 图片可追溯 | ✅ 85 条 asset，零 missing，`pages.index` 交叉引用 |
| 告警可行动 | ✅ 3 条告警，均带页码 + fallback 信息（image_path 或 csv_path） |
| README 可读性 | ✅ 单页含章节大纲 + 表格 kind 分布 + cross-ref 摘要 + alerts，无需先 jq |
| 链接完整性 | ✅ 所有 `csv_path` / `asset.path` / `cross_refs.source_chunk_id` 经人工 integrity 扫无破损 |

Bundle 规模：`document.md` 239 KB / `document.json` 12 MB / `document.html` 210 KB / `assets/` 主导体积（87 页 datasheet 共 16 MB）。

## 7. 已知缺口（保留未修）

按 `开发要求.md` 规则 4/5，以下是**明知但选择不修**的缺口，处理方式都是让 agent 回原 PDF：

- **Figure 没有 index**：`cross_refs.jsonl` 里 4 条 figure 引用 `target_page=null`。构建 figure index 需要额外启发式识别"Figure X-Y"caption，当前不做。
- **p.22 Table 0015、p.79 Table 0066 无 caption**：前者 Docling 两页列头 `Pin` vs `Pin No.` 不一致导致续页判定失败；后者 OCR 列头乱码（`F3.F4` / `Type` 重复）。两张表都以 `table_without_caption` alert 暴露，指向原 PDF。
- **p.78 字体解码污染**：偶发的 Docling 原生解析缺陷，不在本 bundle 层修。
- **TRM（1531 页）未系统验证**：需用户显式许可再跑。

## 8. 决策精选

- **只保留 docling_bundle**（2026-04-18）：用户显式裁剪，OpenDataLoader 分支归档
- **不做 RAG / MCP / 全文检索**：基础设施层职责外
- **不追 bundle 体积最小**：证据完整性优先
- **启发式必须有 alert 兜底**：任何失败可见，不静默降级
- **测试数据只用 `esp32-s3_datasheet_en.pdf`**：TRM 验证需显式许可

完整决策历史在 `task_plan.md` 的 `Decisions Made` 段；实测观察在 `findings.md`；会话日志在 `progress.md`。
