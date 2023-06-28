import typing as T

from fastapi import Depends, status

from app.api.routes.base import BaseHandler
from app.api.dependencies import oauth2_scheme
from app.db.schemas.task import (
    TaskCreate, TaskEdit,
    TaskDB, TaskCreateByProject
)
from app.db.schemas.tracker import TrackerCreate, TrackerCreateByTask, TrackerDB
from app.db.controllers.tasks import TasksController
from app.db.controllers.projects import ProjectsController

from server_utils.cbv import cbv
from server_utils.inferring_router import InferringRouter


router = InferringRouter()
tasks_by_project_router = InferringRouter()


@cbv(router)
class TasksHandler(BaseHandler):
    token = Depends(oauth2_scheme)
    controller: TasksController

    @staticmethod
    def _get_controller_class() -> type[TasksController]:
        return TasksController

    @router.get('/', status_code=status.HTTP_200_OK)
    async def list(self) -> list[TaskDB]:
        return await self.controller.list_tasks()

    @router.get('/{item_id}', status_code=status.HTTP_200_OK)
    async def get(self, item_id: str) -> TaskDB:
        return await self.controller.get_task(item_id)

    @router.post('/', status_code=status.HTTP_201_CREATED)
    async def create(self, create_schema: TaskCreate) -> TaskDB:
        return await self.controller.create_task(create_schema)

    @router.patch('/{item_id}', status_code=status.HTTP_200_OK)
    async def edit(self, item_id: str, edit_schema: TaskEdit) -> TaskDB:
        return await self.controller.edit(item_id, edit_schema)

    @router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
    async def delete(self, item_id: str):
        await self.controller.delete(item_id)

    @router.post('/{item_id}/start_tracker', status_code=status.HTTP_201_CREATED)
    async def start_time_tracker(self, item_id: str,
                                 create_schema: TrackerCreateByTask) -> TrackerDB:
        user = await self.get_current_user()
        tracker = TrackerCreate(user_id=user.id, task_id=item_id, tags=create_schema.tags)
        return await self.controller.start_task_tracker(tracker)

    @router.post('/{item_id}/stop_tracker', status_code=status.HTTP_201_CREATED)
    async def stop_time_tracker(self, item_id: str) -> TrackerDB:
        return await self.controller.stop_task_tracker(item_id)


@cbv(tasks_by_project_router)
class TasksByProjectHandler(BaseHandler):
    token = Depends(oauth2_scheme)
    controller: ProjectsController

    @staticmethod
    def _get_controller_class() -> type[ProjectsController]:
        return ProjectsController

    @tasks_by_project_router.get('/{project_id}/tasks')
    async def get_tasks_by_projects(self, project_id: str) -> T.List[TaskDB]:
        return await self.controller.list_tasks_by_project(project_id)

    @tasks_by_project_router.post('/{project_id}/tasks', status_code=status.HTTP_201_CREATED)
    async def create_task_by_project(self, project_id: str, task: TaskCreateByProject) -> TaskDB:
        return await self.controller.create_task_by_project(project_id, task)
