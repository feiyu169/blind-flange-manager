# 盲板管理系统 - 实施计划（v2）

## 1. 目标与动机

**目标：** 开发一套工业管道法兰盲板管理系统，覆盖盲板信息记录、安装/拆卸/巡检流程管理、库存管理，面向大型工厂使用。

**动机：**
- 工厂盲板数量 > 1000 个，传统 Excel 管理效率低、易出错
- 需要扫码快速定位盲板信息，提升现场操作效率
- 需要流程审批和状态追踪，确保操作合规
- 需要库存预警，避免盲板短缺影响生产

**成功信号：**
- 管理员能通过仪表盘一屏掌握待审批、异常、预警等关键信息
- 操作员能扫码快速获取盲板信息并记录安装/拆卸
- 巡检员能按计划执行巡检，扫码拍照记录结果
- 库存不足时系统自动预警

## 2. 非目标（Non-Goals）

- 不集成现有 ERP/MES 系统（但预留接口）
- 不做复杂的报表分析（基础统计即可）
- 不做设备预测性维护
- 不做多语言支持（先做中文）
- 不做通知/消息推送（v2 再做）

## 3. 技术架构

### 3.1 技术栈

| 层级 | 技术选型 | 理由 |
|------|----------|------|
| 后端 | Python 3.11 + FastAPI | 高性能异步框架，适合 API 开发 |
| ORM | SQLAlchemy 2.0 | 成熟稳定，支持异步 |
| 数据库 | PostgreSQL 15 | 支持大数据量，JSON 支持好 |
| 缓存 | Redis 7 | 会话缓存、热点数据 |
| 前端 | Vue 3 + Element Plus | 组件丰富，企业级 UI |
| 移动端 | Vue 3 + Vant + Capacitor | 复用前端技术栈，原生扫码能力 |
| 部署 | Docker + Docker Compose | 环境一致性 |

### 3.2 项目结构

```
blind-flange-manager/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── v1/           # v1 版本
│   │   │   │   ├── blind_flange.py  # 盲板 CRUD
│   │   │   │   ├── workflow.py      # 流程管理
│   │   │   │   ├── inventory.py     # 库存管理
│   │   │   │   ├── user.py          # 用户管理
│   │   │   │   ├── scan.py          # 扫码接口
│   │   │   │   ├── dashboard.py     # 仪表盘
│   │   │   │   └── inspection_plan.py # 巡检计划
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # 业务逻辑
│   │   ├── core/              # 核心配置
│   │   └── utils/             # 工具函数
│   ├── alembic/               # 数据库迁移
│   ├── tests/                 # 测试
│   └── pyproject.toml
├── frontend/                  # Web 前端
│   ├── src/
│   │   ├── views/            # 页面
│   │   ├── components/       # 组件
│   │   ├── api/              # API 调用
│   │   ├── stores/           # 状态管理
│   │   └── router/           # 路由
│   └── package.json
├── mobile/                    # 移动端（Vue 3 + Vant + Capacitor）
│   ├── src/
│   │   ├── views/            # 页面
│   │   ├── components/       # 组件
│   │   ├── api/              # API 调用
│   │   └── router/           # 路由
│   └── package.json
├── docs/                      # 文档
│   ├── api/                  # API 文档
│   └── design/               # 设计文档
├── scripts/                   # 脚本
│   ├── init_db.py            # 初始化数据库
│   ├── seed_data.py          # 种子数据
│   └── backup.sh             # 数据库备份脚本
├── docker/                    # Docker 配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
└── README.md
```

### 3.3 数据库设计

#### 核心表

**blind_flanges（盲板表）**
```sql
CREATE TABLE blind_flanges (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,        -- 盲板编码（二维码内容）
    name VARCHAR(100) NOT NULL,              -- 盲板名称
    specification VARCHAR(100),              -- 规格型号
    material VARCHAR(50),                    -- 材质
    pressure_rating VARCHAR(20),             -- 压力等级
    size VARCHAR(20),                        -- 尺寸
    location VARCHAR(200),                   -- 安装位置
    pipeline_no VARCHAR(50),                 -- 管道编号
    flange_no VARCHAR(50),                   -- 法兰编号
    status VARCHAR(20) DEFAULT 'in_stock',   -- 状态：in_stock/installed/maintenance/scrapped
    image_url VARCHAR(500),                  -- 盲板图片 URL
    notes TEXT,                              -- 备注
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- 注意：qr_code_url 已移除，二维码改为按需生成
```

**blind_flange_status_logs（盲板状态变更日志表）**
```sql
CREATE TABLE blind_flange_status_logs (
    id BIGSERIAL PRIMARY KEY,
    blind_flange_id BIGINT REFERENCES blind_flanges(id),
    old_status VARCHAR(20),                  -- 旧状态
    new_status VARCHAR(20) NOT NULL,         -- 新状态
    operator_id BIGINT REFERENCES users(id),
    reason VARCHAR(200),                     -- 变更原因
    created_at TIMESTAMP DEFAULT NOW()
);
```

**inventory_records（库存记录表）**
```sql
CREATE TABLE inventory_records (
    id BIGSERIAL PRIMARY KEY,
    blind_flange_id BIGINT REFERENCES blind_flanges(id),
    type VARCHAR(20) NOT NULL,               -- 类型：in/out/adjust
    quantity INTEGER NOT NULL,               -- 数量
    reason VARCHAR(200),                     -- 原因
    operator_id BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**inventory_alerts（库存预警配置表）**
```sql
CREATE TABLE inventory_alerts (
    id BIGSERIAL PRIMARY KEY,
    blind_flange_type VARCHAR(100) NOT NULL, -- 盲板类型/规格
    min_stock INTEGER NOT NULL,              -- 最低库存阈值
    max_stock INTEGER,                       -- 最高库存阈值（可选）
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**workflows（流程表）**
```sql
CREATE TABLE workflows (
    id BIGSERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL,               -- 类型：install/uninstall/inspect
    blind_flange_id BIGINT REFERENCES blind_flanges(id),
    status VARCHAR(20) DEFAULT 'pending',    -- 状态：pending/approved/rejected/in_progress/completed/cancelled
    applicant_id BIGINT REFERENCES users(id),
    approver_id BIGINT REFERENCES users(id),
    applied_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    started_at TIMESTAMP,                    -- 开始执行时间
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,                  -- 取消时间
    cancel_reason VARCHAR(200),              -- 取消原因
    timeout_at TIMESTAMP,                    -- 超时时间
    notes TEXT
);
```

**workflow_logs（流程日志表）**
```sql
CREATE TABLE workflow_logs (
    id BIGSERIAL PRIMARY KEY,
    workflow_id BIGINT REFERENCES workflows(id),
    action VARCHAR(50) NOT NULL,             -- 动作：apply/approve/reject/start/complete/cancel/timeout
    operator_id BIGINT REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**users（用户表）**
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    real_name VARCHAR(50),
    role VARCHAR(20) NOT NULL,               -- 角色：admin/operator/inspector
    phone VARCHAR(20),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**inspection_plans（巡检计划表）**
```sql
CREATE TABLE inspection_plans (
    id BIGSERIAL PRIMARY KEY,
    blind_flange_id BIGINT REFERENCES blind_flanges(id),
    cycle_days INTEGER NOT NULL,             -- 巡检周期（天）
    last_inspected_at TIMESTAMP,             -- 上次巡检时间
    next_inspected_at TIMESTAMP,             -- 下次巡检时间
    assigned_to BIGINT REFERENCES users(id), -- 指定巡检人
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**inspection_records（巡检记录表）**
```sql
CREATE TABLE inspection_records (
    id BIGSERIAL PRIMARY KEY,
    blind_flange_id BIGINT REFERENCES blind_flanges(id),
    inspection_plan_id BIGINT REFERENCES inspection_plans(id),
    inspector_id BIGINT REFERENCES users(id),
    status VARCHAR(20) NOT NULL,             -- 状态：normal/abnormal
    images JSONB,                            -- 拍照图片列表
    notes TEXT,
    inspected_at TIMESTAMP DEFAULT NOW()
);
```

### 3.4 API 设计

#### 仪表盘 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/dashboard/overview | 获取概览数据（待审批、异常、预警等） |
| GET | /api/v1/dashboard/recent-activities | 获取最近操作记录 |

#### 盲板管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/blind-flanges | 创建盲板 |
| GET | /api/v1/blind-flanges | 获取盲板列表（分页、筛选） |
| GET | /api/v1/blind-flanges/{id} | 获取盲板详情 |
| PUT | /api/v1/blind-flanges/{id} | 更新盲板信息 |
| DELETE | /api/v1/blind-flanges/{id} | 删除盲板 |
| POST | /api/v1/blind-flanges/import | 批量导入 |
| GET | /api/v1/blind-flanges/export | 导出 |
| GET | /api/v1/blind-flanges/{id}/status-logs | 获取状态变更历史 |

#### 扫码 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/scan/{code} | 扫码获取盲板信息 |
| GET | /api/v1/scan/{code}/qrcode | 获取二维码图片（按需生成） |

#### 流程管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/workflows | 创建流程（安装/拆卸/巡检） |
| GET | /api/v1/workflows | 获取流程列表 |
| PUT | /api/v1/workflows/{id}/approve | 审批流程 |
| PUT | /api/v1/workflows/{id}/reject | 驳回流程 |
| PUT | /api/v1/workflows/{id}/start | 开始执行 |
| PUT | /api/v1/workflows/{id}/complete | 完成流程 |
| PUT | /api/v1/workflows/{id}/cancel | 取消流程 |

#### 库存管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/inventory | 获取库存列表 |
| POST | /api/v1/inventory/in | 入库 |
| POST | /api/v1/inventory/out | 出库 |
| GET | /api/v1/inventory/alerts | 库存预警 |
| PUT | /api/v1/inventory/alert-config | 配置预警阈值 |

#### 巡检计划 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/inspection-plans | 创建巡检计划 |
| GET | /api/v1/inspection-plans | 获取巡检计划列表 |
| PUT | /api/v1/inspection-plans/{id} | 更新巡检计划 |
| DELETE | /api/v1/inspection-plans/{id} | 删除巡检计划 |
| GET | /api/v1/inspection-plans/due | 获取待巡检列表 |

#### 巡检记录 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/inspections | 创建巡检记录 |
| GET | /api/v1/inspections | 获取巡检记录列表 |
| POST | /api/v1/inspections/upload | 上传巡检图片 |

#### 用户管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/users/login | 登录 |
| GET | /api/v1/users/me | 获取当前用户 |
| PUT | /api/v1/users/me | 更新个人信息 |
| GET | /api/v1/users | 获取用户列表（管理员） |
| POST | /api/v1/users | 创建用户（管理员） |

## 4. 实施切片（Implementation Slices）

> 切片顺序已调整为前后端配对，减少等待时间。

### Slice 1: 项目初始化与基础架构（4h）

**目标：** 搭建项目骨架，配置开发环境

**任务：**
1. 创建项目目录结构
2. 配置 pyproject.toml（后端依赖）
3. 配置 FastAPI 应用框架
4. 配置 SQLAlchemy + Alembic
5. 配置 Docker Compose（PostgreSQL + Redis）
6. 创建基础配置文件

**验收标准：**
- `docker compose up` 能启动数据库
- `uvicorn app.main:app` 能启动后端服务
- 访问 /docs 能看到 Swagger UI

**文件范围：**
- `backend/pyproject.toml`
- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/core/database.py`
- `docker/docker-compose.yml`
- `docker/Dockerfile.backend`

### Slice 2: 用户认证与权限（4h）

**目标：** 实现用户登录、JWT 认证、角色权限控制

**任务：**
1. 创建 User 模型
2. 实现密码哈希（bcrypt）
3. 实现 JWT 认证
4. 实现角色权限装饰器
5. 创建用户 CRUD API
6. 创建登录 API

**验收标准：**
- 能创建用户、登录获取 token
- 未认证请求返回 401
- 无权限请求返回 403
- 测试通过

**文件范围：**
- `backend/app/models/user.py`
- `backend/app/schemas/user.py`
- `backend/app/services/auth.py`
- `backend/app/api/v1/user.py`
- `backend/app/core/security.py`
- `backend/tests/test_user.py`

### Slice 3: 盲板信息管理 + Web 前端登录（6h）

**目标：** 实现盲板 CRUD、批量导入导出、二维码按需生成；同时搭建前端框架和登录页面

**后端任务：**
1. 创建 BlindFlange 模型 + 状态变更日志表
2. 实现盲板 CRUD API
3. 实现分页和筛选
4. 实现批量导入（Excel）
5. 实现导出（Excel）
6. 实现二维码按需生成 API

**前端任务：**
1. 创建 Vue 3 项目
2. 配置 Element Plus
3. 实现登录页面
4. 实现前端路由和状态管理

**验收标准：**
- 能创建、查询、更新、删除盲板
- 支持按状态、位置、编号筛选
- 能导入 Excel 批量创建
- 能导出 Excel
- 二维码按需生成（不存储图片）
- 盲板状态变更自动记录日志
- 前端能登录获取 token
- 测试通过

**文件范围：**
- `backend/app/models/blind_flange.py`
- `backend/app/schemas/blind_flange.py`
- `backend/app/services/blind_flange.py`
- `backend/app/api/v1/blind_flange.py`
- `backend/app/utils/qrcode.py`
- `backend/tests/test_blind_flange.py`
- `frontend/package.json`
- `frontend/src/main.js`
- `frontend/src/router/index.js`
- `frontend/src/stores/user.js`
- `frontend/src/views/Login.vue`

### Slice 4: 扫码功能 + 盲板管理前端（4h）

**目标：** 实现扫码查询；实现盲板列表、详情、编辑页面

**后端任务：**
1. 实现扫码 API（根据编码查询）
2. 返回盲板详情 + 最近操作记录 + 状态变更历史
3. 实现二维码图片生成 API（按需生成，不存储）

**前端任务：**
1. 实现盲板列表页面（分页、筛选）
2. 实现盲板详情页面（含状态变更历史）
3. 实现盲板编辑页面

**验收标准：**
- 扫码能获取盲板信息
- 返回最近 10 条操作记录
- 不存在的编码返回 404 + 提示
- 二维码图片按需生成
- 前端能查看盲板列表、详情、编辑
- 测试通过

**文件范围：**
- `backend/app/api/v1/scan.py`
- `backend/app/services/scan.py`
- `backend/tests/test_scan.py`
- `frontend/src/api/blindFlange.js`
- `frontend/src/views/blind-flange/List.vue`
- `frontend/src/views/blind-flange/Detail.vue`
- `frontend/src/views/blind-flange/Edit.vue`

### Slice 5: 流程管理 + 流程前端（8h）

**目标：** 实现安装/拆卸流程的创建、审批、执行、完成；实现流程管理前端

**后端任务：**
1. 创建 Workflow 和 WorkflowLog 模型
2. 实现流程创建 API
3. 实现审批/驳回 API
4. 实现开始执行 API
5. 实现完成 API
6. 实现取消 API
7. 实现流程状态变更日志
8. 实现流程超时检测（定时任务）

**前端任务：**
1. 实现流程列表页面
2. 实现流程审批页面
3. 实现流程详情页面

**验收标准：**
- 能创建安装/拆卸流程
- 管理员能审批/驳回
- 操作员能开始执行、完成流程
- 支持取消流程
- 状态变更自动记录日志
- 前端能查看流程列表、审批流程
- 测试通过

**流程状态机：**
```
pending → approved → in_progress → completed
    ↓         ↓           ↓
 rejected  cancelled   cancelled
```

**文件范围：**
- `backend/app/models/workflow.py`
- `backend/app/schemas/workflow.py`
- `backend/app/services/workflow.py`
- `backend/app/api/v1/workflow.py`
- `backend/tests/test_workflow.py`
- `frontend/src/api/workflow.js`
- `frontend/src/views/workflow/List.vue`
- `frontend/src/views/workflow/Approve.vue`
- `frontend/src/views/workflow/Detail.vue`

### Slice 6: 库存管理 + 库存前端（6h）

**目标：** 实现出入库、库存查询、库存预警；实现库存管理前端

**后端任务：**
1. 创建 InventoryRecord 和 InventoryAlert 模型
2. 实现出入库 API
3. 实现库存查询
4. 实现库存预警（按类型配置阈值）
5. 实现库存统计

**前端任务：**
1. 实现库存列表页面
2. 实现出入库操作页面
3. 实现库存预警页面
4. 实现预警阈值配置页面

**验收标准：**
- 能记录出入库
- 能查询当前库存
- 库存低于阈值时返回预警
- 支持按类型配置预警阈值
- 前端能查看库存、做出入库操作
- 测试通过

**文件范围：**
- `backend/app/models/inventory.py`
- `backend/app/schemas/inventory.py`
- `backend/app/services/inventory.py`
- `backend/app/api/v1/inventory.py`
- `backend/tests/test_inventory.py`
- `frontend/src/api/inventory.js`
- `frontend/src/views/inventory/List.vue`
- `frontend/src/views/inventory/Operation.vue`
- `frontend/src/views/inventory/AlertConfig.vue`

### Slice 7: 巡检计划与记录（6h）

**目标：** 实现巡检计划管理、巡检记录、拍照上传

**后端任务：**
1. 创建 InspectionPlan 和 InspectionRecord 模型
2. 实现巡检计划 CRUD API
3. 实现待巡检列表查询
4. 实现巡检记录 API
5. 实现图片上传（本地存储）
6. 实现巡检历史查询

**前端任务：**
1. 实现巡检计划管理页面
2. 实现待巡检列表页面
3. 实现巡检记录页面
4. 实现巡检历史页面

**验收标准：**
- 能创建、编辑、删除巡检计划
- 能查看待巡检列表
- 能记录巡检结果
- 能上传图片
- 能查看巡检历史
- 测试通过

**文件范围：**
- `backend/app/models/inspection.py`
- `backend/app/schemas/inspection.py`
- `backend/app/services/inspection.py`
- `backend/app/api/v1/inspection_plan.py`
- `backend/app/api/v1/inspection.py`
- `backend/app/utils/upload.py`
- `backend/tests/test_inspection.py`
- `frontend/src/api/inspection.js`
- `frontend/src/views/inspection/PlanList.vue`
- `frontend/src/views/inspection/DueList.vue`
- `frontend/src/views/inspection/Record.vue`
- `frontend/src/views/inspection/History.vue`

### Slice 8: 仪表盘 + 移动端基础（6h）

**目标：** 实现管理员仪表盘；搭建移动端框架，实现登录和扫码

**后端任务：**
1. 实现仪表盘概览 API（待审批、异常、预警统计）
2. 实现最近操作记录 API

**前端任务：**
1. 实现仪表盘页面

**移动端任务：**
1. 创建 Vue 3 + Vant 项目
2. 配置 Capacitor
3. 实现登录页面
4. 实现扫码功能
5. 实现盲板详情页面

**验收标准：**
- 仪表盘显示待审批、异常、预警等关键信息
- 移动端能登录
- 移动端能扫码获取盲板信息

**文件范围：**
- `backend/app/api/v1/dashboard.py`
- `backend/app/services/dashboard.py`
- `frontend/src/views/Dashboard.vue`
- `mobile/package.json`
- `mobile/src/views/Login.vue`
- `mobile/src/views/Scan.vue`
- `mobile/src/views/blind-flange/Detail.vue`

### Slice 9: 移动端流程与巡检（6h）

**目标：** 实现移动端的流程操作和巡检功能

**移动端任务：**
1. 实现安装/拆卸申请
2. 实现巡检记录（拍照上传）
3. 实现流程历史查看
4. 实现待巡检列表

**验收标准：**
- 能申请安装/拆卸
- 能记录巡检（拍照上传）
- 能查看流程历史
- 能查看待巡检列表

**文件范围：**
- `mobile/src/views/workflow/Apply.vue`
- `mobile/src/views/workflow/History.vue`
- `mobile/src/views/inspection/Record.vue`
- `mobile/src/views/inspection/DueList.vue`

### Slice 10: 测试与部署（6h）

**目标：** 完善测试，配置部署，编写文档

**任务：**
1. 补充单元测试（覆盖率 > 70%）
2. 编写 API 文档
3. 配置 Docker 部署
4. 编写数据库备份脚本
5. 编写 README

**验收标准：**
- 测试覆盖率 > 70%
- API 文档完整
- Docker 部署成功
- 数据库备份脚本可用
- README 清晰

**文件范围：**
- `backend/tests/`
- `docs/api/`
- `docker/`
- `scripts/backup.sh`
- `README.md`

## 5. 测试计划

### 5.1 单元测试

每个 Slice 都包含对应的测试文件，使用 pytest。

**测试框架：** pytest + pytest-asyncio
**测试数据库：** 使用 testing.postgresql 管理测试数据库（独立于开发数据库）
**覆盖率目标：** > 70%

### 5.2 集成测试

- API 接口测试（httpx + TestClient）
- 数据库集成测试（testing.postgresql）
- 扫码功能集成测试（mock 扫码输入）

### 5.3 性能测试

- > 1000 条盲板数据的查询性能
- 批量导入性能
- 并发请求性能

### 5.4 E2E 测试

- 登录流程
- 盲板 CRUD 流程
- 扫码流程
- 审批流程
- 巡检流程

### 5.5 Mock 策略

- 第三方扫码：mock 扫码输入
- 图片上传：使用临时目录
- 邮件/通知：mock 发送

## 6. 风险与开放问题

### 6.1 已识别风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 移动端扫码兼容性 | 中 | 使用 Capacitor 原生扫码插件 |
| 大数据量性能 | 中 | 数据库索引 + 分页 + 缓存 |
| 图片存储成本 | 低 | 先用本地存储，后续迁移到 OSS |
| 权限粒度不足 | 低 | 预留扩展点 |
| 数据丢失 | 高 | 定期数据库备份（pg_dump） |

### 6.2 Blocking Open Questions

无（需求已明确）

### 6.3 Non-Blocking Questions

| 问题 | 工作假设 | 风险 |
|------|----------|------|
| 库存预警阈值如何配置？ | 管理员在系统中按类型配置 | 低 |
| 二维码用什么格式？ | JSON 格式，包含盲板编码 | 低 |
| 图片存储用什么？ | 先用本地存储 | 低 |
| 巡检超时如何处理？ | 定时任务检测，标记为超时 | 低 |

## 7. 数据备份策略

### 7.1 备份方式

- 使用 pg_dump 进行全量备份
- 每日凌晨 2:00 自动执行
- 保留最近 30 天的备份

### 7.2 备份脚本

```bash
#!/bin/bash
# scripts/backup.sh
BACKUP_DIR="/var/backups/blind-flange-manager"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U postgres blind_flange_manager > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
# 清理 30 天前的备份
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

### 7.3 恢复流程

```bash
psql -U postgres blind_flange_manager < backup_XXXXXXXX.sql
```

## 8. Controller 状态

**Work Unit:** 盲板管理系统
**Goal:** 开发完整的盲板管理系统
**Non-Goals:** 系统集成、报表分析、多语言、通知推送
**Current Gate:** plan (approved)
**Branch:** feat/blind-flange-manager
**Baseline:** main (empty)
**Plan Version:** v2（已修复 reviewer 提出的问题）

## 9. 完成报告格式

```markdown
## 实施完成报告

**Work Unit:** 盲板管理系统
**Branch:** feat/blind-flange-manager
**Commits:** [列表]

### 完成的 Slices
- [x] Slice 1: 项目初始化
- [x] Slice 2: 用户认证
...

### 测试结果
- 单元测试: X passed, Y failed
- 覆盖率: Z%

### 残留风险
- [风险描述] — [分类] — [处理方式]

### 准备就绪
- [ ] 所有测试通过
- [ ] 文档完整
- [ ] 无 blocking open questions
```
