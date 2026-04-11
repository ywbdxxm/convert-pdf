# Task Plan: PDF 转 Markdown 工具调研与工具环境诊断

## Goal
完成 PDF 转 Markdown 工具调研，并诊断当前会话中 `fetch` 工具异常的根因，给出可执行的修复或规避方案。

## Current Phase
Complete

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
- [x] 输出中文结论与后续建议
- [x] 处理本次 git 提交与远程推送
- **Status:** complete

### Phase 5: Fetch Tool Diagnosis
- [x] 复现 `fetch` 失败
- [x] 对比沙箱与提权环境网络行为
- [x] 记录根因与修复路径
- **Status:** complete

### Phase 6: Post-Config Validation
- [x] 验证沙箱内普通网络命令
- [x] 验证 `fetch` MCP 对真实目标站点的可用性
- [x] 记录仍存在的边缘案例
- **Status:** complete

## Key Questions
1. 当前有哪些主流 PDF→Markdown 工具适合大模型 RAG/查阅场景？
2. 哪些工具对复杂版面、表格、公式和扫描件表现最好？
3. 在本地开源、自托管和云 API 三类方案中，分别该如何选型？
4. 这个仓库后续应该优先集成哪几种工具做实验？
5. 为什么当前会话里的 `fetch` 工具失败，而用户自己的 WSL 终端网络正常？
6. 配置生效后，沙箱网络和 `fetch` 是否已经达到可用状态？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 使用 `planning-with-files` 维护本次任务 | 任务包含调研、比较、文档沉淀和 git 管理，步骤较多 |
| 先做工具调研，再决定仓库实现方向 | 用户当前优先需求是选型，不是立即编码 |
| 不回滚现有脏工作区中的删除项 | 这些改动可能来自用户，当前只记录并规避误操作 |
| 以“本地开源默认方案 + 云 API 备选 + 轻量基线”输出结论 | 这样最适合当前仓库逐步实验和后续工程化 |
| 先只提交三份研究/规划文件，不携带 `.gitignore` 与 `README.md` 删除 | 避免把用户已有未确认删除混入本次提交 |
| 将 `fetch` 异常按环境问题而非业务逻辑错误处理 | 现有证据显示是运行上下文网络可达性差异 |
| 采用 A 方案：保留 `workspace-write`，显式开启沙箱网络并给 `fetch` 透传代理环境 | 这是风险最低且最贴近用户现有使用方式的修复路径 |
| 当前判定为“沙箱网络正常，`fetch` 基本可用但存在个别站点边缘案例” | 实测中真实文档站点正常，`example.com` 仍触发 `robots.txt` 连接异常 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `fetch` / 沙箱网络请求失败 | 1 | 已定位为沙箱/MCP 与用户 WSL 终端网络上下文不同，并已修改 Codex 配置做修复 |
| `fetch` 对 `example.com` 仍报 `robots.txt` 连接问题 | 1 | 记录为站点级边缘案例，不影响对文档站点和 GitHub 的正常使用 |

## Notes
- 当前 `git status` 显示 `.gitignore`、`README.md`、`findings.md`、`progress.md`、`task_plan.md` 为删除状态，另有未跟踪 `.codex` 文件；不主动回滚。
- 调研将优先参考官方文档、官方仓库与项目主页。
- 结论需要区分：通用最佳、复杂版面最佳、扫描件/OCR 最佳、工程集成最稳妥。
- 已完成提交并推送：`da395da` 推送到 `origin/main`，后续只剩用户决定先落地哪条解析管线。
- 当前新增任务是诊断 `fetch` 工具异常；初步证据指向工具运行环境无法访问用户的本地 Clash 代理。
- 已备份原始配置到 `/home/qcgg/.codex/config.toml.bak-2026-04-11-2135`，并更新 `/home/qcgg/.codex/config.toml`。
- 新会话实测表明：沙箱 `curl` 已可正常通过代理联网，`fetch` 对 OpenAI 文档、Docling 官网、GitHub 页面和 raw 文本都可用。
