from typing import List

from datetime import datetime

from datafest_archive.builder.templating import jinja_environment
from datafest_archive.constants import DATE_YEAR_FORMAT, FEATURED_TAG
from datafest_archive.models.database import Award, Project
from datafest_archive.models.website.pages import DateTimeNone, ProjectPage
from datafest_archive.utils import dump_yaml


def generate_project_url(resource: Project) -> str:
    return f"{resource.year}-{resource.semester}"


def generate_datetime_from_project(project: Project) -> DateTimeNone:
    if project.year:
        return datetime.strptime(str(project.year), DATE_YEAR_FORMAT)
    return None


def build_project_structed_section(project: Project) -> ProjectPage:
    students = (
        [student.name for student in project.students] if project.students else []
    )
    advisors = (
        [advisor.name for advisor in project.advisors] if project.advisors else []
    )
    authors = students + advisors
    edition = f"{project.semester} {project.year}"
    topics = [topic.name for topic in project.topics] if project.topics else []
    tags = [edition] + topics

    if project.awards:
        tags.append(FEATURED_TAG)
        for award in project.awards:
            tags.append(award.name)

    project_date = generate_datetime_from_project(project)
    project_page = ProjectPage(
        title=project.name,
        date=str(project_date),
        summary=project.project_overview,
        authors=authors,
        tags=tags,
        categories=tags,
        external_link=None,
        image=None,
        url_code=None,
        url_pdf=None,
        url_slides=project.final_presentation,
        url_video=None,
        slides=project.final_presentation,
        weight=10,
    )
    return project_page


def awards_to_markdown(awards: list[Award]) -> str:
    awards_text = ""
    if awards:
        awards_text = "\n".join([f"- {award.name}" for award in awards])
        return f"""
        ## Awards
        {awards_text}
    """
    return awards_text


def build_project_unstructed_section(project: Project) -> str:
    template = jinja_environment.get_template("project_page.md.jinja")
    return template.render(
        project=project,
    )


def generate_project_page(project: Project) -> str:
    structed_section = build_project_structed_section(project)
    unstructed_section = build_project_unstructed_section(project)
    structed_section_yaml = dump_yaml(structed_section)
    return f"---\n{structed_section_yaml}---\n{unstructed_section}"
