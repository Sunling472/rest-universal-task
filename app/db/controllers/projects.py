from sqlalchemy.ext.asyncio import AsyncSession

from app.db.controllers.base import BaseController
from app.db.controllers.tokens import TokensController
from app.db.schemas.project import ProjectCreate, ProjectEdit, ProjectDB
from app.db.schemas.task import TaskDB, TaskCreate
from app.db.models import Projects, Tasks


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

    async def list_projects(self, **kw) -> list[ProjectDB]:
        token = await self.token_ctrl.get_by_token()
        return await super().list(user_id=token.user.id, **kw)

    async def list_tasks_by_project(self, project_id: str) -> list[TaskDB]:
        return await super().list(model=Tasks, db_schema=TaskDB, project_id=project_id)

    async def create_task_by_project(self, project_id: str, task: TaskCreate) -> TaskDB:
        task.project_id = project_id
        return await super().create(create_schema=task, model=Tasks, db_schema=TaskDB)

    async def get_project(self, item_id: str) -> ProjectDB:
        return await super().get(item_id)

    async def create_project(self, create_schema: ProjectCreate) -> ProjectDB:
        token = await self.token_ctrl.get_by_token()
        return await super().create(user_id=token.user.id, **create_schema.dict())

    async def edit_project(self, item_id: str, edit_schema: ProjectEdit) -> ProjectDB:
        return await super().edit(item_id, edit_schema)

