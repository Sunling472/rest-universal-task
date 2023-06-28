from fastapi import status, Depends

from app.api.routes.base import BaseHandler
from app.api.dependencies import oauth2_scheme
from app.db.schemas.user import UserDB, UserCreate, UserEdit
from app.db.controllers.users import UsersController

from server_utils.cbv import cbv
from server_utils.inferring_router import InferringRouter


router = InferringRouter()


@cbv(router)
class UsersHandler(BaseHandler):
    token = Depends(oauth2_scheme)
    controller: UsersController

    @staticmethod
    def _get_controller_class() -> type[UsersController]:
        return UsersController

    @router.get('/', status_code=status.HTTP_200_OK)
    async def list(self) -> list[UserDB]:
        await self.token_ctrl.check_token()
        return await self.controller.list()

    @router.get('/{item_id}', status_code=status.HTTP_200_OK)
    async def get(self, item_id: str) -> UserDB:
        await self.token_ctrl.check_token()
        return await self.controller.get(item_id)

    @router.patch('/{item_id}', status_code=status.HTTP_200_OK)
    async def edit(self, item_id: str, edit_schema: UserEdit) -> UserDB:
        await self.token_ctrl.check_token()
        return await self.controller.edit(item_id, edit_schema)

    @router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
    async def delete(self, item_id: str):
        await self.token_ctrl.check_token()
        await self.controller.delete(item_id)





