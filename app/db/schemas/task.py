from app.db.schemas.base import BaseSchema, BaseSchemaOut


class TaskBase(BaseSchema):
    title: str
    description: str | None
    project_id: str | None


class TaskCreate(TaskBase):
    ...


class TaskEdit(TaskBase):
    title: str | None
    description: str | None
    task_time: int | None


class TaskDB(TaskBase, BaseSchemaOut):
    task_time: int
