import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class ClassCar(SqlAlchemyBase):
    __tablename__ = 'class_car'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    cost = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
