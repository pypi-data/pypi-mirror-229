from typing import List

from pathlib import Path

import yaml

from datafest_archive.builder.templating import jinja_environment
from datafest_archive.constants import (
    CONTENT_SEMESTER_DIRECTORY,
    INDEX_REGULAR_PAGE,
    ROLE_ADVISOR,
    ROLE_STUDENT,
    SEMESTER_ADVISORS_PAGE,
    SEMESTER_PROJECTS_PAGE,
    SEMESTER_STUDENTS_PAGE,
)
from datafest_archive.models.database import Edition, Project, Semesters
from datafest_archive.models.website.pages import (
    DesignProject,
    PeopleContent,
    PeopleWidget,
    WidgetPage,
)
from datafest_archive.utils import (
    create_directory,
    get_fall_starting_date,
    get_spring_starting_date,
)


def generate_datetime_from_event(edition: Edition) -> str:
    if edition.semester and edition.semester == Semesters.FALL:
        return get_fall_starting_date(edition.year)
    elif edition.semester and edition.semester == Semesters.SPRING:
        return get_spring_starting_date(edition.year)
    return str(None)


def generate_edition_url(year: int, semester: str) -> str:
    name = f"{CONTENT_SEMESTER_DIRECTORY}/{year}-{semester}"
    return name.lower()


def generate_edition_directory(
    edition: Edition, projects: list[Project], content_directory: Path
):
    # filter the projects by the edition
    semester_projects = [
        project
        for project in projects
        if project.semester == edition.semester and project.year == edition.year
    ]

    semester_advisors = [
        advisor for project in semester_projects for advisor in project.advisors
    ]

    semester_students = [
        student for project in semester_projects for student in project.students
    ]

    role_advisor = f"{ROLE_ADVISOR} ({edition.semester} {edition.year})"
    role_student = f"{ROLE_STUDENT} ({edition.semester} {edition.year})"

    edition_directory = generate_edition_url(edition.year, edition.semester)
    project_edition_directory = create_directory(content_directory / edition_directory)
    with open(project_edition_directory / SEMESTER_PROJECTS_PAGE, "w") as f:
        f.write(generate_edition_projects_page(edition, semester_projects))
    with open(project_edition_directory / SEMESTER_ADVISORS_PAGE, "w") as f:
        f.write(generate_edition_people_page(edition, role_advisor, "Advisors"))
    with open(project_edition_directory / INDEX_REGULAR_PAGE, "w") as f:
        f.write(generate_index_page())
    if semester_students:
        with open(project_edition_directory / SEMESTER_STUDENTS_PAGE, "w") as f:
            f.write(generate_edition_people_page(edition, role_student, "Students"))


def generate_index_page() -> str:
    content = {
        "type": "widget_page",
    }
    structured_content = yaml.dump(content)
    unstructured_content = ""
    return f"---\n{structured_content}\n---\n{unstructured_content}"


def generate_edition_people_page(edition: Edition, role: str, title: str) -> str:
    content = PeopleContent(
        user_groups=[role],
    )
    widget_page = PeopleWidget(
        title=title,
        subtitle=f"{edition.semester} {edition.year}",
        date=generate_datetime_from_event(edition),
        headless=True,
        widget="people",
        content=content,
    )
    structured_content = yaml.dump(widget_page)
    unstructured_content = ""
    return f"---\n{structured_content}\n---\n{unstructured_content}"


def generate_edition_projects_page(
    edition: Edition, projects: list[Project], filter_featured: bool = False
) -> str:
    title = f"{edition.semester} {edition.year} Projects"
    subtitle = f"{len(projects)} projects"
    date_created = generate_datetime_from_event(edition)
    tags = [f"{edition.semester} {edition.year}"]
    title = f"{edition.semester} {edition.year} Projects"
    design = DesignProject()
    portfolio = WidgetPage(
        title=title,
        subtitle=subtitle,
        date=date_created,
        type="landing",
        widget="markdown",
        headless=True,
        design=design,
    )
    structured_content = yaml.dump(portfolio)
    template = jinja_environment.get_template("semester_projects.md.jinja")
    unstructured_content = template.render(
        projects=projects,
    )
    return f"---\n{structured_content}\n---\n{unstructured_content}"
