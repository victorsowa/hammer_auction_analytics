from collections import namedtuple
from typing import List, Dict

import bs4
from rich import print

from shared import get_page, get_soup


Lot = namedtuple("Lot", "number name estimate result")
Estimates = namedtuple("Estimates", "min max currency")
Result = namedtuple("Result", "value currency")


def separate_lot_number_and_name(lot_title: str) -> List[str]:
    return lot_title.split(". ", 1)


def convert_bs4_navigable_string_to_string(
    bs4_navigable_string: bs4.element.NavigableString,
) -> str:
    string = str(bs4_navigable_string)
    return string.replace("\xa0", " ").replace("\xc0", " ")


def scrape_lot_estimate(
    lot_estimate: bs4.element.NavigableString, lot_name: str
) -> Estimates:
    lot_estimate_string = convert_bs4_navigable_string_to_string(lot_estimate)
    raw_values, currency = lot_estimate_string.rsplit(" ", 1)
    values_without_spaces = raw_values.replace(" ", "")
    try:
        min_estimate, max_estimate = [
            int(value) for value in values_without_spaces.split("-")
        ]
        return Estimates(min_estimate, max_estimate, currency)
    except ValueError:
        try:
            min_estimate = int(values_without_spaces)
            return Estimates(min_estimate, None, currency)
        except ValueError:
            print(
                f"[yellow]{lot_name}, could not parse estimate, value was: [/]",
                lot_estimate_string,
            )
            return Estimates(None, None, None)


def scrape_lot_result(lot_result: str, lot_name: str) -> Result:
    """The lot can be sold with a price, returned or it can also be missing
    for various reasons (some known are: lot has been withdrawn before
    the auction, it is a collection of several lots that has there own result
    already in the auction.)"""
    lot_result_string = convert_bs4_navigable_string_to_string(lot_result)
    try:
        raw_value, currency = lot_result_string.rsplit(" ", 1)
        return Result(int(raw_value.replace(" ", "")), currency)
    except ValueError:
        if lot_result_string == "Återrop":
            return Result("Return", None)
        print(
            f"[yellow] {lot_name}, could not parse result, value was: [/]",
            lot_result_string,
        )
        return Result(None, None)


def scrape_lot_information(lots_url: str) -> bs4.element.Tag:
    page = get_page(lots_url)
    soup = get_soup(page.content)
    return soup.find("div", class_="c-lot-index-lots--narrow")


def scrape_structured_information_from_lots(lots: List[bs4.element.Tag]) -> List[dict]:
    structured_lots = []

    for lot in lots:
        lot_title = lot.find("a", class_="c-lot-index-lot__title").string
        lot_number, lot_name = separate_lot_number_and_name(lot_title)

        lot_result = lot.find(
            "div", class_="c-lot-index-lot__result-value"
        ).string  # TODO create int out of space seperated number string, account for Återrop (also in english?) # noqa: E501
        result = scrape_lot_result(lot_result, lot_name)

        lot_estimate = lot.find("div", class_="c-lot-index-lot__estimate-value").string
        estimate = scrape_lot_estimate(lot_estimate, lot_name)

        lot = {
            "number": lot_number,
            "name": lot_name,
            "min_estimate": estimate.min,
            "max_estimate": estimate.max,
            "estimate_currency": estimate.currency,
            "result": result.value,
            "result_currency": result.currency,
        }
        structured_lots.append(lot)
    return structured_lots


def scrape_information_from_lots(lot_url: str) -> List[dict]:
    scraped_lots = scrape_lot_information(lot_url)
    return scrape_structured_information_from_lots(scraped_lots)


if __name__ == "__main__":
    URL = "https://www.bukowskis.com/auctions/632/lots"
    print(scrape_information_from_lots(URL))
