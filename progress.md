# Progress

## 当前状态（2026-04-19，Phase 60 完成 — 完整 TRM 验证 + 最终产物已落盘）

**产物位置**：
- `manuals/processed/docling_bundle/esp32-s3-datasheet-en/`（87 pages, 23s）
- `manuals/processed/docling_bundle/esp32-s3-technical-reference-manual-en/`（1531 pages, ~24min）

**测试**：242/242 通过（P59 baseline 240 + P60 新增 2）

**Phase 60 — 唯一必修发现（完整 TRM 审计触发）**：

### P60-TRM-fix（commit `df84175`）— 页脚短语 footer 导致 silent chunk drop

- **bug**：`NOISY_TEXT_PATTERNS` 之前用 `re.search` 判断并**丢弃整块 chunk**。Docling 偶尔会把 page_footer "Submit Documentation Feedback" 与正文 list_item 合并在同一 chunk；过滤器把整块 chunk 连同正文一起删除
- **TRM 实测损失**：**7 条 substantive chunk** 被静默丢弃，包括 p.1030 的 5 条 I2C 寄存器位描述（`I2C_SCL_ST_TO_INT_RAW` / `I2C_DET_START_INT_RAW` 等）
- **违反 `开发要求.md` 规则 5**：silent failure（agent 在 chunks.jsonl 里查 `I2C_SCL_ST_TO_INT_RAW` 返回 0，且无 alert 提示）
- **修复**：把 filter 策略从"整块拒绝"改成"剥离短语"。新增 `_strip_noisy_text_phrases` 在 `build_chunk_record` 里对 text / contextualized_text 做就地清理：footer 单独成块 → 清理后为空 → 保持之前丢弃语义；混合内容 + footer → 只剥离 footer，保留正文
- **regex 微扩**：`\[?submit documentation feedback\]?(?:\([^)]*\))?` 额外覆盖 markdown link 形态 `[Submit Documentation Feedback](url)`
- **测试**：2 新测试 — 混合场景 chunk 保留 + 纯 footer chunk 仍被丢弃；既有"filter_feedback_link_noise"（纯 footer 拒收）保持绿

### TRM 实测结果对比

| 指标 | fix 前 | fix 后 |
|---|---|---|
| chunks | 3786 | **3793** (+7) |
| I2C_SCL_ST_TO_INT_RAW 查得 | 0 | **1** |
| I2C_SCL_MAIN_ST_TO_INT_RAW 查得 | 0 | **1** |
| I2C_DET_START_INT_RAW 查得 | 0 | **1** |
| pages.index 覆盖 | 1530/1531 | **1531/1531**（p.1030 回归）|
| chunks 含 "Submit Documentation Feedback" | 若干 | **0** |
| sections / tables / alerts | — | 667 / 1663 / 380（其他 count 零回归） |

### Datasheet 实测（零回归）

| 指标 | P59 end | P60 end |
|---|---|---|
| 所有 counts | 145 sec / 339 chunks / 71 tables / 47 xrefs (100% resolved) / 85 assets / 3 alerts | **完全一致**（datasheet 无 footer-leak 场景） |

### TRM 其他观察（**不修**，全部符合 rule 4/5 历史结论）

| 项 | 理由 |
|---|---|
| 371 条 `table_without_caption` alert（56% 表无 "Table X-Y" caption） | TRM 寄存器 / 指令编码表确实没标 `Table`；`alerts.json` 让 agent 回原 PDF（规则 5）|
| 9 条 `empty_table_sidecar` alert | Docling 输出空表结构；alert 已暴露 |
| `is_chapter=True` 97 条（含 `1. Internal ROM 0`, `7 . 1. 1 Overview` 类 OCR 乱码）| Docling 层 OCR artifact + TRM 特殊编号（空格 `7 . 1`）；任何 heuristic 修复会破坏 datasheet，违反 rule 4 跨 vendor 约束 |
| `"Continued from the previous page..."` 4 种变体 heading | fix 生效后内容正常落盘；原以为要扩 `CONTINUATION_MARKER_SECTION_IDS`，实际上根因是 footer filter，变体 filter 不需要 |
| `Notice` ghost section 29 页（p.844-873）| 法律条款段确实 29 页一整块，不是 Docling 错 |
| `7 . 1. 1 Overview` 型 OCR 空格错位 | Docling 层；heuristic 收缩会破坏合法的 `7 . 1`（大纲编号分隔符） |

## Phase 59 session 总结（2026-04-19 已完成）

### P59b（commit `3605c7c`）— cross_refs 填 `target_id`

- `_resolve_section` / `_resolve_table` 改签名返回 `(page, id)`；`_resolve_section_page` / `_resolve_table_page` 作为薄 back-compat 包装
- `extract_cross_refs` 有 target_id 时写入 record；figure 不写（Docling 无 figure id）；无 caption 的 table 不写
- 效果：section xref 26/26 带 target_id；table xref 17/17 带 table_id；figure xref 4/4 按设计不带
- 新 6 测试

### P59d（commit `3846774`）— chunks text 去除前导空白

- `build_chunk_record` 在 `clean_ocr_text` 之后 `.lstrip()` 清理 `text` / `contextualized_text`
- HybridChunker 在续页表序列化时注入的 `\n ` 前缀消除（80 条 → 0）
- 内部换行保留
- 新 2 测试

### P59e（commit `0828bea`）— `rows` = data-row count

- `export_tables` 改逻辑：从 `table_cells` 里统计 `column_header=True` 的不同 `start_row_offset_idx` 个数，从 `num_rows` 中减去
- 效果：71/71 表的 `rows` 与 CSV 数据行数（`wc -l - 1`，TOC 表 `wc -l`）完全对齐
  - `table_0008`（2 级 MultiIndex header）：rows 20 → 18
  - `table_0002`（TOC）：rows 45 → 44
- is_toc 特殊分支移除，因为即使 TOC 表在 Docling 内部模型里也有 column_header 行；规则统一为"减去 header 行数"
- 更新 3 既有测试 + 新 2 测试（multi-level header / zero-row guard）

### P59a+c（commit `1a38690`）— navigational parent sections + `is_chapter` 字段

- 核心缺口：sections.jsonl 原本仅包含有直接 chunk 的叶子 heading → 所有 chapter / 中间 heading 缺席 → README 的 `filter is_chapter=true` 建议在 sections 层拿不到东西
- 新增 `augment_sections_with_navigational_parents`：遍历 TOC，对于"chunk.heading_path 里出现过 + 不是已有 leaf section + 不是 suspicious"的 heading 补 1 条 navigational parent 记录
- 不破坏 chunks 互斥分组（`chunk_ids=[]`/`chunk_count=0`），`is_chapter` 字段标识角色
- `attach_table_references` 移到 augment 之后，parent 也拿到覆盖 page span 的 table_ids（支持"第 4 章有哪些表"查询）
- `build_section_records` 每条叶子 section 同步写 `is_chapter` 字段（`is_chapter_heading` 新 helper，与 `build_toc` 共享判据）
- 效果：sections 136 → 145（+9 navigational parent）；7 chapters 全部可用 `filter is_chapter=true` 查到
- 新 11 测试（augment 行为 + is_chapter helper 判据）
- integrity：chunks 互斥 / 0 重复 section_id / 0 bad page range / is_chapter 与 toc 一致

## Phase 59 最终 baseline（post-commit 1a38690）

| 指标 | P58 end | P59 end |
|---|---|---|
| sections | 136 | **145** (+9 nav parents) |
| sections with is_chapter=true 可查询 | 字段缺 | **7 chapters** |
| chunks | 339 | 339 |
| chunks starting with whitespace | 80 | **0** |
| tables | 71 | 71 |
| `rows` == CSV data lines | 5/71 | **71/71** |
| cross_refs total | 47 | 47 |
| cross_refs resolved | 47 | 47 |
| cross_refs with target_id | 0 | **43** (section + table) |
| alerts | 3 | 3 |
| 测试 | 220/220 | **240/240** |
| Integrity | 全绿 | 全绿 |

## Phase 58 session 总结（2026-04-18 已完成）

- 重跑 esp32-s3 datasheet 实测：**87 pages / 7 chapters / 71 tables / 136 sections / 339 chunks / 47 cross_refs (47/47 resolved, 100%) / 85 assets / 3 alerts**
- 测试：**220/220 通过**（P57 baseline 208 + P58a 2 + P58b 9 + P58c 1）
- P58 三个 commit 已推进：`da0bd80` P58a → `bac833b` P58b → `b519f4d` P58c

## Phase 58 实施总结（2026-04-18 已完成）

### P58a（commit `da0bd80`）— chunks 恢复 28 条表脚注 / 引脚图例

- 拆 `NOISY_SECTION_IDS` → `TOC_DROP_SECTION_IDS`（drop chunk）+ `CONTINUATION_MARKER_SECTION_IDS`（不 drop，lineage promotion 负责 reparent）
- `build_chunk_records` 的 drop filter 收窄到 `TOC_DROP_SECTION_IDS`
- 效果：`chunk_count` 309 → 339；`2.2 Pin Overview` page 16-19（原 16-16）/ `2.3.1 IO MUX Functions` page 20-22（原 20-20）正确反映续页表 footprint
- 关键内容回收：`I - input. O - output. T - high impedance` / `IE - input enabled` / `WPU - internal weak pull-up` / `Bold marks the pin function...` 全部回到 chunks.jsonl
- Cross_refs `source_chunk_id` 缺失 2 → 0；零 ghost section；零 `Cont'd from previous page` 污染 heading_path
- 新 2 测试：continuation marker 下 chunk 保留 + `List of *` 仍被拒绝

### P58b（commit `bac833b`）— figure cross_refs 用 Docling 原生 caption label 解析

- 新增 `build_figure_page_map(doc)`：walk `doc.texts`，label=`caption` 且前缀锚定 `^Figure <id>` 的 text 收集 `{figure_id: page_no}`
- `extract_cross_refs` 新增 `figure_page_map` kwarg；`converter.py` 调用前构建一次 map
- 效果：cross_refs resolved 43/47 (91%) → 47/47 (100%)
  - Figure 2-2 → p.30；Figure 2-3 → p.30；Figure 7-1 → p.77；Figure 7-2 → p.78
- 新 9 测试：caption 提取 / 非 caption label 排除 / Table 前缀排除 / 重复优先第一 / 缺 prov 容错 / 缺 texts 属性容错 / resolve via map / unresolved 无 map / 无参兼容

### P58c（commit `b519f4d`）— TOC CSV 首行去除 pandas 默认索引

- `export_tables` 检测 `label="document_index"`，`to_csv(..., header=not is_toc)`
- 效果：6 个 TOC CSV 首行从 `['0','1','2','3']` 变为真实 TOC 首条（如 `['Product Overview', ..., '2']` / `['1-1', 'ESP32-S3 Series Comparison', '13']`）；65 个非 TOC 表保持真实列头
- 新 1 测试 + 6 处 FakeDataFrame 签名更新接受 `header` kwarg

## Phase 57 session 摘要（2026-04-18 已完成）

**P57a + P57b 实施完成**（TDD RED→GREEN→重跑 datasheet）：

- `docling_bundle/patterns.py`：新增 `OCR_TABLE_SPLIT_RE` / `clean_ocr_text` / `normalize_heading_text`（shared helpers）
- `converter.py`：`_OCR_TABLE_SPLIT_RE` 改为引用 `patterns.OCR_TABLE_SPLIT_RE`（单一来源）
- `indexing.py`：
  - `build_chunk_record`：`text` / `contextualized_text` 应用 `clean_ocr_text`；`heading_path` 元素应用 `normalize_heading_text`（chunker_headings fallback 路径也兜底）
  - `build_doc_item_lineages`：noise 过滤保持在原始文本上（`"Note:"` 仍被 `NOISY_TOC_HEADINGS` 捕获），过滤通过后 `clean_text = normalize_heading_text(text)` 再入栈
  - `_collect_toc_raw_entries`：TOC 条目同样在过滤通过后做 normalize
- 新增 20 测试：`clean_ocr_text` 7 / `normalize_heading_text` 7 / `build_chunk_record` OCR + normalize 3 / lineage + TOC 3

**datasheet 重跑（77s / CUDA / no-ocr）实测指标**：

| 指标 | P56 baseline | P57 后 |
|---|---|---|
| `chunks.jsonl` 含 "T able" | 18 | **0** |
| `cross_refs.source_chunk_id` 缺失 | 18 (全 table) | 2 (全 section，pre-existing — 续页表 footnote 没进 chunk) |
| `sections.jsonl` 尾冒号 section_id | 1 (`Including:`) | **0** |
| `toc.json` 尾标点 heading | 1 | **0** |
| `chunks.heading_path` / section_id 尾标点 | 1 | **0** |
| 其他 counts (pages / tables / sections / chunks / alerts) | — | 零回归 |
| Integrity (dangling / invalid refs) | 0 | **0** |

**本轮重审但决策不做**（详见 `findings.md §7c`）：

- **P57c（`is_front_matter` flag）**：按 `开发要求.md` 规则 2 / 4 评估，前言 section 不构成"明显异常"；agent 可用 `is_chapter=false AND page_start < first_chapter_page` 现成字段组合出同信号。添加冗余计算字段属过度设计
- **P57d（`table_header_degraded` alert）**：`table_without_caption` alert 已按规则 5 让 agent 回原 PDF；冗余 alert 属重复启发式
- **`## Note:` 从 markdown 删**：常见正文前缀，全局删会误伤合法 Note 段
- **4 条 figure cross_refs resolve**：Docling 无 figure 全局 id（结构性缺口）

## 历史归档（2026-04-12 ~ 2026-04-17）

这段时间做了：

- 工作站架构（WSL + RTX 4060 + shared AI base + docling overlay）+ 镜像统一 + bootstrap 脚本
- 方向收敛：Docling / Marker / MinerU / Unstructured / PyMuPDF4LLM / RAGFlow 调研后，阶段性保留 `docling_bundle` 与 `OpenDataLoader hybrid` 对照
- 2026-04-18 起用户明确只做 docling，OpenDataLoader 路径归档（`opendataloader/README.md` 已标 archived）
- 深度 audit（Phase 37）→ Phase 38-45 核心产物契约（toc / pages.index / sections / tables.index / cross_refs / assets.index / README 可读性）

完整历史在 git log 和 `findings.md` 的 "Current Direction / Baseline / Main Comparison Focus / Diminishing Returns Assessment" 段。
