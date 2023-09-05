import sqlite3
from pathlib import Path
from sqlite3 import Connection

from datafest_archive.models.database import Advisor, Project, SkillOrSoftware


class SQLITE_MANAGER:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.conn: Connection = sqlite3.connect(self.file_path)
        self.cursor = self.conn.cursor()

    def insert_project(self, project: Project) -> int:
        """
        Insert data into the table
        :param table_name: name of the table
        :param data: data to be inserted
        :return: id of the inserted row
        """
        existing_user = self.check_if_project_exists(project)
        if existing_user:
            print("Project already exists in the database")
            return existing_user[0]
        else:
            response = self.cursor.execute(
                "INSERT INTO project (name, semester, year, project_overview, final_presentation, student_learning) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    project.name,
                    project.semester,
                    project.year,
                    project.project_overview,
                    project.final_presentation,
                    project.student_learning,
                ),
            )
            self.conn.commit()
            if response and response.lastrowid:
                return response.lastrowid
            else:
                raise Exception("Could not insert project")

    def insert_advisor(self, advisor: Advisor):
        """
        Insert data into the table
        :param table_name: name of the table
        :param data: data to be inserted
        :return:
        """

        existing_user = self.check_if_advisor_exists(advisor)
        if existing_user:
            print("Advisor already exists in the database")
            return existing_user[0]
        else:
            response = self.cursor.execute(
                "INSERT INTO advisor (name, email ) VALUES (?, ?)",
                (advisor.name, advisor.email),
            )
            self.conn.commit()
            if response and response.lastrowid:
                return response.lastrowid
            else:
                raise Exception("Could not insert advisor")

    def insert_project_has_skill(self, project_id: int, skill: SkillOrSoftware):
        """
        Insert data into the table
        :param table_name: name of the table
        :param data: data to be inserted
        :return:
        """
        skill_name = skill.name
        skill_type = skill.type
        existing_skill = self.check_if_project_skill_exists(project_id, skill)
        if existing_skill:
            print("Skill already exists in the database")
            return existing_skill[0]
        else:
            response = self.cursor.execute(
                "INSERT INTO skill_or_software (project_id, name, type) VALUES (?, ?, ?)",
                (project_id, skill_name, skill_type),
            )
            self.conn.commit()
            if response and response.lastrowid:
                return response.lastrowid
            else:
                raise Exception("Could not insert project_has_skill")

    def insert_project_has_advisor(self, project_id: int, advisor_id: int):
        """
        Insert data into the table
        :param table_name: name of the table
        :param data: data to be inserted
        :return:
        """
        response = self.cursor.execute(
            "INSERT INTO project_has_advisor (project_id, advisor_id) VALUES (?, ?)",
            (project_id, advisor_id),
        )
        self.conn.commit()
        if response and response.lastrowid:
            return response.lastrowid
        else:
            raise Exception("Could not insert project_has_advisor")

    def check_if_project_skill_exists(self, project_id: int, skill: SkillOrSoftware):
        """
        Check if a project skill exists in the database
        :param project_id: project id
        :param skill: skill to check
        :return:
        """
        self.cursor.execute(
            "SELECT * FROM skill_or_software WHERE project_id = ? AND name = ? AND type = ?",
            (project_id, skill.name, skill.type),
        )
        return self.cursor.fetchone()

    def check_if_project_exists(self, project: Project):
        """
        Check if a project exists in the database
        :param project: project to check
        :return:
        """
        self.cursor.execute(
            "SELECT * FROM project WHERE name = ? AND semester = ? AND year = ?",
            (project.name, project.semester, project.year),
        )
        return self.cursor.fetchone()

    def check_if_advisor_exists(self, advisor: Advisor):
        """
        Check if an advisor exists in the database
        :param advisor: advisor to check
        :return:
        """
        self.cursor.execute(
            "SELECT * FROM advisor WHERE name = ? AND email = ?",
            (advisor.name, advisor.email),
        )
        return self.cursor.fetchone()

    def close_connection(self):
        """
        Close the connection to the database
        :return:
        """
        self.conn.close()
