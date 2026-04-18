# Task Plan: docling_bundle 手册转换产线

## Goal

把芯片手册 PDF 转成对 Code Agent（Claude Code / Codex）友好的结构化 bundle，让 agent 能：按章导航、按页回溯、按表筛选、按引用跳转、并且对处理不好的页面知道"回原 PDF"。

评价标准只有一个：**agent 实际查阅 `manuals/processed/docling_bundle/<doc_id>/` 时的使用体验**（见 `开发要求.md`）。

## Current Phase

**Phase 52 complete — 用户宣告停止点（2026-04-18）。**

除非新 PDF 暴露新类问题，不再继续扩展 `docling_bundle`。未落地的 Phase 44（测试安全网）和 Phase 46（TRM 验证）保留为 backlog。

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

**P47–P52 (六轮深度审计)**：

- P47：manifest `chunk_count` / `section_count` 补齐；独立页码行 / `T able` OCR 断词清理；`_clean_markdown_ocr_artifacts` 辅助函数
- P48：`backfill_table_captions_from_markdown` prefix bug（`Table sidecars:` vs `Table sidecar:` 单复数不一致）+ `Revision History` 等短标题 caption fallback
- P49：Docling MultiIndex flatten 产生的 `X.X` 镜像列头收敛
- P50：`## Cont'd from previous page` H2 markdown 清理 + `classify_table_kind` electrical/timing 放宽到 ≥2 of {min, typ, max} word-boundary
- P51：**caption 排序 bug**——`export_tables` 在 backfill 之前误跑 `propagate_continuation_captions` 导致错链；`NOISY_TOC_HEADINGS` 同步到 `build_section_records` 过滤 `Note:` ghost section
- **P52（停止点）**：`detect_missing_caption_alerts` 把 Docling 漏 caption 的非 TOC 表暴露为 `table_without_caption` alert，直接指引 agent 回原 PDF

### Backlog（用户触发再开）

### Phase 44: Test Coverage Enhancement

- [ ] 1-2 页合成 PDF 端到端集成测试（从 PDF 跑到 bundle）
- [ ] `docling_bundle.cli.main()` 覆盖
- [ ] 错误路径（损坏 PDF / 空输入 / 无法写 output）
- [ ] 边界（单页 / 纯图片页 / 无表格文档）
- [ ] Bundle 链接完整性作为独立 regression test
- [ ] 可选：从 unittest 迁移到 pytest + fixtures
- **Status:** pending

### Phase 46: TRM Validation

- [ ] 用户显式许可后用 `esp32-s3_technical_reference_manual_en.pdf` (1531 页) 跑完整转换
- [ ] 核对 toc / kind / cross_refs / assets / alerts 在大文档上的表现
- [ ] 记录超大文档边界情况
- **Status:** pending（需用户许可）

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
| Phase 52 起停止 feature 扩展 | 用户明确"最后一轮"，12 轮迭代后已够 |

## Errors Encountered（代表性）

| Error | 分析 | 解决 |
|---|---|---|
| "currently usable" ≠ "near best practice" | 2026-04-14 后才看具体 bundle 文件，误判多次 | 改为以 concrete outputs 的 agent 使用效果为准 |
| 并行跑 OpenDataLoader datasheet + TRM 共用 5002 端口 | backend chunk 回退、TRM 结果污染 | 改为独占端口顺序跑；该分支后续归档 |
| `caption` 被继承启发式抢先填错 | `propagate_continuation_captions` 在 backfill 之前跑（Phase 48 fix 后才暴露） | P51 移除早期调用，改为 backfill-then-propagate 单路径 |
| `Note:` section 跨 62% 文档 | `build_toc` 过滤 `NOISY_TOC_HEADINGS` 但 `build_section_records` 没同步 | P51 在 section 构建里加同一 filter |
| 2 张表 silent 无 caption | Docling 列头裂变 / OCR 乱码，heuristic 无法救 | P52 暴露为 `table_without_caption` alert，让 agent 回原 PDF |

完整历史见 git log 和 `findings.md`。
