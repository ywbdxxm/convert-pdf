# Task Plan: PDF 转 Markdown 工具调研与仓库管理

## Goal
调研当前适合将 PDF 转换为 Markdown 供大模型查阅的工具，给出分场景推荐，并将本次研究记录纳入仓库版本管理。

## Current Phase
Phase 4

## Phases
### Phase 1: Requirements & Discovery
- [x] 理解用户目标与约束
- [x] 检查仓库现状与 git 状态
- [x] 收集候选 PDF→Markdown 工具
- **Status:** complete

### Phase 2: Evaluation Framework
- [x] 明确评估维度
- [x] 对候选工具做分组
- [x] 记录推荐标准与限制
- **Status:** complete

### Phase 3: Research & Comparison
- [x] 查阅官方文档、仓库与说明
- [x] 比较版面保真度、表格/公式/OCR、多语言、部署方式
- [x] 形成按场景推荐
- **Status:** complete

### Phase 4: Documentation & Delivery
- [x] 更新 findings.md 与 progress.md
- [ ] 输出中文结论与后续建议
- [ ] 处理本次 git 提交与远程推送
- **Status:** in_progress

## Key Questions
1. 当前有哪些主流 PDF→Markdown 工具适合大模型 RAG/查阅场景？
2. 哪些工具对复杂版面、表格、公式和扫描件表现最好？
3. 在本地开源、自托管和云 API 三类方案中，分别该如何选型？
4. 这个仓库后续应该优先集成哪几种工具做实验？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 使用 `planning-with-files` 维护本次任务 | 任务包含调研、比较、文档沉淀和 git 管理，步骤较多 |
| 先做工具调研，再决定仓库实现方向 | 用户当前优先需求是选型，不是立即编码 |
| 不回滚现有脏工作区中的删除项 | 这些改动可能来自用户，当前只记录并规避误操作 |
| 以“本地开源默认方案 + 云 API 备选 + 轻量基线”输出结论 | 这样最适合当前仓库逐步实验和后续工程化 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| 无 | 1 | 尚未遇到需要处理的错误 |

## Notes
- 当前 `git status` 显示 `.gitignore`、`README.md`、`findings.md`、`progress.md`、`task_plan.md` 为删除状态，另有未跟踪 `.codex` 文件；不主动回滚。
- 调研将优先参考官方文档、官方仓库与项目主页。
- 结论需要区分：通用最佳、复杂版面最佳、扫描件/OCR 最佳、工程集成最稳妥。
