from .. import settings
from .. import funcs
from .. import db
from ..funcs import cast, get_input
from question import Question, \
    McqQuestion, DevQuestion, ExactQuestion, ApproxQuestion, CodeQuestion, \
    create_question, load_question


class Course:
    def __init__(self, course_id=None):
        if course_id:
            self.load_course(course_id)
        else:
            self._id = funcs.generate_uuid()
            self.tag = ""

            self.set_tag_from_input()

    def load_course(self, course_id):
        course_dic = db.retrieve_sample_from_table(
                                    course_id,
                                    settings.__PATH_EXAMS__)

        self.set_tag_from_existing(course_dic)

    def set_tag_from_input(self):
        self.tag = get_input("Enter the course Tag")

    def set_tag_from_existing(self, exportable):
        self.tag = exportable['description']
