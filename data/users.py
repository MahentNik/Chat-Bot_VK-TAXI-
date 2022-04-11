import sqlalchemy
from .db_session import SqlAlchemyBase


class Users(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, nullable=False, unique=True)
    account_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True)
