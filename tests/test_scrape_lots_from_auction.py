import sys
import os

folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../hammer_auction_analytics")
)
sys.path.insert(0, folder)

import pytest

from scrape_lots_from_auction import (
    create_url_friendly_department_names,
    replace_url_unfriendly_characters_in_department_name,
    scrape_all_department_names,
    scrape_lots_by_department,
)


AUCTION_WITH_DEPARTMENTS = "https://www.bukowskis.com/en/auctions/633/lots"
AUCTION_WITHOUT_DEPARTMENTS = "https://www.bukowskis.com/en/auctions/H022/lots"

RESULTS_FROM_AUCTION_WITH_DEPARTMENTS_BY_DEPARTMENT = scrape_lots_by_department(
    AUCTION_WITH_DEPARTMENTS
)


def test_replace_url_unfriendly_characters_in_department_name_special_character():
    department_name = "Silver & Objects of Vertu"

    url_friendly_name = replace_url_unfriendly_characters_in_department_name(
        department_name
    )

    assert url_friendly_name == "silver-objects-of-vertu"


def test_create_url_friendly_department_names_list_of_url_friendly_names():
    departments = ["Silver & Objects of Vertu", "Glass"]

    url_friendly_departments = create_url_friendly_department_names(departments)

    assert url_friendly_departments == ["silver-objects-of-vertu", "glass"]


def test_scrape_all_department_names_expected_departments():
    departments = scrape_all_department_names(AUCTION_WITH_DEPARTMENTS)
    assert departments == [
        "Furniture and Works of Art",
        "Silver & Objects of Vertu",
        "Carpets and textiles",
        "Glass",
        "Ceramics",
        "Jewellery",
        "Art",
        "Asian Ceramics & Works of Art",
    ]


def test_scrape_all_department_names_get_empty_list_where_there_are_no_departments():
    departments = scrape_all_department_names(AUCTION_WITHOUT_DEPARTMENTS)
    assert departments == []


def test_scrape_results_by_department_get_expected_departments():
    departments = RESULTS_FROM_AUCTION_WITH_DEPARTMENTS_BY_DEPARTMENT[
        "department"
    ].unique()
    assert departments.tolist() == [
        "furniture-and-works-of-art",
        "silver-objects-of-vertu",
        "carpets-and-textiles",
        "glass",
        "ceramics",
        "jewellery",
        "art",
        "asian-ceramics-works-of-art",
    ]
