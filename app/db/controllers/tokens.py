import random
from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status

from app.db.controllers.base import BaseController
from app.db.controllers.users import UsersController
from app.db.schemas.token import TokenCreate, TokenDB
from app.db.models import Tokens
from app.common.errors import ErrorTexts


class TokensController(BaseController):
    def __init__(self, session: AsyncSession, token: str | None = None) -> None:
        self._user_ctrl: UsersController | None = None
        super().__init__(session, token)

    @property
    def _create_schema(self) -> type[TokenCreate]:
        return TokenCreate

    @property
    def _db_schema(self) -> type[TokenDB]:
        return TokenDB

    @property
    def _model(self) -> type[Tokens]:
        return Tokens

    def _edit_schema(self) -> None:
        ...

    @property
    def user_ctrl(self) -> UsersController:
        if self._user_ctrl is None:
            self._user_ctrl = UsersController(
                self.session, self.token
            )
        return self._user_ctrl

    @staticmethod
    def _token_create() -> str:
        token = ''
        result = ''
        for _ in range(4):
            token += uuid4().hex
        for i, ch in enumerate(token):
            is_upp: bool = random.choice([True, False])
            if is_upp:
                result += ch.upper()
            else:
                result += ch
        return result

    @staticmethod
    def _token_is_expired(ts: int) -> bool:
        ts_now = int(datetime.utcnow().timestamp())
        return ts < ts_now

    async def check_token(self):
        token_db = await self.get_by_token()
        if self._token_is_expired(token_db.expires_at):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                ErrorTexts.forbidden_token_expired_error
            )

    async def get_token(self, token_id: str) -> TokenDB:
        return await super().get(token_id)

    async def get_by_token(self) -> TokenDB:
        token_result_list: list[TokenDB] = await self.list(access_token=self.token)
        if not token_result_list:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                ErrorTexts.not_found_error.format(
                    name='Token',
                    id=self.token
                )
            )
        token_result = token_result_list[0]
        return TokenDB.from_orm(token_result)

    async def user_login(self, username: str, password: str) -> TokenDB:
        user_db = await self.user_ctrl.list(username=username)
        if user_db:
            user_db = user_db[0]
        else:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                ErrorTexts.not_found_username_error.format(
                    username=username
                )
            )
        if self.user_ctrl.check_hash_password(password, user_db.password) is False:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorTexts.bad_request_invalid_password
            )
        token_db_model: Tokens = await super().create(
            from_orm=False,
            **TokenCreate(access_token=self._token_create(), user_id=user_db.id).dict()
        )
        return self._db_schema(
            id=token_db_model.id,
            created_at=token_db_model.created_at,
            deleted_at=token_db_model.deleted_at,
            access_token=token_db_model.access_token,
            expires_at=token_db_model.expires_at,
            user=user_db,
        )

