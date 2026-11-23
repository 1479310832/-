# 小说工作区入口规则（taodao-dalu-jintou 分支）

当前分支的活跃轻小说项目位于子目录：`逃到大陆尽头她们还是追上来了/`。

## 每次会话默认行为
1. **必读宪法**：处理任何剧情讨论、写作、润色、返修或同步任务前，优先读取 `逃到大陆尽头她们还是追上来了/AGENTS.md`（包含本书 7 维文风、主角第一人称+女主幕间切入规范与绝对纯爱底线）。
2. **技能位于工作区 `.agents/skills/`**：全套 15 个写作 Skill 均已内置于本仓库根目录 `.agents/skills/`，跨机拉取自带生效。
3. **运行知识图谱 / 进度 / 快照脚本时**：先切换到书目录 `逃到大陆尽头她们还是追上来了/`（或设置环境变量 `NOVEL_PROJECT_ROOT` 指向该目录），再调用 `.agents/skills/` 下对应脚本。
4. **章后推送约定**：每章完成同步确认后，按需执行 `git add .agents/ 逃到大陆尽头她们还是追上来了/ AGENTS.md README.md requirements.txt .gitignore` 提交并推送至 `origin taodao-dalu-jintou`。
