from typing import List

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from rich import print
from rich.padding import Padding

from shared import get_page, get_soup, initiate_db
from scrape_lots_from_auction import scrape_lots_by_department
from get_all_auctions import scrape_auction_names_and_year
from db.db_session import global_init, create_session
from db.auctions import Auction


PREVIOUS_AUCTIONS_URL = "https://www.bukowskis.com/sv/auctions/past/hammer"


def store_auction_successfully_scraped_value(auction_name: str, value: int) -> None:
    session = create_session()
    scraped_auction = (
        session.query(Auction).filter(Auction.name == auction_name).first()
    )
    scraped_auction.successfully_scraped = value
    session.commit()


def main() -> None:
    db_engine = initiate_db()
    previous_auctions = scrape_auction_names_and_year(PREVIOUS_AUCTIONS_URL)
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


def auction_number_from_name(auction_name: str) -> str:
    return auction_name.rsplit(" ", 1)[1]


def create_auction_lot_url_from_number(auction_number: str) -> str:
    return f"https://www.bukowskis.com/auctions/{auction_number}/lots"


def scrape_and_store_auction(
    auction_lot_url, auction_id, auction_year, db_engine
) -> None:
    df = scrape_lots_by_department(auction_lot_url)
    df["auction_year"] = auction_year
    df["auction_id"] = auction_id
    with db_engine.connect() as connection:
        df.to_sql("lots", connection, if_exists="append", index=False)


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
                auction_number = auction_number_from_name(auction_name)

                auction_id = save_auction_in_db_without_scrape_status(
                    auction_number, auction_name, year
                )

                auction_lot_url = create_auction_lot_url_from_number(auction_number)

                try:
                    scrape_and_store_auction(
                        auction_lot_url, auction_id, year, db_engine
                    )
                    store_auction_successfully_scraped_value(auction_name, 1)
                except Exception as e:
                    print("[bold red]Scraping ran in to error:[/]", e)
                    print("[bold red]No results will be saved.[/]")
                    store_auction_successfully_scraped_value(auction_name, 0)

            else:
                print(f"[yellow]{auction_name}, already in database.[/]")


if __name__ == "__main__":
    main()
