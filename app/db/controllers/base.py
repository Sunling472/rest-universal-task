from abc import abstractmethod
from typing import Generic, TypeVar, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from fastapi.exceptions import HTTPException
from fastapi import status

from app.db.schemas.base import BaseSchema, BaseSchemaOut
from app.common.errors import ErrorTexts


IN_SCHEMA = TypeVar('IN_SCHEMA', bound=BaseSchema)
OUT_SCHEMA = TypeVar('OUT_SCHEMA', bound=BaseSchemaOut)
DB_MODEL = TypeVar('DB_MODEL')


class BaseController(Generic[IN_SCHEMA, OUT_SCHEMA, DB_MODEL]):
    def __init__(self, session: AsyncSession, token: str | None = None) -> None:
        self.session = session
        self.token = token

    @property
    @abstractmethod
    def _create_schema(self) -> type[IN_SCHEMA]:
        ...

    @property
    @abstractmethod
    def _edit_schema(self) -> type[IN_SCHEMA]:
        ...

    @property
    @abstractmethod
    def _db_schema(self) -> type[OUT_SCHEMA]:
        ...

    @property
    @abstractmethod
    def _model(self) -> type[DB_MODEL]:
        ...

    @staticmethod
    def _raise_not_allowed() -> None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            ErrorTexts.not_allowed_error
        )

    async def list(self, **kw) -> list[OUT_SCHEMA]:
        query = select(self._model).filter(
            self._model.deleted_at == 0
        )
        if kw:
            query = query.filter_by(**kw)
        items = await self.session.execute(query)
        result: list[OUT_SCHEMA] = []
        for item in items.scalars():
            result.append(self._db_schema.from_orm(item))
        return result

    async def get(self, item_id: str) -> DB_MODEL:
        query = select(self._model).filter(
            self._model.deleted_at == 0,
            self._model.id == item_id
        )
        item = await self.session.execute(query)
        item = item.scalars().one_or_none()
        if not item:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorTexts.model_not_exist_error.format(
                    model_name=self._model.__name__,
                    item_id=item_id
                )
            )
        return self._db_schema.from_orm(item)

    async def create(self, create_schema: IN_SCHEMA | None = None,
                     from_orm: bool = True, **kwargs) -> DB_MODEL | OUT_SCHEMA:
        result: dict[str, Any] = {}
        for k, v in create_schema.dict().items() if create_schema else kwargs.items():
            if v is not None:
                result[k] = v

        item = self._model(**result)
        try:
            self.session.add(item)
            await self.session.commit()
        except IntegrityError as ex:
            await self.session.rollback()
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                ErrorTexts.database_error.format(
                    details=ex.detail
                )
            )
        if from_orm:
            return self._db_schema.from_orm(item)
        return item

    async def edit(self, item_id: str,
                   edit_schema: IN_SCHEMA | None = None, **kwargs) -> DB_MODEL:
        result: dict[str, Any] = {}
        item = await self.session.get(self._model, item_id)
        if (edit_schema and not kwargs) or (
                not edit_schema and kwargs):
            self.session.expunge(item)

            for k, v in edit_schema.dict().items() if edit_schema else kwargs.items():
                if v is not None:
                    result[k] = v

            for k, v in result.items():
                setattr(item, k, v)
            try:
                self.session.add(item)
                await self.session.commit()
            except IntegrityError as ex:
                await self.session.rollback()
                raise HTTPException(
                    status.HTTP_502_BAD_GATEWAY,
                    ErrorTexts.database_error.format(
                        details=ex.detail
                    )
                )
            return self._db_schema.from_orm(item)
        else:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorTexts.database_not_params_error
            )

    async def delete(self, item_id: str) -> None:
        await self.edit(
            item_id,
            deleted_at=int(datetime.utcnow().timestamp())
        )
