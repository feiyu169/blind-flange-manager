# 盲板管理系统 (Blind Flange Manager)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4+-brightgreen.svg)](https://vuejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 工业管道法兰盲板管理系统 - 采用 Gateflow 工作流模式开发

## 项目概述

一套面向大型工厂（>1000 个盲板）的工业管道法兰盲板管理系统，覆盖盲板信息记录、安装/拆卸/巡检流程管理、库存管理。

### 开发模式

本项目采用 **Gateflow 工作流模式**（源自 code-is-cheap 项目），通过严格的 gate-based 推进机制确保代码质量：

- 需求澄清 → 计划制定 → 计划审查 → 切片实施 → 代码审查 → 深度审查 → 优化迭代
- 每个阶段都有明确的门禁标准和验收条件
- 第三方审查评分：6.8/10（中等偏上）

---

## 已知限制

### 速率限制

- **当前实现**：基于内存（`collections.defaultdict`）
- **限制**：仅适用于单实例部署，多实例部署时速率限制不共享
- **重启丢失**：服务器重启后速率限制计数器清零
- **生产建议**：多实例部署需要集成 Redis 实现持久化速率限制

### 数据库

- **开发环境**：使用 SQLite，与生产环境 PostgreSQL 存在行为差异
- **测试覆盖**：单元测试在 SQLite 上运行，未在 PostgreSQL 上验证
- **生产建议**：上线前必须在 PostgreSQL 环境测试

### 令牌管理

- **密码修改**：修改密码后旧令牌立即失效（基于 `password_changed_at` 字段）
- **令牌吊销**：支持黑名单机制，但高频检查时增加数据库压力
- **生产建议**：考虑将黑名单迁移到 Redis

### 中间件

- **实现方式**：使用 `BaseHTTPMiddleware`
- **限制**：不支持流式响应和 WebSocket
- **适用场景**：当前仅用于速率限制，不影响核心功能

---

## 功能模块

### ✅ 已完成（后端 API）

| 模块 | 功能 | 状态 | 测试 |
|------|------|------|------|
| 用户管理 | JWT 认证、角色权限、CRUD | ✅ 完成 | 15 passed |
| 盲板管理 | CRUD、状态追踪、批量导入导出 | ✅ 完成 | 12 passed |
| 流程管理 | 安装/拆卸/巡检、状态机、审批 | ✅ 完成 | 12 passed |
| 库存管理 | 出入库、预警、聚合查询 | ✅ 完成 | 8 passed |
| 巡检管理 | 计划、记录、逾期检测 | ✅ 完成 | 8 passed |
| 仪表盘 | 统计概览、最近操作 | ✅ 完成 | 2 passed |
| 扫码功能 | 扫码查询、二维码生成、扫码日志 | ✅ 完成 | 5 passed |

**测试总计：62 passed, 0 failed**

### ⚠️ 进行中（前端页面）

| 页面 | 功能 | 状态 | 待审核 |
|------|------|------|--------|
| 登录页面 | 用户登录、路由守卫 | ✅ 完成 | ⏳ 待审核 |
| 仪表盘 | 统计卡片、状态分布 | ✅ 完成 | ⏳ 待审核 |
| 盲板列表 | 搜索、分页、CRUD | ✅ 完成 | ⏳ 待审核 |
| 盲板详情 | 基本信息、状态日志 | ✅ 完成 | ⏳ 待审核 |
| 流程管理 | 列表、审批、执行 | ✅ 完成 | ⏳ 待审核 |
| 库存管理 | 列表、出入库、预警 | ✅ 完成 | ⏳ 待审核 |
| 巡检管理 | 计划、待巡检、记录 | ✅ 完成 | ⏳ 待审核 |

### 📋 待实现

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 移动端（Vant + Capacitor） | P2 | 扫码、拍照、现场操作 |
| 文件上传 | P2 | 巡检拍照上传 |
| 通知模块 | P2 | 系统内通知 + Webhook |
| PostgreSQL 验证 | P1 | 生产环境数据库测试 |
| Redis 集成 | P2 | 速率限制持久化、缓存 |

---

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 主语言 |
| FastAPI | 0.104+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM（异步） |
| PostgreSQL | 15 | 生产数据库 |
| SQLite | - | 开发/测试数据库 |
| Redis | 7 | 缓存（待集成） |
| Alembic | 1.13+ | 数据库迁移 |
| JWT | - | 认证 |
| bcrypt | - | 密码哈希 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue.js | 3.4+ | 前端框架 |
| Vite | 5.0+ | 构建工具 |
| Element Plus | 2.4+ | UI 组件库 |
| Pinia | 2.1+ | 状态管理 |
| Vue Router | 4.2+ | 路由 |
| Axios | 1.6+ | HTTP 客户端 |

### 开发工具

| 工具 | 用途 |
|------|------|
| pytest | 单元测试 |
| ruff | 代码检查 |
| mypy | 类型检查 |
| Alembic | 数据库迁移 |
| Docker | 容器化部署 |

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 15（生产环境）
- Redis 7（可选）

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY

# 初始化数据库（开发环境）
python scripts/init_db.py

# 或使用 Alembic 迁移（生产环境）
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000 查看前端页面。

### 初始化管理员

```bash
# 创建管理员用户
curl -X POST http://localhost:8000/api/v1/users/init-admin \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","real_name":"管理员"}'
```

---

## 项目结构

```
blind-flange-manager/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/v1/           # API 路由
│   │   │   ├── user.py       # 用户管理
│   │   │   ├── blind_flange.py  # 盲板管理
│   │   │   ├── scan.py       # 扫码功能
│   │   │   ├── workflow.py   # 流程管理
│   │   │   ├── inventory.py  # 库存管理
│   │   │   ├── inspection.py # 巡检管理
│   │   │   └── dashboard.py  # 仪表盘
│   │   ├── core/             # 配置、数据库、安全
│   │   ├── models/           # 数据模型（10个）
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # 业务逻辑
│   │   └── utils/            # 工具函数
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试（57个）
│   ├── scripts/              # 脚本
│   └── pyproject.toml
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── views/            # 页面（7个）
│   │   ├── components/       # 组件
│   │   ├── api/              # API 调用
│   │   ├── stores/           # 状态管理
│   │   └── router/           # 路由
│   └── package.json
├── docs/
│   ├── plan.md               # 实施计划
│   └── REVIEW_REPORT.md      # 第三方审查报告
├── docker/
│   └── docker-compose.yml
├── .env.example               # 环境变量模板
├── .gitignore
├── PR_DESCRIPTION.md
└── README.md
```

---

## 安全特性

- ✅ JWT 认证 + 过期验证
- ✅ bcrypt 密码哈希
- ✅ 角色权限控制（admin/operator/inspector）
- ✅ SECRET_KEY 环境变量
- ✅ 令牌吊销机制（TokenBlacklist）
- ✅ 速率限制（登录接口 5次/分钟）
- ✅ 数据库外键约束（15个）
- ✅ CORS 配置
- ✅ .env 文件不提交到仓库

---

## 测试

```bash
# 运行所有测试
cd backend && python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_user.py -v

# 查看测试覆盖率
python -m pytest tests/ --cov=app --cov-report=html
```

---

## 部署

### Docker 部署

```bash
# 启动服务
cd docker
docker compose up -d

# 查看日志
docker compose logs -f
```

### 生产环境

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env，设置：
# - DATABASE_URL (PostgreSQL)
# - SECRET_KEY (随机密钥)
# - DEBUG=false

# 运行数据库迁移
cd backend
alembic upgrade head

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API 文档

启动后端服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要 API

| 模块 | 端点 | 说明 |
|------|------|------|
| 用户 | POST /api/v1/users/login | 用户登录 |
| 用户 | POST /api/v1/users/init-admin | 初始化管理员 |
| 盲板 | GET /api/v1/blind-flanges | 获取盲板列表 |
| 盲板 | POST /api/v1/blind-flanges/import | 批量导入 |
| 流程 | POST /api/v1/workflows | 创建流程 |
| 流程 | PUT /api/v1/workflows/{id}/approve | 审批流程 |
| 库存 | GET /api/v1/inventory/summary | 库存汇总 |
| 巡检 | GET /api/v1/inspections/plans/due/list | 待巡检列表 |
| 仪表盘 | GET /api/v1/dashboard/overview | 概览统计 |

---

## 开发流程

本项目采用 **Gateflow 工作流模式**：

```
需求澄清 → 计划制定 → 计划审查 → 切片实施 → 代码审查 → 深度审查 → 优化迭代
```

### 架构决策记录 (ADR)

关键架构决策已记录在 [docs/adr/](docs/adr/) 目录：

- [ADR-001](docs/adr/001-choose-fastapi.md): 选择 FastAPI 作为 Web 框架
- [ADR-002](docs/adr/002-use-sqlite-for-dev.md): 开发环境使用 SQLite
- [ADR-003](docs/adr/003-use-jwt-auth.md): 选择 JWT 作为认证方案
- [ADR-004](docs/adr/004-use-gateflow-workflow.md): 选择 Gateflow 工作流模式

### 已完成的 Gate

1. ✅ 需求澄清（3轮）
2. ✅ 计划制定（12个切片）
3. ✅ 计划审查（11个问题，修复9个）
4. ✅ 切片实施（7个切片）
5. ✅ 代码审查（8个安全问题，全部修复）
6. ✅ 深度审查（架构8/10，安全5/10）
7. ✅ 优化迭代（4轮优化）
8. ✅ 前端开发（7个页面）
9. ✅ P0 问题修复
10. ✅ 推送到 GitHub

---

## 审查报告

第三方审查评分：**6.8/10**（中等偏上）

| 维度 | 评分 | 评级 |
|------|------|------|
| 任务完成度 | 7.5/10 | 良好 |
| 流程遵循度 | 8.0/10 | 良好 |
| 代码质量 | 6.5/10 | 一般 |
| 架构设计 | 6.5/10 | 一般 |
| 安全性 | 5.5/10 | 偏差 |
| 测试覆盖 | 7.0/10 | 良好 |

详见 [REVIEW_REPORT.md](docs/REVIEW_REPORT.md)

---

## 待审核内容

⚠️ **以下内容等待用户审核：**

### 前端页面

- [ ] 登录页面功能
- [ ] 仪表盘数据显示
- [ ] 盲板列表 CRUD
- [ ] 盲板详情展示
- [ ] 流程管理操作
- [ ] 库存管理功能
- [ ] 巡检管理流程

### 后端 API

- [ ] 用户认证流程
- [ ] 盲板导入导出
- [ ] 流程状态机
- [ ] 库存预警逻辑
- [ ] 巡检计划功能

---

## 后续计划

### P1 - 强烈建议

- [ ] PostgreSQL 环境验证
- [ ] 速率限制中间件重构
- [ ] 令牌管理增强

### P2 - 建议改进

- [ ] 移动端开发（Vant + Capacitor）
- [ ] 文件上传功能
- [ ] 通知模块
- [ ] Redis 集成
- [ ] CI/CD 配置

---

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'feat: add xxx'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

---

## 许可证

MIT License

---

## 联系方式

- GitHub: [feiyu169](https://github.com/feiyu169)
- 仓库: [blind-flange-manager](https://github.com/feiyu169/blind-flange-manager)
