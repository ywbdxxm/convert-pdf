# Progress Log

## Session: 2026-04-11

### Phase 1: Requirements & Discovery
- **Status:** complete
- **Started:** 2026-04-11 21:05 CST
- Actions taken:
  - 读取 `planning-with-files` skill 说明
  - 运行会话 catchup 脚本
  - 检查仓库路径与 `git status`
  - 确认当前任务先做工具调研，再输出推荐
- Files created/modified:
  - `task_plan.md` (created)
  - `findings.md` (created)
  - `progress.md` (created)

### Phase 2: Evaluation Framework
- **Status:** complete
- Actions taken:
  - 归纳评估维度：Markdown 输出质量、阅读顺序、表格/公式、OCR、扫描件、多语言、部署与许可
  - 按开源本地、轻量基线、云 API 三类整理候选
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)

### Phase 3: Research & Comparison
- **Status:** complete
- Actions taken:
  - 查阅 Marker、Docling、MinerU、PyMuPDF4LLM 的官方仓库/文档
  - 查阅 Mathpix、Mistral OCR、Azure Document Intelligence、LlamaParse 的官方文档
  - 形成按场景推荐和候选快照表
- Files created/modified:
  - `findings.md` (updated)

### Phase 4: Documentation & Delivery
- **Status:** complete
- Actions taken:
  - 回写研究结论到 planning files
  - 提交研究记录：`docs: research pdf to markdown tooling`
  - 推送远程 `origin/main` 成功
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

### Phase 5: Fetch Tool Diagnosis
- **Status:** complete
- Actions taken:
  - 单独复现 `fetch` 请求 `https://example.com` 的失败
  - 在沙箱内复现 `curl` 失败，并确认代理指向 `127.0.0.1:7897`
  - 在提权环境复现相同 `curl` 成功
  - 测试去代理和改用 `10.255.255.254:7897` 的结果
  - 备份并修改 `/home/qcgg/.codex/config.toml`
  - 用 `tomllib` 校验修改后的 TOML 语法
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)
  - `/home/qcgg/.codex/config.toml` (updated, external)
  - `/home/qcgg/.codex/config.toml.bak-2026-04-11-2135` (created, external)

### Phase 6: Post-Config Validation
- **Status:** complete
- Actions taken:
  - 在当前新会话中复测沙箱 `curl`
  - 验证 `fetch` 对 OpenAI 文档、Docling 官网、GitHub 页面和 GitHub raw 的抓取结果
  - 复测 `example.com` 和 `example.com/robots.txt` 的边缘失败
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

### Phase 7: Repository Docs Refresh
- **Status:** complete
- Actions taken:
  - 按“PDF 处理项目，当前先做 PDF 转 Markdown”的定位重写 README
  - 重建 `.gitignore`，保留 Python 项目基础忽略项和本地实验产物忽略项
  - 更新规划文件并准备提交推送
- Files created/modified:
  - `README.md` (recreated)
  - `.gitignore` (recreated)
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Session catchup | `python3 ~/.codex/skills/planning-with-files/scripts/session-catchup.py "$PWD"` | 输出已有会话上下文或空结果 | 返回空结果，无阻塞 | ✓ |
| Git status | `git status --short --branch` | 识别当前工作区状态 | 检测到已有删除项和未跟踪 `.codex` | ✓ |
| Git push | `git push origin main` | 将研究提交推送到 GitHub | 成功推送 `da395da` 到 `origin/main` | ✓ |
| Sandboxed curl | `curl -I https://example.com` | 通过 Clash 代理出网 | 失败，尝试连接 `127.0.0.1:7897` 但不可达 | ✗ |
| Escalated curl | `curl -I https://example.com` | 通过 Clash 代理出网 | 成功返回 `200 Connection established` / `HTTP/2 200` | ✓ |
| No-proxy curl in sandbox | `env -u ... curl -I https://example.com` | 直接出网 | 失败，`Could not resolve host` | ✗ |
| Host-IP proxy in sandbox | `curl --proxy http://10.255.255.254:7897 -I https://example.com` | 通过宿主代理出网 | 失败，端口不可达 | ✗ |
| Fetch tool | `fetch https://example.com` | 成功拉取页面 | 失败，`robots.txt` 连接错误 | ✗ |
| Config syntax | `python3 -c 'tomllib.load(...)'` | TOML 配置有效 | `TOML OK` | ✓ |
| Sandboxed curl after config | `curl -I https://example.com` | 通过 Clash 代理出网 | 成功返回 `HTTP/1.1 200 Connection established` / `HTTP/2 200` | ✓ |
| Sandboxed curl to GitHub raw | `curl -I https://raw.githubusercontent.com` | 通过 Clash 代理出网 | 成功返回 `HTTP/1.1 200 Connection established` / `HTTP/2 301` | ✓ |
| Fetch OpenAI docs | `fetch https://developers.openai.com/codex/concepts/sandboxing` | 成功抓取文档内容 | 成功返回页面正文 | ✓ |
| Fetch Docling site | `fetch https://www.docling.ai/` | 成功抓取页面内容 | 成功返回页面正文 | ✓ |
| Fetch GitHub page | `fetch https://github.com/datalab-to/marker` | 成功抓取页面内容 | 成功返回仓库正文 | ✓ |
| Fetch GitHub raw | `fetch https://raw.githubusercontent.com/datalab-to/marker/master/README.md` | 成功抓取原始文本 | 成功返回 README 内容 | ✓ |
| Fetch example.com robots | `fetch https://example.com/robots.txt` | 成功抓取 robots.txt 或返回 404 正文 | 失败，`robots.txt` 连接错误 | ✗ |
| README rewrite | 手工审阅新 README | 与当前项目阶段一致 | 已改为阶段导向结构 | ✓ |
| .gitignore refresh | 手工审阅新 `.gitignore` | 忽略基础缓存与本地产物 | 已收敛为最小必要集合 | ✓ |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-04-11 21:05 CST | 无 | 1 | 尚未出现错误 |
| 2026-04-11 21:xx CST | `fetch` / 沙箱网络请求失败 | 1 | 已调整 Codex 配置，等待新会话验证 |
| 2026-04-11 21:5x CST | `fetch` 对 `example.com` 仍失败 | 1 | 记录为边缘案例；不影响真实文档站点和 GitHub 的抓取 |
| 2026-04-11 22:0x CST | 无 | 1 | README / `.gitignore` 改写未出现错误 |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | 所有阶段已完成 |
| Where am I going? | 等待用户决定继续实现哪条 PDF 转 Markdown 管线 |
| What's the goal? | 完成工具调研，并解决或解释当前 `fetch` 异常 |
| What have I learned? | README 需要贴合当前阶段，`.gitignore` 需要收敛而不是泛化 |
| What have I done? | 完成调研、修复沙箱配置、验证 `fetch`，并整理了仓库文档 |

---
*Update after completing each phase or encountering errors*

## Session Update: Embedded Datasheet Recommendation
- Time: 2026-04-11 22:23 CST
- Context:
  - 用户把场景收敛为嵌入式工程文档，重点是芯片 datasheet / app note 转 Markdown。
- Actions taken:
  - 恢复上个会话上下文并复核 `task_plan.md` / `findings.md` / `progress.md`
  - 将通用 PDF→Markdown 结论重新映射到嵌入式资料场景
  - 在 `findings.md` 中新增面向 datasheet / 应用手册的专门推荐
- Decision:
  - 默认首选仍定为 `Docling`
  - `Marker` 作为高保真复杂表格/公式增强方案
  - `MinerU` 作为扫描件/中文/多语言/复杂 OCR 备用方案
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Docling Deep Dive
- Time: 2026-04-11 22:35 CST
- Context:
  - 用户要求详细了解 `Docling` 的使用方式、部署形态、特点，以及是否适合做批处理 PDF 程序。
- Actions taken:
  - 复核当前规划文件
  - 查阅 `Docling` 官方文档和官方仓库说明
  - 提炼本地部署、远程服务、OCR、批处理和编程语言建议
- Key findings:
  - `Docling` 的主形态是本地 Python 库和 CLI，而不是默认依赖云 API
  - 官方推荐使用 `DocumentConverter`，批处理入口是 `convert_all(...)`
  - 远程服务是显式 opt-in 能力，不是普通 PDF->Markdown 的必需项
  - 对批处理 datasheet / app note，最佳实现语言仍是 Python
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: PDF MCP Workflow Recommendation
- Time: 2026-04-11 22:42 CST
- Context:
  - 用户询问我是否能直接读 PDF，是否应先转 Markdown，以及 `pdf-reader-mcp` 是否会更适合嵌入式手册驱动开发。
- Actions taken:
  - 查阅 `SylphxAI/pdf-reader-mcp` 官方仓库说明
  - 将其能力与 `Docling` 主转换管线做对比
  - 提炼“转换管线 + PDF 回查”式最佳实践
- Key findings:
  - `pdf-reader-mcp` 适合按页查阅、抽图、快速验证原文
  - 它当前不是面向 datasheet 结构化抽取的最强主方案
  - 对嵌入式开发，最佳实践是原始 PDF + Docling Markdown/JSON + PDF MCP 回查三层结构
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: WSL GPU Environment Design
- Time: 2026-04-11 23:0x CST
- Context:
  - 用户要求开始 `Docling` 探索，并把 WSL 全局环境打到可支撑后续 `Docling + MinerU/OCR/VLM` 的程度。
- Actions taken:
  - 恢复上一轮规划文件和研究结论
  - 核对本机系统、GPU、Python 和基础工具状态
  - 在 full-access 下复测 `nvidia-smi`
  - 记录本地与云端方案的现实取舍
- Key findings:
  - 当前 WSL2 下 `nvidia-smi` 正常，GPU 路径可用
  - 当前有 `uv/pip/python3/build-essential/cmake`，但无 `nvcc/docker/ninja-build`
  - 对嵌入式 PDF，云端方案上限可能更高，但不必然比本地明显更优
  - 先把 `Docling` 本地链路打通，再和 `MinerU API` 做样本对比更合理
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Global WSL Preference
- Time: 2026-04-11 23:xx CST
- Context:
  - 用户确认采用方案 2，但强调希望 GPU/NVIDIA 相关支持直接装在 WSL 系统里，便于所有项目复用。
- Actions taken:
  - 把“系统级 WSL 基础设施优先”写入任务计划和 findings
  - 识别出剩余的关键设计边界：系统级 GPU 栈与系统级 Python AI 包安装需分开决策
- Key findings:
  - 系统级安装 GPU/CUDA 容器支持是合理目标
  - 是否把 `torch/docling/mineru` 直接装进系统 Python 仍需单独确认
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Isolation Boundary Confirmed
- Time: 2026-04-11 23:xx CST
- Context:
  - 用户确认系统级 GPU/NVIDIA 基础设施全局配置，但认可 Python AI 依赖需要按项目做合理隔离。
- Actions taken:
  - 更新任务计划和 findings
  - 明确系统级与项目级职责边界
- Key findings:
  - WSL 系统层负责 GPU / Docker / NVIDIA runtime / build tools
  - `docling/torch/mineru` 等 Python 依赖保持项目隔离
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: AGENTS Preference Clarified
- Time: 2026-04-11 23:xx CST
- Context:
  - 用户希望以后我能智能判断系统级安装与项目级隔离的边界，并询问这类原则是否应该写进 `AGENTS.md`。
- Actions taken:
  - 将该偏好记录到 findings
  - 归纳为“环境与依赖分层原则”
- Key findings:
  - 这类偏好适合写进 `AGENTS.md`
  - 但应写成原则，而不是一次性实现细节或具体命令
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Design Boundary Approved
- Time: 2026-04-11 23:xx CST
- Context:
  - 用户认可“系统级 GPU/容器基础 + 项目级 Python 依赖隔离”的设计边界。
- Actions taken:
  - 记录该设计已获用户认可
  - 准备进入实施顺序与验收标准设计
- Key findings:
  - 可以继续完成最后一段设计，并在获批后开始执行
- Files created/modified:
  - `progress.md` (updated)

## Session Update: Execution Audit
- Time: 2026-04-11 23:xx CST
- Context:
  - 用户要求检查计划是否执行到位、更新进展，并说明目前是否有遗漏。
- Actions taken:
  - 审计系统层安装结果
  - 审计 `exploration/docling/` 目录状态
  - 审计项目级依赖安装进度
- Verified complete:
  - `docker` 已安装
  - `nvidia-container-toolkit` 已安装
  - Docker daemon 已配置 `nvidia` runtime
  - Docker daemon 已配置代理
  - `hello-world` 容器已成功运行
  - GPU 容器已成功运行 `nvidia-smi`
  - `ninja-build` 与 Tesseract 基础包已安装
  - `docling/` 与基础文件已创建
  - `.venv` 已创建
- In progress:
  - CUDA 版 `torch` 安装仍在进行
- Remaining:
  - 安装 `docling`
  - 运行 `check_gpu.py`
  - 运行 `check_docling.py`
  - 运行最小转换 smoke test
  - 更新 README 并提交推送
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: OpenDataLoader PDF Assessment
- Time: 2026-04-12 00:xx CST
- Context:
  - 用户询问 `opendataloader-project/opendataloader-pdf` 这个项目与当前 PDF->Markdown 路线的关系。
- Actions taken:
  - 查阅官方 GitHub 仓库说明
  - 将其与 `Docling` / `MinerU` / `MarkItDown` 做定位对比
- Key findings:
  - `opendataloader-pdf` 更像专用高质量 PDF parser，而不是轻量通用转换器
  - 它支持本地 deterministic mode，也支持复杂页 hybrid AI backend
  - 它值得进入后续 A/B 测试，但依赖 Java 11+ 和混合栈，工程复杂度高于 `Docling`
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Current Status Check
- Time: 2026-04-12 00:xx CST
- Context:
  - 用户询问当前实际进展。
- Actions taken:
  - 轮询正在运行的 `uv add` 进程
  - 检查 `exploration/docling/` 当前文件状态
  - 对照 planning 文件核对剩余步骤
- Current status:
  - 系统层安装与验证维持完成状态
  - `docling/` 目录、`.venv`、验证脚本、`pyproject.toml` 已存在
  - CUDA 版 `torch` 安装仍在运行，当前仍在下载/安装多组 NVIDIA wheels
- Remaining:
  - 等待 `torch` 安装完成
  - 安装 `docling`
  - 跑 `check_gpu.py`
  - 跑 `check_docling.py`
  - 跑 Docling 最小 smoke test
  - 更新 README / planning 并提交推送
- Files created/modified:
  - `progress.md` (updated)

## Session Update: Torch Download Progress
- Time: 2026-04-12 00:xx CST
- Context:
  - 用户询问当前下载进度。
- Actions taken:
  - 轮询正在运行的 `uv add` 安装会话
  - 检查 `uv` 缓存大小与 `.venv` 现状
- Current observations:
  - `uv add` 进程仍在运行，未退出
  - `uv` 缓存目录当前约 `3.4G`
  - `.venv` 目录当前仍很小，说明安装尚未完成到最终环境落盘阶段
  - 当前仍在处理的大体积 NVIDIA wheels 包括：
    - `nvidia-cudnn-cu12`
    - `nvidia-cublas-cu12`
    - `nvidia-nccl-cu12`
    - `nvidia-cusparselt-cu12`
    - `nvidia-cusolver-cu12`
    - `nvidia-cufft-cu12`
    - `nvidia-curand-cu12`
    - `nvidia-nvshmem-cu12`
- Conclusion:
  - 安装仍在正常推进，但尚未接近完成
- Files created/modified:
  - `progress.md` (updated)

## Session Update: Torch Download Progress (Latest)
- Time: 2026-04-12 01:xx CST
- Context:
  - 用户再次询问当前安装进展。
- Current observations:
  - `uv add` 进程仍在运行，已持续约 `2:03:25`
  - `uv` 缓存目录当前约 `3.7G`
  - `.venv` 仍未进入最终依赖落盘阶段，目录大小约 `100K`
  - 本轮确认新完成的包：`nvidia-curand-cu12`
- Remaining large CUDA wheels still in progress:
  - `nvidia-cublas-cu12`
  - `nvidia-cufft-cu12`
  - `nvidia-nccl-cu12`
  - `nvidia-cudnn-cu12`
  - `nvidia-cusolver-cu12`
  - `nvidia-cusparselt-cu12`
  - `nvidia-nvshmem-cu12`
- Conclusion:
  - 仍在正常推进，但尚未完成 `torch` 安装，因此 `docling` 安装和验证尚未开始
- Files created/modified:
  - `progress.md` (updated)

## Session Update: Download vs Install Clarification
- Time: 2026-04-12 01:xx CST
- Context:
  - 用户质疑此前“torch 已安装完”的表述是否准确，并询问中间是否发生中断。
- Actions taken:
  - 检查当前 `uv add` 进程的启动时间
  - 检查 `.venv/site-packages` 当前实际内容
- Findings:
  - 当前长时间运行的是同一个 `uv` 进程，启动时间为 `2026-04-11 23:31:10`
  - `.venv/site-packages` 当前仍只有 virtualenv 自身文件，尚无 `torch`
  - 因此此前看到的 `Downloaded torch` 只能说明 wheel 已下载到缓存，不代表已安装到 `.venv`
- Conclusion:
  - 不是中途安装完成又丢失，而是我之前把“下载完成”和“安装完成”说混了
  - 当前安装流程仍未完成，`torch` 仍未真正安装到项目环境
- Files created/modified:
  - `progress.md` (updated)

## Session Update: UV Strategy Reassessment
- Time: 2026-04-12 01:xx CST
- Context:
  - 用户询问 `uv` 是否能换源，以及当前超长安装是否意味着每个项目都要重复一次。
- Key findings:
  - 当前安装已经在使用自定义 PyTorch CUDA 源，不是默认 PyPI
  - 当前瓶颈主要来自 CUDA 版 `torch` 及其 NVIDIA wheels 的体积，而不是 `uv` 本身不会换源
  - 更合理的后续策略是先跑通 CPU/默认 `Docling` 链路，再视需要单独建立 GPU 项目环境
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Shared AI Base Direction
- Time: 2026-04-12 01:xx CST
- Context:
  - 用户要求本次继续等待当前 GPU 项目环境完成，但后续要补一个共享 `AI base` 通用环境，避免每个项目都重复下载大体积 CUDA Python 依赖。
- Actions taken:
  - 将该方向写入任务计划和 findings
- Key findings:
  - 当前项目安装继续进行，不中断
  - 后续需要补 Phase 6：共享 `AI base` 环境设计
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Workstation Architecture Scope Expansion
- Time: 2026-04-12 01:xx CST
- Context:
  - 用户明确表示愿意在初期投入更多时间，把整台工作站的长期分层架构认真设计好，而不是只做当前项目的临时环境。
- Actions taken:
  - 将任务范围提升为长期 `WSL -> Docker -> CUDA -> AI base -> Project` 架构设计
  - 在 `task_plan.md` 中新增工作站架构设计阶段
- Key findings:
  - 后续设计重点不再只是当前 `Docling` 项目
  - 需要先明确这台机器未来的主负载类型，再决定共享层应该做到多重
- Files created/modified:
  - `task_plan.md` (updated)
  - `progress.md` (updated)

## Session Update: CUDA Download Failure After Network Drop
- Time: 2026-04-12 01:xx CST
- Context:
  - 用户反馈刚刚出现断网，希望确认当前 CUDA 相关下载是否仍正常。
- Actions taken:
  - 轮询原始 `uv add` 会话
  - 检查进程是否仍在运行
  - 检查 `.venv` 当前内容
- Findings:
  - 原始 `uv add` 进程已退出，不再运行
  - 失败点为下载 `nvidia-cusolver-cu12==11.7.3.90`
  - 错误为 `tls handshake eof`
  - `.venv/site-packages` 仍只有 virtualenv 自身文件，未安装 `torch`
- Conclusion:
  - 当前下载已不正常，且本次安装已经失败结束
  - 下一步不能简单当作“继续下载”，而应结合稳态优先目标重新设计共享 GPU Python 依赖层
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Shared Base Granularity Reconsidered
- Time: 2026-04-12 01:xx CST
- Context:
  - 用户指出“按家族拆多个共享 base”如果处理不当，仍可能重复下载/安装超大依赖。
- Actions taken:
  - 将该风险写入 findings
  - 收敛共享 base 的设计原则
- Key findings:
  - `torch + CUDA` 这类超大高复用依赖不应在多个共享环境里各装一份
  - 稳态优先下，共享 base 应尽量少而厚，项目层只放增量依赖
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Root-Level Project Directory Preference
- Time: 2026-04-12 02:xx CST
- Context:
  - 用户要求去掉 `exploration/` 这一层，后续每个项目目录直接放在仓库根下。
- Actions taken:
  - 将 `exploration/docling` 移动为 `docling/`
  - 清理空的 `exploration/`
  - 开始修正文档中的路径引用
- Key findings:
  - 当前项目目录结构已切换到根下 `docling/`
  - 这更符合用户希望的长期仓库组织方式
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Repository AGENTS Added
- Time: 2026-04-12 02:xx CST
- Context:
  - 用户要求把长期工作站架构原则总结进仓库级 `AGENTS.md`，以便后续会话继承。
- Actions taken:
  - 新建仓库级 `AGENTS.md`
  - 写入系统层 / 单一共享重型 AI base / 项目轻量增量层 / 根目录项目目录 的原则
- Key findings:
  - 本仓库后续会话可以直接继承这些环境分层约束
- Files created/modified:
  - `AGENTS.md` (created)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Shared AI Base Bootstrapped
- Time: 2026-04-12 02:xx CST
- Context:
  - 用户要求把工作站架构原则推广到全局 `~/.codex/AGENTS.md`，并按新的稳态分层继续实施。
- Actions taken:
  - 更新全局 `/home/qcgg/.codex/AGENTS.md`
  - 创建共享重型 AI base：`/home/qcgg/.venvs/ai-base-cu128-stable`
  - 开始将 `torch + CUDA` 安装转移到共享 base，而不是继续塞进项目目录
- Key findings:
  - 全局工作站原则已经可以跨仓库复用
  - 当前重型依赖安装目标已从项目环境切换为共享 AI base
- Files created/modified:
  - `/home/qcgg/.codex/AGENTS.md` (updated)
  - `task_plan.md` (updated)
  - `progress.md` (updated)

## Session Update: Conda Necessity Assessment
- Time: 2026-04-12 02:xx CST
- Context:
  - 用户要求检查当前进度，并评估 `conda` 是否有必要引入。
- Actions taken:
  - 审计共享 `AI base` 当前安装状态
  - 检查本机是否已安装 `conda/mamba/micromamba`
  - 结合当前 `uv + CUDA torch` 的失败模式评估分层工具选择
- Findings:
  - 当前未安装 `conda`、`mamba`、`micromamba`
  - 当前共享 `AI base` 仍在进行重型 `torch + CUDA` 安装
  - `uv` 更适合项目级轻量环境
  - 对共享重型 `AI base`，`micromamba/conda` 已经成为强候选
- Conclusion:
  - `conda` 不是所有层都必须引入
  - 但对共享重型 AI base，这一层使用 `micromamba` 值得认真考虑
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Shared AI Base UV Attempt Ended
- Time: 2026-04-12 02:xx CST
- Context:
  - 在评估 `conda/micromamba` 必要性时，继续检查共享 `AI base` 的 `uv` 安装状态。
- Findings:
  - 原共享 `AI base` 的 `uv pip install` 会话已经结束
  - 当前没有对应的活跃安装进程
  - `/home/qcgg/.venvs/ai-base-cu128-stable` 仍接近空环境
- Conclusion:
  - 共享重型 AI base 继续用 `uv + CUDA torch wheels` 的方案，当前已证明不够稳
  - `micromamba` 已从“强候选”升级为“下一步应切换的方案”
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Batch Program Design Added
- Time: 2026-04-12 02:xx CST
- Context:
  - 用户要求在环境配置之外，提前深度思考后续基于 `Docling` 的批处理 PDF 程序，目标是最适合我后续查阅手册并辅助嵌入式开发。
- Actions taken:
  - 在任务计划中新增批处理程序设计阶段
- Key findings:
  - 后续设计重点不仅是“PDF 转 Markdown”，而是“如何组织多份手册，方便长期检索、引用和代码开发”
- Files created/modified:
  - `task_plan.md` (updated)
  - `progress.md` (updated)

## Session Update: Mirror Reset And Download Cleanup
- Time: 2026-04-12 11:40 CST
- Context:
  - 用户要求清除之前所有下载内容，重新设计方案，并把 `conda` / `uv` / `pip` 都切到中国国内镜像。
- Actions taken:
  - 审计上次中断的共享 `AI base` 创建状态
  - 确认 `micromamba create` 仍在运行，但环境目录仅 `8K`，包缓存已膨胀到 `5.5G`
  - 停止未完成的 `micromamba create` 进程
  - 清理 `~/.mamba`、`~/.cache/pip`、`~/.cache/uv` 中与本轮失败安装相关的残留
  - 复核并修正 `pip.conf`、`uv.toml`、`.condarc`
  - 修正 `uv.toml` 中无效的 `default-index` 键为 `index-url`
  - 用 `pip index versions`、`uv pip install --dry-run`、`micromamba create --dry-run` 验证国内镜像可用性
  - 为保持“干净状态”，在验证后再次清空缓存
- Key findings:
  - `pip` 当前已正常使用清华镜像
  - `uv` 之前虽然写了镜像文件，但因为键名错误，实际上处于不可用状态
  - `micromamba` 在国内镜像配置下可以成功 dry-run 解析 `pytorch-cuda=12.4`
  - `micromamba` 的 dry-run 会生成很大的 repodata 缓存，这不等于环境已安装成功
  - 当前最合理的分层仍然是：共享重型 `AI base` 用 `micromamba`，项目级轻量环境用 `uv`
- Files created/modified:
  - `AGENTS.md` (updated)
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)
  - `/home/qcgg/.config/uv/uv.toml` (updated, external)

## Session Update: AI Workstation Design Audit
- Time: 2026-04-12 11:xx CST
- Context:
  - 用户要求完整审计 AI 工作站设计，确认遗漏与优化点，并在执行前先做一次 git 提交。
- Actions taken:
  - 审计仓库当前结构、规划文件、README、`docling/` 目录和系统层实际状态
  - 复测 GPU、Docker GPU runtime、镜像配置、基础工具版本
  - 发现仓库内原先引用的设计文档并不存在
  - 发现全局 `/home/qcgg/.codex/AGENTS.md` 实际为空
  - 补写全局 AGENTS 工作站规则
  - 新增架构审计文档和执行计划文档
  - 新增共享 `AI base`、`docling` overlay 环境和验证脚本
- Key findings:
  - 之前缺的不是系统层，而是“设计落盘”和“复用机制”
  - `docling/` 之前是空目录，项目层并未真正成形
  - 共享 `AI base` 与项目环境之间，采用 overlay venv 是当前最合理的折中方案
- Files created/modified:
  - `/home/qcgg/.codex/AGENTS.md` (updated, external)
  - `docs/architecture/2026-04-12-ai-workstation-design-audit.md` (created)
  - `docs/architecture/2026-04-12-ai-workstation-execution-plan.md` (created)
  - `scripts/bootstrap_ai_base.sh` (created)
  - `scripts/bootstrap_docling_env.sh` (created)
  - `scripts/verify_ai_stack.sh` (created)
  - `docling/README.md` (created)
  - `docling/requirements.txt` (created)
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Historical State Corrected
- Time: 2026-04-12 11:xx CST
- Context:
  - 在提交前做一致性检查时，发现部分旧进度记录仍保留了“当时视角”的中间状态，容易被误读成当前状态。
- Actions taken:
  - 将规划文件中的旧路径和旧工具状态改为带时间上下文的描述
  - 明确标记：`micromamba` 现已安装，旧的 `uv` 共享 base 路径已被清理，`~/.codex/AGENTS.md` 已由本次审计真正补齐
- Key findings:
  - 历史记录可以保留，但当前状态必须在新条目里被重新锚定
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Shared AI Base Build In Progress
- Time: 2026-04-12 12:10 CST
- Context:
  - 在完成设计审计提交并推送后，开始执行共享重型 `AI base` 的真实创建。
- Actions taken:
  - 执行 `./scripts/bootstrap_ai_base.sh`
  - 确认 `micromamba create -n ai-base-cu124-stable ...` 仍在运行
  - 检查 `~/.mamba` 当前落盘状态
- Key findings:
  - 当前 `~/.mamba/pkgs` 已增长到约 `9.9G`
  - 当前 `~/.mamba/envs/ai-base-cu124-stable` 仍约 `8K`
  - 这说明当前仍在重型事务阶段，包缓存已下载/解压很多，但环境本体尚未完成最终落盘
- Files created/modified:
  - `findings.md` (updated)
  - `progress.md` (updated)

## Session Update: Shared AI Base And Docling Overlay Verified
- Time: 2026-04-12 12:xx CST
- Context:
  - 用户要求继续按计划执行，当前主线是共享 `AI base` 完成后继续做 `docling` 项目层和整体验证。
- Actions taken:
  - 确认 `micromamba create` 已结束且 `ai-base-cu124-stable` 已真实落盘
  - 验证共享 `AI base` 中 `torch 2.5.1` 可正常访问 CUDA 与当前 GPU
  - 初次尝试用 `uv` 给 overlay 安装 `docling`，发现其会重复解析并下载 PyPI 的 `torch + cu13`
  - 中止该错误路径，读取 `docling` wheel 元数据确认 `torch>=2.2.2,<3.0`
  - 改用 `pip` 作为 overlay 安装器
  - 重建 `docling/.venv` 并成功安装 `docling 2.86.0`
  - 复跑验证脚本，确认 WSL GPU、Docker GPU runtime、共享 `AI base`、`docling` overlay 全部通过
- Key findings:
  - `uv` 不适合当前这种依赖共享 site-packages 复用的 overlay 场景
  - `pip` 可以正确复用共享 base 的 `torch`
  - 共享 `AI base + overlay venv` 方案已经从设计变成可运行事实
- Files created/modified:
  - `task_plan.md` (updated)
  - `findings.md` (updated)
  - `progress.md` (updated)
  - `scripts/bootstrap_docling_env.sh` (updated)
  - `scripts/verify_ai_stack.sh` (updated)
  - `docs/architecture/2026-04-12-ai-workstation-design-audit.md` (updated)
  - `docs/architecture/2026-04-12-ai-workstation-execution-plan.md` (updated)
  - `docling/README.md` (updated)
