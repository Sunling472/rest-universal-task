import bcrypt as bc

from app.db.controllers.base import BaseController
from app.db.schemas.user import UserCreate, UserEdit, UserDB
from app.db.models import Users


class UsersController(BaseController):
    @property
    def _create_schema(self) -> type[UserCreate]:
        return UserCreate

    @property
    def _edit_schema(self) -> type[UserEdit]:
        return UserEdit

    @property
    def _db_schema(self) -> type[UserDB]:
        return UserDB

    @property
    def _model(self) -> type[Users]:
        return Users

    @staticmethod
    def create_hash_password(password: str) -> str:
        return bc.hashpw(password, bc.gensalt())

    @staticmethod
    def check_hash_password(password: str, hashed_password: str) -> bool:
        return bc.checkpw(password, hashed_password)

    async def list(self, **kw) -> list[UserDB]:
        return await super().list(**kw)

    async def create_user(self, user: UserCreate) -> UserDB:
        user_hashed_password = self.create_hash_password(user.password)
        return await self.create(
            username=user.username,
            password=user_hashed_password
        )

