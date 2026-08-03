from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username :str = Field(..., description="用户名")

class UserCreateDTO(UserBase):
    password :str = Field(..., min_length=6, description="密码")

class UserUpdateDTO(UserBase):
    username :str | None = Field(None,description="用户名")
    password :str | None = Field(None, min_length=6, description="密码，可选")

class UserResponseDTO(UserBase):
    id :int
    create_time :datetime

    class Config:
        from_attributes = True