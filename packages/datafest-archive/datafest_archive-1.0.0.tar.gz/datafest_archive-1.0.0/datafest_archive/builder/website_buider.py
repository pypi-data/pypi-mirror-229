import logging
from pathlib import Path

from datafest_archive.builder.advisor_page_builder import generate_advisor_page
from datafest_archive.builder.page_builder import (
    create_advisor_directory,
    create_project_directory,
    create_student_directory,
)
from datafest_archive.builder.project_page_builder import generate_project_page
from datafest_archive.builder.semester_page_builder import generate_edition_directory
from datafest_archive.builder.student_page_builder import generate_student_page
from datafest_archive.models.database import Advisor, Edition, Project, Student
from datafest_archive.utils import write_file


def generate_website(
    projects: list[Project],
    advisors: list[Advisor],
    students: list[Student],
    content_directory: Path,
) -> None:
    generate_content(projects, advisors, students, content_directory)


def generate_content(
    projects: list[Project],
    advisors: list[Advisor],
    students: list[Student],
    content_directory: Path,
) -> None:
    editions: list[Edition] = []
    # this is to avoid name collisions
    rename_project_duplicates(projects)
    for project in projects:
        create_project(content_directory, project)
        add_editions(editions, project)

    for advisor in advisors:
        create_advisor(content_directory, advisor)

    for student in students:
        create_student(content_directory, student)

    for edition in editions:
        generate_edition_directory(edition, projects, content_directory)


def rename_project_duplicates(projects: list[Project]):
    for project in projects:
        project_name = project.name
        project_year = project.year
        for other_project in projects:
            if other_project.name == project_name and (
                other_project.year != project_year
                or other_project.semester != project.semester
            ):
                other_project.name = f"{other_project.name} ({other_project.semester} - {other_project.year})"


def create_student(content_directory, student):
    content = generate_student_page(student)
    student_page_path = create_student_directory(student, content_directory)
    validate_write(content, student_page_path)


def create_advisor(content_directory, advisor):
    content = generate_advisor_page(advisor)
    advisor_page_path = create_advisor_directory(advisor, content_directory)
    validate_write(content, advisor_page_path)


def create_project(content_directory, project):
    content = generate_project_page(project)
    project_page_path = create_project_directory(project, content_directory)
    validate_write(content, project_page_path)


def validate_write(content: str, resource_path: Path):
    try:
        write_file(content, resource_path)
    except ValueError as e:
        logging.error(f"Could not write file: {resource_path}")
        logging.error(e)


def add_editions(editions: list[Edition], project: Project) -> list[Edition]:
    edition = Edition(project.semester, project.year)
    if edition not in editions:
        editions.append(edition)
    return editions
