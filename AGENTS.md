# Repository Guidance

## Planning With Files

对 3 步以上或含研究的任务，维护项目根下的 `task_plan.md` / `findings.md` / `progress.md`。这些文件是长期记忆，不是临时便签。

## 产线

**只维护 `docling_bundle` 一条产线**（2026-04-18 起）。`opendataloader_hybrid/` 代码仍在树中但已冻结，不要在其中扩展新功能。

## 默认运行

```sh
docling/.venv/bin/python -m docling_bundle convert \
  --input manuals/raw/<vendor>/<chip>/<manual>.pdf \
  --output manuals/processed \
  --device cuda \
  --no-ocr
```

- OCR 默认关闭；仅当扫描/图片密集 PDF 才启用
- 窗口缓存 `--enable-window-cache --cache-window-size 250` 仅当 PDF 超大或运行不稳定时使用
- 测试迭代默认只跑 `esp32-s3_datasheet_en.pdf`；TRM（1531 页）需要用户显式许可

## Bundle 消费

见 `README.md` 里的「消费流程」。关键规则：

- **原始 PDF 永远是最终权威**
- `alert_count > 0` 时先读 `alerts.json` 再用任何内容
- 寄存器值 / 位域 / 电气参数 / 引脚映射 / 时序在回答前必须回 PDF 对应页核对

## 环境分层

- WSL 系统层：Docker / NVIDIA 容器 / CUDA 桥接 / 编译工具
- 共享 AI base（`~/.mamba/envs/ai-base-cu124-stable`）：`torch` 及 CUDA Python wheel
- 项目环境 `docling/.venv`：复用共享 base 的 `torch`，只装项目级依赖
- 不要在项目环境里重装 `torch`；不要在 shell 启动脚本里 auto-activate

## 国内镜像

- `pip` / `uv` / `conda` / `micromamba` 全部走国内镜像（配置文件已落盘到 `~/.config/{pip,uv}/`、`~/.condarc`）
- 超大依赖安装中断要先清干净再重试，不要叠在半装状态上

## 修改 docling_bundle 的原则

- 不要手改 `manuals/processed/**` 下的任何文件。这些是产物，改代码、重跑才是正道
- 以"AI 使用 bundle 时的真实体验"为最高评判标准
- 任何新产物或 schema 变更都要有对应的单元测试
- 大幅改动后要重跑 datasheet 并在 `findings.md` 里记录实测观察

## 测试

```sh
docling/.venv/bin/python -m unittest discover -s tests -v
```

当前基线 74 通过。新功能必须扩充测试。
