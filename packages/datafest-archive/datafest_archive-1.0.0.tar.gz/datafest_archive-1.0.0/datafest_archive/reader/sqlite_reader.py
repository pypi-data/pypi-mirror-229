import sqlite3
from pathlib import Path

from datafest_archive.builder.website_buider import generate_website
from datafest_archive.models.database import (
    Advisor,
    Award,
    Project,
    SkillOrSoftware,
    Student,
    Topic,
)
from datafest_archive.utils import (
    full_name_to_first_and_last_name,
    people_name_to_directory_name,
)

PROJECT_KEY = "projects"
ADVISOR_KEY = "advisors"


def handle_sqlite(file: Path, content_directory: Path):
    connection = sqlite3.connect(file)
    cursor = connection.cursor()
    projects = get_projects(cursor)
    advisors = get_advisors(cursor)
    students = get_students(cursor)
    generate_website(
        projects=projects,
        advisors=advisors,
        students=students,
        content_directory=content_directory,
    )


def get_projects(cursor: sqlite3.Cursor) -> list[Project]:
    projects: list[Project] = []
    cursor.execute("SELECT * FROM project")
    for row in cursor.fetchall():
        project = Project(
            id=row[0],
            name=row[1],
            semester=row[2],
            year=row[3],
            project_overview=row[4],
            final_presentation=row[5],
            student_learning=row[6],
        )
        projects.append(project)
        if project.id is None:
            raise ValueError("Project id is None")
        students = get_students_by_project_id(cursor, project.id)
        advisors = get_advisors_by_project_id(cursor, project.id)
        topics = get_topics_by_project_id(cursor, project.id)
        awards = get_awards_by_project_id(cursor, project.id)
        skills = get_skills_by_project_id(cursor, project.id)
        project.topics = topics
        project.skill_required = skills
        project.awards = awards
        project.advisors = advisors
        project.students = students
        projects.append(project)
    return projects


def get_skills_by_project_id(
    cursor: sqlite3.Cursor, project_id: int
) -> list[SkillOrSoftware]:
    skills: list[SkillOrSoftware] = []
    cursor.execute(
        "SELECT name, type FROM skill_or_software WHERE project_id = ?",
        (project_id,),
    )
    for row in cursor.fetchall():
        skill = SkillOrSoftware(name=row[0], type=row[1])
        skills.append(skill)
    return skills


def get_topics_by_project_id(cursor: sqlite3.Cursor, project_id: int) -> list[Topic]:
    topics: list[Topic] = []
    cursor.execute(
        "SELECT id, topic FROM project_has_topic WHERE id = ?",
        (project_id,),
    )
    for row in cursor.fetchall():
        topic = Topic(name=row[1])
        topics.append(topic)
    return topics


def get_awards_by_project_id(cursor: sqlite3.Cursor, project_id: int) -> list[Award]:
    awards: list[Award] = []
    cursor.execute(
        "SELECT project_id, award FROM project_has_award WHERE project_id = ?",
        (project_id,),
    )
    for row in cursor.fetchall():
        award = Award(name=row[1])
        awards.append(award)
    return awards


def get_students_by_project_id(
    cursor: sqlite3.Cursor, project_id: int
) -> list[Student]:
    students: list[Student] = []
    cursor.execute(
        "SELECT * FROM student WHERE student.id IN (SELECT student_id FROM project_has_student WHERE project_id = ?)",
        (project_id,),
    )
    for row in cursor.fetchall():
        semesters_participated = get_semesters_by_student_id(cursor, row[0])
        student = Student(
            id=row[0],
            name=row[1],
            email=row[2],
            degree_program=row[3],
            school=row[4],
            semesters_participated=semesters_participated,
        )
        students.append(student)
    return students


def get_semesters_by_student_id(cursor: sqlite3.Cursor, student_id: int):
    if student_id:
        semester_participated: list[str] = []
        for project in get_projects_by_student_id(cursor, student_id):
            semester = f"{project.semester} {project.year}"
            if semester not in semester_participated:
                semester_participated.append(semester)

        return semester_participated


def get_semester_advisor(cursor: sqlite3.Cursor, advisor: Advisor):
    if advisor.id:
        semester_participated: list[str] = []
        for project in get_projects_by_advisor_id(cursor, advisor.id):
            semester = f"{project.semester} {project.year}"
            if semester not in semester_participated:
                semester_participated.append(semester)

        return semester_participated


def get_advisors_by_project_id(
    cursor: sqlite3.Cursor, project_id: int
) -> list[Advisor]:
    advisors: list[Advisor] = []
    cursor.execute(
        "SELECT * FROM advisor WHERE advisor.id IN (SELECT advisor_id FROM project_has_advisor WHERE project_id = ?)",
        (project_id,),
    )
    for row in cursor.fetchall():
        advisor = Advisor(
            id=row[0],
            name=row[1],
            email=row[2],
            organization=row[3],
            primary_school=row[4],
        )
        advisor.semesters_participated = get_semester_advisor(cursor, advisor)
        advisors.append(advisor)
    return advisors


def get_advisors(cursor: sqlite3.Cursor) -> list[Advisor]:
    advisors: list[Advisor] = []
    cursor.execute("SELECT * FROM advisor")
    for row in cursor.fetchall():
        advisor = Advisor(
            id=row[0],
            name=row[1],
            email=row[2],
            organization=row[3],
            primary_school=row[4],
        )
        advisor.semesters_participated = get_semester_advisor(cursor, advisor)
        advisors.append(advisor)

    return advisors


def get_students(cursor: sqlite3.Cursor) -> list[Student]:
    students: list[Student] = []
    cursor.execute("SELECT * FROM student")
    for row in cursor.fetchall():
        semesters_participated = get_semesters_by_student_id(cursor, row[0])
        student = Student(
            id=row[0],
            name=row[1],
            email=row[2],
            degree_program=row[3],
            school=row[4],
            semesters_participated=semesters_participated,
        )
        first_name, last_name = full_name_to_first_and_last_name(student.name)
        student.url_name = people_name_to_directory_name(first_name, last_name)
        students.append(student)
    return students


def get_projects_by_student_id(
    cursor: sqlite3.Cursor, student_id: int
) -> list[Project]:
    projects: list[Project] = []
    cursor.execute(
        "SELECT * FROM project WHERE project.id IN (SELECT project_id FROM project_has_student WHERE student_id = ?)",
        (student_id,),
    )

    for row in cursor.fetchall():
        project = Project(
            id=row[0],
            name=row[1],
            semester=row[2],
            year=row[3],
            project_overview=row[4],
            final_presentation=row[5],
            student_learning=row[6],
        )
        projects.append(project)
    return projects


def get_projects_by_advisor_id(
    cursor: sqlite3.Cursor, student_id: int
) -> list[Project]:
    projects: list[Project] = []
    cursor.execute(
        "SELECT * FROM project WHERE project.id IN (SELECT project_id FROM project_has_advisor WHERE advisor_id = ?)",
        (student_id,),
    )

    for row in cursor.fetchall():
        project = Project(
            id=row[0],
            name=row[1],
            semester=row[2],
            year=row[3],
            project_overview=row[4],
            final_presentation=row[5],
            student_learning=row[6],
        )
        projects.append(project)
    return projects
