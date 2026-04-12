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

## 仓库当前计划

短期计划：

1. 接入至少一条本地 `PDF -> Markdown` 转换管线
2. 准备一组真实 PDF 样本做对比测试
3. 比较不同工具在以下维度的表现：
   - 阅读顺序
   - 表格保真度
   - 公式保真度
   - OCR 能力
   - 中文文档支持
   - 输出是否适合大模型直接使用

中期计划：

1. 统一转换接口
2. 增加批处理能力
3. 增加结果评估与样本对比
4. 逐步扩展到更多 PDF 处理能力

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

## 后续实现方向

后续代码实现预计会围绕以下模块展开：

- `converters/`
  - 不同 PDF 转 Markdown 工具的适配层
- `samples/`
  - 测试 PDF 样本
- `outputs/`
  - 转换结果
- `benchmarks/`
  - 对比结果和评估脚本

## 当前结论

如果现在就开始落地实现，我的建议是：

- 先接入 `Docling`
- 再补 `Marker` 做高保真对比
- 再用 `PyMuPDF4LLM` 做轻量 baseline

这样可以在工程复杂度、精度和实现速度之间取得比较合理的平衡。
