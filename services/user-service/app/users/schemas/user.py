import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    group_id: int | None = None


class UserCreate(schemas.BaseUserCreate):
    first_name: str = None
    last_name: str = None
    age: int = None
    group_id: int | None = None


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str = None
    last_name: str = None
    age: int = None
    group_id: int | None = None
