# BLF_PPT

一套用于规划、制作、改版和检查科研、技术及项目汇报 PPT 的中文 Codex Skill。正式 Skill 入口是 [`.agents/skills/blf-ppt/SKILL.md`](.agents/skills/blf-ppt/SKILL.md)；仓库没有第二份入口文件。普通论文问答不属于它的触发范围。

## 安装

把下列命令中的 `OWNER/REPO` 换成这个仓库实际的 GitHub 地址。使用支持 `gh skill` 的新版 GitHub CLI 时，推荐：

```powershell
gh skill install OWNER/REPO .agents/skills/blf-ppt --agent codex --scope user --allow-hidden-dirs
```

该命令把 Skill 安装到 Codex 用户范围。安装前检查同名 Skill；不要无意覆盖本地修改。`gh skill` 是 GitHub CLI 的预览功能，旧版 CLI 可能没有此命令；先用 `gh skill install --help` 核对。

没有适用的 GitHub CLI 时，可从 GitHub 下载仓库 ZIP 或用 `git clone https://github.com/OWNER/REPO.git` 取得仓库，随后只复制 `.agents/skills/blf-ppt/` 整个目录到目标电脑的 `~/.agents/skills/blf-ppt/`；Windows 常见目标是 `$env:USERPROFILE\.agents\skills\blf-ppt\`。不要把仓库根目录、测试输出或其他材料复制进 Skill 目录。安装前先查看目标是否已存在，保留本地自定义修改。

开启新的 Codex 任务后，可以输入 `$blf-ppt 请根据这篇论文制作组会汇报。`，也可以自然语言提出 PPT 制作或检查请求。如果 Skill 没出现，重启 Codex。

## 更新

由 `gh skill install` 安装的副本可运行 `gh skill update blf-ppt`；更新前先查看是否有本地修改。手动安装的副本需重新下载仓库或对本地克隆执行 `git pull --ff-only`，然后比对并重新复制该 Skill 目录。**GitHub 不会自动同步其他电脑上的本地副本。** 若本机 CLI 不支持 `gh skill update`，使用手动方法。

## 使用、维护与限制

Skill 的工作流程与审计脚本说明见 [目录内 README](.agents/skills/blf-ppt/README.md)。脚本只需 Python 3.9+ 标准库；测试命令：

```powershell
python -m unittest discover -s .agents/skills/blf-ppt/tests -p 'test_*.py' -v
```

维护时只编辑仓库中的 `.agents/skills/blf-ppt/`，记录重要变化于 `CHANGELOG.md`，运行现有测试并检查待提交文件。图像生成、PowerPoint 渲染和跨窗口交接取决于使用者环境；结构审计不能替代真实打开、科学事实与视觉复核。本仓库不包含论文、实验数据、参考 PPT、密钥或私人项目素材。
