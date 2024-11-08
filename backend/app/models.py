import uuid
from datetime import datetime
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Column, Field, Relationship, SQLModel
from sqlmodel import Enum as SQLEnum


class Role(str, Enum):
    hr = 'HR'
    interviewer = 'interviewer'
    applicant = 'applicant'


class InterviewType(str, Enum):
    algo = 'algorithm'
    backend = 'backend'


class InterviewStatus(str, Enum):
    waiting = 'waiting'
    in_progress = 'in_progress'
    finished = 'finished'


class InterviewMark(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'


# Shared properties
class UserBase(SQLModel):
    class Config:
        arbitrary_types_allowed = True

    login: str = Field(min_length=4, max_length=255, index=True, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    role: Role = Field(sa_column=Column(SQLEnum(Role), nullable=False))
    is_active: bool = True
    is_superuser: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(UserCreate):
    pass


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    hashed_password: str


class StackTag(SQLModel, table=True):
    tag_code: str = Field(min_length=1, max_length=255, primary_key=True)


class InterviewSlot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_login: str = Field(foreign_key='user.login', nullable=False)
    max_applicant: int = Field(default=1, nullable=False)
    from_datetime: datetime = Field(default_factory=datetime.utcnow)
    to_datetime: datetime = Field(nullable=False)


class Interview(SQLModel, table=True):
    class Config:
        arbitrary_types_allowed = True

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    interviewer_login: str = Field(foreign_key='user.login')
    applicant_login: str = Field(foreign_key='user.login')
    link: str = Field(min_length=8, max_length=255)
    stack_tag: str = Field(foreign_key='stacktag.tag_code')
    event_datetime: datetime = Field(default_factory=datetime.utcnow)
    type: InterviewType = Field(sa_column=Column(SQLEnum(InterviewType), nullable=False))
    status: InterviewStatus =  Field(sa_column=Column(SQLEnum(InterviewStatus), nullable=False))
    mark: InterviewMark | None = Field(sa_column=Column(SQLEnum(InterviewStatus), default=None))
    comments: str = Field(min_length=40)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    pass


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = 'bearer'


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
