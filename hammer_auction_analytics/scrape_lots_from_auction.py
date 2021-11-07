from typing import List, Optional

import pandas as pd
from rich import print

from scrape_lots_from_lot_page import scrape_information_from_lots
from shared import get_page, get_soup


AUCTION_URL: str = "https://www.bukowskis.com/auctions/567/lots"

NON_DEPARTMENT_SEARCH_FILTERS: List[str] = [
    "Kortast tid kvar",
    "Lägsta utropspris",
    "Högsta utropspris",
    "Bokstavsordning",
    "Endast favoriter",
    "Ending soon",
    "Alphabetical",
    "Lowest estimate",
    "Highest estimate",
    "Catalogue number",
    "Only favourites",
]


def scrape_lots_from_all_subpages(parent_url: str) -> Optional[List[dict]]:
    current_page = 1
    try_another_page = True

    child_url_template = parent_url + "/page/"

    print(parent_url)
    scraped_lots = []

    while try_another_page:
        # Pages are numbered from 1 to x. This loop will continue to take the next page until TypeError
        try:
            url_to_get_lots_from = child_url_template + str(current_page)
            scraped_lots += scrape_information_from_lots(url_to_get_lots_from)
            current_page += 1
        except TypeError:
            return scraped_lots
    return None  # This is not really a possible outcome. Added to make mypy happy and for consistency.


def scrape_all_department_names(lots_url: str) -> List[str]:
    page = get_page(lots_url)
    soup = get_soup(page.content)
    search_filters_boxes = soup.find_all("ul", class_="c-search-filters__box")

    search_filters = []

    for box in search_filters_boxes:
        for option in box.find_all("a"):
            search_filters.append(option.string)

    return [
        search_filter
        for search_filter in search_filters
        if search_filter not in NON_DEPARTMENT_SEARCH_FILTERS
    ]


def replace_url_unfriendly_characters_in_department_name(department: str) -> str:
    return (
        department.replace(" &", "")
        .replace(" ", "-")
        .lower()
        .replace("ö", "o")
        .replace("å", "a")
        .replace("ä", "a")
    )


def create_url_friendly_department_names(departments: List[str]) -> List[str]:
    url_friendly_department_names = []
    for department in departments:
        url_friendly_name = replace_url_unfriendly_characters_in_department_name(
            department
        )
        url_friendly_department_names.append(url_friendly_name)
    return url_friendly_department_names


def scrape_lots_by_department(auction_url: str) -> pd.DataFrame:
    departments = scrape_all_department_names(auction_url)
    print("Found", len(departments), "departments.")
    print(departments)

    url_friendly_departments = create_url_friendly_department_names(departments)

    if len(departments) == 0:
        lots = scrape_lots_from_all_subpages(auction_url)
        return pd.DataFrame(lots)

    department_dfs = []

    for department in url_friendly_departments:
        department_url = auction_url + "/department/" + department
        department_lots = scrape_lots_from_all_subpages(department_url)
        department_df = pd.DataFrame(department_lots)
        department_df["department"] = department
        print(f"Number of scraped objects in department: {department_df.shape[0]}")
        department_dfs.append(department_df)
    full_auction_df = pd.concat(department_dfs, ignore_index=True)
    print(f"[bold]Number of scraped objects in auction[/]: {full_auction_df.shape[0]}")
    return full_auction_df


if __name__ == "__main__":
    print(scrape_lots_by_department(AUCTION_URL))
