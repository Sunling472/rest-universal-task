from fastapi import status, Depends

from app.api.routes.base import BaseHandler
from app.api.dependencies import oauth2_scheme
from app.db.schemas.user import UserDB

from server_utils.cbv import cbv
from server_utils.inferring_router import InferringRouter


router = InferringRouter()


@cbv(router)
class MeHandler(BaseHandler):
    token = Depends(oauth2_scheme)

    @staticmethod
    def _get_controller_class():
        ...

    @router.get('/', status_code=status.HTTP_200_OK)
    async def get(self) -> UserDB:
        await self.token_ctrl.check_token()
        return await super().get_current_user()

    async def list(self) -> None:
        ...

    async def create(self, create_schema) -> None:
        ...

    async def edit(self, item_id: str, edit_schema) -> None:
        ...

    async def delete(self, item_id: str) -> None:
        ...
