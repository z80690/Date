---
name: "skill-writer"
description: 当新建、修改、评审码道技能（SKILL.md）时触发，基于官方最佳实践提供写法标准与合规核对；不适用于规则(.mdc)初始化。
---
目标：基于官方最佳实践指导当前项目技能编写与合规。
核心原则：必须 name与目录一致；description含“当…时触发”且≤1024字；YAML必备；三层渐进加载。禁止描述仅写功能、指令冗长、滥用脚本。
操作：1.查 docs/官方最佳实践-如何写好一个Skill-bp0010.md；2.核对 name、描述触发条件、frontmatter、目录结构；3.输出合规清单与修改建议，单条不超8行。
参考：docs/官方最佳实践-如何写好一个Skill-bp0010.md（必），docs/官方文档-码道热门Skills清单-desktop0003.md（选）。