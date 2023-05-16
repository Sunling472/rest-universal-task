from abc import abstractmethod

from fastapi import Depends, status, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.user import UserDB
from app.api.dependencies import get_session
from app.db.controllers.base import BaseController
from app.db.controllers.tokens import TokensController
from app.db.schemas.base import BaseSchemaOut, BaseSchema
from app.common.errors import ErrorTexts

EXCLUDE_VARS = (
    'controller', '_controller', '_token_controller',
)


class BaseHandler:
    _controller: type[BaseController] | None = None
    _token_controller: TokensController | None = None

    session: AsyncSession = Depends(get_session)
    token: str | None = None

    @staticmethod
    def _raise_not_allowed() -> None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            ErrorTexts.not_allowed_error
        )

    @staticmethod
    @abstractmethod
    def _get_controller_class() -> type[BaseController]:
        ...

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.session,
                self.token
            )
        return self._controller

    @property
    def token_ctrl(self) -> TokensController:
        if self._token_controller is None:
            self._token_controller = TokensController(
                self.session, self.token
            )
        return self._token_controller

    async def get_current_user(self) -> UserDB | None:
        if self.token is not None:
            token_db = await self.token_ctrl.get_by_token()
            return token_db.user

    @abstractmethod
    async def list(self) -> type[list[BaseSchemaOut]]:
        ...

    @abstractmethod
    async def get(self, item_id: str) -> type[BaseSchemaOut]:
        ...

    @abstractmethod
    async def create(self, create_schema: type[BaseSchema]) -> type[BaseSchemaOut]:
        ...

    @abstractmethod
    async def edit(self, item_id: str, edit_schema: type[BaseSchema]) -> type[BaseSchemaOut]:
        ...

    @abstractmethod
    async def delete(self, item_id: str):
        ...

