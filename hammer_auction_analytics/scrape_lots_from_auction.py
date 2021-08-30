import pandas as pd

from scrape_lots_from_lot_page import get_information_from_lots, get_page, get_soup

AUCTION_URL = "https://www.bukowskis.com/auctions/567/lots"

NON_DEPARTMENT_SEARCH_FILTERS = [
    "Kortast tid kvar",
    "Lägsta utropspris",
    "Högsta utropspris",
    "Bokstavsordning",
    "Endast favoriter",
]


def get_lots_from_all_subpages(parent_url):
    current_page = 1
    try_another_page = True

    child_url_template = parent_url + "/page/"

    print(child_url_template)
    scraped_lots = []

    while try_another_page:
        try:
            url_to_get_lots_from = child_url_template + str(current_page)
            scraped_lots += get_information_from_lots(url_to_get_lots_from)
            current_page += 1
        except TypeError:
            return scraped_lots


def get_all_departments(lots_url):
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


def get_url_friendly_department_names(departments):
    url_friendly_department_names = []
    for department in departments:

        url_friendly_name = (
            department.replace(" ", "-")
            .lower()
            .replace("ö", "o")
            .replace("å", "a")
            .replace("ä", "a")
        )
        url_friendly_department_names.append(url_friendly_name)
    return url_friendly_department_names


def get_lots_by_department(auction_url):
    departments = get_all_departments(auction_url)
    url_friendly_departments = get_url_friendly_department_names(departments)

    if len(departments) == 0:
        return get_lots_from_all_subpages(auction_url)

    department_dfs = []

    for department in url_friendly_departments:
        department_url = auction_url + "/department/" + department
        department_lots = get_lots_from_all_subpages(department_url)
        department_df = pd.DataFrame(department_lots)
        department_df["department"] = department
        department_dfs.append(department_df)

    return pd.concat(department_dfs, ignore_index=True)


if __name__ == "__main__":
    print(get_lots_by_department(AUCTION_URL))
