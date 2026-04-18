# docling_bundle Architecture

日期：2026-04-18（基线：commit `32eae51`，Phase 38 完成）

## 1. 目标

把一份芯片手册 PDF 转成一个**自包含目录**，让 agent 可以：

1. 在单一入口（`README.md`）立刻知道：页数、表数、告警数、阅读顺序
2. 在固定路径上做程序化访问（manifest / toc / pages index / sections / chunks / tables index）
3. 按页、按章、按表三种维度交叉跳转
4. 对任何怀疑点，能立刻回到原 PDF 的确切页

**不做**的事：全文检索 / RAG / 模型推理 / 语义问答。这些是更上层应用的职责，这个项目只负责把 PDF 压缩成可信、结构化、可导航的证据层。

## 2. 分层

```
PDF (权威真相)
  │
  ▼
Docling pipeline (CUDA, HybridChunker)         ← 代码在 docling_bundle/converter.py
  │
  ▼
canonical document.{json,md,html}              ← 原始解析结果（不二次处理）
  │
  ▼
navigation layer                                ← 代码在 docling_bundle/indexing.py
  - toc.json           (hierarchical headings)
  - sections.jsonl     (chunk-derived sections + heading_level + suspicious)
  - pages.index.jsonl  (page → chunk/table/alert reverse index)
  - chunks.jsonl       (Docling HybridChunker output)
  │
  ▼
evidence layer                                  ← 代码在 docling_bundle/tables.py / images.py
  - tables.index.jsonl + tables/*.csv
  - assets/*.png
  │
  ▼
quality layer                                   ← 代码在 docling_bundle/alerts.py
  - alerts.json        (heuristic warnings with page refs)
  │
  ▼
entry layer                                     ← 代码在 docling_bundle/reading_bundle.py
  - README.md          (human/agent single entry)
  - manifest.json      (machine single entry)
```

## 3. 设计原则

1. **原始 PDF 是最终权威。** 任何结构化产物都只是索引，不是 source of truth。
2. **单入口 + 机器入口双轨。** `README.md` 给 agent/人，`manifest.json` 给程序。没有第二个 "index of indexes"。
3. **不可变 dataclass + 纯函数。** Paths、RuntimeConfig 都是 frozen；indexing / tables / alerts 模块都是无副作用的计算。
4. **heuristic 全部有 alert 兜底。** 任何启发式判断失败都要在 `alerts.json` 里说清楚，不静默降级。
5. **体积不算 KPI，可用性算。** `assets/` 主导 bundle 体积，但手册的框图/时序图是最贵的证据，不做激进剪枝。

## 4. 已落地的产物契约（Phase 38）

### `toc.json`

平铺列表，按页序排列：

```json
{"heading": "2.1 Pin Layout", "level": 2, "page": 15}
```

- `level` 从 heading 文本的数字前缀推断：`1` / `1.2` / `A.1.3` → 1 / 2 / 3
- 无数字前缀 → `level: 1`

**已知问题（Phase 39 将修复）**：把所有 `label=heading` 的元素全部收进来，导致表格 caption / 封面文字 / `Cont'd from previous page` 大量污染 L1。

### `pages.index.jsonl`

```json
{"page": 27, "chunk_ids": ["...:0100", "...:0101"], "table_ids": [], "alert_kinds": ["table_caption_followed_by_image_without_sidecar"]}
```

覆盖所有在任何 chunk / table / alert 中出现过的页。

### `sections.jsonl`

```json
{"section_id": "2.1 Pin Layout", "heading_level": 2, "page_start": 15, "page_end": 16, "chunk_count": 3, "table_ids": [...], "suspicious": false}
```

- `suspicious: true` 当该 section 的跨页 > 总页数 30%（启发式，阈值在 `indexing.flag_suspicious_sections`）
- 该标记表示 heading 很可能被误判（典型例："Note:" 被当顶级章节导致横跨半本文档）

### `tables.index.jsonl`

```json
{"table_id": "...:table:0009", "page_start": 17, "page_end": 17, "csv_path": "tables/table_0009.csv", "label": "document_index", "caption": ""}
```

- `label: "document_index"` 标记目录页表格，agent 可据此过滤掉非工程表格

### `alerts.json`

每条告警有 `kind` / `page` / `caption` / 可选 `detail`。当前 kinds：

- `table_caption_followed_by_image_without_sidecar`：Markdown 里 "Table X-Y" caption 后紧跟图片且无 CSV sidecar → 说明 Docling 把该表识别成图
- 后续 Phase 可能扩展 `register_table_without_bitfield_column` / `crossref_target_unresolved` 等

## 5. 代码模块边界

| 模块 | 行数 | 职责 |
|---|---|---|
| `docling_bundle/converter.py` | 531 | pipeline 编排 + 窗口/缓存 + bundle 写入（**待拆：Phase 43**） |
| `docling_bundle/indexing.py` | 302 | chunk / section / toc / pages_index / 异常检测 |
| `docling_bundle/tables.py` | 217 | 表格导出 / caption 回填 / Markdown sidecar 注入 |
| `docling_bundle/alerts.py` | 108 | Markdown + sidecar 告警启发式 |
| `docling_bundle/cli.py` | 112 | CLI 入口 |
| `docling_bundle/images.py` | 94 | 图片引用过滤、artifact 目录解析 |
| `docling_bundle/reading_bundle.py` | 63 | README 生成 |
| `docling_bundle/config.py` | 42 | Docling pipeline 参数 |
| `docling_bundle/paths.py` | 38 | DocumentPaths dataclass |
| `docling_bundle/models.py` | 24 | RuntimeConfig dataclass |
| `docling_bundle/patterns.py` | 17 | 共享正则常量 |

测试：`tests/` 74 通过。核心模块（indexing / tables / alerts / converter-workflow / bundle）覆盖充分，CLI `main()` 与端到端集成测试缺失（**Phase 44 补强**）。

## 6. 质量维度（AI-consumer 标准）

按"我作为 agent 查手册"的视角，产物应满足：

| 维度 | 当前 | 目标 |
|---|---|---|
| 章节导航 | toc L1 噪声高（真实章节 ~9/111） | toc 章节节点直接可用（Phase 39） |
| 按页反查 | ✅ `pages.index.jsonl` | 保持 |
| 表格 caption 覆盖 | 74%（缺失多为续页表） | ≥ 90%（Phase 40） |
| 表格语义分类 | 无 | `kind: register/pinout/electrical/timing/generic`（Phase 40） |
| 交叉引用索引 | 无（全文 30 条未抽取） | `cross_refs.jsonl`（Phase 41） |
| 图片可追溯 | 哈希文件名 | `p{page:04d}_asset_{seq:03d}.png` + `assets.index.jsonl`（Phase 42） |
| 告警可行动 | 告知问题但不给下一步 | 告警附带 `fallback_image` / 替代路径（Phase 42） |
| 链接完整性 | 无自动校验 | bundle 完整性测试（Phase 44） |

## 7. 路线图

| Phase | 内容 | 状态 |
|---|---|---|
| 38 | TOC / pages.index / heading_level / suspicious | **complete** (commit `32eae51`) |
| 39 | TOC 去噪与章节识别 | in_progress |
| 40 | 续页表 caption 继承 + 表格 kind 分类 | pending |
| 41 | 交叉引用抽取 `cross_refs.jsonl` | pending |
| 42 | 图片语义命名 + `assets.index.jsonl` + 链接完整性 | pending |
| 43 | `converter.py` 拆分 + 代码清理 | pending |
| 44 | 端到端 / CLI / 错误路径测试 | pending |
| 45 | README 丰富化 + TRM 最终验证 | pending |

每个 Phase 的验收标准：
1. 新产物 / schema 有单元测试
2. datasheet 重跑后 `findings.md` 记录实测观察
3. bundle 实际查阅体验（以 AI 使用为标准）明显改善

## 8. 决策历史（精简）

- **不再维护 OpenDataLoader 产线**（2026-04-18）：用户显式裁剪，所有精力投入 docling_bundle
- **不做 RAG / MCP / 全文检索**：这些是消费层，不是基础设施层
- **不追求 bundle 体积最小**：证据完整性优先
- **不为单一缺陷堆启发式**：缺陷先进 `alerts.json`，证据多了再决定是否解决
- **测试数据只用 `esp32-s3_datasheet_en.pdf`（87 页）**：TRM（1531 页）需要显式许可才跑

更详细的决策历史见 `task_plan.md` 的 `Decisions Made` 段与 `Errors Encountered` 段。
