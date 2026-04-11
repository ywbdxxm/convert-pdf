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

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-04-11 21:05 CST | 无 | 1 | 尚未出现错误 |
| 2026-04-11 21:xx CST | `fetch` / 沙箱网络请求失败 | 1 | 已调整 Codex 配置，等待新会话验证 |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | 所有阶段已完成，等待重启会话验证新配置 |
| Where am I going? | 在新会话里复测 `curl` 和 `fetch` |
| What's the goal? | 完成工具调研，并解决或解释当前 `fetch` 异常 |
| What have I learned? | `fetch` 与沙箱网络上下文无法访问本地代理，已通过配置补齐网络权限和代理透传 |
| What have I done? | 完成调研、推送研究记录、诊断 `fetch` 异常并更新 Codex 配置 |

---
*Update after completing each phase or encountering errors*
