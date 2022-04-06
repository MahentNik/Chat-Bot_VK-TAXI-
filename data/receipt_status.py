import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class ReceiptStatus(SqlAlchemyBase):
    __tablename__ = 'receipt_status'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, nullable=False, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
