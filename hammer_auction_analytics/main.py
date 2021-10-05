import sys
import os
from typing import List

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from rich import print
from rich.padding import Padding

from shared import get_page, get_soup
from scrape_lots_from_auction import get_lots_by_department
from get_all_auctions import get_all_auctions
from db.db_session import global_init, create_session
from db.auctions import Auction


PREVIOUS_AUCTIONS_URL = "https://www.bukowskis.com/sv/auctions/past/hammer"

DATABASE_NAME = "db.sqlite"


def set_auction_successfully_scraped_value(auction_name: str, value: int) -> None:
    session = create_session()
    scraped_auction = (
        session.query(Auction).filter(Auction.name == auction_name).first()
    )
    scraped_auction.successfully_scraped = value
    session.commit()


def initiate_db() -> sqlalchemy.engine.base.Engine:
    db_file = os.path.join(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", DATABASE_NAME)
    )
    return global_init(db_file)


def main() -> None:
    db_engine = initiate_db()
    previous_auctions = get_all_auctions(PREVIOUS_AUCTIONS_URL)
    scrape_auctions(previous_auctions, db_engine)


def check_if_auction_already_in_db(auction_name) -> bool:
    session = create_session()
    auction_exists = (
        session.query(Auction.name).filter(Auction.name == auction_name).first()
    )

    return auction_exists is not None


def save_auction_in_db_without_scrape_status(
    auction_number: str, auction_name: str, auction_year: int
):
    session = create_session()
    auction = Auction(number=auction_number, name=auction_name, year=auction_year)
    session.add(auction)
    session.commit()
    return auction.id


def get_auction_number_from_name(auction_name: str) -> str:
    return auction_name.rsplit(" ", 1)[1]


def create_auction_lot_url_from_number(auction_number: str) -> str:
    return f"https://www.bukowskis.com/auctions/{auction_number}/lots"


def scrape_and_store_auction(
    auction_lot_url, auction_id, auction_year, db_engine
) -> None:
    df = get_lots_by_department(auction_lot_url)
    df["auction_year"] = auction_year
    df["auction_id"] = auction_id
    df.to_sql("lots", db_engine, if_exists="append", index=False)


def scrape_auctions(
    auctions_to_scrape: List, db_engine: sqlalchemy.engine.base.Engine
) -> None:
    for year, auction_names in auctions_to_scrape:

        for auction_name in auction_names:
            print(Padding(f"[bold]{auction_name}[/]", (1, 0, 0, 0), expand=True))
            auction_exists = check_if_auction_already_in_db(
                auction_name
            )  # This could be done once instead, and filter away all existing
            if not auction_exists:
                print(
                    f"{auction_name}, does not exist in database, will try to scrape."
                )
                auction_number = get_auction_number_from_name(auction_name)

                auction_id = save_auction_in_db_without_scrape_status(
                    auction_number, auction_name, year
                )

                auction_lot_url = create_auction_lot_url_from_number(auction_number)

                try:
                    scrape_and_store_auction(
                        auction_lot_url, auction_id, year, db_engine
                    )
                    set_auction_successfully_scraped_value(auction_name, 1)
                except Exception as e:
                    print("[bold red]Scraping ran in to error:[/]", e)
                    print("[bold red]No results will be saved.[/]")
                    set_auction_successfully_scraped_value(auction_name, 0)

            else:
                print(f"[yellow]{auction_name}, already in database.[/]")


if __name__ == "__main__":
    main()
