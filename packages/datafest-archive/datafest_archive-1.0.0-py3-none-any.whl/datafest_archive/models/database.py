from typing import Optional, Union

from dataclasses import dataclass
from enum import Enum

from dataclass_wizard import JSONWizard

from datafest_archive.constants import FALL, SPRING, SUMMER, WINTER
from datafest_archive.utils import (
    full_name_to_first_and_last_name,
    people_name_to_directory_name,
)


@dataclass
class Award(JSONWizard):
    name: str
    id: Optional[int] = None
    description: Optional[str] = None


@dataclass
class SkillOrSoftware:
    name: str
    type: str
    id: Optional[int] = None


@dataclass
class Topic:
    name: str
    id: Optional[int] = None


@dataclass
class People:
    name: str
    url_name: Union[str, None] = None

    def __post_init__(self):
        first_name, last_name = full_name_to_first_and_last_name(self.name)
        self.url_name = people_name_to_directory_name(first_name, last_name)


@dataclass
class Student(People):
    email: Optional[str] = None
    semesters_participated: Optional[list[str]] = None
    id: Optional[int] = None
    degree_program: Optional[str] = None
    school: Optional[str] = None


@dataclass
class Advisor(People):
    email: Optional[str] = None
    organization: Optional[str] = None
    semesters_participated: Optional[list[str]] = None
    title: Optional[str] = None
    primary_school: Optional[str] = None
    id: Optional[int] = None


@dataclass
class Project(JSONWizard):
    name: str
    semester: str
    year: int
    project_overview: str
    id: Optional[int] = None
    skill_required: Optional[list[SkillOrSoftware]] = None
    awards: Optional[list[Award]] = None
    topics: Optional[list[Topic]] = None
    students: Optional[list[Student]] = None
    final_presentation: Optional[str] = None
    advisors: Optional[list[Advisor]] = None
    student_learning: Optional[str] = None


class Semesters(Enum):
    FALL = FALL
    WINTER = WINTER
    SPRING = SPRING
    SUMMER = SUMMER


@dataclass
class Edition:
    semester: str
    year: int
