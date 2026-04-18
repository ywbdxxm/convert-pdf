# Task Plan: docling_bundle 手册转换产线

## Goal

把芯片手册 PDF 转成对 Code Agent（Claude Code / Codex）友好的结构化 bundle，让 agent 能：按章导航、按页回溯、按表筛选、按引用跳转、并且对处理不好的页面知道"回原 PDF"。

评价标准只有一个：**agent 实际查阅 `manuals/processed/docling_bundle/<doc_id>/` 时的使用体验**（见 `开发要求.md`）。

## Robustness Principle

> **改动必须对所有 PDF 普遍适用，不为单一 datasheet 过拟合。**
> **避免为改善一个场景而在另一个场景恶化。**

操作层：

- 每个启发式都要过一遍"在其他 vendor 手册里会发生什么"
- 有地理/排版/命名风险的启发式必须要有 adjacency / number-match / text-pattern 多重约束
- 添加 fallback 到 conservative 类（如 `kind=generic`）而不是强行分类
- 测试必须覆盖：正常场景、相似但无关场景、跨 vendor 差异场景
- **处理不好的表 / 图 / 页直接在 `alerts.json` 里暴露，让 agent 回原 PDF**（规则 5）

## Phases

### 已完成（历史摘要）

**P1–P56b**：环境架构 → 工具选型收敛到 Docling → bundle 结构定稿（toc/pages/sections/tables/cross_refs/assets/alerts + README）→ 八轮深度审计（caption ordering / ghost sections / bullet-prefix headings / heading breadcrumbs / Cont'd paragraphs / TOC columns / rows count）。

**P57（2026-04-18 第二轮审计 + 实施）**：
- P57a：chunks.jsonl 的 `T able` OCR 残留清理（共享 `clean_ocr_text` + word-boundary `\bT (ables?)\b`）
- P57b：`section_id` / `heading_path` / TOC `heading` 尾标点（`:`/`,`/`;`）清理（共享 `normalize_heading_text`）
- 新增 20 测试 → 208/208 通过
- 重跑 datasheet：chunks 零 `T able`、section_id/heading_path/toc 零尾标点；18→2 缺 `source_chunk_id`（剩余 2 条为 p.17 table footnote，需 P58a 解决）

### 已完成（Phase 58 — 2026-04-18 第三轮产物审计 + 实施）

**Baseline 变化**：chunks 309→339 / cross_refs resolved 91%→100% / TOC CSV 首行噪声消除 / 测试 208→220 / counts 其他零回归 / integrity 全绿。

详见 `progress.md` "Phase 58 实施总结"。

### 计划背景（Phase 58 之前）

重跑 esp32-s3 datasheet（77s / CUDA / no-ocr），counts 与 P57 baseline 完全一致：87 pages / 7 chapters / 71 tables / 136 sections / 309 chunks / 47 cross_refs (43 resolved) / 85 assets / 3 alerts / 208 tests green。

**审计证据详见 `findings.md §7d`**。判据：`开发要求.md` 规则 2（避免过度设计）+ 规则 4（谨慎启发式）+ 规则 5（处理不好的回原 PDF）。

本轮只发现一条"明显异常"（A）+ 两条"低风险可选优化"（B、C），其余均符合不修原则。每条 **RED→GREEN→重跑 datasheet** 独立 commit，不混批。

---

**P58a [HIGH, MUST FIX] — 恢复 28 条表脚注 / 引脚图例 chunks**

- **现象**：`chunks.jsonl` 缺失 28 条 `list_item`，分布在 p.16 (3) / p.17 (4) / p.18 (16) / p.22 (3) / p.25 (2)
  - p.17: "Bold marks the pin function set..." / "In column Pin Providing Power, ... see Section 2.5.2 Power Scheme" / "For more information about the boot mode, see Section 3.1 Chip Boot Mode Control"
  - p.22: "I - input. O - output. T - high impedance" — **引脚类型图例**
  - p.18: `EFUSE_PIN_POWER_SELECTION` 驱动强度等
- **影响**：agent 用 chunks.jsonl 查询 "pin type I/O/T 含义" / "VDD_SPI power source" 返回零结果；2 条 section cross_refs（`see Section 3.1` / `see Section 2.5.2`）的 `source_chunk_id` 永远缺失
- **根因**：`indexing.py:333` 丢弃所有 `chunker_headings[-1] in NOISY_SECTION_IDS` 的 chunk。`NOISY_SECTION_IDS` 混用了两类语义：
  - **TOC 区域**（`Contents` / `List of Tables` / `List of T ables` / `List of Figures`）——内容是 TOC 条目复述，丢弃合理
  - **续页标记**（`Cont'd from previous page`）——后续 list_items 是**合法表脚注 / 图例**，不该丢；lineage promotion（P56a）已能把它们 reparent 到真实父 section
- **修复**：把 `NOISY_SECTION_IDS` 拆成两个角色常量：
  - `TOC_DROP_SECTION_IDS = {"Contents", "List of Tables", "List of T ables", "List of Figures"}` — `build_chunk_records` 用它做 drop filter
  - `CONTINUATION_MARKER_SECTION_IDS = {"Cont'd from previous page"}` — 继续作为 lineage-exclusion / `should_keep_chunk_record` / `_is_noisy_toc_heading` 的过滤项（保持 TOC / sections / lineage 不污染），但**不**触发 chunk-drop
  - `NOISY_SECTION_IDS` 保持兼容（= 两者并集），外部调用者不感知
- **验收**：
  1. 重跑 datasheet：`chunk_count` 309 → ~337，`section_count` 仍 136（lineage promotion 接收 reparenting）
  2. `sections.jsonl` 依然零 `Cont'd from previous page` / `List of *` / `Contents` 条目
  3. 缺 `source_chunk_id` 的 cross_ref 降为 0（4 条 figure 仍 `target_page=null` 但那不是 source_chunk_id 问题）
  4. p.17 / p.18 / p.22 的 chunks 能在 `pages.index` 查到
  5. `heading_path` 正确指向真实父 section（如 p.17 footnotes 应挂到 `2.3.2 Pin Assignment` 之类，不是 `"Cont'd from previous page"`）
- **普适性验证**（其他 vendor 手册也会出现续页页脚）：
  - STM32 datasheet 有 `Note: This table continues on next page` — 不在 NOISY_SECTION_IDS，不受影响
  - 核心 invariant：TOC 区的 chunk drop 规则**未放松**（仍丢 Contents / List of *）
- **测试**（RED 先写）：
  - `build_chunk_records` 对 chunker_headings=`["2 Pins", "Cont'd from previous page"]` 的 chunk 保留（lineage promotion 接管）
  - `build_chunk_records` 对 chunker_headings=`["Contents"]` / `["List of Figures"]` 的 chunk 仍丢弃
  - TOC / sections 层对 `"Cont'd from previous page"` 仍然过滤（不新增 ghost）

---

**P58b [MEDIUM, 随 a 或独立] — 4 条 figure cross_refs 用 Docling 原生 caption 解析 target_page**

- **现象**：`cross_refs.jsonl` 有 4 条 `kind=figure`（`Figure 2-2` / `Figure 2-3` / `Figure 7-1` / `Figure 7-2`），全部 `target_page=null, unresolved=true`
- **根因**（之前定性"Docling 无 figure 全局 id" — **需修正**）：其实 Docling `document.json` 直接提供结构化证据：
  - `texts[n]` 里有 `label="caption"` 的 text item，文本形如 `"Figure 2-2. ESP32-S3 Power Scheme"`，带 `prov[0].page_no`
  - 部分 `pictures[k]` 还有 `captions` 字段指向对应 text ref
  - datasheet 实测：6 处 caption 包括全部需要的 Figure 2-2/2-3/7-1/7-2
- **影响**：resolved 率 91% → 100%；agent 拿到 figure 引用可一步跳到目标页
- **修复**：
  - `cross_refs.py` 新增 `_build_figure_page_map(doc)`：遍历 `doc.texts`，label=`caption` 且 `text` 匹配 `^(Figure\s+[A-Z]?\d+(?:[-.]\d+)*)` → `{"Figure X-Y": page_no}`
  - `extract_cross_refs` 接受 `figure_page_map` 参数；`kind=figure` 时用它 resolve
  - `converter.py` 在调用 `extract_cross_refs` 前构建 map 传入
  - 只用 `label=caption` 的 text，不扫描整个 markdown（避免误匹散文中的 "as shown in Figure 2-2" 引用自身的情况）
- **验收**：
  - 4 条 figure refs 全部拿到 `target_page`
  - resolved 47/47（100%）
  - `unresolved=true` 字段从这 4 条移除
- **普适性验证**：`label=caption` 是 Docling 原生、跨 vendor 一致；字段缺失时 map 为空，fallback 到 `unresolved=true`，零回归
- **不做的事**：不扫描 markdown 裸文本做 caption 识别（需启发式区分 caption vs 散文提及，风险高）
- **测试**：
  - caption-labeled text → map 正确
  - 非 caption label 的 text 含 "Figure 2-2" 不进 map
  - map 缺 target 时保持 unresolved

---

**P58c [LOW, 可选] — TOC CSV header row 清洁**

- **现象**：`tables/table_0001.csv` 等 5 个 `is_toc=true` 的 CSV，row 0 是 `['0','1','2','3']`（pandas 默认列索引），table_0001/0003/0004/0005/0006 均有此问题
- **影响**：极低。`tables.index.jsonl` 已把 TOC 表标 `is_toc=true, columns=[], kind=document_index`，agent 按 README "Table Breakdown" 不会点开这些 CSV；但如果 agent **确实**打开 CSV，第一行是无意义数字
- **修复**（两选一，偏向 A）：
  - **方案 A（推荐）**：`export_tables` 在写 CSV 前检测 TOC（或 `columns=[]`），用 `to_csv(header=False)` 写出；其他 65 个表不受影响
  - 方案 B：根本不为 `is_toc=true` 的表写 CSV — 更激进，可能影响依赖 `csv_path` 存在的消费者（`alerts.json` / `tables.index.jsonl` 里 csv_path 引用）
- **验收**：
  - 5 个 TOC CSV 首行不再是 `['0','1','2',...]`
  - 其他 66 个 CSV 列头保持不变
  - `tables.index.jsonl` 的 `csv_path` 仍然有效
- **Decision（留给用户确认）**：LOW 影响 + 低风险，但已接近"过度设计"边界。如果做，用方案 A。

---

**不修（findings.md §7d 详述）**

| 项 | 理由 | 契约 |
|---|---|---|
| 41 non-chapter level-1 sections（前言 + 非数字子标题 + Glossary 术语） | 已在 P55 §7b 决定。无编号前言 heading 普适存在；判据会过拟合 | agent 用 `is_chapter=true` 过滤（README Start Here 步骤 2 已写明） |
| p.22 Table_0015 / p.79 Table_0066 无 caption + MultiIndex 列头混乱 | Docling OCR / layout 层问题 | `alerts.json: table_without_caption` 让 agent 回原 PDF（规则 5） |
| p.78 字体解码污染（`6,*1$785( $5($` 等） | Docling 层问题，bundle 层不救 | document.md 保留污染字符，agent 可见即回原 PDF |
| p.27 Table 2-9 被识别成图片 | Docling 层 | `table_caption_followed_by_image_without_sidecar` alert + fallback image path |
| `assets.index` 不自动填 caption | `assets_index.py` docstring 明确说不猜（6 个有 caption 但其余 79 张靠近的散文易误判） | 保持"只记录可观察事实" |

**推进顺序**：P58a（必做，高影响）→ 重跑 → P58b（必做或紧随）→ 重跑 → P58c（用户确认后）→ 重跑。每步单独 commit，测试先 RED。

### 已完成（Phase 59 — 2026-04-19 第四轮产物审计 + 实施）

**Baseline 变化**：sections 136→145 (+9 navigational parents) / is_chapter=true 可用 0→7 chapters / cross_refs 43 条新增 `target_id` / table `rows` 字段与 CSV 数据行对齐 / 80 条 chunks 去除前导空白 / 测试 220→240 / counts 其他零回归 / integrity 全绿。

详见 `progress.md` "Phase 59 实施总结"。

### 计划背景（Phase 59 之前）

**审计证据详见 `findings.md §7e`**。判据：`开发要求.md` 规则 2（避免过度设计）+ 规则 4（谨慎启发式）+ 规则 5（处理不好的回原 PDF）。

本轮发现 **1 个 HIGH + 2 个 MEDIUM + 2 个 LOW**，其余重复项按历史结论不修。每条 **RED→GREEN→重跑 datasheet** 独立 commit，不混批。

---

**P59a [HIGH] — sections.jsonl 补齐 top-level chapter 与中间 navigational parent 记录**

- **现象**：`4 Functional Description` / `2 Pins` / `5 Electrical Characteristics` 等所有 7 个 chapter 和 7 个中间 heading（`1.2 Comparison` / `2.3 IO Pins` / `4.1.3.3 Clock` / `4.1.3.9 XTAL32K Watchdog Timers` / `5.6 Current Consumption` / `Features` / `Glossary` / `Related Documentation and Resources` / `ESP32-S3 Series`）在 `toc.json` 有、`chunks.jsonl` 的 `heading_path` 引用、但在 `sections.jsonl` **无记录**。README "filter is_chapter=true" 的导航建议在 sections 层兑现不了
- **根因**：`build_section_records` 按 `section_id = heading_path[-1]`（叶子）分组，顶层 / 中间 heading 下无 direct chunk 时就被丢
- **修复**（方案 3 — 最小变动）：
  1. 在 section 记录里加 `is_chapter: bool` 字段（同步 B 修复）
  2. 为每条 TOC 条目（排除 `suspicious=true`、排除 dropped labels），若在 chunks 的 `heading_path` 出现过但不在 sections 里，补一条 "navigational parent" section 记录：
     - `section_id = toc.heading`
     - `heading_path = <祖先链>`（lineage 可复用 `build_doc_item_lineages` 的结果）
     - `heading_level = toc.level`
     - `is_chapter = toc.is_chapter`
     - `page_start = toc.page`
     - `page_end = <最晚一个 heading_path 包含它的 chunk 的 page_end>`
     - `chunk_ids = []`（保持"chunks 互斥分组"契约不破）
     - `chunk_count = 0`
     - `text_preview = ""`
     - `table_ids = []`
- **验收**：
  - `sections.jsonl` section_count 136 → **≥ 150**（新增至少 14 条：7 chapters + ~7 中间 heading）
  - `sections.jsonl` 包含 `section_id == "4 Functional Description"` 记录，`is_chapter=true, page_start=36`
  - 原叶子 section 的 `chunk_ids` / `page_range` 不变
  - `pages.index` 不回归；`cross_refs` / `tables` 不回归
- **普适性**：规则普适（所有手册都有 chapter heading），`chunk_ids=[]` 语义明确（新字段 `is_chapter` + 现有 `chunk_count=0` 组合已明确区分"叶子 section" vs "navigational parent"）
- **测试**（RED 先）：
  - TOC 有 chapter heading `1 Overview`，无直接 chunk 但子 section `1.1 Scope` 有 chunk → sections.jsonl 应含 `1 Overview`（`is_chapter=true, chunk_ids=[], page_start=toc page`）
  - 叶子 section 的 `chunk_ids` / `page_start-end` 保持原值
  - `heading_path` 中间 heading 出现但非 TOC → 不补（避免为每条中间 non-numbered 锚点都造幽灵 section）

---

**P59b [MEDIUM] — cross_refs 填入 `target_id`**

- **现象**：47 条 cross_refs 全部缺 `target_id`，agent 从 xref 跳到目标表/section 记录要再搜
- **修复**：`extract_cross_refs` 在 resolve `target_page` 的同时记录：
  - `kind="section"`：`target_id` = 找到 `section.section_id.startswith(target + " ")` 或 `== target` 的 section
  - `kind="table"`：`target_id` = 找到 `table.caption` 以 `Table <target>` 开头的 `table_id`
  - `kind="figure"`：不填（Docling 无 figure 全局 id）
  - 无匹配 → 不加 key
- **验收**：
  - 26 条 section xref 至少有对应 section 的都拿到 `target_id`（验证每条 `target_id` 存在于 sections 里）
  - 17 条 table xref 同理
  - 4 条 figure 不变
- **测试**：单测已有 `_resolve_section_page` / `_resolve_table_page`，加覆盖 `target_id` 的断言即可

---

**P59c [MEDIUM] — sections.jsonl 加 `is_chapter` 字段**

已并入 P59a（与新增 navigational parent 一起加）。单独列出以在测试里明确覆盖"叶子 section 也带 `is_chapter=false`"。

---

**P59d [LOW] — chunk text 去掉 table_like 的 leading whitespace**

- **现象**：80 个 `table_like=True` chunk 的 `text` 以 `\n` 或 `\n ` 开头，是 Docling HybridChunker 的 table 序列化 artifact
- **修复**：`build_chunk_record` 在 `clean_ocr_text` 之后对 `text` / `contextualized_text` 做 `.lstrip()`（或更保守的 `re.sub(r'^[\s\n]+', '', ...)`）
- **验收**：
  - chunks.jsonl 零 chunk 以 `\n` 或 `\n ` 开头
  - 非 table_like chunk 不受影响（它们已经不以空白开头，lstrip 是幂等操作）
- **测试**：lstrip 的幂等性；table_like chunk 前导空白清除；保留内部换行（只 strip 前导）

---

**P59e [LOW] — `rows` 字段语义改为 "data rows"**

- **现象**：`rows` 当前是 Docling `num_rows`（含 header），所有 65 个非 TOC 表 `rows == CSV 行数`，实际数据行是 `rows - 1`；TOC 表 P58c 之后 header=False，Docling `num_rows` 仍包含 header 的概念行
- **修复**：`export_tables` 中 `rows = max(docling_data.num_rows - 1, 0) if not is_toc else docling_data.num_rows`（TOC 表所有行都是"数据"，非 TOC 表减去 header）
- **验收**：
  - 所有非 TOC 表 `rows = CSV lines - 1`
  - TOC 表 `rows = CSV lines`（P58c 后 header=False）
  - table_0002: rows=44, CSV=44 ✓
  - table_0007: rows=8, CSV=9 (1 header + 8 data) ✓
- **测试**：修改 `test_export_tables_populates_row_count_from_docling_data` 使 `num_rows=3` 时 `rows=2`（header 扣掉）

---

**推进顺序**：P59b → P59d → P59e（小而独立）→ P59a+c（大改动，需扫描消费者）。每步单独 commit；P59a 是 schema 扩张，单独 audit。

**不修**（findings.md §7e 表）：41 non-chapter level-1 sections / p.22+p.79 table 列头 / p.27 Table 2-9 / 4 figure target_id / `## Note:` 等 h2 in md / `Submit Documentation Feedback` 链接。

## Decisions Made（精选）

| Decision | Rationale |
|---|---|
| 只维护 `docling_bundle` 一条产线 | 用户 2026-04-18 裁剪，资源聚焦 |
| 评价标准=agent 实际查阅体验，不是架构纯度 | 用户明确（开发要求.md） |
| 启发式失败必须进 `alerts.json`，不静默降级 | Robustness Principle + 开发要求.md 规则 5 |
| 处理不好的表 / 图 / 页让 agent 回原 PDF | 开发要求.md 规则 5 |
| `NOISY_SECTION_IDS` 拆分（P58a）| TOC drop vs continuation 语义本来就不同，原混用是历史债 |
| Figure resolution 用 Docling `label=caption` 而非扫 markdown | Docling 原生信号 > 启发式；零误伤 |
| 不为 assets 猜 caption | `assets_index.py` 既定契约：只记录可观察事实 |
| 测试数据只用 esp32-s3 datasheet (87 页) | 迭代速度；TRM 耗时大需显式许可 |
| `kind=generic` 是合法分类 | 规则 4：不为填满 kind 分类率而降精度 |

## Errors Encountered（代表性）

| Error | 分析 | 解决 |
|---|---|---|
| "Cont'd from previous page" 混入 NOISY_SECTION_IDS 导致 chunks 被误丢 | P56a 为防 lineage promotion 复活 TOC 内容，引入硬过滤；未区分 TOC-only vs continuation | P58a 拆常量 |
| Figure cross_refs 始终 unresolved | 之前定性"Docling 无 figure 全局 id"未细查 `label=caption` | P58b 用 Docling 原生 caption |
| TOC CSV 首行是 pandas 默认列索引 | `to_csv()` 默认写 header；TOC 表没真实列头时这层是噪声 | P58c 选择性 `header=False` |

完整历史见 git log 和 `findings.md`。
