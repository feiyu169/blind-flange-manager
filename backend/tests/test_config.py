"""基础配置测试"""

import pytest
from app.core.config import settings


def test_settings_loaded():
    """测试配置是否正确加载"""
    assert settings.APP_NAME == "盲板管理系统"
    assert settings.DATABASE_URL is not None
    assert settings.REDIS_URL is not None
    assert settings.SECRET_KEY is not None


def test_database_url_format():
    """测试数据库 URL 格式"""
    # 测试环境使用 SQLite，生产环境使用 PostgreSQL
    assert settings.DATABASE_URL is not None
    assert len(settings.DATABASE_URL) > 0


def test_redis_url_format():
    """测试 Redis URL 格式"""
    assert "redis://" in settings.REDIS_URL
