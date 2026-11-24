# 小说工作区入口规则（taodao-dalu-jintou 分支）

当前分支的活跃轻小说项目位于子目录：`逃到大陆尽头她们还是追上来了/`。

## 每次会话默认行为
1. **必读宪法**：处理任何剧情讨论、写作、润色、返修或同步任务前，优先读取 `逃到大陆尽头她们还是追上来了/AGENTS.md`（包含本书 7 维文风、主角第一人称+女主幕间切入规范与绝对纯爱底线）。
2. **技能位于工作区 `.agents/skills/`**：全套 15 个写作 Skill 均已内置于本仓库根目录 `.agents/skills/`，跨机拉取自带生效。
3. **运行知识图谱 / 进度 / 快照脚本时**：先切换到书目录 `逃到大陆尽头她们还是追上来了/`（或设置环境变量 `NOVEL_PROJECT_ROOT` 指向该目录），再调用 `.agents/skills/` 下对应脚本。
4. **强制完整创作工作流（严禁主会话自己写自己审）**：只要用户要求写新章节（哪怕只说「继续写」「写下一章」），无需用户额外提醒，**必须严格按以下 5 步闭环执行，不得跳步**：
   - ① **事件卡前置**（`novel-discuss`）：确认 `memory/future/40-events/` 对应事件卡 `设计阶段: done` 且新实体已建档，否则先补全事件卡与实体；
   - ② **正文撰写**（`novel-write`）：完成写作前反思后展开章节正文；
   - ③ **本地四脚本硬检**（`novel-polish`）：依次运行 `ai_pattern_checker.py`、`translationese_checker.py`、`emotion_checker.py`、`fragment_checker.py --threshold 3`，全部 `exit 0`；
   - ④ **独立子代理盲审**（防视角越界与企划词穿帮）：调用只读 `research` 子代理，仅读取目标章节、`AGENTS.md`、`consistency-guard.md`、`fiction-humanizer-zh/SKILL.md` 与知识图谱做独立盲审（重点抓第一人称视角越界、未命名招式、企划标签残留、设定冲突与梗概感），主会话按盲审报告修净并复跑脚本；
   - ⑤ **同步与推送**（`novel-sync`）：更新 `past.md`、伏笔追踪表、重建 `knowledge_graph.py` 并更新创作进度。
5. **章后推送约定**：每章完成同步确认后，按需执行 `git add .agents/ "逃到大陆尽头她们还是追上来了/" AGENTS.md README.md .gitignore` 提交并推送至 `origin taodao-dalu-jintou`。
