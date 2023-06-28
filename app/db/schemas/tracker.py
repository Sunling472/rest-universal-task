from datetime import datetime
from app.db.schemas.base import BaseSchema, BaseSchemaOut
from app.db.schemas.task import TaskDB


class TrackerBase(BaseSchema):
    user_id: str
    task_id: str
    tags: str | None
    start_tracker_ts: int = int(datetime.now().timestamp())
    is_active: bool = True


class TrackerCreateByTask(BaseSchema):
    tags: str | None


class TrackerCreate(TrackerBase):
    ...


class TrackerEdit(TrackerBase):
    ...


class TrackerDB(TrackerBase, BaseSchemaOut):
    end_tracker_ts: int | None
    full_time_seconds: int = 0


