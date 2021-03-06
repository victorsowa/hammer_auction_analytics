from typing import List, Tuple, Iterable

from shared import get_page, get_soup

PREVIOUS_AUCTIONS_URL = "https://www.bukowskis.com/sv/auctions/past/hammer"


def scrape_auction_names_and_year(
    previous_auctions_url: str,
) -> Iterable[Tuple[int, List[str]]]:
    page = get_page(previous_auctions_url)
    soup = get_soup(page.content)

    auction_years = scrape_auction_years(soup)
    auction_names = scrape_auction_names(soup)

    return zip(auction_years, auction_names)


def scrape_auction_years(previous_auction_soup) -> List[int]:
    auction_year_divs = previous_auction_soup.find_all("div", class_="s-markdown")
    return [
        int(year.find("h2").string)
        for year in auction_year_divs
        if year.find("h2") is not None
    ]


def scrape_auction_names(previous_auction_soup) -> List[List[str]]:
    auction_grids = previous_auction_soup.find_all("ul", class_="c-grid")
    auction_name_grid_divs = [
        grid.find_all("div", class_="c-auctions__name") for grid in auction_grids
    ]
    return [
        [auction_name.string for auction_name in auction_name_divs]
        for auction_name_divs in auction_name_grid_divs
    ]


if __name__ == "__main__":
    scrape_auction_names_and_year(PREVIOUS_AUCTIONS_URL)
