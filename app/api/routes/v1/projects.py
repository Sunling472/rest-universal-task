from typing import List
from fastapi import Depends, status

from app.api.routes.base import BaseHandler
from app.api.dependencies import oauth2_scheme
from app.db.schemas.project import ProjectCreate, ProjectEdit, ProjectDB
from app.db.schemas.task import TaskDB, TaskCreate
from app.db.controllers.projects import ProjectsController

from server_utils.cbv import cbv
from server_utils.inferring_router import InferringRouter


router = InferringRouter()


@cbv(router)
class ProjectsHandler(BaseHandler):
    token = Depends(oauth2_scheme)
    controller: ProjectsController

    @staticmethod
    def _get_controller_class() -> type[ProjectsController]:
        return ProjectsController

    @router.get('/', status_code=status.HTTP_200_OK)
    async def list(self) -> List[ProjectDB]:
        return await self.controller.list_projects()

    @router.get('/{item_id}', status_code=status.HTTP_200_OK)
    async def get(self, item_id: str) -> ProjectDB:
        return await self.controller.get_project(item_id)

    @router.post('/', status_code=status.HTTP_201_CREATED)
    async def create(self, create_schema: ProjectCreate) -> ProjectDB:
        return await self.controller.create_project(create_schema)

    @router.patch('/{item_id}', status_code=status.HTTP_200_OK)
    async def edit(self, item_id: str, edit_schema: ProjectEdit) -> ProjectDB:
        return await self.controller.edit_project(item_id, edit_schema)

    @router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
    async def delete(self, item_id: str):
        await self.controller.delete(item_id)
