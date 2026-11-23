---
name: novel-knowledge
description: 小说知识图谱数据访问层：实体搜索、关系查询、标签查询、索引重建。供其他小说 skill 或子代理在检索世界观/角色/物品/势力设定与重建索引时调用。
---
# 知识图谱工具

供其他 skill 调用，负责数据访问，不包含高层语义判断。

## 命令

```bash
python .agents/skills/novel-knowledge/scripts/knowledge_graph.py <command> [args]
```

### search — 搜索设定

```bash
python .agents/skills/novel-knowledge/scripts/knowledge_graph.py search <query> [-t type] [-l limit] [-j]
```

### update — 创建实体文件

```bash
python .agents/skills/novel-knowledge/scripts/knowledge_graph.py update <type> <name> [-j]
```

创建空模板文件，不覆盖已有文件。编辑完成后需运行 `rebuild`。

### relations — 查询实体关系

```bash
python .agents/skills/novel-knowledge/scripts/knowledge_graph.py relations <entity_id>
```

返回出向和入向关系。

### tags — 按标签查询

```bash
python .agents/skills/novel-knowledge/scripts/knowledge_graph.py tags <tag>
```

### rebuild — 重建知识图谱（核心命令）

```bash
python .agents/skills/novel-knowledge/scripts/knowledge_graph.py rebuild
```

扫描 `memory/entities/` 下所有 md 文件的 YAML frontmatter，重新生成 `_graph.json` 和 `_index.json`。

运行时机：创建新实体文件后、编辑实体 frontmatter 后、批量修改后、novel-sync 完成后。

## 实体文件格式

每个实体文件的 YAML frontmatter：

```yaml
---
id: <唯一标识符，中文>
name: <显示名称>
type: <character/location/item/faction/concept>
tags: [标签1, 标签2]
relations:
  - target: <目标实体id>
    relation: <关系类型>
    description: <关系描述>
---
```

关系是双向的：A → B 的关系会自动生成 B → A 的入向关系。

## 推荐工作流

1. 直接编辑 `memory/entities/<type>/<name>.md`
2. 运行 `rebuild` 同步知识图谱

不要手动编辑 `_graph.json` 或 `_index.json`。

## 依赖

零第三方依赖（优先使用 PyYAML；若新环境未安装 PyYAML，自动启用内置纯标准库 YAML 解析，开箱即用）。
