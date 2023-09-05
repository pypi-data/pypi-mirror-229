from typing import Any

import datetime
import pathlib
import re

import yaml

from datafest_archive.constants import DATE_YEAR_FORMAT
from datafest_archive.models.website.configuration import Menu
from datafest_archive.models.website.pages import (
    Image,
    Organization,
    Page,
    ProjectPage,
    Social,
)


def project_page_representer(dumper: yaml.Dumper, data: ProjectPage) -> Any:
    data_dict = {
        "title": data.title,
        "summary": data.summary,
        "authors": data.authors,
        "tags": data.tags,
        "categories": data.categories,
        "date": data.date,
        "weight": data.weight,
        "external_link": data.external_link,
        "image": data.image,
        "url_code": data.url_code,
        "url_pdf": data.url_pdf,
        "url_slides": data.url_slides,
        "url_video": data.url_video,
        "slides": data.slides,
    }
    return dumper.represent_mapping("!ProjectPage", data_dict)


def organization_representer(dumper: yaml.Dumper, data: Organization) -> Any:
    return dumper.represent_mapping(
        "!Organization", {"name": data.name, "url": data.url}
    )


def image_representer(dumper: yaml.Dumper, data: Image):
    return dumper.represent_mapping(
        "!Image", {"path": data.path, "caption": data.caption}
    )


def social_representer(dumper: yaml.Dumper, data: Social):
    return dumper.represent_mapping(
        "!Social",
        {
            "icon": data.icon,
            "icon_pack": data.icon_pack,
            "link": data.link,
        },
    )


def menu_representer(dumper: yaml.Dumper, data: Menu):
    return dumper.represent_mapping(
        "!Menu",
        {"main": data.main},
    )


def get_dumper():
    """Add representers to a YAML seriailizer."""
    safe_dumper = yaml.Dumper
    safe_dumper.add_representer(ProjectPage, project_page_representer)
    safe_dumper.add_representer(Organization, organization_representer)
    safe_dumper.add_representer(Image, image_representer)
    safe_dumper.add_representer(Social, social_representer)
    safe_dumper.add_representer(Menu, menu_representer)
    return safe_dumper


def dump_yaml(page: Page) -> str:
    return yaml.dump(page, Dumper=get_dumper())


def create_directory(path: pathlib.Path) -> pathlib.Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_file(content: str, path: pathlib.Path):
    if path.is_dir():
        raise ValueError(f"Path {path} is a directory.")
    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    with open(path, "w") as f:
        f.write(content)


def sanitanize_name(name: str) -> str:
    """Sanitize a name for use in a directory name."""
    # remove non-alphanumeric characters
    return re.sub(r"\W+", "", name).lower()


def people_name_to_directory_name(first_name: str, last_name: str) -> str:
    """Convert a person's name to a directory name."""
    return f"{sanitanize_name(first_name)}-{sanitanize_name(last_name)}"


def full_name_to_first_and_last_name(full_name: str) -> tuple[str, str]:
    """Convert a person's full name to a first and last name."""
    split_name = full_name.split(" ")
    first_name = split_name[0]
    last_name = " ".join(split_name[1:])
    return first_name, last_name


def get_fall_starting_date(current_year: int) -> str:
    return datetime.datetime(current_year, 8, 1).strftime(DATE_YEAR_FORMAT)


def get_spring_starting_date(current_year: int) -> str:
    return datetime.datetime(current_year, 1, 1).strftime(DATE_YEAR_FORMAT)
