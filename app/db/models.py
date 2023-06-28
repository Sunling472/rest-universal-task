import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.common.enums import PricePeriodTypes, CurrencyTypes


class Users(Base):
    __tablename__ = 'users'

    username = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)


class Tokens(Base):
    __tablename__ = 'tokens'

    access_token = sa.Column(sa.String, nullable=False, unique=True)
    expires_at = sa.Column(sa.Integer, nullable=False)
    user_id = sa.Column(sa.ForeignKey('users.id'), nullable=False)
    user = relationship('Users', lazy='selectin')


class Tasks(Base):
    __tablename__ = 'tasks'

    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    project_id: str | None = sa.Column(
        sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True
    )
    project = sa.orm.relationship('Projects', lazy='selectin')


class Projects(Base):
    __tablename__ = 'projects'

    user_id: str | None = sa.Column(
        sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    price = sa.Column(sa.Numeric, nullable=False, default=0)
    currency: str | None = sa.Column(sa.Enum(CurrencyTypes, name='currency_types'),
                                     nullable=False, default=CurrencyTypes.RUB)  # type: ignore
    price_period_type: PricePeriodTypes = sa.Column(
        sa.Enum(PricePeriodTypes, name='price_period_types'),
        nullable=False,
        default=PricePeriodTypes.Hour,
    )


class Trackers(Base):
    __tablename__ = 'trackers'

    task_id = sa.Column(sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = sa.Column(sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    start_tracker_ts = sa.Column(sa.Integer, nullable=False)
    end_tracker_ts = sa.Column(sa.Integer, nullable=True, default=0)
    is_active = sa.Column(sa.Boolean, nullable=False, default=True)
    tags = sa.Column(sa.Text, nullable=True)

