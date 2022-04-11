import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Drivers(SqlAlchemyBase):
    __tablename__ = 'drivers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True, nullable=False)
    account_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
    location_latitude = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
    location_longitude = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=False)
    status_of_work_id = sqlalchemy.Column(sqlalchemy.Integer,
                                          sqlalchemy.ForeignKey("driver_status.id"), unique=False,
                                          nullable=False)
    class_car_id = sqlalchemy.Column(sqlalchemy.Integer,
                                     sqlalchemy.ForeignKey("class_car.id"), unique=False,
                                     nullable=False)
    status_on_receipt_id = sqlalchemy.Column(sqlalchemy.Integer,
                                             sqlalchemy.ForeignKey("driver_status_in_receipt.id"), unique=False,
                                             nullable=False)
