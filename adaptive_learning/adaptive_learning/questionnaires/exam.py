"""
Manage exams
"""
#TODO: create a class db for functions interacting with tables
# and extracting data (e.g. extract_question)

from .. import settings
from .. import funcs
from .. import db
from ..funcs import cast, get_input
from question import Question, \
    McqQuestion, DevQuestion, ExactQuestion, ApproxQuestion, CodeQuestion, \
    create_question, load_question


class Exam:
    """
    Class to manage exams (create, load, modify, delete)

    Returns:
        default exam instance ready to be composed.

    Notes:
        grade_rebase: enables to obtain a grade on e.g. /20, although there
        are only e.g. 10 questions graded /1 point.
    """
    def __init__(self, exam_id=None):
        if exam_id:
            self.load_exam(exam_id)
        else:
            self._id = funcs.generate_uuid()
            self._title = ""
            self._description = ""
            self._randomize_questions = True
            self._auto_rebase_grade = True
            self._grade_base = 20
            self._questions = []

            self.set_title_from_input()
            self.set_description_from_input()
            self.add_questions()


    def __str__(self):
        return "title: {title}, id: {id}".format(title=self._title, id=self._id)


    def add_questions(self):
        """ Add new questions to exam """
        new_question = True

        while new_question:
            question = create_question()
            self._questions.append(question)
            new_question = funcs.input_bool("Create new question?")


    def load_question(self, load_id):
        """ Add existing question """
        # load_question()
        pass


    def make_exportable(self):
        """
        Stores exam properties in a dictionary

        Returns:
            the exam in dic format, ready to export in json file
        """
        data_export = {
            'id': self._id,
            'title': self._title,
            'description': self._description,
            'randomize_questions': self._randomize_questions,
            'auto_rebase_grade': self._auto_rebase_grade,
            'grade_base': self._grade_base,
            'questions': [q.make_exportable() for q in self._questions]
        }
        return data_export


    def load_exam(self, exam_id):
        """
        Load a specific exam from the exam table
        """
        exam_dic = db.retrieve_sample_from_table(
                                    exam_id,
                                    settings.__PATH_EXAMS__)

        self.set_id_from_existing(exam_dic)
        self.set_title_from_existing(exam_dic)
        self.set_description_from_existing(exam_dic)
        self.set_randomize_questions_from_existing(exam_dic)
        self.set_auto_rebase_grade_from_existing(exam_dic)
        self.set_grade_base_from_existing(exam_dic)
        self._questions = [load_question(question_dic=q) for q in exam_dic['questions']]


    def save(self):
        """
        Stores the exam in database

        It inserts the new content at the end of the file,
        on a new line, and takes a single line (each in json like format)

        Notes:
            To increase performances, each exam is stored in json format,
            even though the file is in text format.
            This enables to store new exams by appending them in the first empty
            rows, without the need to read and parse the whole file
            (which would be the case with a json file).

            A method should contol that no duplicates can be added to the db
        """
        exportable = self.make_exportable()
        funcs.append_to_file(exportable, settings.__PATH_EXAMS__)


    def set_auto_rebase_grade_from_existing(self, exportable):
        """ Load auto_rebase_grade parameter from existing exam """
        param = exportable['auto_rebase_grade']
        self._auto_rebase_grade = param

    def set_auto_rebase_grade_from_input(self):
        """ Set auto_rebase_grade property """
        auto_rebase = get_input("Activate automatic grade rebasing?")
        casted_auto_rebase = cast(auto_rebase, bool)
        self._auto_rebase_grade = casted_auto_rebase


    def set_description_from_existing(self, exportable):
        """ Load description from existing exam """
        self._description = exportable['description']

    def set_description_from_input(self):
        """ Set description """
        self._description = get_input("Enter the exam description")


    def set_grade_base_from_existing(self, exportable):
        """ Load grade_base parameter from existing exam """
        param = exportable['grade_base']
        self._grade_base = param

    def set_grade_base_from_input(self):
        """ Set grade_base property """
        grade_base = get_input("Enter the grade base")
        casted_grade_base = cast(grade_base, int)
        self._grade_base = casted_grade_base


    def set_id_from_existing(self, exportable):
        """ Load id from existing exam """
        self._id = exportable['id']


    def set_randomize_questions_from_existing(self, exportable):
        """ Load randomize_questions parameter from existing exam """
        param = exportable['randomize_questions']
        self._randomize_questions = param

    def set_randomize_questions_from_input(self):
        """ Set randomize_order property """
        randomize_order = get_input("Randomize questions order?")
        casted_randomize_order = cast(randomize_order, bool)
        self._randomize_questions = casted_randomize_order


    def set_title_from_existing(self, exportable):
        """ Load title from existing exam """
        self._title = exportable['title']

    def set_title_from_input(self):
        """ Set title """
        self._title = get_input("Enter the exam title")


    def show(self):
        """
        Display the exam properties
        """
        # TODO: split into multiple functions
        questions = self._questions
        if questions:
            text_questions = ["({nb_points}) {type}: {text}"\
                .format(nb_points=q.make_exportable()['nb_points'],
                        type=q.make_exportable()['type'],
                        text=q.make_exportable()['text']) \
                        for q in questions]

            text_questions = "\n\t".join(text_questions)
        else:
            text_questions = "No question registered"

        text_exam = \
            "id: {id}\n" \
            "title: {title}\n" \
            "description: {description}\n\n" \
            "randomize_questions: {randomize_questions}\n" \
            "auto_rebase_grade: {auto_rebase_grade}\n" \
            "grade_base: {grade_base}\n\n" \
            "questions\n" \
            "\t{text_questions}" \
            .format(
                    id=self._id,
                    title=self._title,
                    description=self._description,
                    randomize_questions=self._randomize_questions,
                    auto_rebase_grade=self._auto_rebase_grade,
                    grade_base=self._grade_base,
                    text_questions=text_questions,
                )
        print(text_exam)


    def update(self, id_exam):
        """
        Update an existing exam

        Notes:
            Implement a method to find a specific id in the db file, and get the
            corresponding row number. Then delete this row. Finally, add the
            updated version of the exam.
        """
        # TODO: Implement
        raise NotImplementedError


if __name__ == "__main__":
    exam = Exam()
    print(exam._id)
