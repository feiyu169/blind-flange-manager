"""JWT 调试测试"""

import pytest
from app.core.security import create_access_token, decode_access_token


def test_jwt_create_and_decode():
    """测试 JWT 创建和解码"""
    # 创建 token - sub 必须是字符串
    token = create_access_token(data={"sub": "1"})
    assert token is not None

    # 解码 token
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == "1"


def test_jwt_decode_invalid():
    """测试 JWT 解码无效 token"""
    payload = decode_access_token("invalid_token")
    assert payload is None
