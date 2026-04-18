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

### 完成阶段（历史摘要）

**P1–P7 (环境与架构打底)**：WSL + RTX 4060 Laptop GPU 工作站架构、共享 AI base (`torch + CUDA`)、docling 项目级 overlay、WSL / conda / uv / pip 镜像统一、bootstrap + verify 脚本落地。

**P8–P17 (方向收敛)**：第一性原理下的手册产出结构论证、RAG 边界认知、避免 NIH 反复自检、确认 Docling 是 ingest 层而非 RAG 应用。

**P18–P28 (多工具对比 → 最终收敛)**：对比 Docling / Marker / MinerU / Unstructured / PyMuPDF4LLM / RAGFlow 的能力边界；阶段性保留 `docling_bundle` 与 `OpenDataLoader hybrid` 两条线做对照；最终因资源聚焦裁剪到只做 docling。

**P29–P34 (Bundle 结构整形)**：`manuals/processed/docling_bundle/<doc_id>/` 目录规范落地；单入口 `README.md` + 机器入口 `manifest.json`；窗口缓存挪出 bundle；默认 table sidecar 收敛到单一 CSV；OpenDataLoader 归档。

**P35–P42 (导航层与证据层)**：`toc.json` + `is_chapter` + `suspicious` 传播、`pages.index.jsonl` 反向索引、`sections.jsonl` heading_level、`tables.index.jsonl` + kind 分类 + continuation 链路、`cross_refs.jsonl` 页码 resolve、`assets.index.jsonl` 不改文件名方案。

**P45 (README 可读性)**：章节大纲 + 表格分布 + cross-ref 摘要 + alert fallback image 都直接进 `README.md`，agent 无需先 `jq`。

**P47–P54 (八轮深度审计)**：

- P47：manifest `chunk_count` / `section_count` 补齐；独立页码行 / `T able` OCR 断词清理；`_clean_markdown_ocr_artifacts` 辅助函数
- P48：`backfill_table_captions_from_markdown` prefix bug（`Table sidecars:` vs `Table sidecar:` 单复数不一致）+ `Revision History` 等短标题 caption fallback
- P49：Docling MultiIndex flatten 产生的 `X.X` 镜像列头收敛
- P50：`## Cont'd from previous page` H2 markdown 清理 + `classify_table_kind` electrical/timing 放宽到 ≥2 of {min, typ, max} word-boundary
- P51：**caption 排序 bug**——`export_tables` 在 backfill 之前误跑 `propagate_continuation_captions` 导致错链；`NOISY_TOC_HEADINGS` 同步到 `build_section_records` 过滤 `Note:` ghost section
- P52：2 张非 TOC 表 caption 缺失（p.22 / p.79），新增 `detect_missing_caption_alerts` 结构性检查把它们暴露成 `alerts.json` 的 `table_without_caption` 条目
- P53：**ghost section 第二轮**——`Feature List`（30 chunks，p.36-59）/`Pin Assignment`（15 chunks，p.51-60）span 刚好低于 30% suspicious 阈值；根因是 `build_toc` 有 `TOC_REPEAT_DROP_THRESHOLD` 但 `build_section_records` 没同步 → 提取共享 helper `collect_heading_occurrences` / `compute_dropped_repeat_labels`，converter 算一次传给两层
- P54：**孤立 chunk 重新归属 + table-caption leak 修复**——P53 之后 53 条 chunk（Feature List / Pin Assignment / Note: heading_path）在 sections.jsonl 完全丢失，agent 按 section tree 找不到 UART 的 feature bullets；`Table 2-9. Peripheral Pin Assignment` 作为 table caption 被 Docling 升格成 heading 漏进 sections.jsonl。修复：`build_section_records` 改成用 `_is_noisy_toc_heading`（和 TOC 同一过滤规则）判定 orphan；orphan chunk 按 doc 顺序重新 parent 到最近的真实 section，但**不扩张 parent 的 page range**（防止 ghost-span 从侧门回来）。结果：section_count 138→137；chunk coverage 256/309 → 309/309；TOC 零 ghost 条目；零 page span 暴涨
- P55：**Unicode bullet-prefix heading filter**——datasheet 全量重审发现 `· IO MUX:` 作为 level-1 TOC 锚点 + 独立 section；Docling 的 layout analyzer 把以 Unicode 项目符号开头的行当成 heading。新增 `_BULLET_HEADING_PREFIX_RE = re.compile(r"^[·•◦▪▫►◆∙⬧]")`，在 `_is_noisy_toc_heading` 加一条分支过滤这类 heading；ASCII `-`/`*`/`+` 不碰以免误伤 `Wi-Fi` / `2.4 GHz` / `Low-Power Modes`。orphan chunk 靠 P54 的 re-parenting 路径自动接到 `4.1.3.1 IO MUX and GPIO Matrix`，page range 不扩张。结果：section_count 137→136；其他 count 零回归；167/167 通过。
- P56a：**heading breadcrumbs**——chunks.jsonl 每条 chunk 的 `heading_path` 原本深度恒 1，agent 看不到 UART chunk 属于哪个章。新增 `build_doc_item_lineages` 按 doc 顺序构建 heading 祖先栈，`self_ref` 作为稳定查找 key（HybridChunker 会重包裹 DocItem，`id()` miss）；编号 heading 权威决定 level，非编号 heading 要么用 Docling 自己的 `heading_level`、要么挂在最深编号祖先下（不 pop 编号骨架）；`dropped_repeat_labels` 也从栈排除；`section_id` 仍取 `heading_path[-1]`，sections.jsonl 分组不变；`build_chunk_records` 用 chunker 原始 leaf 判定 NOISY_SECTION_IDS 防止 lineage 提升复活 TOC 内容。9 新测试。结果：depth 分布 19/86/92/100/12（d1/d2/d3/d4/d5）；UART chunks 带完整 4 级链；counts 零回归。
- P56b：**polish batch (Cont'd paragraphs / TOC columns / rows count)**——document.md 里 14 条独立 `Cont'd on next page` / `Table X-Y - cont'd from previous page` 段落清掉（行锚定，inline 散文保留）；TOC 表的 `columns` 统一设 `[]`（Docling 识别成行数据的假表头不再暴露）；所有表的 `rows` 从 `TableItem.data.num_rows` 填入（原恒 null）。10 新测试。188/188 通过。

**P56 前的评估（2026-04-18 第二轮审计）**：同时记录 5 条发现但**不修**（`findings.md` §7b）——非数字型子标题 level=1 偏高、Glossary 术语散出独立 heading、TOC 表列头垃圾（D 部分修复）、Uncaptioned 表 MultiIndex 列头混乱（`alerts.json` 已暴露）、4 条 figure cross_refs unresolved（Docling 不给 figure 全局 id）。以上都符合"过拟合风险 vs 收益"不平衡或已通过 alerts 暴露给 agent 回原 PDF 的契约。设计 spec: `docs/superpowers/specs/2026-04-18-docling-bundle-phase56-design.md`。

### 计划中（Phase 57 — 2026-04-18 产物重审）

重审证据：`findings.md §7c`。按 "影响 × 安全" 排序，每个子阶段 **RED→GREEN→重跑 datasheet** 独立闭环、不混批。

**P57a [HIGH] — chunk OCR 断词清理 + cross_ref source 回连（耦合双修）**

- 根因：`_clean_markdown_ocr_artifacts` 只跑在 markdown 字符串，chunk 由 DocItem 原值构建，18 条 chunk 的 `text` / `contextualized_text` 里 `T able` 未被替换；cross_refs 抽自 markdown（已清洗成 `Table`），`_find_source_chunk` 子串匹配失败 → 18/47 cross_refs 缺 `source_chunk_id`
- 实现：把 `_OCR_TABLE_SPLIT_RE` 移到 `docling_bundle/patterns.py`（已有文件），在 `build_chunk_record` 构建 text/contextualized_text 时应用；word-boundary `\bT (ables?)\b` 保证不误伤 `T ype` / `T otal`
- 验收：`chunks.jsonl` 零 `T able`；`cross_refs` 缺 `source_chunk_id` 的只剩 4 条 figure（unresolved）；其他 count 零回归

**P57b [LOW] — section_id 尾标点清理**

- 仅 `Including:` → `Including` 一条命中；其他 135 条 section_id 均无尾标点
- 实现：`build_section_records` 在入库前对 section_id 做 `rstrip(":,;")`（`.` 不清，避免破坏编号 `4.1.1`）；`heading_path` 同步清理
- 验收：`section_count` 不变；受影响 chunk 的 `section_id` / `heading_path[0]` 同步更新

**P57c — `is_front_matter` 字段**（**决策：不做**）

- 评估：13 条前言 section 不构成"明显异常"（它们是封面 Features 下的合法 feature bullets，内容可读），只是在 `sections.jsonl` 按顺序列举时排在前面
- agent 可用现有字段组合 `is_chapter=false AND page_start < min(page for is_chapter=true)` 复现同样信号，不需新字段
- 按 `开发要求.md` 规则 2（避免过度设计）与规则 4（谨慎启发式），**拒绝**添加冗余计算 flag

**P57d — `table_header_degraded` alert**（**决策：不做**）

- `table_without_caption` alert 已按规则 5 让 agent 回原 PDF；再加冗余 alert 是重复启发式
- 按 `开发要求.md` 规则 2 / 4，**拒绝**添加冗余 alert 分类

**不做（findings.md §7c 详述）**

| 项 | 理由 |
|---|---|
| `## Note:` heading 从 markdown 里删 | 常见正文前缀，全局删会误伤合法 Note 段 |
| Table_0066 / Table_0015 列头重建 | 已由 `table_without_caption` alert 路径回原 PDF |
| 无编号子标题降级到 level=2 | "最近编号父级 +1" 启发式会误伤前言区合法 level-1 |
| Glossary 术语 heading 合并 | "同页多条无编号 heading" 判据强过拟合 |
| Figure cross_refs resolve | Docling 无 figure 全局 id，结构性缺口 |

**推进顺序**：P57a（必做）→ P57b（随 a 或独立）→ P57c（待用户认可）→ 重跑重审 → P57d（若仍有必要）。每步单独 commit。

## Decisions Made（精选）

| Decision | Rationale |
|---|---|
| 只维护 `docling_bundle` 一条产线 | 用户 2026-04-18 裁剪，资源聚焦 |
| 评价标准=agent 实际查阅体验，不是架构纯度 | 用户明确（开发要求.md） |
| 启发式失败必须进 `alerts.json`，不静默降级 | Robustness Principle + 开发要求.md 规则 5 |
| 处理不好的表 / 图 / 页让 agent 回原 PDF | 开发要求.md 规则 5；原 PDF 是权威 source of truth |
| 不追 bundle 体积最小，证据完整优先 | 框图 / 时序图 / 表证据对嵌入式开发价值最高 |
| 不做 RAG / 全文检索 / MCP | 基础设施层，不侵入消费层 |
| 测试数据只用 `esp32-s3_datasheet_en.pdf` (87 页) | 迭代速度；TRM 耗时大需显式许可 |
| 不改 assets 文件名 | 避免断 `document.json` / `document.html` 内部引用 |
| `kind=generic` 是合法分类 | 规则 4：不为填满 kind 分类率而降精度 |
| 窗口缓存默认关，只做显式容错 | 普通单次转换不承担额外复杂度 |

## Errors Encountered（代表性）

| Error | 分析 | 解决 |
|---|---|---|
| "currently usable" ≠ "near best practice" | 2026-04-14 后才看具体 bundle 文件，误判多次 | 改为以 concrete outputs 的 agent 使用效果为准 |
| 并行跑 OpenDataLoader datasheet + TRM 共用 5002 端口 | backend chunk 回退、TRM 结果污染 | 改为独占端口顺序跑；该分支后续归档 |
| `caption` 被继承启发式抢先填错 | `propagate_continuation_captions` 在 backfill 之前跑（Phase 48 fix 后才暴露） | P51 移除早期调用，改为 backfill-then-propagate 单路径 |
| `Note:` section 跨 62% 文档 | `build_toc` 过滤 `NOISY_TOC_HEADINGS` 但 `build_section_records` 没同步 | P51 在 section 构建里加同一 filter |
| 2 张表 silent 无 caption | Docling 列头裂变 / OCR 乱码，heuristic 无法救 | P52 暴露为 `table_without_caption` alert，让 agent 回原 PDF |

完整历史见 git log 和 `findings.md`。
