# 项目现状与方案对比汇报

日期：2026-04-15

## 1. 项目背景与最高需求

本项目最初的核心需求非常明确，不是“做一个通用 PDF 工具”，也不是“做一个聊天式 RAG 应用”，而是：

> 把芯片数据手册、技术参考手册、应用笔记等 PDF，转换成适合 AI 编码代理直接查阅、检索、引用、回溯原文的结构化产物。

这个需求面向的不是普通阅读，而是**嵌入式开发场景**。在这个场景里，AI 需要频繁做这些事情：

- 查某个寄存器字段定义
- 查 pin mux / pin assignment
- 查某个时序参数、电气参数、推荐工作条件
- 查某个外设模块的寄存器摘要、地址映射、流程说明
- 把结论回溯到具体页码甚至具体表格/图

因此，本项目真正追求的不是“能不能把 PDF 变成 Markdown”，而是：

1. AI 是否能快速定位信息
2. AI 是否能保留页码和证据链
3. AI 是否能识别不可靠页面并回到原 PDF 复核
4. 最终产物是否能稳定支持 Codex、Claude Code 这类 agent 长期使用

## 2. 设计原则

围绕上述最高需求，本项目最终收敛出以下设计原则：

### 2.1 原始 PDF 始终是最终权威

无论任何解析器输出多好，芯片手册里的以下内容都不能直接盲信：

- 寄存器位定义
- pin 映射
- 时序限制
- 电气特性
- 图形化时序图、框图、宽表

解析后的结构化产物只能用于：

- 加速定位
- 降低查阅成本
- 暴露证据
- 提醒风险

最终工程结论仍必须能回到原 PDF 页面确认。

### 2.2 以 Agent 使用效果为最高评价标准

本项目在中期明确废弃了“先定义统一 schema，再要求所有工具强行适配”的思路。

当前标准是：

> 以 Codex / Claude Code 最终使用这些产物的效果来判断好坏。

衡量标准包括：

- 是否容易找到入口文件
- 是否容易按页或按章节定位
- 是否容易看到表格、图像、旁证
- 是否容易发现风险点
- 是否能保留页码/证据链
- 是否容易回到原 PDF

### 2.3 不把解析器输出和消费层混为一谈

本项目最终保留了两条产线，但不再要求它们在内部结构上完全一致。

原因是：

- `OpenDataLoader` 更偏“富结构证据树”
- `Docling` 更偏“稳定阅读副本 + 检索索引 + sidecar”

强行统一会损失各自优势。

### 2.4 优先保留低风险、高收益的 bundle 层改进

我们已经明确进入“收益递减阶段”。

因此，允许的优化主要是：

- 更好的 README 入口
- 更好的 quality summary
- 更清晰的 page slices
- 更清晰的 runtime report
- 更清晰的 alerts

不再鼓励无限制地加入：

- parser 修补 heuristic
- VLM 修复流水线
- 自研检索系统
- 新的通用 schema 工程

## 3. 当前总体架构

当前项目可以理解为“两条解析/产物产线 + 一套共享工作站基础设施”。

### 3.1 工作站分层

当前实际采用的是分层环境：

1. WSL 系统层
2. 共享 AI base
3. 项目级 overlay 环境
4. 原始 PDF / 最终 bundle / staging 数据

具体为：

- 系统层：
  - Java 17
  - Docker
  - NVIDIA runtime
  - OCR 与通用构建工具
- 共享 AI base：
  - `/home/qcgg/.mamba/envs/ai-base-cu124-stable`
  - 复用 `torch + CUDA`
- 项目 overlay：
  - `docling/.venv`
  - `opendataloader/.venv`

这个架构的目的，是避免每个工具或项目重复安装大体积 GPU 依赖。

### 3.2 代码层产线

当前核心代码分为两套：

- `docling_bundle/`
- `opendataloader_hybrid/`

这两个目录不是解析器本身，而是**最终产物组织器 / bundle builder**。

### 3.3 数据层

数据层分为：

- `manuals/raw/`
  - 原始 PDF
- `manuals/processed/`
  - 最终可供 AI 使用的 bundle 根目录
- `tmp/`
  - 可选 staging，中间原始输出暂存

## 4. 当前项目目录结构

当前项目顶层结构为：

```text
convert-pdf/
  AGENTS.md
  README.md
  docling/
  docling_bundle/
  docs/
  manuals/
  opendataloader/
  opendataloader_hybrid/
  progress.md
  scripts/
  task_plan.md
  tests/
  findings.md
```

其中最重要的目录角色如下：

### 4.1 `docling/`

Docling 的项目 overlay 环境目录。

用于：

- 运行 `python -m docling_bundle convert`
- 保持 Docling 的 Python 依赖隔离

### 4.2 `docling_bundle/`

Docling 侧最终 bundle builder。

当前职责：

- 组织 `document.json / md / html`
- 构建 `sections.jsonl / chunks.jsonl`
- 导出 `tables/`
- 生成 `pages/`
- 生成 `README.generated.md`
- 生成 `quality-summary.md`
- 生成 `alerts.json`
- 维护 `runtime/cache/`

### 4.3 `opendataloader/`

OpenDataLoader 的项目 overlay 环境目录。

用于：

- 运行 `opendataloader-pdf`
- 运行 `opendataloader-pdf-hybrid`

### 4.4 `opendataloader_hybrid/`

OpenDataLoader 侧最终 bundle builder。

当前职责：

- 选择 native 输出文件
- 构建 `elements.index.jsonl`
- 导出 `tables.index.jsonl`
- 导出 `tables/`
- 生成 `pages/`
- 保留 `runtime/native/`
- 生成 `runtime/report.json`
- 生成 `quality-summary.md`
- 生成 `alerts.json`

### 4.5 `manuals/raw/`

原始 PDF 样本。

当前主要样本：

- `ESP32-S3 datasheet`
- `ESP32-S3 TRM`
- `STM32H743VI`

### 4.6 `manuals/processed/`

最终给 AI 使用的可见 bundle 根目录。

当前仅保留两个正式根：

```text
manuals/processed/docling_bundle/
manuals/processed/opendataloader_hybrid/
```

注意：

- git 中只跟踪占位目录
- 真实 bundle 是本地生成物
- 不提交真实输出

## 5. 两种方案的设计与实现

当前活跃方案只有两种：

1. `docling_bundle`
2. `opendataloader_hybrid`

下面分别说明。

## 6. 方案一：Docling Bundle

### 6.1 设计目标

`docling_bundle` 的目标不是“证明 Docling 原生输出最纯”，而是：

> 把 Docling 的结构化能力和阅读副本能力组织成一套更适合 Codex/Claude Code 直接使用的 bundle。

它强调的是：

- 读起来顺手
- 检索路径清晰
- sidecar 容易核对
- 风险点容易发现

### 6.2 核心架构

当前 Docling bundle 输出根是：

```text
manuals/processed/docling_bundle/<doc_id>/
```

典型产物包括：

- `README.generated.md`
- `quality-summary.md`
- `document.json`
- `document.md`
- `document.html`
- `sections.jsonl`
- `chunks.jsonl`
- `tables.index.jsonl`
- `pages/`
- `tables/`
- `artifacts/`
- `alerts.json`
- `runtime/cache/`

### 6.3 代码实现重点

主要代码在：

- `docling_bundle/converter.py`
- `docling_bundle/indexing.py`
- `docling_bundle/reading_bundle.py`
- `docling_bundle/tables.py`
- `docling_bundle/alerts.py`
- `docling_bundle/paths.py`

当前已经完成的重要实现包括：

1. 将输出根切换到 `manuals/processed/docling_bundle/<doc_id>/`
2. 增加 `README.generated.md`
3. 增加 `quality-summary.md`
4. 增加 `pages/`
5. 增加 `tables.index.jsonl`
6. 将窗口缓存移到 `runtime/cache/`
7. 将 `chunks/sections` 中的 table 引用从“嵌整表对象”改为 `table_ids`
8. 在 `quality-summary.md` 中直接展示 alert 页码与说明

### 6.4 当前产物特点

优点：

- `document.md` 更适合作为主阅读副本
- `README.generated.md` 是清晰入口
- `quality-summary.md` 有较强的操作指导性
- `tables/` sidecar 与阅读副本结合得更好
- `pages/` 更接近“页级阅读切片”
- `runtime/cache/` 在大文档上稳定、清晰

缺点：

- bbox / spatial metadata 弱
- 表格覆盖率低于 OpenDataLoader
- 一些 figure-like table 仍会退化
- 大 TRM 上更吃 GPU、更重

### 6.5 当前实测结果

ESP32-S3 datasheet：

- 87 页
- 71 张表
- 1 个 alert

ESP32-S3 TRM：

- 1531 页
- 668 张表
- 10 个 alert

### 6.6 适用场景

更适合：

- 默认主阅读入口
- 要快速按章节读上下文
- 要边读边看 table sidecar
- 要在 summary 指引下快速定位风险页

## 7. 方案二：OpenDataLoader Hybrid

### 7.1 设计目标

`opendataloader_hybrid` 的目标不是把 OpenDataLoader 改造成 Docling，而是：

> 保留 OpenDataLoader 的证据优势，把它封装成 Codex/Claude Code 能高效消费的 bundle。

它强调的是：

- page-level evidence
- bbox-aware debugging
- 结构化表格覆盖
- runtime 行为可见

### 7.2 核心架构

当前 OpenDataLoader bundle 输出根是：

```text
manuals/processed/opendataloader_hybrid/<doc_id>/
```

典型产物包括：

- `README.generated.md`
- `quality-summary.md`
- `document.json`
- `document.md`
- `document.html`
- `elements.index.jsonl`
- `tables.index.jsonl`
- `pages/`
- `tables/`
- `figures/`
- `alerts.json`
- `runtime/report.json`
- `runtime/native/`

### 7.3 代码实现重点

主要代码在：

- `opendataloader_hybrid/bundle.py`
- `opendataloader_hybrid/paths.py`
- `opendataloader_hybrid/cli.py`
- `scripts/run_opendataloader_hybrid.sh`
- `scripts/bootstrap_opendataloader_env.sh`

当前已经完成的重要实现包括：

1. 建立独立 `opendataloader/.venv`
2. 确保复用 shared AI base，而不是重复安装 `torch`
3. 建立 `runtime/native/` 保存 native 原始输出
4. 建立 `elements.index.jsonl`
5. 建立 `tables.index.jsonl` 与 `tables/`
6. 建立 `pages/`
7. 建立 `runtime/report.json`
8. 增加 image-backed hard-table alert
9. 支持多文档 staging 目录下按 `source_pdf_path` stem 选对文件

### 7.4 当前产物特点

优点：

- bbox / page metadata 很强
- 结构化表格数量明显更多
- `elements.index.jsonl` 对细粒度证据检索很强
- `runtime/report.json` 能暴露 triage/fallback 行为
- 速度更快
- GPU 占用相对没有那么持续

缺点：

- 直接阅读体验不如 Docling calm
- 某些 hard table 仍然是 `image + paragraph fragments`
- 大 TRM 上如果不带 `--hybrid-fallback`，稳定性不足
- page slices 更偏“证据视图”，不如 Docling page slices 顺手阅读

### 7.5 当前实测结果

ESP32-S3 datasheet：

- 87 页
- 3187 个元素
- 68 张结构化表
- 0 个基础 alert
- 新增 page 27 hard-table alert

ESP32-S3 TRM：

- 1531 页
- 30290 个元素
- 2467 张结构化表
- 0 个基础 alert

### 7.6 当前最佳实践参数

当前不建议裸跑 hybrid。

当前最优的实践是：

- `docling-fast`
- `--device cuda`
- `--hybrid-fallback`

因为我们已经在真实大 TRM 上验证过：

- backend sort/transform 会报错
- 不开 fallback 会导致整本失败
- 开了 fallback 才能稳定生成最终产物

### 7.7 适用场景

更适合：

- 要做 bbox-aware page evidence 检查
- 要提取更多结构化表格
- 要做“这一页到底发生了什么”的 forensic 检查
- 要在复杂表格和复杂版面上优先拿证据

## 8. 两种方案当前对比

### 8.1 结论先行

如果按“提取证据能力”评判：

- `OpenDataLoader hybrid` 更强

如果按“Codex 直接查阅和验证体验”评判：

- `docling_bundle` 更强

因此当前最合理的结论不是“只留一个”，而是：

- 保留两者
- 把它们视为互补产线

### 8.2 为什么没有强行统一成一个输出 schema

原因很简单：

- 强行统一会压掉各自优势

`docling_bundle` 的优势在：

- 阅读副本
- summary
- alerts
- sidecar workflow

`OpenDataLoader hybrid` 的优势在：

- rich element tree
- page number
- bounding box
- 高覆盖结构化表格

如果强行揉成一个 schema，很容易：

- 让 OpenDataLoader 丢掉证据优势
- 让 Docling 丢掉成熟阅读层优势

### 8.3 对 Codex 的最终判断

今天如果必须二选一：

- **最佳证据提取器**：`OpenDataLoader hybrid`
- **最佳阅读 bundle**：`docling_bundle`

如果从“整体给 Codex 用”的角度只选一个当前总包：

- `docling_bundle` 略占优势

原因不是它解析更强，而是：

- 它更 calm
- 更自解释
- 更适合日常“先读、再查、再核验”

## 9. Codex / Claude Code 如何使用这些产物

## 9.1 使用原则

无论是 Codex 还是 Claude Code，推荐的使用顺序都是：

1. 打开 `README.generated.md`
2. 打开 `quality-summary.md`
3. 根据任务走章节索引、元素索引或页切片
4. 必要时打开 table/figure sidecar
5. 最终回到原 PDF 页码做确认

### 9.2 使用 `docling_bundle` 的建议顺序

推荐从：

- `manuals/processed/docling_bundle/<doc_id>/README.generated.md`

开始。

然后：

1. 看 `quality-summary.md`
2. 用 `sections.jsonl` 找主题
3. 用 `chunks.jsonl` 找页级引用
4. 用 `tables.index.jsonl` 和 `tables/` 核对表
5. 用 `pages/` 看具体页
6. 再回原 PDF

### 9.3 使用 `opendataloader_hybrid` 的建议顺序

推荐从：

- `manuals/processed/opendataloader_hybrid/<doc_id>/README.generated.md`

开始。

然后：

1. 看 `quality-summary.md`
2. 看 `runtime/report.json`
3. 用 `elements.index.jsonl` 做页级/元素级定位
4. 用 `tables.index.jsonl` 看结构化表
5. 用 `pages/` 做页级证据核查
6. 用 `figures/` 和原 PDF 做最终确认

### 9.4 Claude Code 与 Codex 的差异

对于这类产物，两者的消费方式本质相同，区别主要在于使用习惯和工具组合，不在于产物格式本身。

共同点：

- 都适合先看 `README.generated.md`
- 都需要先看 `quality-summary.md`
- 都要保留页码与原文回溯链

差异：

- Codex 更适合基于目录和文件直接做 agentic file retrieval
- Claude Code 同样能消费这些文件，但如果上下文管理稍弱，更依赖入口文件和 summary 的质量

所以当前产物设计已经默认兼容两者：

- 入口文件明确
- summary 明确
- 索引明确
- sidecar 明确

## 10. 当前成熟度判断

这是目前最重要的管理判断。

结论是：

> 对当前项目目标来说，已经进入“相对完善、明显收益递减”的阶段。

这意味着：

- 现在已经够好，可以正式用
- 不是完全没有可改进点
- 但后续改动大多不再是“明显缺失能力”

### 10.1 为什么说已经比较完善

因为以下关键目标已经都满足：

1. 两条产线都能处理真实样本
2. 两条产线都能输出 Codex-facing bundle
3. 都有明确入口
4. 都有风险提示
5. 都能支持页级回溯
6. 都能支持表格/图像核对
7. OpenDataLoader 的 fallback 经验已经验证
8. Docling 的 cache 恢复路径已经验证

### 10.2 为什么说再优化已经进入收益递减

剩下最可能继续做的事情，已经不是“明显必赢”的工作，而是：

- OpenDataLoader 去重建 image-backed hard tables
- Docling 去加更激进的 heuristics / page prioritization
- 建更正式的比较基准系统

这些都有可能带来收益，但同时：

- 复杂度更高
- 维护成本更高
- 不确定性更高
- 不一定稳定提升实际使用效果

因此当前最合理的策略是：

- 先用
- 真实使用里出现明确痛点再重开优化

## 11. 后续可能的改进方向

虽然已经进入收益递减阶段，但仍然可以列出后续方向，供后续立项参考。

### 11.1 OpenDataLoader 可继续改进点

1. 对 image-backed hard tables 增加强提示或半结构化导出
2. 在 `README.generated.md` 里加入更强的页级重点导航
3. 在 `quality-summary.md` 中增加更明显的 figure/table/alert 入口
4. 对 fallback 页范围做更精细的 runtime 报告

### 11.2 Docling 可继续改进点

1. 在 `README.generated.md` 中直接列 alert pages
2. 对 hard pages 加更轻量的 page-evidence 索引
3. 减少低价值 index/contents tables 的存在感
4. 对 figure-like table 的失败页做更强提示

### 11.3 共同可继续改进点

1. 固定一组比较任务
2. 记录：
   - 打开文件数量
   - 找到答案所需路径
   - 是否保留页码引用
   - 是否仍需回原 PDF
3. 用任务得分而不是印象来做持续比较

## 12. 当前建议

如果是给老板/管理层的最终建议，我会这样表述：

1. **当前阶段建议停止继续大规模 parser-output 工程。**
2. **当前产物已经足以支持真实嵌入式开发辅助工作。**
3. **保留两条产线：**
   - `docling_bundle`：默认阅读/验证路径
   - `opendataloader_hybrid`：高证据、高表格覆盖路径
4. **后续仅在真实使用暴露明确痛点时再继续投入优化。**
5. **若后续要继续投入，优先做 bundle 层增强，不优先做 parser 修补工程。**

## 13. 当前文档入口

老板或新同事如果要快速了解项目，建议按这个顺序读：

1. [README.md](../README.md)
2. [docs/README.md](../README.md)
3. [2026-04-15-parser-status-and-next-steps.md](2026-04-15-parser-status-and-next-steps.md)
4. [2026-04-15-project-structure.md](2026-04-15-project-structure.md)
5. [2026-04-12-docling-embedded-manual-processing.md](2026-04-12-docling-embedded-manual-processing.md)
6. [2026-04-15-parser-optimization-roadmap.md](../superpowers/plans/2026-04-15-parser-optimization-roadmap.md)
