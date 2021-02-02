"""
Main settings file
"""

import os

dirname = os.path.dirname(__file__)

# Paths to db
__PATH_EXAMS__ = os.path.join(dirname,"data/table_exams.txt")

__PATH_QUESTIONS__ = os.path.join(dirname,"data/table_questions.txt")

__PATH_TAB_SCHOOLS_INFOS__ = os.path.join(dirname,"data/table_schools_info.json")

