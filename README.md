# convert-pdf

一个面向 PDF 处理的项目，当前第一阶段专注于将 PDF 转换为适合大模型阅读、检索和 RAG 使用的 Markdown。

## 当前阶段

当前目标不是做一个“什么都支持”的 PDF 工具箱，而是先把 `PDF -> Markdown` 这条链路做扎实，包括：

- 保留尽可能好的阅读顺序
- 提升表格、公式、图片说明等结构信息的保真度
- 兼顾文本型 PDF 和扫描件 PDF
- 为后续大模型检索、摘要、问答和结构化抽取做准备

## 为什么先做 PDF 转 Markdown

Markdown 是当前大模型处理中最实用的中间格式之一：

- 比纯文本更能保留文档结构
- 比直接喂 PDF 更容易切分、清洗和检索
- 适合进入 RAG、embedding、chunking 和 agent 工作流
- 便于人工检查和版本管理

## 当前选型方向

基于当前调研，这个仓库接下来优先关注以下工具：

### 1. Docling

默认优先尝试的基础方案。

- 导出 Markdown 能力完整
- 对 OCR、表格、公式、阅读顺序支持较均衡
- 很适合作为本仓库第一条可落地的转换管线

### 2. Marker

偏高精度和复杂版面的方案。

- 对复杂 PDF、表格、公式、版面还原更强
- 适合做高保真对照实验

### 3. PyMuPDF4LLM

偏轻量、快速集成的 baseline。

- 接入成本低
- 适合先跑通最小可用链路

### 4. MinerU

针对扫描件、中文、多语言和复杂学术文档的重要备选方案。

## 当前实现状态

当前仓库已经落地了第一版 `Docling` 批处理程序，目标不是“单纯导出 Markdown”，而是把芯片手册转成更适合 AI 查阅和引用的一组资产：

1. 原始 PDF
2. `Docling JSON`
3. 阅读版 `Markdown`
4. 章节级索引 `sections.jsonl`
5. 检索级索引 `chunks.jsonl`
6. 文档级 `manifest.json`
7. 批处理级 `run summary`

当前默认路线是：

`PDF -> Docling JSON -> HybridChunker(native) -> contextualized chunks + Markdown companion`

## 当前仓库内容

- `README.md`
  - 项目说明
- `docs/architecture/`
  - AI 工作站架构审计和执行计划
- `task_plan.md`
  - 任务规划和阶段记录
- `findings.md`
  - 工具调研与结论
- `progress.md`
  - 执行过程和验证记录
- `scripts/`
  - 共享 AI base、Docling overlay 和环境验证脚本
- `docling/`
  - Docling 项目级工作区
- `docling_batch/`
  - 第一版 Docling 批处理程序
- `tests/`
  - 批处理程序的单元测试

## 当前工作站架构

当前仓库采用分层工作站设计：

1. `Host`
   - Windows 驱动、WSL 集成、宿主代理
2. `WSL System`
   - Docker、NVIDIA runtime、OCR、本地构建工具
3. `Shared Heavy AI Base`
   - 单一共享的 `torch + CUDA` 重型环境
4. `Project Overlay`
   - 每个项目自己的轻量 Python 依赖层
5. `Data / Outputs`
   - PDF 样本、转换结果、索引和实验产物

这样做的目标是既保持项目隔离，又避免每个项目都重新下载完整的 GPU Python 栈。

## 当前推荐启动顺序

从仓库根目录执行：

```sh
./scripts/bootstrap_ai_base.sh
./scripts/bootstrap_docling_env.sh
./scripts/verify_ai_stack.sh
```

## 批处理程序用法

先准备环境：

```sh
./scripts/bootstrap_ai_base.sh
./scripts/bootstrap_docling_env.sh
./scripts/verify_ai_stack.sh
```

然后运行批处理：

```sh
docling/.venv/bin/python -m docling_batch convert \
  --input /path/to/manuals \
  --output /path/to/output \
  --device cuda
```

若当前 PDF 是数字版手册，建议先关闭 OCR：

```sh
docling/.venv/bin/python -m docling_batch convert \
  --input /path/to/manuals \
  --output /path/to/output \
  --device cuda \
  --no-ocr
```

若是扫描件或图片化 PDF，再启用 OCR，默认走 `RapidOCR`：

```sh
docling/.venv/bin/python -m docling_batch convert \
  --input /path/to/manuals \
  --output /path/to/output \
  --device cuda \
  --ocr-engine rapidocr \
  --force-full-page-ocr
```

## 输出结构

每个文档会生成：

- `<output>/<doc_id>/document.json`
- `<output>/<doc_id>/document.md`
- `<output>/<doc_id>/manifest.json`
- `<output>/<doc_id>/sections.jsonl`
- `<output>/<doc_id>/chunks.jsonl`

每次批处理还会生成：

- `<output>/_runs/<timestamp>.json`

其中：

- `document.json`
  - Docling canonical source，后续索引和结构化抽取应从这里派生
- `document.md`
  - 供人工阅读和 diff 的副产物
- `sections.jsonl`
  - 章节级索引，方便快速定位某个主题在哪章哪页
- `chunks.jsonl`
  - 原生 `HybridChunker` 产出的检索级片段，带 `contextualized_text` 和页码引用
- `manifest.json`
  - 文档元数据、处理参数和输出路径

## 当前结论

对这个仓库，当前最佳实践已经收敛为：

- 默认主线：`Docling`
- canonical source：`Docling JSON`
- 检索切块：Docling 原生 `HybridChunker`
- 阅读副本：`Markdown`
- GPU：优先 `--device cuda`
- OCR：按需启用，而不是默认总开
