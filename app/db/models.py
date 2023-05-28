import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.common.enums import PricePeriodTypes


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
    project_id = sa.Column(sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True)
    project = sa.orm.relationship('Projects', lazy='selectin')
    task_time = sa.Column(sa.Integer, nullable=False, default=0)


class Projects(Base):
    __tablename__ = 'projects'

    user_id = sa.Column(sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    price = sa.Column(sa.Numeric, nullable=False, default=0)
    currency = sa.Column(sa.String, nullable=False, default='RUB')
    price_period_type = sa.Column(
        sa.Enum(PricePeriodTypes, name='price_period_types'),
        nullable=False,
        default=PricePeriodTypes.Hour,

    )


