import sqlalchemy as sa
from sqlalchemy.orm import relationship

from app.db.base import Base


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
