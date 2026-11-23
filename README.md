# 《逃到大陆尽头她们还是追上来了》— AI 轻小说创作工作区

本分支（`taodao-dalu-jintou`）是完全独立的新书工作区，已内置全套本地工作区级写作 Skills（位于 `.agents/skills/`），**换电脑拉取后即可直接接着创作，无需重新配置全局环境**。

---

## 换电脑 30 秒续写指南

### 1. 拉取本分支
```bash
git clone -b taodao-dalu-jintou --single-branch https://github.com/1479310832/-.git yuling-novel
cd yuling-novel
```

### 2. 安装唯一 Python 依赖（用于知识图谱与质检脚本）
确保本机已安装 Python 3.10+，然后执行：
```bash
pip install -r requirements.txt
```
*(若为 macOS / Linux，按环境使用 `python3` / `pip3` 即可。)*

### 3. 在 Antigravity 打开该目录
用 Antigravity 打开克隆下来的目录：
- 根目录下 `.agents/skills/` 中的 **15 个写作 Skill 会自动发现并仅在本工作区生效**；
- 根目录 `AGENTS.md` 与 `逃到大陆尽头她们还是追上来了/AGENTS.md` 会自动加载《小说宪法》与当前进度；
- 直接在对话里说：**「同步第 X 章」**、**「继续写下一章」** 或 **「讨论下一段事件」** 即可无缝续写。

---

## 目录说明

```text
.
├── AGENTS.md                                 # 工作区入口指路规则
├── requirements.txt                          # Python 脚本唯一依赖（PyYAML）
├── .agents/skills/                           # 15 个工作区专属小说创作 Skills（vibe-noveling + fiction-humanizer-zh）
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
