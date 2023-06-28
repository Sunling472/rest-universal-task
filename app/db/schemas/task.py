from app.db.schemas.base import BaseSchema, BaseSchemaOut


class TaskBase(BaseSchema):
    title: str
    description: str | None


class TaskCreate(TaskBase):
    project_id: str


class TaskCreateByProject(TaskBase):
    ...


class TaskEdit(TaskBase):
    title: str | None
    description: str | None
    project_id: str | None


class TaskDB(TaskBase, BaseSchemaOut):
    project_id: str

