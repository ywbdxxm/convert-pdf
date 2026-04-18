# Progress

## 当前状态（2026-04-18）

- 基线 PDF：`manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf` (87 页)
- 最新 bundle：`manuals/processed/docling_bundle/esp32-s3-datasheet-en/`
- 测试：188/188 通过
- Counts（P56 后）：87 pages / 7 chapters / 71 tables / 47 cross_refs (43 resolved) / 85 assets / 136 sections / 309 chunks / 3 alerts
- Chunk coverage: 309/309（sections.jsonl 覆盖全部 chunk，零 orphan）
- Integrity: 全部 chunk_id / table_id / asset_id / csv_path 引用零破损
- 新增产物字段：`chunks.heading_path` 深度 1-5（之前恒为 1）、`tables.rows`（之前恒 null）、`tables.columns=[]` for TOC tables
- Design spec: `docs/superpowers/specs/2026-04-18-docling-bundle-phase56-design.md`

## 最近 session（2026-04-18）

**P56b（polish: Cont'd paragraphs / TOC columns / rows count）**：

- G — document.md 里 14 条独立 `Cont'd on next page` / `Table X-Y - cont'd from previous page` 段落清掉（原来的 heading-only 清理没抓到段落形式）。新 `_CONTINUATION_PARAGRAPH_RE` 锚定行边界，inline 散文提及保留
- D — TOC 表（`is_toc=true`）的 `columns` 改成 `[]`，不再暴露 Docling 误识别的行数据当表头（`["0","1","2"]` / `["","4.1.1.3","...","37"]`）
- C — 所有表的 `rows` 字段从 `TableItem.data.num_rows` 填入（原来恒 null），agent 可按表大小筛选
- 10 新测试，188/188 通过；esp32-s3 bundle counts 零回归；所有 71 张表现在都有 rows，所有 6 张 TOC 表 columns=[]

**P56a（heading breadcrumbs）**：

- 核心问题：chunks.jsonl 每条 chunk 的 `heading_path` 深度恒为 1，只有直接父 heading，无章节上下文。agent 做关键词搜索拿到 chunk 但看不到它属于哪个章
- 新增 `build_doc_item_lineages`：doc 顺序遍历 `iterate_items()`，维护 `(level, text, is_numbered)` 栈，每个 item 快照当前栈。查找 key 用 `self_ref`（HybridChunker 会重新包装 DocItem，`id()` 会 miss 到；`self_ref` 稳定）
- 层级规则：编号前缀权威（`4.1.3.5` → 4）；非编号 heading 优先用 Docling 的 `heading_level`，否则挂在最深的编号祖先之下（level = max_numbered + 1），不 pop 编号骨架（防止 `BACKUP32K_CLK` 这种章内粗体子标题把 `4 Functional Description` 顶出）
- `dropped_repeat_labels`（Feature List 等 30x 重复标签）也从栈排除，防止污染祖先
- `section_id` 仍是 `heading_path[-1]`，sections.jsonl 分组语义不变
- 补漏：`build_chunk_records` 现在用 chunker 原始 leaf 判定 NOISY_SECTION_IDS 以过滤 TOC-region chunk（防止 lineage 提升把之前被 section_id 规则 reject 的 Contents / List of Tables 内容复活）
- 9 新测试，178/178 通过；datasheet counts 零回归；UART chunks 现在正确带 `[4 Functional Description, 4.2 Peripherals, 4.2.1 Connectivity Interface, 4.2.1.1 UART Controller]` 四级链；depth 分布 19(d1)/86(d2)/92(d3)/100(d4)/12(d5)

**P55（bullet-prefixed heading filter）**：

- 按 `开发要求.md` 重跑 datasheet 全量审计（77s / CUDA / no-ocr）：计数与 P54 baseline 完全一致（3 alerts 继续如预期暴露回原 PDF 的那几张表）
- TOC / sections / chunks / cross_refs / assets / tables.index 全层 integrity 扫描零破损
- 剩余结构性问题中符合"普适 + 低风险"标准的只有一个：Docling 把 `· IO MUX:` 这类**以 Unicode 项目符号（U+00B7 / U+2022 等）开头的行**升格成 heading，于是它进 TOC 成了 level-1 锚点、进 sections.jsonl 成了独立 section
- 根因：`_is_noisy_toc_heading` 只过滤硬编码名单 + table-caption 正则 + noisy-text pattern，没处理 bullet-prefix
- 修复：新增 `_BULLET_HEADING_PREFIX_RE = re.compile(r"^[·•◦▪▫►◆∙⬧]")`（只管 Unicode 项目符号，ASCII `-` / `*` / `+` 不碰以免误伤 `Wi-Fi` / `2.4 GHz` / `Low-Power Modes`），在 `_is_noisy_toc_heading` 里加一条判定分支
- 已有 P54 orphan re-parenting 路径自动接住被过滤的 chunk，内容不丢
- 3 新测试（TOC 过滤 / 相邻 ASCII 字符保留 / sections 层 re-parenting 保持 parent page range）
- 结果：`section_count` 137 → 136；`· IO MUX:` 不再出现在 TOC，内容挂回 `4.1.3.1 IO MUX and GPIO Matrix` 的 `chunk_ids`，parent 的 page range 未扩张（40-40 保持）；其他 count 零回归；167/167 通过
- 其他观察到但**不修**的问题（见 `findings.md` Phase 55 节 & `task_plan.md` Decisions Made）：非数字型子标题（`CPU Clock` / `General Features` 等）level=1 偏高、Glossary 术语散成独立 heading、TOC 表列头是垃圾 —— 都属于过拟合高风险，agent 通过 `is_chapter=true` 过滤即可绕开

**P54（orphan chunk 重新归属 + table-caption leak）**：

- P53 commit 后重跑 datasheet 深度审计发现：
  1. 53 条 chunk 从 sections.jsonl 彻底丢失——heading_path 是 `Feature List` / `Pin Assignment` / `Note:` 的 chunk 现在没有 section 收留，agent 从 section tree 导航到 `4.2.1.1 UART Controller` 只能看到 intro 段，看不到它的 feature bullets
  2. `Table 2-9. Peripheral Pin Assignment` 作为 table caption 被 Docling 层分析器升格成 heading，漏进 sections.jsonl（TOC 用 `TABLE_CAPTION_RE` 过滤掉了，sections 没同步）
- 修复策略：`build_section_records` 的 orphan 判定改成和 TOC 同一规则（`_is_noisy_toc_heading(section_id) or section_id in dropped_repeat_labels`）；orphan chunk 按 doc 顺序 re-parent 到最近的真实 section，但**不扩张 parent 的 page range**（避免 ghost-span 从侧门回来）
- 4 新测试 + 已有测试保持绿；164/164 通过
- 结果：section_count 138→137；chunk coverage 256/309 → 309/309；`4.2.1.1 UART Controller` 现在正确含 intro + Feature List + Pin Assignment 三条 chunk，page 范围仍是 p.51-51；`Table 2-9` 的 note chunk 被合并回 `2.3.5 Peripheral Pin Assignment`
- Full integrity sweep：0 issue；7 chapters / 71 tables / 47 cross_refs (43 resolved) / 85 assets 全部引用零破损

**P53（ghost sections：Feature List / Pin Assignment）**：

- 重新审视 bundle 产物发现 `sections.jsonl` 仍有两个 ghost section：
  - `"Feature List"`：30 chunks，p.36-59（28% 文档，刚好低于 30% suspicious 阈值）
  - `"Pin Assignment"`：15 chunks，p.51-60
- 根因：`build_toc` 通过 `TOC_REPEAT_DROP_THRESHOLD=3` 过滤了重复的无编号 heading，但 `build_section_records` 只过滤硬编码的 `NOISY_TOC_HEADINGS`（Note/Notes），没同步 repeat-count 规则 → 两层导航不一致
- 修复：提取 `collect_heading_occurrences` / `compute_dropped_repeat_labels` 两个 helper，converter 计算一次 `dropped_repeat_labels` 传给 sections 和 toc；`build_toc` 内部也改为用同一 helper
- 7 新测试（section 过滤 + 保留 + collect_heading_occurrences + compute_dropped_repeat_labels 边界）
- 重跑 datasheet：`section_count` 140 → 138，chunks.jsonl 里 30 条 Feature List chunks 仍在（只是不再作为独立 section 出现），其他 count 零回归
- 测试：160/160 通过

## 早前 session（2026-04-18）

当天分六轮深度审计 + 修复（Phase 47-52），见 git log 和 `task_plan.md` Phases 段。

- integrity 扫描零破损：全部 `csv_path` / `assets.path` / `cross_refs.source_chunk_id` / `chunk_id` 引用完整
- 唯一命中"明显异常"：2 张非 TOC 表 caption 缺失 (p.22 / p.79)，bundle 对 agent silent failure
- 修复：新增 `detect_missing_caption_alerts`（纯结构检查，非启发式），挂进 alerts pipeline
- 3 新测试（正面 + 过滤 TOC + 过滤有 caption）
- 重跑 datasheet：`alert_count` 1 → 3，其他 count 零回归

**P51（caption ordering bug + ghost section filter）**：

- 发现 `export_tables` 在 backfill 之前误跑 continuation 启发式 → 列头相似的不同表被错链（Table 6-10 被打成 "Table 6-9 (cont'd)"）
- 发现 `build_section_records` 没过滤 `NOISY_TOC_HEADINGS` → "Note:" 成 ghost section 横跨 62% 文档
- TDD RED-GREEN 双修复；`section_count` 141 → 140；零其他回归

**P47-P50**：manifest 计数补齐 / `T able` OCR 清理 / backfill prefix bug / MultiIndex 镜像列头 / H2 `Cont'd` 清理 / electrical 分类放宽。

## 历史归档（2026-04-12 ~ 2026-04-17）

这段时间做了：

- 工作站架构（WSL + RTX 4060 + shared AI base + docling overlay）+ 镜像统一 + bootstrap 脚本
- 方向收敛：Docling / Marker / MinerU / Unstructured / PyMuPDF4LLM / RAGFlow 调研后，阶段性保留 `docling_bundle` 与 `OpenDataLoader hybrid` 对照
- 2026-04-18 起用户明确只做 docling，OpenDataLoader 路径归档（`opendataloader/README.md` 已标 archived）
- 深度 audit（Phase 37）→ Phase 38-45 核心产物契约（toc / pages.index / sections / tables.index / cross_refs / assets.index / README 可读性）

完整历史在 git log 和 `findings.md` 的 "Current Direction / Baseline / Main Comparison Focus / Diminishing Returns Assessment" 段。
