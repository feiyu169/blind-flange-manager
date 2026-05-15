# 架构决策记录 (ADR)

本目录记录项目中的关键架构决策。

## ADR 列表

| ADR | 标题 | 状态 | 日期 |
|-----|------|------|------|
| [ADR-001](001-choose-fastapi.md) | 选择 FastAPI 作为 Web 框架 | 接受 | 2026-05-15 |
| [ADR-002](002-use-sqlite-for-dev.md) | 开发环境使用 SQLite | 接受 | 2026-05-15 |
| [ADR-003](003-use-jwt-auth.md) | 选择 JWT 作为认证方案 | 接受 | 2026-05-15 |
| [ADR-004](004-use-gateflow-workflow.md) | 选择 Gateflow 工作流模式 | 接受 | 2026-05-15 |

## ADR 模板

```markdown
# ADR-XXX: 标题

## 状态
接受/废弃/替代

## 背景
为什么需要做这个决策？

## 决策
我们做了什么决策？

## 理由
为什么做出这个决策？

## 后果
这个决策有什么影响？
```

## 相关文档

- [实施计划](../plan.md)
- [审查报告](../REVIEW_REPORT.md)
- [README](../../README.md)
