from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        use_enum_values = True
        orm_mode = True


class BaseSchemaOut(BaseModel):
    id: str
    created_at: int
    deleted_at: int
