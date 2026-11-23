# 实体文件格式规范

`memory/entities/` 按类别分为 5 个子目录：`characters/`、`locations/`、`factions/`、`items/`、`concepts/`。

每个实体 `.md` 文件顶部必须包含以下 YAML frontmatter，修改后运行 `python ../.agents/skills/novel-knowledge/scripts/knowledge_graph.py rebuild` 重建知识图谱：

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
