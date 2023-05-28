from fastapi import Depends, status

from app.api.routes.base import BaseHandler
from app.api.dependencies import oauth2_scheme
from app.db.schemas.task import TaskCreate, TaskEdit, TaskDB
from app.db.controllers.tasks import TasksController

from server_utils.cbv import cbv
from server_utils.inferring_router import InferringRouter


router = InferringRouter()


@cbv(router)
class TasksHandler(BaseHandler):
    token = Depends(oauth2_scheme)
    controller: TasksController

    @staticmethod
    def _get_controller_class() -> type[TasksController]:
        return TasksController

    @router.get('/', status_code=status.HTTP_200_OK)
    async def list(self) -> list[TaskDB]:
        return await self.controller.list()

    @router.get('/{item_id}', status_code=status.HTTP_200_OK)
    async def get(self, item_id: str) -> TaskDB:
        return await self.controller.get(item_id)

    @router.post('/', status_code=status.HTTP_201_CREATED)
    async def create(self, create_schema: TaskCreate) -> TaskDB:
        return await self.controller.create(create_schema)

    @router.patch('/{item_id}', status_code=status.HTTP_200_OK)
    async def edit(self, item_id: str, edit_schema: TaskEdit) -> TaskDB:
        return await self.controller.edit(item_id, edit_schema)

    @router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
    async def delete(self, item_id: str):
        await self.controller.delete(item_id)

    # @router.post('/{item_id}/start_tracker', status_code=status.HTTP_204_NO_CONTENT)
    async def start_time_tracker(self, item_id: str):
        await self.controller.start_task_tracker(item_id)

    # @router.post('/{item_id}/stop_tracker', status_code=status.HTTP_204_NO_CONTENT)
    async def stop_time_tracker(self, item_id: str):
        await self.controller.stop_task_tracker(item_id)
