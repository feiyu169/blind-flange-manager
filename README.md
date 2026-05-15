# 盲板管理系统 (Blind Flange Manager)

工业管道法兰盲板管理系统，覆盖盲板信息记录、安装/拆卸/巡检流程管理、库存管理。

## 功能特性

### 核心功能
- **盲板信息管理** - 记录盲板位置、规格、状态、历史记录
- **流程管理** - 安装、拆卸、巡检流程，支持审批和状态追踪
- **库存管理** - 出入库、盘点、预警
- **巡检计划** - 计划驱动的巡检管理
- **仪表盘** - 一屏掌握待审批、异常、预警等关键信息

### 辅助功能
- **扫码功能** - 扫描盲板二维码，快速定位盲板信息
- **拍照上传** - 现场拍照记录盲板状态
- **数据导入导出** - Excel 批量导入导出
- **用户权限** - 多角色权限控制（管理员/操作员/巡检员）

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| 后端 | Python 3.11 + FastAPI + SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| 认证 | JWT + bcrypt |
| 前端 | Vue 3 + Element Plus（待实现） |
| 移动端 | Vue 3 + Vant + Capacitor（待实现） |
| 部署 | Docker + Docker Compose |

## 快速开始

### 环境要求

- Python 3.11+
- Docker & Docker Compose
- Node.js 18+（前端开发）

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

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY

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

### 运行测试

```bash
cd backend
python -m pytest tests/ -v
```

## 项目结构

```
blind-flange-manager/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API 路由
│   │   │   ├── user.py      # 用户管理
│   │   │   ├── blind_flange.py  # 盲板管理
│   │   │   ├── scan.py      # 扫码功能
│   │   │   ├── workflow.py  # 流程管理
│   │   │   ├── inventory.py # 库存管理
│   │   │   ├── inspection.py # 巡检管理
│   │   │   └── dashboard.py # 仪表盘
│   │   ├── core/            # 配置、数据库、安全
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具函数
│   ├── tests/               # 测试
│   └── pyproject.toml
├── frontend/                # Web 前端（待实现）
├── mobile/                  # 移动端（待实现）
├── docs/
│   └── plan.md              # 实施计划
├── docker/
│   └── docker-compose.yml
└── README.md
```

## API 文档

### 用户管理
- `POST /api/v1/users/login` - 用户登录
- `GET /api/v1/users/me` - 获取当前用户
- `POST /api/v1/users` - 创建用户（管理员）
- `GET /api/v1/users` - 获取用户列表（管理员）

### 盲板管理
- `POST /api/v1/blind-flanges` - 创建盲板
- `GET /api/v1/blind-flanges` - 获取盲板列表
- `GET /api/v1/blind-flanges/{id}` - 获取盲板详情
- `PUT /api/v1/blind-flanges/{id}` - 更新盲板
- `DELETE /api/v1/blind-flanges/{id}` - 删除盲板
- `POST /api/v1/blind-flanges/import` - 批量导入
- `GET /api/v1/blind-flanges/export` - 导出

### 扫码功能
- `GET /api/v1/scan/{code}` - 扫码获取盲板信息
- `GET /api/v1/scan/{code}/qrcode` - 获取二维码

### 流程管理
- `POST /api/v1/workflows` - 创建流程
- `GET /api/v1/workflows` - 获取流程列表
- `PUT /api/v1/workflows/{id}/approve` - 审批流程
- `PUT /api/v1/workflows/{id}/start` - 开始执行
- `PUT /api/v1/workflows/{id}/complete` - 完成流程
- `PUT /api/v1/workflows/{id}/cancel` - 取消流程

### 库存管理
- `POST /api/v1/inventory` - 创建库存记录
- `GET /api/v1/inventory` - 获取库存记录
- `GET /api/v1/inventory/summary` - 库存汇总
- `GET /api/v1/inventory/alerts` - 库存预警

### 巡检管理
- `POST /api/v1/inspections/plans` - 创建巡检计划
- `GET /api/v1/inspections/plans` - 获取巡检计划
- `GET /api/v1/inspections/plans/due/list` - 待巡检列表
- `POST /api/v1/inspections/records` - 创建巡检记录
- `GET /api/v1/inspections/records` - 获取巡检记录

### 仪表盘
- `GET /api/v1/dashboard/overview` - 仪表盘概览
- `GET /api/v1/dashboard/recent-activities` - 最近操作

## 测试覆盖

- 单元测试：57 个测试全部通过
- 覆盖模块：用户、盲板、流程、库存、巡检、仪表盘

## 安全特性

- JWT 认证 + 过期验证
- bcrypt 密码哈希
- 角色权限控制
- SECRET_KEY 环境变量
- CORS 配置

## 开发流程

本项目使用 Gateflow 工作流管理：

1. **Plan** - 实施计划已通过审查
2. **Implementation** - 按 Slice 实施（7 个切片）
3. **Code Review** - 代码审查（发现并修复安全漏洞）
4. **Deepreview** - 深度审查（架构、安全、性能评估）
5. **Ready-to-Create-PR** - 准备 PR

## 残留风险

| 风险 | 分类 | 处理方式 |
|------|------|----------|
| 前端未实现 | assigned to later slice | 后续迭代 |
| 移动端未实现 | assigned to later slice | 后续迭代 |
| 通知模块未实现 | deferred to v2 | 后续迭代 |
| N+1 性能问题 | assigned to optimization | 后续优化 |
| 令牌吊销机制 | deferred | 后续实现 |

## 许可证

MIT License
