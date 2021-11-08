from sqlalchemy import Column, Integer, String

from db.modelbase import SqlAlchemyBase


class Auction(SqlAlchemyBase):
    __tablename__ = "auctions"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    number = Column(Integer, unique=True)
    name = Column(String, unique=True)
    year = Column(Integer)
    successfully_scraped = Column(Integer)
