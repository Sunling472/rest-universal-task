from fastapi import status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.routes.base import BaseHandler
from app.db.schemas.token import TokenDB
from app.db.schemas.user import UserLogin
from app.db.controllers.tokens import TokensController

from server_utils.cbv import cbv
from server_utils.inferring_router import InferringRouter


router = InferringRouter()


@cbv(router)
class TokensHandler(BaseHandler):
    controller: TokensController

    @staticmethod
    def _get_controller_class() -> type[TokensController]:
        return TokensController

    @router.post('/', status_code=status.HTTP_201_CREATED)
    async def create(self, form_data: OAuth2PasswordRequestForm = Depends()) -> TokenDB:
        return await self.controller.user_login(form_data.username, form_data.password)

    @router.get('/', status_code=status.HTTP_200_OK)
    async def list(self) -> list[TokenDB]:
        return await self.controller.list()
