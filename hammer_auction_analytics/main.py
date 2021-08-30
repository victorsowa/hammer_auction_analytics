import sys
import os

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)

from sqlalchemy.orm import sessionmaker

from scrape_lots_from_lot_page import get_page, get_soup
from scrape_lots_from_auction import get_lots_by_department
from get_all_auctions import get_all_auctions
from db.db_session import global_init, create_session
from db.auctions import Auction


PREVIOUS_AUCTIONS_URL = "https://www.bukowskis.com/sv/auctions/past/hammer"

DATABASE_NAME = "db.sqlite"


def set_auction_successfully_scraped_value(auction_name, value):
    session = create_session()
    scraped_auction = (
        session.query(Auction).filter(Auction.name == auction_name).first()
    )
    scraped_auction.successfully_scraped = 1
    session.commit()


def initiate_db():
    db_file = os.path.join(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", DATABASE_NAME)
    )
    return global_init(db_file)


def main():
    db_engine = initiate_db()
    previous_auctions = get_all_auctions(PREVIOUS_AUCTIONS_URL)
    scrape_auctions(previous_auctions, db_engine)


def check_if_auction_already_in_db(auction_name):
    session = create_session()
    auction_exists = (
        session.query(Auction.name).filter(Auction.name == auction_name).first()
    )

    return auction_exists is not None


def save_auction_in_db_without_scrape_status(
    auction_number, auction_name, auction_year
):
    session = create_session()
    auction = Auction(number=auction_number, name=auction_name, year=auction_year)
    session.add(auction)
    session.commit()


def get_auction_number_from_name(auction_name):
    return auction_name.rsplit(" ", 1)[1]


def create_auction_lot_url_from_number(auction_number):
    return f"https://www.bukowskis.com/auctions/{auction_number}/lots"


def scrape_and_store_auction(auction_lot_url, db_engine):
    get_lots_by_department(auction_lot_url).to_sql(
        "lots", db_engine, if_exists="append", index=False
    )


def scrape_auctions(auctions_to_scrape, db_engine):
    for year, auction_names in auctions_to_scrape:
        for auction_name in auction_names:
            print(auction_name)
            auction_exists = check_if_auction_already_in_db(
                auction_name
            )  # This could be done once instead, and filter away all existing
            if not auction_exists:
                print(auction_name, "does not exist in database, will try to scrape.")
                auction_number = get_auction_number_from_name(auction_name)

                save_auction_in_db_without_scrape_status(
                    auction_number, auction_name, year
                )

                auction_lot_url = create_auction_lot_url_from_number(auction_number)

                try:
                    scrape_and_store_auction(auction_lot_url, db_engine)
                    set_auction_successfully_scraped_value(auction_name, 1)
                except Exception as e:
                    print("Scraping ran in to error:", e)
                    print("No results will be saved.")
                    set_auction_successfully_scraped_value(auction_name, 0)

            else:
                print(auction_name, "already in database.")


if __name__ == "__main__":
    main()
