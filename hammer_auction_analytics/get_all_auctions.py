from shared import get_page, get_soup

PREVIOUS_AUCTIONS_URL = "https://www.bukowskis.com/sv/auctions/past/hammer"


def get_all_auctions(previous_auctions_url):
    page = get_page(previous_auctions_url)
    soup = get_soup(page.content)

    auction_years = get_auction_years(soup)
    auction_names = get_auction_names(soup)

    return zip(auction_years, auction_names)


def get_auction_years(previous_auction_soup):
    auction_year_divs = previous_auction_soup.find_all("div", class_="s-markdown")
    return [
        int(year.find("h2").string)
        for year in auction_year_divs
        if year.find("h2") is not None
    ]


def get_auction_names(previous_auction_soup):
    auction_grids = previous_auction_soup.find_all("ul", class_="c-grid")
    auction_name_grid_divs = [
        grid.find_all("div", class_="c-auctions__name") for grid in auction_grids
    ]
    return [
        [auction_name.string for auction_name in auction_name_divs]
        for auction_name_divs in auction_name_grid_divs
    ]


if __name__ == "__main__":
    get_all_auctions(PREVIOUS_AUCTIONS_URL)
