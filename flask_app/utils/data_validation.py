from datetime import datetime, time, timezone, timedelta
from pydantic import BaseModel, EmailStr, field_validator, constr
from typing import Literal, Optional, Any


class UserValidator(BaseModel):
    email: EmailStr
    password: str
    name: str

    @field_validator('password')
    def password_check(cls, v):
        if len(v) < 12:
            raise ValueError('Password must be 12 characters and more')
        if not v.strip():
            raise ValueError('Password cannot be empty')
        return v


class TaskValidator(BaseModel):
    title: str
    description: str | None = None
    status: Literal['pending', 'done', 'failed'] | None = 'pending'
    priority: Literal['low', 'middle', 'high'] | None = 'low'
    deadline: Any

    @field_validator('title')
    def title_must_not_be_empty(cls, v, info):
        if not v:
            raise ValueError(f'{info.field_name} cannot be empty')
        if not v.strip():
            raise ValueError(f'{info.field_name} cannot be empty')
        return v

    @field_validator('deadline', mode='before')
    def parse_deadline(cls, v):
        if not v:
            return datetime.now(timezone.utc) + timedelta(days=2)
        if isinstance(v, datetime):
            return v
        try:
            dt = datetime.strptime(v.strip(), '%d/%m/%Y')
            return datetime.combine(dt.date(), time(23, 59)).replace(tzinfo=timezone.utc)
        except Exception:
            raise ValueError('Wrong format, use DD/MM/YYYY')



class TaskUpdateModel(BaseModel):
    title: Optional[constr(min_length=1)] = None
    description: Optional[str] = None
    status: Optional[Literal['pending', 'done', 'failed']] = None
    priority: Optional[Literal['low', 'middle', 'high']] = None