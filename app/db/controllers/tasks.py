import logging
import typing as T
from datetime import datetime

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.controllers.base import BaseController
from app.db.controllers.tokens import TokensController
from app.db.controllers.projects import ProjectsController
from app.db.controllers.trackers import TrackersController
from app.db.schemas.task import TaskCreate, TaskEdit, TaskDB
from app.db.schemas.token import TokenDB
from app.db.schemas.tracker import TrackerDB, TrackerCreate
from app.db.models import Tasks
from app.common.errors import ErrorTexts


LOG = logging.getLogger(__name__)


class TasksController(BaseController):
    def __init__(self, session: AsyncSession, token: str) -> None:
        self._token_ctrl: TokensController | None = None
        self._project_ctrl: ProjectsController | None = None
        self._tracker_ctrl: TrackersController | None = None
        super().__init__(session, token)

    @property
    def token_ctrl(self) -> TokensController:
        if self._token_ctrl is None:
            self._token_ctrl = TokensController(
                self.session, self.token
            )
        return self._token_ctrl

    @property
    def project_ctrl(self) -> ProjectsController:
        if self._project_ctrl is None:
            self._project_ctrl = ProjectsController(
                self.session, self.token
            )
        return self._project_ctrl

    @property
    def tracker_crl(self) -> TrackersController:
        if self._tracker_ctrl is None:
            self._tracker_ctrl = TrackersController(
                self.session, self.token
            )
        return self._tracker_ctrl

    @property
    def _create_schema(self) -> type[TaskCreate]:
        return TaskCreate

    @property
    def _edit_schema(self) -> type[TaskEdit]:
        return TaskEdit

    @property
    def _db_schema(self) -> type[TaskDB]:
        return TaskDB

    @property
    def _model(self) -> type[Tasks]:
        return Tasks

    async def list_tasks(self, token: TokenDB | None = None, **kw) -> T.List[TaskDB]:
        if token is None:
            token = await self.token_ctrl.get_by_token()
        user_projects = await self.project_ctrl.list_project_id_by_user_id(token.user.id)

        query = select(Tasks).filter(
            and_(
                Tasks.deleted_at == 0,
                Tasks.project_id.in_(user_projects)
            )
        )
        if kw:
            query = query.filter_by(**kw)
        result_db = await self.session.execute(query)
        task_list: list[TaskDB] = await self.prepare_list(list(result_db.scalars().all()))
        result: list[TaskDB] = []
        for task in task_list:
            if task.start_ts and task.end_ts:
                task.task_time = task.end_ts - task.start_ts
            result.append(task)

        return result

    async def get(self, item_id: str, from_orm: bool = True,
                  model: type[Tasks] | None = None,
                  db_schema: type[TaskDB] | None = None) -> Tasks | TaskDB:
        return await super().get(item_id, from_orm, model, db_schema)

    async def get_task(self, item_id: str) -> TaskDB:
        task = await self.get(item_id)
        if task.start_ts and task.end_ts:
            task.task_time = task.end_ts - task.start_ts
        return task

    async def _is_active_timer(self, task_id: str) -> bool:
        query = (
            select(self._model.is_active_timer).filter(
                and_(
                    self._model.id == task_id,
                    self._model.deleted_at == 0
                )
            )
        )
        result_db = await self.session.execute(query)
        result: bool = result_db.scalars().one()
        return result

    async def create_task(self, task: TaskCreate) -> TaskDB:
        return await super().create(task)

    async def start_task_tracker(self, tracker: TrackerCreate) -> TrackerDB:
        return await self.tracker_crl.create_for_task(tracker)

    async def stop_task_tracker(self, task_id: str | None = None,
                                tracker_id: str | None = None) -> TrackerDB:
        tracker: TrackerDB
        if task_id and not tracker_id:
            tracker = await self.tracker_crl.get_last_tracker_by_task_id(task_id)
        elif not task_id and tracker_id:
            tracker = await self.tracker_crl.get_last_tracker_by_task_id(task_id)
        else:
            raise

        if tracker.is_active is True:
            tracker = await self.tracker_crl.edit(
                tracker.id,
                is_active=False,
                end_tracker_ts=int(datetime.now().timestamp())
            )
        tracker.full_time_seconds = tracker.end_tracker_ts - tracker.start_tracker_ts
        return tracker



