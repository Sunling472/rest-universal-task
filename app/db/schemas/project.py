from app.db.schemas.base import BaseSchema, BaseSchemaOut
from app.common.enums import PricePeriodTypes


class ProjectBase(BaseSchema):
    title: str
    description: str | None
    price: float
    currency: str
    price_period_type: PricePeriodTypes


class ProjectCreate(ProjectBase):
    price: float | None
    currency: str | None
    price_period_type: PricePeriodTypes | None


class ProjectEdit(ProjectBase):
    user_id: str | None
    title: str | None
    price: float | None
    currency: str | None
    price_period_type: PricePeriodTypes | None


class ProjectDB(ProjectBase, BaseSchemaOut):
    user_id: str


