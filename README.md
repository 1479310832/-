# 《逃到大陆尽头她们还是追上来了》— AI 轻小说创作工作区

本分支（`taodao-dalu-jintou`）是完全独立的新书工作区，已内置全套本地工作区级写作 Skills（位于 `.agents/skills/`），**换电脑拉取后即可直接接着创作，无需重新配置全局环境**。

---

## 换电脑一步续写指南（零额外依赖）

### 直接克隆本分支并打开即可
```bash
git clone -b taodao-dalu-jintou --single-branch https://github.com/1479310832/-.git yuling-novel
```
*(若你用 Git 图形工具克隆了整仓，克隆完把分支切到 `taodao-dalu-jintou` 即可；也可以在 GitHub 仓库 Settings → Branches 把默认分支设为 `taodao-dalu-jintou`，以后直接克隆连切分支都省了。)*

### 打开即用（无需 `pip install`）
用 Antigravity 打开目录即可直接续写：
- 根目录下 `.agents/skills/` 中的 **15 个写作 Skill 会自动发现并仅在本工作区生效**；
- 全部 8 个 Python 质检/图谱脚本均为**纯标准库零依赖**（只要电脑有 Python 即可直接跑，无需安装第三方包）；
- 根目录 `AGENTS.md` 与 `逃到大陆尽头她们还是追上来了/AGENTS.md` 会自动加载《小说宪法》与当前进度；
- 直接在对话里说：**「同步第 X 章」**、**「继续写下一章」** 或 **「讨论下一段事件」** 即可无缝续写。

---

## 目录说明

```text
.
├── AGENTS.md                                 # 工作区入口指路规则
├── .agents/skills/                           # 15 个工作区专属小说创作 Skills（零第三方依赖）
└── 逃到大陆尽头她们还是追上来了/
    ├── AGENTS.md                             # 本书《小说宪法》（7 维文风、人称规范、红线）
    ├── memory/                               # 知识图谱、世界观、角色/势力/能力卡、全书与卷大纲、事件卡
    ├── chapters/                             # 各事件章节大纲与正文
    └── templates/                            # 角色卡与章节模板
```

## 常用创作流程

1. **事件画布**：`novel-discuss`（把分卷职责段拆成 `done` 事件卡；嫌太平可用 `booming` / `fuck-it`）
2. **写正文**：`novel-write`（读事件卡 → 强制反思 → 写正文）
3. **质检与去 AI 味**：`novel-polish`（4 个 Python 脚本自动检测 + 一致性校验 + 闸门）+ `fiction-humanizer-zh`（深度精修）
4. **标记返修**：`novel-revise`（在正文中用 `**加粗**`=扩写、`~~删除线~~`=简写、`*斜体*`=润色）
5. **同步与推送**：`novel-sync`（回写 `past.md`、伏笔表与知识图谱）→ `git commit && git push`
