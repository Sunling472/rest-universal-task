from app.db.schemas.base import BaseSchema, BaseSchemaOut


class UserBase(BaseSchema):
    username: str
    password: str


class UserCreate(UserBase):
    ...


class UserEdit(UserBase):
    username: str | None
    password: str | None
    new_password: str | None


class UserDB(UserBase, BaseSchemaOut):
    ...


class UserLogin(UserBase):
    ...
