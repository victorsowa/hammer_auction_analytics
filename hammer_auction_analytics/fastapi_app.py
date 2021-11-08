from typing import List, Union

from fastapi import FastAPI, Query
import sqlalchemy

from shared import initiate_db
from db.db_session import global_init, create_session
from db.auctions import Auction
from db.lots import Lot


app = FastAPI()
initiate_db()


@app.get("/get_auctions/")
async def get_auctions():
    session = create_session()
    return session.query(Auction).all()


@app.get("/get_lots_from_auctions/")
async def get_lots_from_auctions(auctions: List[str] = Query(None)):
    session = create_session()
    query = session.query(Lot.name).join(Auction, Auction.id == Lot.auction_id)

    return query.filter(Auction.name.in_(auctions)).all()
