from typing import List

import yaml

from datafest_archive.builder.semester_page_builder import generate_edition_url
from datafest_archive.constants import (
    PREVIOUS_SEMESTERS_NAME,
    contact,
    info_for_advisors,
    info_for_students,
    people,
    projects,
)
from datafest_archive.models.database import Edition
from datafest_archive.models.website.configuration import Menu, MenuItem
from datafest_archive.models.website.pages import Pages
from datafest_archive.utils import dump_yaml


def get_static_menu_items() -> list[MenuItem]:
    return [info_for_advisors, info_for_students, projects, people, contact]


def generate_menu(editions: list[Edition]) -> str:
    menu_base = get_static_menu_items()
    menu_items = generate_menu_item(editions) + menu_base
    menu = Menu(_main=menu_items)
    return dump_yaml(menu)


def generate_menu_item(editions: list[Edition]) -> list[MenuItem]:
    menu_items: list[MenuItem] = []
    weight = 20
    # sort editions by year
    editions.sort(key=lambda x: x.year, reverse=True)
    for edition in editions:
        name = f"{edition.semester} {edition.year}"
        url_name = generate_edition_url(edition.year, edition.semester)
        menu_item = MenuItem(name, url_name, weight, PREVIOUS_SEMESTERS_NAME)
        menu_items.append(menu_item)
        weight += 1
    return menu_items


def generate_menu_page(pages: list[Pages]) -> str:
    return yaml.dump(pages)
