# 模板参考文档

## 模板文件位置

所有模板位于：`scripts/` 目录（相对于技能根目录）

## 模板列表

| 文件名 | 类型 | 适用场景 |
|--------|------|----------|
| `decision-report.lark.md` | 决策汇报型 | 高层汇报、决策申请 |
| `product-solution.lark.md` | 产品方案型 | 产品方案、BRD |
| `project-progress.lark.md` | 项目推进型 | 项目周会、进展同步 |
| `governance-improvement.lark.md` | 治理专项型 | 体验优化、跨团队治理 |
| `holiday-support.lark.md` | 大促保障型 | 节假日、大促保障 |
| `product-tool.lark.md` | 产品工具型 | 工具建设、系统迭代 |
| `project-management.lark.md` | 项目管理型 | 长周期、能力建设 |
| `team-intro.lark.md` | 团队说明型 | 团队介绍、协作地图 |
| `personal-review.lark.md` | 个人述职型 | 个人述职、阶段性总结、绩效回顾 |

## 各模板结构

### 1. 决策汇报型 (decision-report)

```
结论（必须）
↓
方案对比（核心）
↓
推荐方案（强化）
↓
收益（量化）
↓
风险（必须）
```

**必须包含**：方案A/B对比 + 推荐理由（3条以内）

---

### 2. 产品方案型 (product-solution)

```
背景（Why）
↓
方案（What）
↓
用户价值（Value）
↓
实现方式（How）
```

**必须包含**：用户视角

---

### 3. 项目推进型 (project-progress)

```
当前状态（Status）
↓
关键进展（Progress）
↓
问题/风险（Risk）
↓
下一步（Next）
```

**必须包含**：时间节点 + Owner

---

### 4. 治理专项型 (governance-improvement)

```
问题拆解（Problem）
↓
根因分析（Root Cause）
↓
治理方案（Solution）
↓
长期机制（Mechanism）
```

**必须包含**：根因 + 长期策略

---

### 5. 大促保障型 (holiday-support)

```
目标（Goal）
↓
保障策略（Plan）
↓
关键指标（Metrics）
↓
应急预案（Emergency）
```

**必须包含**：风险预案 + 监控指标

---

### 6. 产品工具型 (product-tool)

```
问题（Pain）
↓
工具方案（Tool）
↓
使用方式（Usage）
↓
收益（Efficiency）
```

---

### 7. 项目管理型 (project-management)

```
愿景（Vision）
↓
路径（Roadmap）
↓
阶段目标（Milestone）
↓
资源（Resource）
```

---

### 8. 团队说明型 (team-intro)

```
我们是谁（Who）
↓
做什么（What）
↓
怎么找（How）
↓
合作方式（Collaboration）
```

---

### 9. 个人述职型 (personal-review)

```
核心成果（What I delivered）
↓
能力成长（How I grew）
↓
反思与不足（What I learned）
↓
下阶段规划（Where I'm going）
```

**必须包含**：量化指标达成率 + 坦诚的反思 + 下阶段目标

---

## 模板变量

模板中使用 `{{title}}` 作为标题占位符，生成时会自动替换。

## 模板选择建议

| 用户场景 | 推荐模板 |
|----------|----------|
| 需要高层决策 | decision-report |
| 产品方案对齐 | product-solution |
| 项目进度汇报 | project-progress |
| 长期问题治理 | governance-improvement |
| 节假日保障 | holiday-support |
| 工具系统建设 | product-tool |
| 长期能力建设 | project-management |
| 团队介绍 | team-intro |
| 个人述职/绩效回顾 | personal-review |
