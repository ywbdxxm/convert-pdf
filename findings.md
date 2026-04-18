# Findings

> Durable research + architectural knowledge for this repo.
> Ephemeral per-phase implementation notes live in git commit messages and
> `progress.md`; this file is for conclusions that outlive individual phases.

## 1. 项目方向（当前锁定）

**只做 `docling_bundle`。** 把芯片手册 PDF 转成对 Claude Code / Codex 友好的结构化目录，agent 在 `manuals/processed/docling_bundle/<doc_id>/` 直接查阅。

**不做**：

- RAG / 全文检索 / 向量索引 / MCP server
- 通用 PDF→Markdown 转换器
- UI / 应用壳 / 工作流平台
- OpenDataLoader / Marker / MinerU / Unstructured 等平行路线（2026-04-18 用户裁剪）

评价标准只有一个：**agent 查阅 bundle 做嵌入式开发时"从问题到可信答案"的步数**。架构纯度、体积最小、feature 丰富度都不是目标。

## 2. Docling 能力与边界（实测）

**Docling 做对的**：

- PDF 布局解析 + page number + Markdown / JSON / HTML 多视图
- `HybridChunker` 段级分块，带 heading path 和 table grouping
- 表格→CSV 导出 + 多层 MultiIndex header 支持
- `iterate_items()` 提供 heading / table / picture / text item 的统一遍历接口
- page_break placeholder 机制（`<!-- page_break -->`）让 markdown 层可与页码对齐

**Docling 的典型失败模式**（不可修，只能暴露）：

| 失败 | 例（ESP32-S3 datasheet） | 处理 |
|---|---|---|
| 表被识别成图 | p.27 Table 2-9 | `table_caption_followed_by_image_without_sidecar` alert + `image_path` |
| 漏 caption | p.22 Table 0015、p.79 Table 0066 | `table_without_caption` alert + 指向原 PDF |
| 续页列头名漂移 | p.21 "Pin" vs p.22 "Pin No." | 续页链路断开，接受为已知缺口 |
| OCR 列头乱码 | p.79 Table 0066 `F3.F4 / Type / Type` | 列头作为观察值呈现，不修复 |
| OCR 断词 | `T able` / `T ables` / `## Cont'd from previous page` | markdown 层后处理正规化（word-boundary 匹配） |
| 字体解码污染 | p.78 偶发 | 不修 |
| MultiIndex 镜像列头 | `Pin No..Pin No.` | CSV 导出时合并相同两半 |

**结论**：Docling 是可靠的**层次化解析器**，不是**语义理解器**。bundle 层只做**可验证的结构化后处理**，一切语义判断仍需原 PDF 核验。

## 3. 当前 bundle 质量（ESP32-S3 datasheet, 87 页）

实测基线（Phase 54 完成状态）：

- 页数 87 / 章节 7 (is_chapter=true) / 表 71 / 非 TOC 表有 caption 63/65 (97%) / chunk 309 / section 137 / 告警 3
- sections.jsonl 覆盖全部 309 条 chunk（orphan 率 0%）；孤立 chunk 按 doc 顺序 reparent 到前一个真实 section，不扩张其 page range
- `tables.index` kind 分布：pinout=13 / electrical=27 / strap=1 / revision=4 / generic=20
- 续页表 13 条链路，全部 `(cont'd)` 规范化 + `continuation_of` 指向父表
- `cross_refs` 47 条，43 resolved (91%)，剩 4 全是 figure（结构性缺口）
- `assets` 85 张图，零 missing，与 `pages.index.asset_ids` 交叉引用
- Integrity：全部 `csv_path` / `asset.path` / `cross_refs.source_chunk_id` / `chunk_id` 引用零破损（人工扫描确认）

**Bundle 对 agent 的典型步数**：

| 场景 | 步数 |
|---|---|
| GPIO14 默认功能 | 2（README → tables.index 定位 → CSV） |
| VDD 电气参数 | 2（README Table Breakdown electrical → CSV） |
| Section 4.1.3.5 原文 | 2（cross_refs resolve → chunk） |
| 找 block diagram | grep document.md（约 1-2 步） |
| Table 2-5 被谁引用 | 1（cross_refs.jsonl filter） |
| 遇到不可信内容 | 1（alerts.json → 原 PDF 页） |

**结论**：产物已处于"对 AI 消费足够好"的状态。继续优化的边际回报递减。

## 4. 已知缺口（选择不修，按规则 5 让 agent 回原 PDF）

| 缺口 | 为何不修 | Agent 感知 |
|---|---|---|
| Figure 没有 index，cross_refs 里 figure 引用 unresolved | 需要额外启发式识别 "Figure X-Y" caption 和关联图片，过度设计风险 | `cross_refs.jsonl` 标 `target_page: null` |
| p.22 Table 0015 无 caption | Docling 续页列头不一致；放宽匹配会引入误匹 | `alerts.json: table_without_caption p.22` |
| p.79 Table 0066 无 caption + 列头乱码 | OCR 原生错误，列头启发式修复会过拟合 | `alerts.json: table_without_caption p.79` |
| p.78 字体解码偶发污染 | Docling 层问题，不在 bundle 层修 | document.md 有污染字符，agent 看到后回原 PDF |
| TRM (1531 页) 未系统验证 | 耗时大、需用户显式许可 | Backlog Phase 46 |

## 5. 设计原则（从失败中提炼）

### 5.1 启发式必须有 alert 兜底

所有启发式失败都要在 `alerts.json` 留痕，不静默降级。两个关键实例：

- 续页判定要求三重约束：**page adjacency + column 相似 / 显式 cont'd marker + 数字匹配**。单独任何一个信号都不足以链接表。
- `kind=generic` 是合法兜底。不要为了填满 kind 分类率而降精度。

### 5.2 操作顺序比算法更重要

Phase 51 发现的 caption ordering bug 示范了这一点：`propagate_continuation_captions` 写得完全正确，但跑在 `backfill_table_captions_from_markdown` 之前就会把错 caption 固化到空 caption slot，backfill 再也纠正不了。**先从权威来源（markdown 上下文）填 caption，后跑继承启发式**。

### 5.3 两层过滤要同步

TOC 过滤 `NOISY_TOC_HEADINGS`，sections 构建也必须过滤——否则 `"Note:"` 在一个索引里消失、在另一个索引里聚合 62% 文档（Phase 51 ghost section bug）。Single source of truth 为过滤规则。

Phase 53 同类 bug 再现：`build_toc` 用 `TOC_REPEAT_DROP_THRESHOLD` 过滤高频无编号 heading（`Feature List` / `Pin Assignment`），`build_section_records` 漏掉同一规则 → 两个 ghost section 刚好压在 30% suspicious 阈值之下溜过。解决办法是把 heading-occurrence 计数和 repeat-drop 规则提成 `collect_heading_occurrences` / `compute_dropped_repeat_labels` 共享 helper，converter 算一次传给两层。**规则原文级别统一，不光是过滤集合统一**。

Phase 54 又揭示一层：drop 不等于丢内容。P53 把 Feature List 之类从 section 层移除后，53 条 chunk 彻底从 sections.jsonl 消失，agent 按 section tree 找不到 UART 的 feature bullets。修复：orphan chunk 按 doc 顺序 reparent 到最近的真实 section；同时把 `_is_noisy_toc_heading` 全集（含 `TABLE_CAPTION_RE`）接入 `build_section_records`，sections 和 TOC 共用一个 orphan 判定。**关键约束**：orphan reparent 到 host section 时**不扩张 host 的 page range**——否则 Feature List 碎片会反过来把 host 的 span 拉长回 ghost-span 区（阻止同一 bug 从侧门回来）。

### 5.4 不改 assets 文件名

Docling 的 `document.json` / `document.html` 内部引用使用 hash-based 文件名。改名会断链。接受 `image_NNNNNN_<hash>.png` 的命名，通过 `assets.index.jsonl` 提供语义索引。

### 5.5 Bundle 内不写 runtime 状态

窗口缓存挪到 `tmp/docling_bundle-cache/`。`manifest.json` 只放 document identity + counts + file paths，不放 runtime 配置、cache 状态、完整 catalog。

### 5.6 规则 4/5 的落地

- **规则 4**（谨慎使用启发式）：任何新启发式前问自己"在别的 vendor PDF 上会发生什么"；测试要覆盖正常 + 相似无关 + 跨 vendor 场景。
- **规则 5**（处理不好的让 agent 回原 PDF）：bundle 的价值不是"让 Docling 结果变完美"，是"让 agent 知道什么能信、什么要核验"。silent failure 是最大反模式。

## 6. 架构分层（代码与产物对应）

```text
docling_bundle/converter.py      → pipeline 编排 + 窗口 / 缓存
docling_bundle/tables.py         → tables.index.jsonl + tables/*.csv + continuation
docling_bundle/indexing.py       → toc.json + sections.jsonl + pages.index.jsonl + chunks.jsonl
docling_bundle/cross_refs.py     → cross_refs.jsonl
docling_bundle/assets_index.py   → assets.index.jsonl
docling_bundle/alerts.py         → alerts.json
docling_bundle/reading_bundle.py → README.md（整合所有 index 的面向 agent 摘要）
docling_bundle/patterns.py       → 共享正则（被 indexing / tables / alerts / cross_refs 复用）
```

详细产物契约见 `docs/architecture.md`。


## 8. 参考资料

- Docling: <https://docling-project.github.io/docling/>
- Docling `HybridChunker`: <https://docling-project.github.io/docling/concepts/chunking/>
- Docling LlamaIndex integration: <https://docling-project.github.io/docling/integrations/llamaindex/>
- LangChain Docling loader: <https://docs.langchain.com/oss/python/integrations/document_loaders/docling>

历史上考察过但目前不用：OpenDataLoader PDF、Marker、MinerU、Unstructured、PyMuPDF4LLM、MarkItDown、RAGFlow、Dify、AnythingLLM、Kotaemon、Open WebUI。归档理由见 `task_plan.md` 的 `Decisions Made`。
