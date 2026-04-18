# Progress

## 当前状态（2026-04-18）

`docling_bundle` 进入**用户宣告的停止点**（Phase 52 完成）。除非新 PDF 暴露新类问题，不再继续扩展。

- 基线 PDF：`manuals/raw/espressif/esp32s3/esp32-s3_datasheet_en.pdf` (87 页)
- 最新 bundle：`manuals/processed/docling_bundle/esp32-s3-datasheet-en/`
- 测试：153/153 通过
- 最新 commit：`46fe62d feat(docling_bundle): surface uncaptioned tables as alerts`

## 最近 session（2026-04-18）

当天分六轮深度审计 + 修复（Phase 47-52），见 git log 和 `task_plan.md` Phases 段。

**P52（用户明确最后一轮）**：

- 历史 commit 复盘确认 12 轮优化已足够
- 按 `开发要求.md` 更新版（规则 4/5：不过度设计、启发式谨慎、坏结果让 agent 回原 PDF）做最后一轮
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

## 下一步

用户未提出新需求前不再扩展 `docling_bundle`。Backlog 保留在 `task_plan.md`：

- Phase 44：测试安全网（端到端 / CLI / 错误路径 / 链接完整性 regression）
- Phase 46：TRM（1531 页）验证（需用户显式许可）
