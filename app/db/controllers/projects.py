import typing as T

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.controllers.base import BaseController
from app.db.controllers.tokens import TokensController
from app.db.schemas.project import ProjectCreate, ProjectEdit, ProjectDB
from app.db.schemas.task import TaskDB, TaskCreate, TaskCreateByProject
from app.db.schemas.token import TokenDB
from app.db.models import Projects, Tasks
from app.common.errors import ErrorTexts


class ProjectsController(BaseController):
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
    def _create_schema(self) -> type[ProjectCreate]:
        return ProjectCreate

    @property
    def _edit_schema(self) -> type[ProjectEdit]:
        return ProjectEdit

    @property
    def _db_schema(self) -> type[ProjectDB]:
        return ProjectDB

    @property
    def _model(self) -> type[Projects]:
        return Projects

    async def list_projects(self, token: TokenDB | None = None, **kw) -> list[ProjectDB]:
        if token is None:
            token = await self.token_ctrl.get_by_token()
        return await super().list(user_id=token.user.id, **kw)

    async def list_tasks_by_project(self, project_id: str) -> list[TaskDB]:
        token = await self.token_ctrl.get_by_token()
        project = await self.get_project(project_id)
        if token.user.id != project.user_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                ErrorTexts.forbidden_error
            )
        return await super().list(model=Tasks, db_schema=TaskDB, project_id=project_id)

    async def get_user_id_by_project_id(self, project_id: str) -> str:
        project = await self.get_project(project_id)
        return project.user_id

    async def list_project_id_by_user_id(self, user_id: str) -> T.List[str]:
        query = select(Projects.id).filter(
            and_(
                Projects.deleted_at == 0,
                Projects.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        result = result.scalars().all()
        return list(result)

    async def create_task_by_project(self, project_id: str, task: TaskCreateByProject) -> TaskDB:
        return await super().create(
            create_schema=TaskCreate(project_id=project_id, **task.dict()),
            model=Tasks,
            db_schema=TaskDB
        )

    async def get_project(self, item_id: str) -> ProjectDB:
        return await super().get(item_id)

    async def create_project(self, create_schema: ProjectCreate) -> ProjectDB:
        token = await self.token_ctrl.get_by_token()
        return await super().create(user_id=token.user.id, **create_schema.dict())

    async def edit_project(self, item_id: str, edit_schema: ProjectEdit) -> ProjectDB:
        return await super().edit(item_id, edit_schema)

