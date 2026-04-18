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

## 3. 当前 bundle 质量（Phase 60 baseline, 2026-04-19）

### ESP32-S3 Datasheet（87 页）

实测基线：

- 页数 87 / 章 7 (is_chapter=true) / sections 145 (含 9 nav parent) / chunks 339 / tables 71 / cross_refs 47 (100% resolved, 43 target_id) / assets 85 / alerts 3
- sections.jsonl 覆盖全部 339 条 chunk（orphan 率 0%）；orphan chunk 按 doc 顺序 reparent 到前一个真实 section，不扩张其 page range
- `tables.index` kind 分布：pinout=13 / electrical=27 / strap=1 / revision=4 / generic=20 / document_index=6
- 续页表 13 条链路，全部 `(cont'd)` 规范化 + `continuation_of` 指向父表
- `rows` 71/71 与 CSV 数据行精确对齐（扣 header row）
- `cross_refs` 47 条 100% resolved（Figure 通过 Docling `label=caption` text 解析，P58b）；43 带 `target_id`（section/table）；4 figure 无 target_id（Docling 无 figure 全局 id）
- `assets` 85 张图，零 missing，与 `pages.index.asset_ids` 交叉引用
- Integrity：全部 `csv_path` / `asset.path` / `cross_refs.source_chunk_id` / `chunk_id` / `section_id` / `target_id` 引用零破损

### ESP32-S3 TRM（1531 页）

实测基线（Phase 60 完成）：

- 页数 1531 / sections 1663（含 73 nav parent）/ chunks 3793 / tables 667 / cross_refs 47 (~100% resolved) / assets 1448 / alerts 380
- `alerts`：371 条 `table_without_caption` + 9 条 `empty_table_sidecar`（TRM 寄存器 / 指令编码表普遍无 "Table X-Y" caption，符合规则 5 契约回原 PDF）
- pages.index 覆盖 1531/1531（Phase 60 footer-strip 修复解锁 p.1030）

**Bundle 对 agent 的典型步数（datasheet）**：

| 场景 | 步数 |
|---|---|
| GPIO14 默认功能 | 2（README → tables.index 定位 → CSV） |
| VDD 电气参数 | 2（README Table Breakdown electrical → CSV） |
| Section 4.1.3.5 原文 | 2（cross_refs.target_id → sections.jsonl chunk_ids → chunks.jsonl） |
| 第 4 章概览 | 1（sections.jsonl `section_id="4 Functional Description"`，nav parent 带 page range + table_ids） |
| 找 block diagram | grep document.md（约 1-2 步） |
| Table 2-5 被谁引用 | 1（cross_refs.jsonl filter target_id）|
| 遇到不可信内容 | 1（alerts.json → 原 PDF 页） |

**结论**：datasheet 基线产物已达到"对 AI 消费足够好"；TRM 规模扩展到 17×页，pattern 一致，**rule 5 契约正在发挥作用**（371 个 `table_without_caption` alert 让 agent 不误信 Docling OCR 层失败）。继续优化的边际回报递减。

## 4. 已知缺口（选择不修，按规则 5 让 agent 回原 PDF）

| 缺口 | 为何不修 | Agent 感知 |
|---|---|---|
| Figure 无全局 id；cross_refs figure 无 `target_id` | Docling 结构性缺口；`target_page` 已通过 caption label 解析 | `cross_refs.jsonl` figure 无 `target_id` 字段，但 `target_page` 可用 |
| p.22 Table 0015 / p.79 Table 0066 无 caption | Docling 续页列头不一致 / OCR 列头乱码；放宽匹配会引入误匹 | `alerts.json: table_without_caption` + 回原 PDF |
| p.27 Table 2-9 被识别成图片 | Docling 层 | `alerts.json: table_caption_followed_by_image_without_sidecar` + fallback image path |
| TRM 371 张表 caption 缺失 | TRM 寄存器 / 指令编码表普遍无"Table X-Y"标题；加 heuristic 识别会大量误匹 | 每张都有 `table_without_caption` alert，回原 PDF |
| TRM 9 张表 CSV 为空 | Docling 输出空 grid；可能是图被识别成表 | `empty_table_sidecar` alert |
| TRM `is_chapter=True` 97 条含 `1. Internal ROM 0` 类噪声 | Docling OCR 层把编号列表项升格为 section_header；跨 vendor 约束下不能用更严格的判据（会破坏 datasheet `1 ESP32-S3 Series Comparison`） | 靠 `Chapter NN` 文本关键词再做二次定位 |
| p.78 字体解码偶发污染 | Docling 层问题，不在 bundle 层修 | document.md 有污染字符，agent 可见后回原 PDF |
| Docling HybridChunker 把 `Table 1-1` 归到 `1.1 Nomenclature` 而非 `1.2 Comparison` | 两连续 numbered heading 之间的内容归属启发式 = 过拟合 | 可通过 `Table 1-1` 文本 grep 定位 |

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


## 7b. Phase 55 audit — 2026-04-18 (re-run)

重跑 esp32-s3 datasheet，counts 与 P54 一致（137 sec / 309 chunks / 71 tab / 47 xref / 85 asset / 3 alert），integrity 全部零破损。`开发要求.md` 视角下剩余瑕疵逐项分类如下：

| 现象 | 是否修 | 判据 |
|---|---|---|
| `· IO MUX:` 等 Unicode 项目符号开头的 heading 升格成 level-1 锚点 | **修** | 普适（所有 vendor 手册的 bullet 都是同一批 glyph）；零误伤风险（ASCII 不碰）；re-parenting 路径已存在 |
| `CPU Clock` / `Device Mode Features` 等无编号子标题以 level=1 进 TOC | 不修 | 前言区的 `Features` / `Wi-Fi` 也是无编号 level-1 锚点，用"前面最近的编号父级 +1"会误伤前言 |
| Glossary 的 9 个术语各自成 level-1 | 不修 | 判据只能是"同一页多条无编号 heading"，强过拟合 |
| TOC 表（is_toc=true）列头是整行数据而非表头 | 不修 | 已通过 `is_toc` 标记，agent 直接跳过 |
| p.22 / p.79 两张表 caption 缺失 + MultiIndex 列头混乱 | 不修 | 已进 `alerts.json` 的 `table_without_caption`，契约是回原 PDF |
| Figure 2-2 / 2-3 / 7-1 / 7-2 这 4 条 cross_refs 的 target_page 是 null | 不修 | Docling 不给 figure 全局 id，无法 resolve；`unresolved=true` 已显式标记 |

**修复后**：`section_count` 137 → 136（唯一移除 `· IO MUX:`），bullet chunk 被 re-parent 到 `4.1.3.1 IO MUX and GPIO Matrix`，parent 的 page range 保持 40-40 不扩张。

## 7c. Phase 57 audit — 2026-04-18 (re-run after P56)

不重跑（commit 62bd40d 后产物与代码一致），直接在现有 bundle 上做**逐字段的深度审计**，以"agent 打开文件拿到答案的步数"为判据。Counts：87 pages / 7 chapters / 71 tables / 136 sections / 309 chunks / 47 cross_refs / 85 assets / 3 alerts。

### 发现

| # | 现象 | 证据 | 分类 |
|---|---|---|---|
| A1 | **18 条 chunk 的 `text` + `contextualized_text` 里 "Table" 仍是 "T able"** | `chunks.jsonl` 18 条含 `T able` 字样；document.md 已干净（0 条） | **修**（高优先级） |
| A2 | **18/47 cross_refs 缺 `source_chunk_id`（38%）** | 根因 = A1：cross_refs 的 `raw` 是 "Table 1-1"（从 markdown 抽），chunk text 是 "T able 1-1"（未清洗），`_find_source_chunk` 子串匹配失败 | **修**（随 A1 一并修复） |
| B1 | **13 条前言 section（p.1-7）以 `level=1` 占据 `sections.jsonl` 前排** | `Datasheet Version 2.2` / `Including:` / `ESP32-S3 Functional Block Diagram` / `Power consumption` / `Product Overview` / `Bluetooth ®` / `CPU and Memory` / `Wi-Fi` / `Peripherals` / `Power Management` / `RF Module` / `Security` / `Applications`，全部 `heading_path` 深度=1 | **评估**（加 `is_front_matter` 标记还是不动） |
| B2 | **`section_id = "Including:"` 带尾冒号** | `sections.jsonl` 第 2 行；其他 135 条 section_id 均无尾标点 | **修**（低优先级，清理时一并做） |
| C1 | **`## Note:` 作为 h2 出现在 document.md 第 199 行** | Docling 把 p.1 的 QR-code 指引块升格成 heading；TOC / sections 已过滤（`NOISY_TOC_HEADINGS`），markdown 没同步 | **不修** — 视觉不干扰阅读；`## Note:` 是常见 datasheet 正文前缀（e.g. 寄存器注脚），全局删 heading 会误伤 |
| D1 | **Table_0066 (p.79) 列头崩坏**：21 列、`Type` 出现 3 次、`F3.F4` / `F3.` 这类 MultiIndex flatten 残骸 | `tables.index.jsonl`；CSV row0 就是列头；caption 已缺，已进 `table_without_caption` alert | **不修**（已由 `table_without_caption` alert 代理回原 PDF）；可选：加 `column_header_degraded` alert 做冗余提示 |
| D2 | **Table_0015 (p.22) MultiIndex flatten**：`IO MUX Function 1, 2, 3.F0` 类列头 | `tables.index.jsonl`；8 列全部带 `.F0/.F1/...` 后缀 | **不修**（信息完整，agent 可解析；caption 缺失已进 alert） |
| E1 | 4 条 figure cross_refs `target_page=null` | `Figure 2-2 / 2-3 / 7-1 / 7-2` | **不修**（Docling 无 figure 全局 id，P55 已记录） |
| F1 | 整数完整性：0 orphan chunk / 0 dangling chunk_id / 0 bad page range / 0 rows=null | `sections` / `chunks` / `tables` 全层 | 健康 |

### 根因分析（A1 ↔ A2 的耦合）

P47 修的是 `document.md` 里的 `T able` → `Table`（`_clean_markdown_ocr_artifacts`/`_OCR_TABLE_SPLIT_RE`，在 `converter.py:329` 的最终 markdown 字符串层运行）。chunk 记录由 `HybridChunker` 在 DocItem 上构建（`converter.py:498-540` 附近），取的是 `TextItem.text` 原值，未经 markdown 清洗。因此 markdown 干净而 chunk 脏，导致 `cross_refs.py:_find_source_chunk` 用 markdown 抽出的 `raw="see Table 1-1"` 去 chunk text（"T able 1-1"）匹配时一致 miss。

### 修复原则（沿用 Robustness Principle）

- **A1 / A2**：在 chunk 记录构建的一端加同一个 word-boundary regex（`\bT (ables?)\b` → `T\1`），与 markdown 层共享 compiled pattern。word-boundary 保证不误伤 `T ype` / `T otal` 等。会影响的只有已被 OCR 断词的 Table 字样。**普适、零误伤**。
- **B2**：在 `build_section_records` 结尾对 `section_id` 做尾标点清理（`:` / `,` / `.` / `;`）。**普适、零误伤**。
- **B1**：加 `is_front_matter` 布尔字段，计算 = "section 的 `page_start` < 第一个 `is_chapter=true` section 的 `page_start`" ∧ "section_id 非编号前缀"。agent 仍能看见前言内容（chunk 不丢），但可一行过滤。README 表格按 `is_chapter` 展示原逻辑不变。**普适**；风险点：万一 PDF 没有编号章节（极罕见），flag 会降级为"无 front matter"，等于不动原状，**无负作用**。
- **D1**（可选）：引入 `table_header_degraded` alert kind，判据 = 列数 > 12 **且** (列名重复短 token `Type` / `F\d` 出现 > 2 次 **或** MultiIndex 点分段数 ≥ 3)。仅当已是 `table_without_caption` 时做**冗余提示**，不作为唯一线索。**中等风险**——列数 > 12 的真实合法表（e.g. 复杂 register map）可能误触；因此限制为"同时无 caption 才加"。

### 不修的理由（符合规则 5：回原 PDF）

- D1 / D2 的结构性失真已由 `table_without_caption` alert 暴露给 agent，agent 会按契约回原 PDF，再修列头等于双重启发式。
- C1 的 `## Note:` 在 markdown 里读起来无歧义；进入 TOC / sections / cross_refs 的通道已全部关闭。强删 heading 会侵蚀正文中合法的 Note 段。
- E1 是 Docling 结构性缺口，在 P55 已记录。

## 7d. Phase 58 audit — 2026-04-18 (re-run after P57, 第三轮深度审计)

重跑 esp32-s3 datasheet（77s / CUDA / no-ocr）得到**新 bundle**（`/tmp/esp32-bundle-audit/`），counts 与已提交 bundle 完全一致，208/208 测试绿。以"agent 打开文件拿答案的步数"为判据对每个产物做字段级审计。

### 整体健康指标（baseline）

- 87 pages / 7 chapters / 71 tables / 136 sections / **309 chunks** / 47 cross_refs / 85 assets / 3 alerts
- `heading_path` 深度分布：19 (d1) / 86 (d2) / 92 (d3) / 100 (d4) / 12 (d5) — 无 d0，无 `section_id != heading_path[-1]` 不一致
- Integrity 扫描：0 dangling `csv_path` / `chunk_id` / `target_id`；0 duplicate `section_id`；0 empty-chunk section；0 `rows=null` table（P56b 修复生效）
- P57 遗留指标：0 "T able" OCR 残留（chunks + md）；0 尾标点 heading（TOC + sections）；0 `## Cont` / `## Note:` markdown heading

### 本轮新发现

| # | 现象 | 证据 | 分类 | Severity |
|---|---|---|---|---|
| **A** | **12 页 `pages.index` 记录 `chunk_ids=[]`**（p.8–12 / 17–19 / 22 / 84–86），其中 **28 条 `list_item`** 存在于 `document.md` 和 `document.json` 但 **未进 `chunks.jsonl`** | `document.json#/texts/473-476` 是 p.17 的 pin footnote list_items；`chunks.jsonl` 全库搜索首 60 字符均 miss | **修**（P58a）| HIGH |
| **B** | 4 条 `kind=figure` cross_refs `target_page=null`（`Figure 2-2 / 2-3 / 7-1 / 7-2`）；但 `doc.texts` 存在 **6 个** `label="caption"` 的 text 条目，文本为 `"Figure X-Y. ..."` 且带 `prov.page_no`，直接可用 | `document.json` 中 `texts[idx].label=="caption"` + `re.match(r"^Figure\\s+[A-Z]?\\d+", text)` | **修**（P58b）| MEDIUM |
| **C** | **5 个 `is_toc=true` 的 CSV**（table_0001/0003/0004/0005/0006）首行是 `['0','1','2',...]`（pandas 默认列索引），不是真实表头 | `tables/table_0001.csv` row 0 | **修**（P58c 可选）| LOW |
| **D** | **2 条 section cross_refs 缺 `source_chunk_id`**（`see Section 3.1` / `see Section 2.5.2`，均 source_page=17） | 根因 = A：p.17 list_items 没进 chunks，substring-match 找不到 source | **随 A 同修**（P58a） | MEDIUM |

### A 的根因深挖（P58a）

Docling 在 p.17 顶部把 `"Cont'd from previous page"` 识别为 `label=section_header` 的 text item（texts/472）。其后 4 条 `label=list_item`（texts/473-476）是续页表脚注。

`HybridChunker` 构建 chunk 时把 leaf heading 设成了 `"Cont'd from previous page"`。`build_chunk_records` (`indexing.py:333`) 看到 `chunker_headings[-1] in NOISY_SECTION_IDS` 就 `continue`，整个 chunk 丢掉。

`NOISY_SECTION_IDS` 实际上混了两类语义：

| 成员 | 语义 | 合理的 drop-filter 行为 |
|---|---|---|
| `Contents` / `List of Tables` / `List of T ables` / `List of Figures` | **TOC 区本身**，内容就是 TOC 条目重复 | drop chunk（合理）|
| `Cont'd from previous page` | **续页标记**，后续 list_item 是合法表脚注/图例 | **不该** drop（P56a lineage promotion 已能正确 reparent）|

P56a 引入这条过滤是为了防止 lineage promotion 把 Contents / List of Figures 的内容复活到其真实父 section。但"Cont'd from previous page"本身就没有被 lineage 当成 heading（被 `_is_noisy_toc_heading` 在 `build_doc_item_lineages` 阶段排除），所以即使保留它的 chunk，lineage 也会正确 reparent 到真实父 section（如 `2.3.2 Pin Assignment`），不会污染。

### B 的根因（P58b）

`cross_refs.py:__doc__` 第 14 行注释写 "leaves Figure targets unresolved until a figure index exists"。实际上 Docling 已提供 figure index 所需的原材料：

- `doc.texts[n].label == "caption"` + 文本匹配 `^(Figure\s+[A-Z]?\d+(?:[-.]\d+)*)` → 直接拿到 figure_id → page 映射
- ESP32-S3 实测：6 个 caption（Figure 1-1 / 2-2 / 2-3 / 3-1 / 4-1 / Table 7-1），覆盖了所有 4 条 unresolved figure ref（2-2 / 2-3 / 7-1 / 7-2；后两者在 p.77/78 的 caption-labeled 散文段，上面的 6 个筛选没拿全 — 实际 walk 整个 texts 会抓到 p.77 `#/texts/2861` 和 p.78 `#/texts/2881`）

**普适性**：`label="caption"` 是 Docling 跨 vendor 的原生标签，非启发式。

### C 的根因（P58c）

`export_tables` 在 TOC 表（`is_toc=true`）上调用 `to_csv()` 时 DataFrame 的列索引是 0/1/2/…（因为 TOC 表没被 Docling 识别到真实 header），pandas 默认把它们写成 CSV 首行。

不影响 `tables.index.jsonl`（那里 `columns=[]` 已正确），只影响如果 agent 直接打开 CSV 的第一视觉印象。

### 不修的项（本轮重新审核）

| 项 | 证据 | 为何不修 |
|---|---|---|
| 41 non-chapter level-1 sections 在 `sections.jsonl` / `toc.json` 中占据排名靠前位置 | `Datasheet Version 2.2`、`Features`、`Wi-Fi`、`Bluetooth ®`、`CPU Clock`、`Device Mode Features`、`Glossary`、以及 Glossary 下 8 个小写术语（`module` / `peripheral` / `in-package flash` 等） | P55 §7b 已决。任何"前面最近的编号父级 +1"或"同页多条无编号 heading"判据都会误伤前言区合法 level-1 锚点（`Features` / `Wi-Fi`）。agent 使用契约是 `is_chapter=true` 过滤（README Start Here 步骤 2 明文） |
| p.22 Table_0015 / p.79 Table_0066 无 caption + 列头乱码 | Alert `table_without_caption` 已挂，agent 回原 PDF | Docling OCR 层失败，bundle 层修会过拟合到单表 |
| p.27 Table 2-9 被识别成图 | Alert `table_caption_followed_by_image_without_sidecar` + fallback image path | 同上 |
| p.78 字体解码污染（`6,*1$785( $5($`） | document.md 保留污染字符 | Docling 层，bundle 层不救 |
| `assets.index.jsonl` 不填 caption | `assets_index.py` docstring 明确说不猜 | 6 个 picture 有结构化 caption 但其余 79 张靠散文猜会高误匹；保持"只记录可观察事实" |

### 修复原则

沿用 Robustness Principle：
- **A（P58a）**：拆 `NOISY_SECTION_IDS` 为两个角色常量（TOC-drop vs continuation-marker），lineage promotion 自然接管续页 chunk。**普适、零误伤、零新启发式**——本质是去除一条错误耦合。
- **B（P58b）**：用 Docling 原生 `label="caption"` + prefix-anchored regex (`^Figure\s+...`)。**普适、零启发式（Docling 给的现成标签）**。
- **C（P58c）**：`to_csv(..., header=False)` 仅对 `is_toc=true` 生效。**普适、零风险**。

## 7e. Phase 59 audit — 2026-04-19 (re-run after P58)

重跑 esp32-s3 datasheet 得到 `/tmp/esp32-p59/` 新 bundle（counts 与已提交一致：87 pages / 7 chapters / 71 tables / 136 sections / **339 chunks** / 47 cross_refs (47/47 resolved) / 85 assets / 3 alerts）。以"agent 打开文件拿答案的步数"为判据做字段级深度审计。

### 本轮新发现

| # | 现象 | 证据 | Severity |
|---|---|---|---|
| **A** | **`sections.jsonl` 缺所有 top-level chapter 和中间数字 section**（14 个 TOC 条目在 sections 里无对应记录） | `1 ESP32-S3 Series Comparison` / `2 Pins` / `4 Functional Description` / `5 Electrical Characteristics` 等全部 7 个 `is_chapter=true` 以及 `1.2 Comparison` / `2.3 IO Pins` / `4.1.3.3 Clock` / `4.1.3.9 XTAL32K Watchdog Timers` / `5.6 Current Consumption` / `Features` / `Glossary` / `Related Documentation and Resources` / `ESP32-S3 Series` 等非叶 heading 均无 section 记录 | **HIGH**（README 建议"filter is_chapter=true"但 sections 没这些 heading） |
| **B** | `sections.jsonl` **没有 `is_chapter` 字段**（`toc.json` 有，sections 没），agent 只能 cross-ref 或用正则识别 `^\d+\s` 判定 | `sections.jsonl` 字段：`doc_id / section_id / heading_path / heading_level / page_start / page_end / chunk_count / chunk_ids / text_preview / table_ids`（无 `is_chapter`）| **MEDIUM**（README 提示"chapter outline"由 toc.json 给，但 sections 没同步标记，两层 schema 不对齐） |
| **C** | **cross_refs.jsonl 的 `target_id` 未填**（47 条全部没有 `target_id` key） | `xr[0]` 只有 `kind / raw / source_chunk_id / source_page / target / target_page` | **MEDIUM**（agent 从 cross-ref → 目标表/section 记录要再搜 `caption.startswith("Table 1-1")` / `section_id.startswith("4.1.3.5")`，多一跳） |
| **D** | **80 个 `table_like=True` chunk 的 `text` 以 `\n` 或 `\n ` 开头**（Docling HybridChunker 的 table serialization leading-whitespace 伪 artifact） | `p13` / `p16` 等的 pinout chunk text：`'\n ESP32-S3R8, VDD_SPI Voltage 4 = 3.3 V...'` | **LOW**（视觉瑕疵，不影响搜索；但在 contextualized_text 里也会出现类似 preview 不整洁） |
| **E** | **`tables.index.jsonl` 的 `rows` 字段与 CSV 实际数据行不对齐**（所有 65 个非 TOC 表 `rows = CSV lines`，等于 Docling num_rows 含 header 的计数；TOC 表因 P58c 写入 `header=False` 也 +1 偏差出现了 1 条：table_0002 `rows=45 / CSV=44`） | 66/71 表 `rows` 与 CSV 数据行不一致；语义是 Docling 原生 `num_rows`（包含 header 行），不是 data rows | **LOW**（字段语义没 README 说明；agent 粗略按 rows 过滤"大表"够用，但精确行数差 1） |
| **F** | 41 个 non-chapter level-1 section / 8 个 Glossary 小写术语 | P55/P58 §7b, §7d 已决 | **不修** |

### A 的证据与后果

`4 Functional Description` 在 chunks.jsonl 里 **124 条 chunk** 的 `heading_path` 包含它；在 TOC 里 `is_chapter=true, page=36`；但 `sections.jsonl` 查 `section_id == "4 Functional Description"` 返回 **0 条**。agent 问"第 4 章讲什么"的第一直觉操作会 miss。

### A 的根因

`build_section_records` 把 chunk 按 `section_id = heading_path[-1]`（叶子 heading）分组。因此只有"直接挂 chunk 的 heading"进 sections。顶层 chapter 和中间分组 heading 下面没有 direct chunk（Docling 把内容挂在最深 numbered heading），所以它们在 sections 层消失。

### A 的修复思路（多方案对比）

| 方案 | 优点 | 缺点 | 风险 |
|---|---|---|---|
| (1) 为每个 TOC 条目都建 section 记录（含无 direct chunk 的父级） | sections.jsonl 与 toc.json 1:1 对应；agent 能找到 "4 Functional Description" | 引入"空 chunk_ids 的 section"（chunk_count=0），和现有"0 empty chunk_ids section"的一致性契约冲突 | 中 |
| (2) 给 chapter/中间 heading 的 section 记录填入**descendant 聚合 chunk_ids**（把 `4.1.*` 全部 chunks 累加到 `4 Functional Description`） | 简单、符合"按章查阅"直觉 | chunks 重复出现在多个 section（叶子 + 所有祖先），`sections.jsonl` 的"chunks 互斥分组"契约被打破；pages.index.section_ids 也要重算 | 高 — 跨契约 |
| (3) 只补空 chunk_ids 的 "navigational parent" 记录，带 `is_navigation_only=true` 标记 | 保持 chunks 互斥分组；agent 仍能按 section_id 定位 chapter；加一个显式 flag 解释"为什么 chunk_ids=[]" | schema 变复杂；但这个 flag 语义清楚 | 低 |
| (4) **不动 sections**，只在 **README 修正导航建议**：把 "filter is_chapter=true" 的建议从第 2 步挪到专门说明"从 toc.json 拿到 chapter.page 后用 `jq '.[] \| select(.page_start<=PAGE and PAGE<=.page_end)'` 查 sections"；增加"用 toc.json 按 prefix 找 section" | 零代码改动，只改 agent 使用契约 | agent 多一步 | 极低 |

**推荐 (3)**：最小 schema 变动（+1 字段 + 1 布尔），对 agent 最直接（一步 `section_id == '4 Functional Description'` 就能拿到聚合信息）。同时 B（`is_chapter` 字段）也顺便解决。但需评估"empty chunk_ids 的 section 是否破坏其他消费者"。

### B、C、D、E 的修复方向

- **B** — `build_section_records` 对每条 section 计算 `is_chapter = _is_chapter_heading(section_id)`（同 toc.json 的判据，提取共享 helper）。零风险。
- **C** — `extract_cross_refs` 在 resolve `target_page` 的同时记录 `target_id`：
  - section 类型：扫 `toc` / section_records 找 `heading.startswith(target + " ")`，取 `section_id`
  - table 类型：扫 `table_records` 找 `caption` 的 `Table X-Y` 前缀匹配，取 `table_id`
  - figure 类型：暂无（Docling 无 figure id）
  - 无匹配时不加 `target_id`。零风险。
- **D** — `clean_ocr_text` 已清洗 `T able`；新增 leading-whitespace trim（`text.lstrip()` / `contextualized_text.lstrip()`）对 `table_like=True` 的 chunk。这是 Docling serialization 的 artifact 而非信息，零损失。
- **E** — 两个选项：
  - (E1) 把 `rows` 字段语义改成 "CSV 数据行数"（非 TOC = num_rows - 1；TOC = num_rows），即 data-row-count；README / 字段注释同步更新。
  - (E2) 保持 Docling 原生 `num_rows` 语义，但 README 明确注明"包含 header 行"。
  - 推荐 (E1)：更符合 agent 直觉"rows 就是数据行数"；对 TOC 表 header=False 写入后仍正确。

### 不修的项（沿用 P55/P58 结论）

| 项 | 理由 |
|---|---|
| 41 个 non-chapter level-1 section | P55 §7b 已决（前言 + 非数字子标题 + Glossary 术语）；任何判据会误伤合法前言 |
| p.22 Table_0015 / p.79 Table_0066 无 caption + 列头崩坏 | `alerts.json: table_without_caption` 契约回原 PDF |
| p.27 Table 2-9 被识别成图 | alert + fallback image |
| 4 条 figure cross_refs `target_id` 缺失 | Docling 无 figure 全局 id（P58b 已让 target_page resolve，但无稳定 id 可引） |
| `Cont'd from previous page` h2 / `## Note:` / `## Contents` / `## List of *` 仍在 document.md | 它们在 TOC/sections/chunks 层已过滤；删 md heading 会破坏正文上下文可读性 |
| `## Note:` x8 h2 in md | 合法 note 块前缀 |
| "Submit Documentation Feedback" x1 链接 | 是 Espressif 的正式 feedback URL，不是 OCR 垃圾 |

## 8. 参考资料

- Docling: <https://docling-project.github.io/docling/>
- Docling `HybridChunker`: <https://docling-project.github.io/docling/concepts/chunking/>
- Docling LlamaIndex integration: <https://docling-project.github.io/docling/integrations/llamaindex/>
- LangChain Docling loader: <https://docs.langchain.com/oss/python/integrations/document_loaders/docling>

历史上考察过但目前不用：OpenDataLoader PDF、Marker、MinerU、Unstructured、PyMuPDF4LLM、MarkItDown、RAGFlow、Dify、AnythingLLM、Kotaemon、Open WebUI。归档理由见 `task_plan.md` 的 `Decisions Made`。
