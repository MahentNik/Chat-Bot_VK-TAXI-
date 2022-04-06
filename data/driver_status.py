import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class DriverStatus(SqlAlchemyBase):
    __tablename__ = 'driver_status'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
