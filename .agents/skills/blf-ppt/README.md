# BLF_PPT

为科研、技术和项目汇报提供从材料分析、逐页规划、生图路线选择到 PPTX 验收的流程。主要使用中文，支持自动发现和显式调用；普通论文问答不应触发。

## 安装与迁移

正式维护源是本仓库中的这个目录；仓库根目录的 `README.md` 提供 GitHub CLI 安装和更新命令。本目录单独复制时，确保目标路径形如 `<项目>/.agents/skills/blf-ppt/SKILL.md`；用户级目录通常为 `~/.agents/skills/blf-ppt/`（Windows：`$env:USERPROFILE\.agents\skills\blf-ppt\`）。安装前检查同名目录，不直接覆盖自定义内容。复制后开启新任务；若仍未发现 Skill，重启 Codex。GitHub 上的更新不会自动同步已复制到其他电脑的 Skill。

显式调用示例：`$blf-ppt 请根据这篇论文规划组会汇报 PPT。` 也可以自然语言提出制作、改版或检查科研 PPT 的任务。更新时替换自己安装的同名目录即可；先比较现有自定义改动。

## 使用与限制

制作前提供论文、项目材料或参考 PPT（如有）；只有主题也能启动。规划完成并即将生图时，Skill 会让用户在当前 Codex 生图与独立 ChatGPT 窗口生图之间选择，已有明确选择则沿用。独立窗口的图片需由用户带回。图像生成与 PPT 渲染能力取决于目标电脑的工具，Skill 本身不包含模型、API Key、字体或模板，也不保证某种工具始终可用。

结构检查脚本仅需 Python 3.9+ 标准库：

```powershell
python .agents/skills/blf-ppt/scripts/audit_pptx.py path/to/deck.pptx
```

它读取 ZIP/XML，报告页数、可识别占位词、显著越界对象、疑似空页及包结构错误。退出码 0 为未发现结构问题，1 为发现问题，2 为无法解析；警告本身不改变退出码。它无法判断字体实际渲染、文字遮挡、视觉品质、图中文字、科学正确性或文件在 PowerPoint 中必然可打开。正式交付仍需实际打开和两遍视觉检查。

若旧版 Windows 控制台显示中文乱码，可先运行 `$env:PYTHONIOENCODING='utf-8'` 再调用脚本。

`tests/scenarios.md` 列出六类后续人工行为测试。`tests/test_audit_pptx.py` 用合成 PPTX 实际测试脚本的结构判断。
