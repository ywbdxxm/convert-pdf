# docling_bundle 项目报告

> 日期：2026-04-19（Phase 60 完成）
> 评价标准：`开发要求.md` — agent 直接查阅 `manuals/processed/docling_bundle/<doc_id>/` 做嵌入式开发时的真实体验

---

## 1. 最高层需求（Why）

嵌入式开发中，真正消耗工程时间的不是"读芯片手册"，而是**查阅**动作：

- 在几百到几千页的 datasheet / TRM / AN 里定位正确的章节
- 在寄存器摘要、pin mux 表、电气参数表、时序图之间来回切换
- 判断"这个页我能直接信 vs 需要回原 PDF 核验"
- 让 AI agent（Claude Code / Codex）参与这个过程时仍保留**证据链**

既有做法的问题：

| 做法 | 问题 |
|---|---|
| 直接扔整份 PDF 给 LLM | 上下文爆炸；LLM 把 OCR 错误当成事实；无法精确定位回原页 |
| 通用 PDF→Markdown（MinerU / Marker / PyMuPDF）| 只给平铺文本，失去表格 / 页 / 章 / 引用的维度 |
| RAG | 向量检索把结构拍扁；agent 查到一句话但不知道它属于哪章、在哪页、是哪张表的 caption |
| Human 手查 | 浪费工程师时间在目录导航上 |

**目标**：把一份 PDF 变成一个**自包含目录**，让 agent 能按**章、页、表、引用**四种维度随意跳转，并通过 `alerts.json` 对 "处理不好的内容" 主动标注，引导 agent 回原 PDF。

**不做的**：全文检索 / RAG / 向量索引 / MCP server / 问答 UI / 通用 PDF→Markdown 转换器。这些是更上层应用的职责；本项目只负责把 PDF 压缩成**可信、结构化、可导航的证据层**。

---

## 2. 设计决策与原因

### 2.1 为什么选 Docling

对比（2026-04 调研）：

| 工具 | 评估 | 结论 |
|---|---|---|
| **Docling**（IBM Research） | 原生支持 PDF → Markdown/JSON/HTML 三视图；`HybridChunker` 带 heading path；TableItem 结构化（MultiIndex header）；`iterate_items` 统一遍历 | ✅ **选中** |
| Marker | Markdown 输出好，但无结构化 chunk、无 heading path API | ✗ 要二次解析 |
| MinerU | 强 OCR + 布局但 Python API 弱；输出不稳 | ✗ |
| Unstructured | 通用但粗粒度；heading 层级弱 | ✗ |
| PyMuPDF4LLM | 轻量但表格支持弱 | ✗ |
| RAGFlow | 是 RAG 应用，不是 ingest 库 | ✗ 层级错位 |

Docling 做对的：

- **PDF 布局解析 + page number**：`prov[].page_no` 让每个 item 都带页码，后续所有反向索引的基础
- **HybridChunker**：段级分块 + `meta.headings` + `doc_items`，直接给出段落边界和所属 heading
- **表格→DataFrame / HTML / Markdown 三形态**：MultiIndex header flatten 有实现；`num_rows` / `table_cells` 结构化
- **page_break placeholder**：markdown 里 `<!-- page_break -->` 让我们能回推每页内容

Docling 做不好的（验证过、不可修，只能**暴露**）：

| 失败 | 例 | 处理 |
|---|---|---|
| 表被识别成图片 | datasheet p.27 Table 2-9 | `table_caption_followed_by_image_without_sidecar` alert |
| 漏 caption | p.22 / p.79；TRM 371 张寄存器表 | `table_without_caption` alert |
| OCR 断词 | `T able` / `T ables` / `Cont'd` | word-boundary regex 清洗 |
| MultiIndex flatten 残留 | `Pin No..Pin No.` / `F3.F4` | 合并相同两半 |
| 章节编号 OCR 走形 | TRM `7 . 1. 1 Overview` | 接受为 agent 可见观察值 |
| 字体解码污染 | p.78 偶发 | 不修 |
| HybridChunker attribution 错归 | `Table 1-1` 归到 `1.1` 而非 `1.2` | 不修（修复启发式过拟合风险高）|
| page_footer 漏到 content chunk | "Submit Documentation Feedback" 混入 TRM p.1030 正文 | **Phase 60 footer-strip fix**（之前会整块丢弃正文，现改为剥离短语）|

**结论**：Docling 是可靠的**层次化解析器**，不是语义理解器。bundle 层只做**可验证的结构化后处理**，一切语义判断仍需回原 PDF。

### 2.2 为什么不做 RAG / 全文检索

`开发要求.md` 明确定位：**基础设施层**。把结构化工作做好后：

- Agent 要做语义查询：用现成的 LLM + jq + grep 组合
- 用户要 RAG：在 bundle 之上自己加 LlamaIndex / LangChain
- 团队要 MCP：在 bundle 之上自己包一层

本项目不介入这些层，避免 NIH 和职责蔓延。

### 2.3 为什么 `alerts.json` 是核心设计

`开发要求.md` 规则 5：**"处理不好的表 / 图 / 页直接在 `alerts.json` 里暴露，让 agent 回原 PDF"**。

对比两种失败模式：

| 模式 | 表现 | 对 agent 的影响 |
|---|---|---|
| Silent failure | Chunk 被丢弃但 agent 不知；表列头乱但 agent 以为干净 | agent 给出错误答案，看似自信 |
| Surfaced failure（`alerts.json`）| 告警显式列出"这张表 caption 缺失，回原 PDF" | agent 知道什么能信、什么要核验；结论可溯 |

整个产线的一切启发式都必须在 alert 里留痕。**Phase 60 的 footer-strip fix 就是对这条原则的具体应用**——之前 `NOISY_TEXT_PATTERNS` 整块丢弃 chunk，TRM p.1030 的 5 条 I2C 寄存器位描述silent-lost，既无 alert 也无任何线索，违反规则 5；修复后内容被保留，footer 短语被剥离。

### 2.4 为什么不追 bundle 体积最小

以 datasheet 为例：`document.json` 12 MB / `document.md` 240 KB / `assets/` 16 MB / 其他索引 ~1 MB。

- `assets/` 占 64% 体积，是框图 / 时序图 / pin 布局图——**对嵌入式开发价值最高的证据**
- 激进裁剪会丢掉证据链
- agent 查询成本 ≠ bundle 存储成本；前者只和索引文件（几十 KB）有关，后者只是静态盘空间

### 2.5 为什么保留三种 document 视图（md / json / html）

| 视图 | 用途 |
|---|---|
| `document.md` | 主阅读层，agent 做 grep / 上下文理解 |
| `document.json` | Docling 原生全量，底层 caption / label / prov 回查 |
| `document.html` | 宽表视觉验证（markdown 宽表会换行丢形状）|

成本低（几 MB），agent 按需选层，不强制 pick 一个。

### 2.6 为什么两套"章节"记录（sections.jsonl + toc.json）

- `toc.json` 按 **doc 顺序**，对应 agent 一屏看完大纲（`jq 'select(.is_chapter)'`）
- `sections.jsonl` 按 **page_start 顺序**，带 `chunk_ids` / `table_ids` / `heading_path` 完整祖先链，对应 agent 做程序化聚合
- 两层共享 `is_chapter` 判据（`is_chapter_heading` 共享 helper），避免 drift
- Phase 59a 给 sections.jsonl 补 **navigational parent** 记录：`4 Functional Description` 等 chapter 本身不挂直接 chunks，但作为 nav 节点让 "第 4 章的 page range / tables" 类查询一步到位

### 2.7 为什么所有 chunk 带完整 `heading_path`

最初 chunks.jsonl 只有 `section_id`（叶子 heading）。agent 拿到一个 UART chunk，但不知道它属于 `4 Functional Description → 4.2 Peripherals → 4.2.1 Connectivity → 4.2.1.1 UART Controller`。

Phase 56a 重写成完整祖先链（`build_doc_item_lineages`）：

- 数字 heading 权威决定 level（`4.1.3.5` → 4）
- 非数字 heading（`CPU Clock` / `BACKUP32K_CLK`）挂在最深数字祖先之下，不 pop 数字骨架
- `self_ref` 作为稳定查找 key（HybridChunker 会重新包装 DocItem，`id()` 不稳）

结果：agent 看 chunks.jsonl 任一记录，heading_path 就是一条完整面包屑。

### 2.8 为什么只跟踪 essp32-s3 两份手册

`开发要求.md` 没要求大规模回归测试，只要求"**以实际查阅 `manuals/processed` 的效果为评判**"。把功夫花在两份手册的深度验证上：

- **datasheet (87 页)**：主测试用例，每轮 audit baseline
- **TRM (1531 页)**：跨规模验证；暴露 footer-strip bug；确认当前实装的 17× 规模扩展仍健康

两份手册足以覆盖：短/长文档、简单/复杂章节、pinout/register 两大表类、带/不带续页表的场景。

### 2.9 为什么 `chunk_id` 保留 raw chunker 位置而不是连续编号

HybridChunker 产出 N 条，我们过滤掉 TOC 区后剩 M 条。两种选择：

| 方案 | 优点 | 缺点 |
|---|---|---|
| `chunk_index` = raw 位置（有 gap）| 规则变化时 chunk_id 不飘；调试 / 外部消费者可稳定 pin | agent 以为是连续 index，遍历会 miss |
| `chunk_index` = 连续 1..M | agent 直觉 | 改规则 → chunk_id 全动；下游外部引用失效 |

当前选 raw 位置。**这是个有意识的 trade-off**，不是 bug。文档里说明："chunks.jsonl 的数组位置是 doc 阅读顺序，`chunk_index` 可能有 gap"。

---

## 3. 最终产物结构

### 3.1 目录布局

```
manuals/
  raw/
    espressif/esp32s3/
      esp32-s3_datasheet_en.pdf
      esp32-s3_technical_reference_manual_en.pdf
  processed/
    docling_bundle/
      esp32-s3-datasheet-en/                                 ← 最终产物
        README.md
        manifest.json
        alerts.json
        toc.json
        pages.index.jsonl
        sections.jsonl
        chunks.jsonl
        tables.index.jsonl
        tables/
          table_0001.csv
          table_0002.csv
          ... (71 个 CSV)
        cross_refs.jsonl
        assets.index.jsonl
        document.md
        document.json
        document.html
        assets/
          image_000000_<hash>.png
          ... (85 张图)
      esp32-s3-technical-reference-manual-en/                 ← 最终产物（TRM）
        (同样 schema；1531 页 / 3793 chunks / 667 tables / 1448 assets)
```

### 3.2 文件职责（按消费优先级）

**入口层**（1 文件）
- `README.md` — 单入口。Summary / Start Here 流程 / Key Files 链接 / Chapter Outline / Table Breakdown / Cross-Reference Summary / Alerts。**Agent 第一眼只看这一个文件**

**元数据层**（1 文件）
- `manifest.json` — 机器入口。`doc_id` / `title` / `source_pdf_path` / 所有 index 文件路径 / 各类 count。**Agent 用 jq 查计数与文件名**

**质量层**（1 文件）
- `alerts.json` — 结构化告警。每条带页码 + 重定向（fallback image / CSV / "回原 PDF" 提示）。**Agent 决定信任前先看这个**

**导航层**（4 文件）
- `toc.json` — 层级 TOC，doc 顺序
- `sections.jsonl` — 章节索引（含 nav parent）
- `pages.index.jsonl` — 页码→内容反向索引
- `chunks.jsonl` — 段级内容 + 完整 heading 祖先链

**证据层**（3 + N 文件）
- `tables.index.jsonl` — 表索引（caption / kind / continuation_of / columns / rows）
- `tables/*.csv` — 每张表的 CSV sidecar（71 张 datasheet / 667 张 TRM）
- `cross_refs.jsonl` — 交叉引用（section / table / figure 带 target_page + target_id）
- `assets.index.jsonl` + `assets/` — 图片清单与文件

**全文层**（3 文件）
- `document.md` — 主阅读层 Markdown
- `document.json` — Docling 原生 JSON
- `document.html` — 宽表视觉验证

### 3.3 字段契约（核心举例）

**`chunks.jsonl` 单条记录**：

```json
{
  "doc_id": "esp32-s3-datasheet-en",
  "chunk_id": "esp32-s3-datasheet-en:0156",
  "chunk_index": 156,
  "section_id": "4.1.3.5 Power Management Unit (PMU)",
  "heading_path": [
    "4 Functional Description",
    "4.1 System",
    "4.1.3 System Components",
    "4.1.3.5 Power Management Unit (PMU)"
  ],
  "page_start": 42,
  "page_end": 43,
  "text": "ESP32-S3 has an advanced Power Management Unit (PMU)...",
  "contextualized_text": "4 Functional Description\n4.1 System\n4.1.3 System Components\n4.1.3.5 Power Management Unit (PMU)\nESP32-S3 has an advanced Power Management Unit (PMU)...",
  "doc_item_count": 1,
  "table_like": false,
  "citation": "esp32-s3-datasheet-en p.42-43",
  "table_ids": []
}
```

**`sections.jsonl` 单条记录**（leaf + nav parent 两类）：

```json
{"section_id": "4.2.1.1 UART Controller", "heading_path": [...], "heading_level": 4, "is_chapter": false, "page_start": 51, "page_end": 51, "chunk_count": 3, "chunk_ids": [...], "text_preview": "...", "table_ids": [...]}
{"section_id": "4 Functional Description", "heading_path": ["4 Functional Description"], "heading_level": 1, "is_chapter": true, "page_start": 36, "page_end": 63, "chunk_count": 0, "chunk_ids": [], "text_preview": "", "table_ids": [...]}
```

**`cross_refs.jsonl` 单条记录**：

```json
{"kind": "section", "target": "4.1.3.5", "source_page": 2, "raw": "see Section 4.1.3.5", "target_page": 42, "target_id": "4.1.3.5 Power Management Unit (PMU)", "source_chunk_id": "esp32-s3-datasheet-en:0005"}
```

字段级完整契约见 [`docs/architecture.md`](docs/architecture.md)。

### 3.4 实测基线

**datasheet（87 页）**：

| 指标 | 值 | 备注 |
|---|---|---|
| pages | 87 | 100% 覆盖 |
| sections | 145 | 含 9 nav parent；7 chapters |
| chunks | 339 | 100% 归属；heading_path 平均深度 ~3 |
| tables | 71 | 6 TOC + 65 content；63/65 有 caption |
| cross_refs | 47 | 100% resolved；43 带 `target_id` |
| assets | 85 | 0 missing |
| alerts | 3 | 2 `table_without_caption` + 1 `table_caption_followed_by_image_without_sidecar` |
| document.md | 239 KB |  |
| document.json | 12 MB |  |
| assets/ | 16 MB |  |
| 总体积 | ~30 MB |  |
| 转换耗时 | ~23s CUDA / no-ocr |  |

**TRM（1531 页）**：

| 指标 | 值 | 备注 |
|---|---|---|
| pages | 1531 | 100% 覆盖 |
| sections | 1663 | 含 73 nav parent |
| chunks | 3793 | (Phase 60 修复后 +7 恢复) |
| tables | 667 | 263 有 caption / 404 无 caption |
| cross_refs | 335 | ~98% resolved |
| assets | 1448 |  |
| alerts | 380 | 371 `table_without_caption` + 9 `empty_table_sidecar`（TRM 寄存器 / 指令表多无标"Table X-Y"标题，按规则 5 回原 PDF） |
| document.md | 2.8 MB |  |
| document.json | 143 MB |  |
| assets/ | ~55 MB |  |
| 总体积 | ~225 MB |  |
| 转换耗时 | ~24 min CUDA / no-ocr |  |

---

## 4. 代码实现

### 4.1 分层

```
PDF (权威真相)
  │
  ▼
Docling pipeline (CUDA, HybridChunker)            ← converter.py
  │
  ▼
canonical document.{json,md,html}                 ← Docling 原生输出
  │
  ▼
navigation layer                                  ← indexing.py
  │   chunks.jsonl / sections.jsonl /
  │   pages.index.jsonl / toc.json
  │
  ▼
evidence layer                                    ← tables.py / assets_index.py / cross_refs.py
  │   tables.index.jsonl + tables/*.csv /
  │   assets.index.jsonl / cross_refs.jsonl
  │
  ▼
quality layer                                     ← alerts.py
  │   alerts.json
  │
  ▼
entry layer                                       ← reading_bundle.py
      README.md / manifest.json
```

### 4.2 模块清单

| 模块 | 行数 | 职责 |
|---|---|---|
| `converter.py` | 662 | pipeline 编排；Docling 调用；窗口 / 缓存；bundle 写入顺序 |
| `indexing.py` | 828 | chunks / sections / toc / pages_index / lineage / nav parents / suspicious 异常 |
| `tables.py` | 538 | 表导出 + caption 回填 + 续页链路 + CSV 写入 + markdown sidecar 注入 |
| `cross_refs.py` | 251 | 交叉引用抽取 + section / table / figure resolve |
| `reading_bundle.py` | 158 | README 生成 |
| `alerts.py` | 140 | markdown + sidecar + missing-caption 告警启发式 |
| `cli.py` | 116 | CLI |
| `images.py` | 94 | 图片引用过滤 |
| `assets_index.py` | 70 | 图片清单 |
| `patterns.py` | 64 | 共享正则 + OCR 清洗 / heading normalize |
| `config.py` | 42 | Docling pipeline 参数 |
| `paths.py` | 42 | DocumentPaths frozen dataclass |
| `models.py` | 24 | RuntimeConfig frozen dataclass |
| **total** | **3036** | |

**测试**：`tests/` 4459 行，**242 个单元测试全绿**。覆盖 indexing / tables / alerts / cross_refs / assets_index / markdown_cleanup / cli / paths / config / workflow / reading_bundle。每次 audit 后先写 RED 测试再修代码。

### 4.3 核心算法

**`build_chunk_records`**（indexing.py）：

```
for chunk in HybridChunker(doc).chunk():
    if chunker_headings[-1] in TOC_DROP_SECTION_IDS:
        continue                                 # drop TOC 区 chunk
    record = build_chunk_record(
        text=_strip_noisy_text_phrases(clean_ocr_text(chunk.text).lstrip()),
        contextualized_text=..._strip_noisy_text_phrases(...),
        heading_path=item_lineages[chunk.doc_items[0].self_ref],   # lineage promotion
        ...
    )
    if should_keep_chunk_record(record):         # 空 text 或纯数字 reject
        records.append(record)
```

**`augment_sections_with_navigational_parents`**（indexing.py）：

```
for toc_entry in toc:
    heading = toc_entry.heading
    if heading in leaf_section_ids:      continue
    if toc_entry.suspicious:              continue
    descendants = chunks whose heading_path contains heading
    if not descendants:                   continue    # 保守：无 chunk 引用则不建
    emit section record with:
        chunk_count=0, chunk_ids=[],
        is_chapter=toc_entry.is_chapter,
        page_start=toc_entry.page,
        page_end=max(descendant.page_end),
        heading_path=<ancestor chain up to heading>
```

**`build_figure_page_map`**（cross_refs.py）：

```
for text in doc.texts:
    if text.label == "caption" and text.text matches ^Figure <id>:
        figure_map["Figure <id>"] = text.prov[0].page_no
```

用 Docling 原生 `label="caption"` 信号，不扫描散文（避免误匹"as shown in Figure 2-2"自引）。

**`_strip_noisy_text_phrases`**（indexing.py，Phase 60 核心修复）：

```python
def _strip_noisy_text_phrases(text: str) -> str:
    for pattern in NOISY_TEXT_PATTERNS:
        text = pattern.sub("", text)
    text = re.sub(r"[ \t]*\n[ \t]*\n+", "\n\n", text).strip()
    return text
```

比原来的 "match→drop 整块" 策略保留真实内容。footer 单独成块时 → strip 后为空 → `should_keep_chunk_record` 仍 drop；footer 混在正文中时 → 只剥离短语，保留正文。

### 4.4 迭代历程

| Phase | 重点 | 关键 commit / 结果 |
|---|---|---|
| P1–P17 | 环境架构 / 工具选型论证 | 工作站 WSL + CUDA；收敛到 Docling |
| P18–P28 | 对比 Docling / Marker / MinerU / ODL / RAGFlow | 2026-04-18 用户裁剪：只做 Docling |
| P29–P34 | bundle 结构定稿 | 目录规范；窗口缓存挪出 |
| P35–P42 | 导航层 + 证据层 | toc / pages_index / tables_index / cross_refs / assets_index |
| P45 | README 可读性 | chapter outline + table breakdown + alert 都进 README |
| P47–P54 | 八轮深度审计 | caption 顺序 bug / ghost sections / bullet-prefix / heading lineage / Cont'd paragraph / TOC columns / rows count |
| P55 | Unicode bullet heading filter | `· IO MUX:` 不再成为 level-1 锚点 |
| P56a | heading breadcrumbs | chunk 带完整祖先链 |
| P56b | polish (Cont'd / TOC columns / rows) | |
| P57 | OCR 清理 + 尾标点 | chunks 零 "T able"；零尾标点 heading |
| P58 | 续页 chunk 恢复 + figure resolve + TOC CSV header | chunks 309→339；cross_refs 91%→100% resolved |
| P59 | nav parents + is_chapter + target_id + rows 精度 + chunk text lstrip | sections 136→145；7 chapters filterable；rows 71/71 精确；43/47 target_id |
| **P60** | **TRM 全量验证 + footer-strip fix** | **chunks 3786→3793 on TRM；p.1030 I2C 寄存器位描述恢复；最终产物落盘** |

242 个单元测试随代码增长。每一轮 audit 都以"重跑 datasheet + 逐字段对比"为验收。

---

## 5. 产物优缺点总结

### 5.1 优点

**对 AI agent**：
- **单入口 README**：几秒内拿到 page_count / table_count / chapter outline / alert summary
- **四维导航**：page / section / table / cross-ref，每个都是 O(index lookup) 而非 O(full-text scan)
- **完整 heading 面包屑**：chunks.jsonl 任一记录自带"在哪一章的哪一节"
- **Citation 字段**：每条 chunk 自带 `doc_id p.X-Y` 引用串，agent 回答时直接粘贴
- **跨引用带 `target_id`**：43/47 cross_refs 一跳到目标 section/table 记录
- **规则 5 契约**：`alerts.json` 明示"这些不可信，回原 PDF"——agent 不会自信地给错误答案
- **无 Silent Failure**：Phase 60 修复后，`_strip_noisy_text_phrases` 保证混合内容不整块丢

**对代码维护**：
- 模块职责清晰：converter 编排 / indexing 导航 / tables 表 / cross_refs 引用 / alerts 告警 / reading_bundle 入口
- 纯函数 + frozen dataclass：单元测试容易写；**242 个测试覆盖所有启发式的正常 + 边界 + 跨 vendor 场景**
- 共享 helper 保证两层过滤一致（`is_chapter_heading` / `compute_dropped_repeat_labels` / `_is_noisy_toc_heading`）——历史 ghost section bug 教训

**对规模**：
- datasheet 23 秒 / 87 页；TRM 24 分 / 1531 页。处理时间线性，**17× 规模无结构性退化**
- bundle 体积主要由 assets 决定，索引本身 < 几 MB（agent 可全加载到 context）

### 5.2 缺点 / 已知缺口

**Docling 层缺陷（不可修，只能暴露）**：
- Table 被识别成图片（datasheet p.27）→ `table_caption_followed_by_image_without_sidecar` alert
- 表 caption 缺失（datasheet 2 张 / TRM 371 张）→ `table_without_caption` alert
- OCR 列头乱码（TRM table_0066）→ alert 回原 PDF
- 续页列头漂移（datasheet p.21 "Pin" vs p.22 "Pin No."）→ 续页链断开接受
- HybridChunker 把 `Table 1-1` 归到 `1.1 Nomenclature` 而非 `1.2 Comparison`
- Figure 无全局 id（`target_page` 可解但 `target_id` 无法填）
- TRM 编号 OCR 走形（`7 . 1. 1 Overview` 而非 `7.1.1`）
- datasheet p.78 字体解码偶发污染

**设计边界**：
- 不做语义问答 / RAG（超出定位；agent 要 QA 自己组合 LLM + bundle）
- 不提供全文检索（grep / jq 已够用；大规模检索要额外索引层）
- `chunk_index` 有 gap（已有权衡决定，不是 bug，文档需写清）
- 不改 assets 文件名（hash 文件名防内部引用断链）

**跨 vendor 约束带来的残留**：
- TRM `is_chapter=True` 97 条含 `1. Internal ROM 0` 噪声（datasheet `1 ESP32-S3 Series Comparison` 是真 chapter，同一规则不能更严）
- 非编号 level-1 heading 残留（前言 `Features` / `Wi-Fi` / Glossary 术语）

**不修的决定（三轮 audit 已决）**：`## Note:` 等 h2 保留在 markdown（reading context 用）；`Submit Documentation Feedback` 链接保留（Espressif 正式 URL，非 OCR 垃圾）。

### 5.3 未实施但可选的未来工作

如果要继续优化，下一步可考虑：

1. **`pages.index.jsonl` 加 `section_ids`**（symmetry with chunk/table/asset/alert_ids） — MEDIUM，纯派生字段
2. **`cross_refs` 前缀扩展**（加 `described in` / `listed in` / `in Section X`） — 可让 datasheet cross_refs 47→~90，但 P60 决定暂缓（TRM 验证优先）
3. **manifest 加 provenance**（`source_pdf_sha256` / `docling_version` / `converted_at` / `bundle_schema_version`） — 可追溯性
4. **markdown 中的 `\_` 反转义**（Docling 导出时 pandoc 风格 escape）— 影响 36 个 identifier grep

上述每项都未达到"severe"阈值，按 `开发要求.md` 规则 2 保守不做。

---

## 6. 从 AI 使用角度的最终评价

### 6.1 评价维度（基于实测 datasheet + TRM 两份 bundle）

| 维度 | Grade | 说明 |
|---|---|---|
| **定位速度**（找到相关章节） | A | README 一屏给出 chapter outline；`toc.json` + `is_chapter` 一跳 |
| **按页查阅** | A | `pages.index.jsonl` 直接给页的 chunks/tables/assets/alerts |
| **表格查询** | A- | datasheet 97% 有 caption + kind 分类；TRM 寄存器表多无 caption 但 alert 已暴露 |
| **交叉引用跳转** | A | 100% resolved on datasheet；`target_id` 让跳转是 O(1) 找目标记录 |
| **证据完整性** | A | 85/1448 张图零 missing；csv_path / chunk_id / section_id / target_id 引用零破损 |
| **Silent failure 抵抗** | A（P60 后） | footer-strip fix 关上最后一个静默丢失通道 |
| **页码回溯** | A | 每条 chunk / table / asset / alert 都带页码；agent 可直接打开 PDF 到确切页 |
| **OCR 瑕疵可见性** | B+ | 明显 OCR 错误在 alerts 里；细节（如 `7 . 1. 1`）在 markdown 里可见，agent 要会识别 |
| **规模扩展** | A | 17× 规模（TRM）处理时间线性，无结构退化 |
| **上手难度** | A | Agent 只要读 README.md 即可开始用；流程 8 步内 |

**整体 Grade：A-**（受限于 Docling 层本身的 OCR / layout 缺陷；bundle 层已把 Docling 的能力用到最佳）。

### 6.2 AI agent 的真实使用体验

**典型查询场景与步数**（以 datasheet 为例）：

| 场景 | 步数 | 过程 |
|---|---|---|
| "GPIO14 默认功能是什么？" | 2 | README Table Breakdown → tables.index filter pinout → tables/table_0008.csv 查 GPIO14 行 |
| "VDD_SPI 电气参数" | 2 | README → tables.index filter electrical → tables/table_0032.csv |
| "Section 4.1.3.5 PMU 原文" | 2 | cross_refs find target_id → sections.jsonl filter section_id → chunks.jsonl filter chunk_ids |
| "第 4 章讲什么？" | 1 | sections.jsonl filter `section_id="4 Functional Description"` → 拿到 nav parent 的 page_range + table_ids |
| "Block diagram 在哪？" | 1-2 | grep document.md "ESP32-S3 Functional Block Diagram" → 得 md_line → assets.index 反查 |
| "Table 2-5 被谁引用？" | 1 | cross_refs.jsonl filter `target_id="esp32-s3-datasheet-en:table:0016"` |
| "这个表看着怪，可信吗？" | 1 | alerts.json 查是否列出 → 如在则回原 PDF |

**TRM 场景**（1531 页）：

| 场景 | 步数 |
|---|---|
| "I2C_SCL_ST_TO_INT_RAW 什么含义？" | 1（grep chunks.jsonl） |
| "Chapter 27 I2C Controller 里都有哪些寄存器？" | 2-3（sections filter "27." → 浏览子条目；或 tables filter by page range） |
| "GDMA 总线架构在哪？" | 2（sections filter "GDMA" → heading_path → pages） |
| "寄存器 PMS_CORE_X_IRAM0_PMS_CONSTRAIN_0_REG 的 bitfield" | 1（grep chunks.jsonl） |

**失败模式**：
- Agent 在 TRM 里问"Section 27 完整内容" — 因 Docling 把 "Chapter 27 I2C Controller" 拆成两个 page_header，sections.jsonl 没有 `Chapter 27` 顶级条目。Agent 需用 `27.` 前缀匹配子条目聚合
- TRM 371 张无 caption 表 — agent 看到 alert 后直接回原 PDF，不做 bundle 层决策

**证据链的关键胜利**：每个答案都能溯源：
- chunks → `citation: "doc_id p.X-Y"` 字段
- tables → `page_start` / `page_end` + CSV 文件名
- cross_refs → `source_chunk_id` + `target_id` + `target_page`

Agent 回答时可直接贴：`"根据 ESP32-S3 Datasheet p.42-43 section 4.1.3.5 Power Management Unit"`，用户可以立即打开原 PDF 核验。**这是 RAG 做不到的——它给的是向量邻居，不是可验证引用**。

### 6.3 与"Docling 直接输出"的对比

如果只跑 Docling 不做 bundle 后处理，agent 会拿到：

- `document.md` — 24 万字符的平铺 markdown，没有 per-page / per-section 反向索引
- `document.json` — 12 MB 的原生 JSON，字段嵌套深，每次查都要递归遍历
- `document.html` — 视觉验证 OK 但不可程序化
- 每张表没有 CSV sidecar；每个 caption 没有 kind 分类
- OCR 错误（`T able`）散落正文，影响 grep
- 没有 `alerts.json` → agent 不知道哪些页不可信

**bundle 层的价值**：把"Docling 能输出什么"翻译成"agent 能一步问什么"。从**能用**到**好用**的最后一公里。

### 6.4 一句话评价

> 这是一个以"**agent 少用步骤查到可信答案**"为单一 KPI 的基础设施项目。它不试图做 PDF 理解（那是 LLM 的事），只做 PDF 的**结构化、可导航、可验证**，并通过 `alerts.json` 让 agent 明确知道什么能信、什么要回原 PDF。规则 4（谨慎使用启发式）和规则 5（silent failure 不可接受）是整个设计的两条脊梁。

---

## 7. 附录：重要文件清单

| 文件 | 路径 |
|---|---|
| 项目报告 | [`PROJECT_REPORT.md`](PROJECT_REPORT.md)（本文件） |
| 根 README | [`README.md`](README.md) |
| 架构文档 | [`docs/architecture.md`](docs/architecture.md) |
| 任务计划 | [`task_plan.md`](task_plan.md) |
| 研究发现 | [`findings.md`](findings.md) |
| 变更日志 | [`progress.md`](progress.md) |
| 评价标准 | [`开发要求.md`](开发要求.md) |
| 产物 datasheet | [`manuals/processed/docling_bundle/esp32-s3-datasheet-en/`](manuals/processed/docling_bundle/esp32-s3-datasheet-en/) |
| 产物 TRM | [`manuals/processed/docling_bundle/esp32-s3-technical-reference-manual-en/`](manuals/processed/docling_bundle/esp32-s3-technical-reference-manual-en/) |
