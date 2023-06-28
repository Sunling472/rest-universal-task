from fastapi import status

from app.api.routes.base import BaseHandler
from app.db.schemas.user import UserCreate, UserDB
from app.db.controllers.users import UsersController

from server_utils.cbv import cbv
from server_utils.inferring_router import InferringRouter


router = InferringRouter()


@cbv(router)
class RegisterHandler(BaseHandler):
    controller: UsersController

    @staticmethod
    def _get_controller_class() -> type[UsersController]:
        return UsersController

    @router.post('/', status_code=status.HTTP_201_CREATED)
    async def create(self, create_schema: UserCreate) -> UserDB:
        return await self.controller.create_user(create_schema)
