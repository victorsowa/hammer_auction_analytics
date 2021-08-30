from sqlalchemy import Column, Integer, String, Date

from hammer_auction_analytics.db.modelbase import SqlAlchemyBase


class Lot(SqlAlchemyBase):
    __tablename__ = "lots"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    name = Column(String)
    auction_id = Column(String)
    auction_year = Column(Date)
    department = Column(String)
    min_estimate = Column(Integer)
    max_estimate = Column(Integer)
    estimate_currency = Column(String)
    result = Column(Integer)
    result_currency = Column(String)
