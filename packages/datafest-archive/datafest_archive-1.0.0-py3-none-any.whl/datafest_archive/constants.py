from datafest_archive.models.website.configuration import MenuItem

CONTENT_DIRECTORY = "content"
CONTENT_SEMESTER_DIRECTORY = "editions"
CONTENT_PEOPLE_DIRECTORY = "authors"
CONTENT_PROJECT_DIRECTORY = "projects"
CONFIG_DIRECTORY = "config"
INDEX_REGULAR_PAGE = "index.md"
INDEX_LIST_PAGE = "_index.md"
SEMESTER_ADVISORS_PAGE = "advisors.md"
SEMESTER_STUDENTS_PAGE = "students.md"
SEMESTER_PROJECTS_WINNER_PAGE = "projects-winner.md"
SEMESTER_PROJECTS_PAGE = "projects.md"

FEATURED_TAG_NAME = "Award-Winning Projects"
ALL_TAG_NAME = "All Projects"
FEATURED_TAG = "Featured"
ALL_TAG = "*"
MENUS_FILE_NAME = "menus.yaml"

ROLE_ADVISOR = "Advisor"
ROLE_STUDENT = "Student"

DATE_YEAR_FORMAT = "%Y"
DATE_YEAR_MONTH_DAY_FORMAT = "%Y-%m-%d"

WINTER = "Winter"
SPRING = "Spring"
SUMMER = "Summer"
FALL = "Fall"

PREVIOUS_SEMESTERS_NAME = "Previous Semesters"
# Menu items for the main menu

info_for_advisors = MenuItem(
    name="Info for Advisors", url="info-advisors", weight=1, parent=None
)
info_for_students = MenuItem(
    name="Info for Students", url="info-students", weight=2, parent=None
)
projects = MenuItem(
    name=PREVIOUS_SEMESTERS_NAME, url="previous-semesters", weight=3, parent=None
)
people = MenuItem(name="People", url="people", weight=4, parent=None)
contact = MenuItem(name="Contact", url="contact", weight=6, parent=None)
