import logging

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.controllers.base import BaseController
from app.db.controllers.tokens import TokensController
from app.db.schemas.task import TaskCreate, TaskEdit, TaskDB
from app.db.models import Tasks
from app.common.errors import ErrorTexts


LOG = logging.getLogger(__name__)


class TasksController(BaseController):
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

    async def get_task_time(self, item_id: str) -> int:
        query = select(self._model.task_time).filter(
            and_(
                self._model.id == item_id,
                self._model.deleted_at == 0
            )
        )
        result_db = await self.session.execute(query)
        result: int | None = result_db.scalars().one_or_none()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorTexts.not_found_error.format(
                    name='Task', id=item_id
                )
            )
        return result

    @staticmethod
    async def start_task_tracker(task_id: str) -> None:
        # @rocketry.task('every 1 seconds', name=f'update_time {task_id}')
        ...

    @staticmethod
    async def stop_task_tracker(task_id: str) -> None:
        # rocketry.session.remove_task(f'update_time {task_id}')
        ...
