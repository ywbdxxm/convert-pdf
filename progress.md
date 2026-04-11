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
