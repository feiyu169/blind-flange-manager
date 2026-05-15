# 盲板管理系统 - 后端服务

工业管道法兰盲板管理系统后端 API 服务。

## 技术栈

- Python 3.11
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL 15
- Redis 7

## 开发

```bash
# 安装依赖
pip install -e ".[dev]"

# 启动服务
uvicorn app.main:app --reload

# 运行测试
pytest

# 代码检查
ruff check .
mypy .
```
