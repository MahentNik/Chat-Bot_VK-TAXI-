import sqlalchemy
from .db_session import SqlAlchemyBase
import datetime
from sqlalchemy import orm


class Receipt(SqlAlchemyBase):
    __tablename__ = 'receipt'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True, nullable=False)
    driver_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("drivers.id"))
    status_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("receipt_status.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    cost = sqlalchemy.Column(sqlalchemy.Float, nullable=False, unique=False)
    special_id = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    first_place_latitude = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=False)
    first_place_longitude = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=False)
    second_place_latitude = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
    second_place_longitude = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
    date_need_for_user = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, unique=False)
    date_now = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    date_close = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
