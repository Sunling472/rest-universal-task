from datetime import datetime, timedelta

from app.db.schemas.base import BaseSchema, BaseSchemaOut
from app.db.schemas.user import UserDB


class TokenBase(BaseSchema):
    ...


class TokenCreate(TokenBase):
    user_id: str
    access_token: str
    expires_at: int = int(
        (datetime.utcnow() + timedelta(days=1)).timestamp()
    )


class TokenDB(TokenBase, BaseSchemaOut):
    access_token: str
    token_type: str = 'bearer'
    expires_at: int
    user: UserDB
