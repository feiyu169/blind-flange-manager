# ADR-001: 选择 FastAPI 作为 Web 框架

## 状态

接受

## 背景

项目需要选择一个 Python Web 框架来构建后端 API。主要候选方案：
- FastAPI
- Django REST Framework
- Flask

项目需求：
1. 高性能异步支持
2. 自动 API 文档生成
3. 类型注解支持
4. 学习曲线适中
5. 社区活跃度

## 决策

选择 **FastAPI** 作为 Web 框架。

## 理由

### 优势

1. **原生异步支持**
   - FastAPI 基于 Starlette，原生支持 async/await
   - 对于 IO 密集型操作（数据库查询、API 调用）性能优异
   - 适合处理并发请求

2. **自动 API 文档**
   - 自动生成 Swagger UI 和 ReDoc 文档
   - 基于 Pydantic 模型自动生成请求/响应文档
   - 减少文档维护成本

3. **类型注解支持**
   - 使用 Python 类型注解定义请求/响应模型
   - Pydantic 自动验证请求数据
   - IDE 支持更好（自动补全、类型检查）

4. **学习曲线**
   - 对于熟悉 Python 的开发者，学习曲线较低
   - 文档清晰，示例丰富
   - 与 Flask 类似的路由风格

5. **社区活跃**
   - GitHub stars: 70k+
   - 活跃的社区和丰富的插件
   - 定期更新和维护

### 劣势

1. **生态相对年轻**
   - 相比 Django，插件生态较少
   - 某些功能需要自己实现

2. **ORM 需要单独选择**
   - 不像 Django 自带 ORM
   - 需要选择 SQLAlchemy 或其他 ORM

## 后果

### 正面影响

- 开发效率高（自动文档、类型检查）
- 性能好（异步支持）
- 代码质量高（类型注解）

### 负面影响

- 需要学习 SQLAlchemy（ORM）
- 某些功能需要自己实现（如管理后台）

## 相关决策

- [[ADR-002]]: 为什么开发环境使用 SQLite
- [[ADR-003]]: 为什么选择 JWT 而不是 Session
