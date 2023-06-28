import logging
import typing as T
from datetime import datetime, timedelta

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.controllers.base import BaseController
from app.db.controllers.tokens import TokensController
from app.db.schemas.tracker import TrackerCreate, TrackerEdit, TrackerDB
from app.db.models import Trackers
from app.common.errors import ErrorTexts


LOG = logging.getLogger(__name__)


class TrackersController(BaseController):
    def __init__(self, session: AsyncSession, token: str) -> None:
        self._token_ctrl: TokensController | None = None
        super().__init__(session, token)

    @property
    def token_ctrl(self) -> TokensController:
        if self._token_ctrl is None:
            self._token_ctrl = TokensController(
                self.session, self.token
            )
        return self._token_ctrl

    @property
    def _create_schema(self) -> type[TrackerCreate]:
        return TrackerCreate

    @property
    def _edit_schema(self) -> type[TrackerEdit]:
        return TrackerEdit

    @property
    def _db_schema(self) -> type[TrackerDB]:
        return TrackerDB

    @property
    def _model(self) -> type[Trackers]:
        return Trackers

    async def get_tracker(self, item_id: str) -> TrackerDB:
        return await super().get(item_id)

    async def get_last_tracker_by_task_id(self, task_id: str) -> TrackerDB:
        query = select(self._model).filter(
            and_(
                self._model.task_id == task_id,
                self._model.deleted.is_(False)
            )
        ).order_by(
            self._model.created_at.desc()
        )
        result_db = await self.session.execute(query)
        result = result_db.scalars().first()
        return result

    async def list_trackers(
            self,
            task_id: str | None,
            start_date: int | None,
            end_date: int | None,
            tags: str | None, **kw) -> T.List[TrackerDB]:
        result_db: T.List[TrackerDB]
        result: T.List[TrackerDB] = []
        if task_id:
            result_db = await self.list(start_date, end_date, task_id=task_id, **kw)
        else:
            result_db = await self.list(start_date, end_date, **kw)
        for item in result_db:
            if item.start_tracker_ts and item.end_tracker_ts:
                item.full_time_seconds = item.end_tracker_ts - item.start_tracker_ts
                result.append(item)
                continue
            result.append(item)
        return result

    async def create_for_task(self, create_schema: TrackerCreate) -> TrackerDB:
        return await super().create(create_schema)
