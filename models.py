import sqlalchemy
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Reservations(Base):
    __tablename__ = 'reservations'

    reservation_id = sqlalchemy.Column('reservation_id', sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column('name', sqlalchemy.String(60))
    start_date = sqlalchemy.Column('start_datetime', sqlalchemy.DateTime)
    end_date = sqlalchemy.Column('end_datetime', sqlalchemy.DateTime)
