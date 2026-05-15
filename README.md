# 盲板管理系统 (Blind Flange Manager)

工业管道法兰盲板管理系统，覆盖盲板信息记录、安装/拆卸/巡检流程管理、库存管理。

## 功能特性

- **盲板信息管理** - 记录盲板位置、规格、状态、历史记录
- **流程管理** - 安装、拆卸、巡检流程，支持审批和状态追踪
- **库存管理** - 出入库、盘点、预警
- **扫码功能** - 扫描盲板二维码，快速定位盲板信息
- **拍照上传** - 现场拍照记录盲板状态
- **仪表盘** - 一屏掌握待审批、异常、预警等关键信息
- **巡检计划** - 计划驱动的巡检管理

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| 后端 | Python 3.11 + FastAPI + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 前端 | Vue 3 + Element Plus |
| 移动端 | Vue 3 + Vant + Capacitor |
| 部署 | Docker + Docker Compose |

## 快速开始

### 环境要求

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+ (前端开发)

### 启动后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"

# 启动数据库
cd ../docker
docker compose up -d postgres redis

# 运行数据库迁移
cd ../backend
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

### 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 查看前端页面。

## 项目结构

```
blind-flange-manager/
├── backend/                    # 后端服务
├── frontend/                  # Web 前端
├── mobile/                    # 移动端
├── docs/                      # 文档
├── scripts/                   # 脚本
├── docker/                    # Docker 配置
└── README.md
```

## 文档

- [实施计划](docs/plan.md)
- [API 文档](docs/api/) (待生成)

## 开发流程

本项目使用 Gateflow 工作流管理：

1. **Plan** - 实施计划已通过审查
2. **Implementation** - 按 Slice 实施
3. **Code Review** - 代码审查
4. **Deepreview** - 深度审查
5. **Ready-to-Create-PR** - 准备 PR

## 许可证

MIT License
