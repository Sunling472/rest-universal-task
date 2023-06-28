import typing as T

from fastapi import Depends, status

from app.api.routes.base import BaseHandler
from app.api.dependencies import oauth2_scheme
from app.db.schemas.tracker import TrackerCreate, TrackerEdit, TrackerDB
from app.db.controllers.trackers import TrackersController
from app.db.models import Trackers

from server_utils.cbv import cbv
from server_utils.inferring_router import InferringRouter


router = InferringRouter()


@cbv(router)
class TrackersHandler(BaseHandler):
    token = Depends(oauth2_scheme)
    controller: TrackersController

    @staticmethod
    def _get_controller_class() -> type[TrackersController]:
        return TrackersController

    @router.get('/', status_code=status.HTTP_200_OK)
    async def list(
            self,
            task_id: str | None = None,
            start_date: int | None = None,
            end_date: int | None = None,
            tags: str | None = None) -> T.List[TrackerDB]:
        user = await self.get_current_user()
        return await self.controller.list_trackers(
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            user_id=user.id,
            task_id=task_id
        )
