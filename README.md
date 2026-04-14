# convert-pdf

把芯片数据手册、技术参考手册、应用笔记等 PDF，转换成适合 `Codex`、`Claude Code` 这类 agent 直接查阅、定位、引用、回到原文核验的结构化产物。

它不是一个通用 PDF 转 Markdown 小工具，也不是一个先上来就做 RAG 的应用壳子。它的定位更接近：

> AI 时代嵌入式开发的手册基础设施。

## 为什么这个项目重要

在嵌入式开发里，真正耗时间的不是“看文档”本身，而是：

- 在几百页到几千页手册里快速找到正确章节
- 在表格、图片、寄存器摘要、时序图之间来回切换
- 知道哪些页面可以初步相信，哪些页面必须回原 PDF 复核
- 让 agent 在保留证据链的前提下参与开发，而不是只会瞎猜

这个项目解决的就是这些问题。

目标不是让 AI“总结 PDF”，而是让 AI在工程上真正可用：

- 能查寄存器字段
- 能查 pin mux / pin assignment
- 能查电气参数和时序参数
- 能查外设模块摘要和流程说明
- 能把结论回到具体页码、具体表格、具体图

## 当前方案

当前只保留两条正式产线：

1. `docling_bundle`
2. `opendataloader_hybrid`

它们都把原始 PDF 转成面向 agent 的最终 bundle：

- `manuals/processed/docling_bundle/<doc_id>/`
- `manuals/processed/opendataloader_hybrid/<doc_id>/`

原始 PDF 在：

- `manuals/raw/`

非最终产物的 staging / cache 在：

- `tmp/opendataloader_hybrid-*-native/`
- `tmp/docling_bundle-cache/`

## 当前设计原则

### 1. 原始 PDF 永远是最终权威

解析是为了加速定位和暴露证据，不是为了取代原文。

对下面这些内容，最终工程结论必须能回到原 PDF 页面确认：

- 寄存器位定义
- pin 映射
- 时序限制
- 电气特性
- 时序图、框图、宽表

### 2. 以 agent 使用效果为最高评价标准

当前不再以“parser 纯度”或“统一 schema 美感”做第一判断。

当前真正看的标准是：

- 入口是不是足够明确
- 导航是不是足够清晰
- 表格和图片是不是容易核验
- 风险页是不是容易暴露
- 是否容易回到原 PDF

### 3. 保留完整图片证据

当前明确采用：

- `assets/` 默认完整保留
- 不做 heuristic 图片删减

原因很简单：

- 时序图、框图、寄存器图、视觉化表格经常是后续真正需要的证据
- 误删图片的风险，高于 bundle 变大的代价

### 4. 最终 bundle 只保留 agent 真正会用的层

当前默认保留的是：

- 单入口 `README.md`
- `manifest.json`
- `alerts.json`
- `document.md`
- `document.json`
- `document.html`
- 一套导航层
- `tables.index.jsonl`
- `tables/*.csv`
- `assets/`

运行期 staging、native dump、cache 统一留在 `tmp/`，不再混入最终 bundle。

## 当前两条产线

### `docling_bundle`

当前更偏“阅读 / 验证工作流”。

默认 bundle 结构：

```text
<doc_id>/
  README.md
  manifest.json
  alerts.json
  document.md
  document.json
  document.html
  sections.jsonl
  chunks.jsonl
  tables.index.jsonl
  tables/
  assets/
```

它的优势：

- 阅读体验更 calm
- 章节导航更自然
- 更适合日常“先读、再查、再核验”

### `opendataloader_hybrid`

当前更偏“证据 / 结构化提取能力”。

默认 bundle 结构：

```text
<doc_id>/
  README.md
  manifest.json
  alerts.json
  document.md
  document.json
  document.html
  elements.index.jsonl
  tables.index.jsonl
  tables/
  assets/
```

它的优势：

- bbox / page metadata 更强
- 结构化表格覆盖率更高
- 对复杂页面的证据核查能力更强

## 当前实测结果

基于最新一轮 clean rerun：

### OpenDataLoader Hybrid

ESP32-S3 datasheet：

- `87` 页
- `3187` 个元素
- `68` 张结构化表
- `1` 个 alert
- `triage_summary = JAVA=18, BACKEND=69`
- `fallback_detected = false`

ESP32-S3 TRM：

- `1531` 页
- `30290` 个元素
- `2467` 张结构化表
- `triage_summary = JAVA=173, BACKEND=1,358`
- `fallback_detected = true`

### Docling Bundle

ESP32-S3 datasheet：

- `87` 页
- `71` 张表
- `1` 个 alert

ESP32-S3 TRM：

- `1531` 页
- `667` 张表
- `9` 个 alert

## 当前判断

如果按“提取证据能力”评判：

- `OpenDataLoader hybrid` 更强

如果按“给 Codex / Claude Code 直接查阅和验证的工作流”评判：

- `docling_bundle` 更强

所以当前最合理的结论不是只留一个，而是：

- 把两者视为互补产线

如果现在必须二选一：

- 最强证据提取器：`OpenDataLoader hybrid`
- 最强阅读 bundle：`docling_bundle`

如果从“整体给 Codex 用”的当前总体验看：

- `docling_bundle` 仍略占优势

原因不是它解析更强，而是它更 calm、更自解释，更适合日常“先读、再查、再核验”的工作流。

## 当前 bundle 大小

最新 clean rerun 后：

- `opendataloader_hybrid` datasheet: `5.2M`
- `opendataloader_hybrid` TRM: `53M`
- `docling_bundle` datasheet: `16M`
- `docling_bundle` TRM: `203M`

这说明：

- 结构层冗余已经大幅收掉
- 当前新的主要体积来源已经不在结构冗余层
- 而是 `assets/` 和主文件本身

但由于我们已经明确保留完整图片证据，因此当前不把“继续删图片”当成默认优化方向。

## 典型使用方式

agent 使用最终 bundle 时，推荐顺序是：

1. 打开 `README.md`
2. 查看 `alerts.json`
3. 用导航层定位：
   - `sections.jsonl / chunks.jsonl` for `docling_bundle`
   - `elements.index.jsonl` for `opendataloader_hybrid`
4. 用 `tables.index.jsonl` 和 `tables/*.csv` 核对关键表
5. 用 `assets/` 和原 PDF 做最终确认

## 当前阶段结论

这个项目已经完成了从“能跑”到“可正式使用”的关键过渡。

更准确地说：

- 已经明显比之前更接近最佳实践
- 但还没有彻底定型
- 当前处于“可用且持续优化中”的阶段，而不是“完全无需再改”的阶段

## 下一步重点

当前下一步最值得继续推进的点：

1. 继续统一两条产线的 agent-facing 使用方式
2. 继续评估是否需要把导航层进一步收敛成统一 `locator.index.jsonl`
3. 基于固定任务继续做 A/B 对比，而不是靠印象判断
4. 把旧文档口径彻底收敛到当前真实产物结构

## 文档入口

- [项目报告](项目报告.md)
- [四份产物详细对比分析](四份产物详细对比分析.md)
- [Docs Index](docs/README.md)
- [Project Structure](docs/architecture/2026-04-15-project-structure.md)
- [Parser Status And Next Steps](docs/architecture/2026-04-15-parser-status-and-next-steps.md)
- [Docling Embedded Manual Processing](docs/architecture/2026-04-12-docling-embedded-manual-processing.md)
