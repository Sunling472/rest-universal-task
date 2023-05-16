from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from app.common.enums import ColumnPermissions


@as_declarative()
class Base:
    __allow_unmapped__ = True
    __name__: str
    __tablename__: str

    id = Column(String, primary_key=True,
                default=lambda: uuid4().hex, info=ColumnPermissions.create_only)
    created_at = Column(Integer, nullable=False,
                        default=lambda: int(datetime.utcnow().timestamp()),
                        info=ColumnPermissions.create_only)
    deleted_at = Column(Integer, nullable=False, default=0,
                        info=ColumnPermissions.full)

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @hybrid_property
    def deleted(self) -> bool:
        return self.deleted_at != 0
