"""用户 Schema"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """用户角色"""
    ADMIN = "admin"
    OPERATOR = "operator"
    INSPECTOR = "inspector"


class UserBase(BaseModel):
    """用户基础 Schema"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    role: UserRole = Field(UserRole.OPERATOR, description="角色")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")


class UserCreate(UserBase):
    """创建用户 Schema"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserUpdate(BaseModel):
    """更新用户 Schema"""
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")


class UserInDB(UserBase):
    """数据库中的用户 Schema"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """用户响应 Schema"""
    pass


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: list[UserResponse]
    total: int
    page: int
    page_size: int


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
