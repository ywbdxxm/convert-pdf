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

## 8. 参考资料

- Docling: <https://docling-project.github.io/docling/>
- Docling `HybridChunker`: <https://docling-project.github.io/docling/concepts/chunking/>
- Docling LlamaIndex integration: <https://docling-project.github.io/docling/integrations/llamaindex/>
- LangChain Docling loader: <https://docs.langchain.com/oss/python/integrations/document_loaders/docling>

历史上考察过但目前不用：OpenDataLoader PDF、Marker、MinerU、Unstructured、PyMuPDF4LLM、MarkItDown、RAGFlow、Dify、AnythingLLM、Kotaemon、Open WebUI。归档理由见 `task_plan.md` 的 `Decisions Made`。
