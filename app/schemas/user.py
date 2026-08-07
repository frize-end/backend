from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username :str = Field(..., description="用户名")

class UserCreateDTO(UserBase):
    password :str = Field(..., min_length=6, description="密码")
    phone :str = Field(...,pattern=r'^1[3-9]\d{9}$', description="手机号(11位)")

class UserUpdateDTO(BaseModel):
    username :str | None = Field(None,description="用户名")
    password :str | None = Field(None, min_length=6, description="密码，可选")
    phone :str | None = Field(None,pattern=r'^1[3-9]\d{9}$', description="手机号,可选")

class UserLoginDTO(BaseModel):
    username :str = Field(..., description="用户名")
    password :str = Field(..., min_length=6, description="密码")

class UserResponseDTO(UserBase):
    id :int
    create_time :datetime
    phone :str

    class Config:
        from_attributes = True