"""
Manage questions
"""
from .. import settings
from .. import funcs
from ..funcs import cast, get_input
from .. import db
from answer import Answer, McqAnswer


def create_question():
    """
    Generate the question of specific type defined by user

    Returns:
        question object
    """
    q_type = funcs.input_from_list(
        message="Choose question type",
        vals=['mcq', 'dev', 'exact', 'approx', 'code'])

    return generate_specific_question(q_type)


def generate_specific_question(q_type, question_dic=None):
    """
    Generate a question of type 'q_type'

    Returns:
        child question object

    Notes:
        It loads the question if question_dic is passed
        Otherwise, it creates a question
    """
    if q_type == 'mcq':
        return McqQuestion(load_dic=question_dic)
    elif q_type == 'dev':
        return DevQuestion(load_dic=question_dic)
    elif q_type == 'exact':
        return ExactQuestion(load_dic=question_dic)
    elif q_type == 'approx':
        return ApproxQuestion(load_dic=question_dic)
    elif q_type == 'code':
        return CodeQuestion(load_dic=question_dic)


def load_question(load_id=None, question_dic=None):
    """
    Load a specific question from the questions library

    Args:
        load_id: the id of the question to load from table
        question_dic: the question in dictionary format

    Returns:
        question object

    Note:
        At least one of the two args must be set.

        The question must be a specific object defined by its type (mcq, dev,
        etc.). Idem for its answers.
    """
    if not question_dic:
        question_dic = db.retrieve_sample_from_table(
                                    load_id,
                                    settings.__PATH_QUESTIONS__)
    q_type = question_dic['type']

    return generate_specific_question(q_type=q_type, question_dic=question_dic)



class Question:
    """
    Class for the questions

    They can be dealt independently (of exams) or be called in the creation
    of an exam. Answers however are only called within a question.

    TODO: add possibility to create question (by selecting the question type)
    from the Question class directly (for now, a question can only be created
    using the subclasses McqQuestion, etc.).
    """
    def __init__(self):
        self._id = funcs.generate_uuid()
        self._text = ""
        self._keywords = ""
        self._use_question = True
        self._nb_points = 1.
        self._difficulty = 1
        self._answers = []

        self.set_text_from_input()
        self.set_keywords_from_input() # TODO make a list


    def __str__(self):
        return "text: {text}, id: {id}".format(text=self._text, id=self._id)


    def load(self, load_dic):
        """ Set main properties to correspond to an existing question """
        self._id = load_dic['id']
        self._text = load_dic['text']
        self._keywords = load_dic['keywords']
        self._use_question = load_dic['use_question']
        self._nb_points = load_dic['nb_points']
        self._difficulty = load_dic['difficulty']


    def make_exportable(self):
        """
        Stores the main question properties in a dictionary

        Returns:
            the data in dic format, ready to export in json file
        """
        exportable = {
            'id': self._id,
            'text': self._text,
            'keywords': self._keywords,
            'use_question': self._use_question,
            'nb_points': self._nb_points,
            'difficulty': self._difficulty,
        }
        return exportable


    def save(self):
        """
        Stores the question in database

        It inserts the new content at the end of the file,
        on a new line, and takes a single line (each in json like format)

        Method should be executed one time only, when finished with the creation
        of the question. Otherwise, the question would be stored (with a new id)
        each time save method would be called.

        Notes:
            To increase performances, each question is stored in json format,
            even though the file is in text format.
            This enables to store new questions by appending them in the first
            empty rows, without the need to read and parse the whole file
            (which would be the case with a json file).
        """
        question_dump = self.make_exportable()
        funcs.append_to_file(question_dump, settings.__PATH_QUESTIONS__)


    def set_keywords_from_input(self):
        """ Set property keywords """
        self._keywords = get_input("Enter the question keywords")

    def set_text_from_input(self):
        """ Set property text """
        self._text = get_input("Enter the question text")

    def set_difficulty_from_input(self):
        """ Set property difficulty """
        ans = get_input("Enter the question difficulty")
        self._difficulty = cast(ans, int)

    def set_nb_points_from_input(self):
        """ Set property nb_points """
        ans = get_input("Enter the number of points")
        self._nb_points = cast(ans, float)

    def set_use_question_from_input(self):
        """ Set property use_question """
        ans = get_input("Use this question?")
        self._use_question = cast(ans, bool)


    def show(self):
        """
        Display the main question properties
        """
        text = "id: {id}\n" \
               "text: {text}\n" \
               "type: {type}\n" \
               "keywords: {keywords}\n\n" \
               "use_question: {use_question}\n" \
               "nb_points: {nb_points}\n" \
               "difficulty: {difficulty}\n" \
               .format(
                    id=self._id,
                    text=self._text,
                    keywords=self._keywords,
                    use_question=self._use_question,
                    nb_points=self._nb_points,
                    difficulty=self._difficulty,
                )
        print(text)


class McqQuestion(Question):
    """
    Manage an MCQ question

    Note:
        has an automatic grading system
        _notif_correct_answers: says if single or multiple answers TODO: rename
        _
    """
    def __init__(self, load_dic=None):
        if load_dic:
            self.load(load_dic=load_dic)
        else:
            Question.__init__(self)
            self._type = 'mcq'
            self._notif_correct_answers = True
            self._notif_num_exact_answers = False
            self._randomize_answers_order = True

            self.add_answers()


    def add_answers(self):
        """
        Add answers to the question
        """
        new_answer = True

        while new_answer:
            answer = McqAnswer()
            self._answers.append(answer)
            new_answer = funcs.input_bool("Create new answer?")


    def get_type(self):
        """ Get property type """
        return self._type

    def get_randomize(self):
        """ Get property randomize_answers_order """
        return self._randomize_answers_order

    def get_notif_exact_answers(self):
        """ Get property notif_num_exact_answers """
        return self._notif_num_exact_answers

    def get_notif_answers(self):
        """ Get property notif_correct_answers """
        return self._notif_correct_answers


    def load(self, load_dic):
        """
        Set the properties according to an existing question
        """
        super().load(load_dic=load_dic)
        self.type = load_dic['type']
        self.notif_correct_answers = load_dic['notif_correct_answers']
        self.notif_num_exact_answers = load_dic['notif_num_exact_answers']
        self.randomize_answers_order = load_dic['randomize_answers_order']
        self._answers = [McqAnswer(load_dic=ans) for ans in load_dic['answers']]


    def make_exportable(self):
        """
        Stores the question properties in a dictionary

        Returns:
            the data in dic format, ready to export in json file
        """
        exportable = super().make_exportable()
        exportable['type'] = self._type
        exportable['notif_correct_answers'] = self._notif_correct_answers
        exportable['notif_num_exact_answers'] = self._notif_num_exact_answers
        exportable['randomize_answers_order'] = self._randomize_answers_order
        exportable['answers'] = [ans.make_exportable() for ans in self._answers]
        return exportable


    def set_randomize(self):
        """ Set property randomize_answers_order """
        ans = get_input("Randomize answers order?")
        self.randomize_answers_order = cast(ans, bool)

    def set_notif_exact_answers(self):
        """ Set property notif_num_exact_answers """
        ans = get_input("Inform exact num?")
        self.notif_num_exact_answers = cast(ans, bool)

    def set_notif_answers(self):
        """ Set property notif_correct_answers """
        ans = get_input("Inform on num of answers?")
        self.notif_correct_answers = cast(ans, bool)


    def show_detailed(self):
        """
        Display the question properties
        """
        super().show()

        answers = self._answers
        if answers:
            text_answers = ["{}".format(ans.make_exportable()) for ans in answers]
            text_answers = "\n\t".join(text_answers)
        else:
            text_answers = "No answer registered"

        text = "type: {type}\n" \
               "notif_correct_answers: {notif_correct_answers}\n" \
               "notif_num_exact_answers: {notif_num_exact_answers}\n" \
               "randomize_answers_order: {randomize_answers_order}\n\n" \
               "answers\n" \
               "\t{text_answers}" \
               .format(
                    type=self._type,
                    notif_correct_answers=self._notif_correct_answers,
                    notif_num_exact_answers=self._notif_num_exact_answers,
                    randomize_answers_order=self._randomize_answers_order,
                    text_answers=text_answers,
                )
        print(text)




class DevQuestion(Question):
    """
    Manage questions with development

    Teacher must set the grade
    """
    def __init__(self, load_dic=None):
        Question.__init__(self)



class ExactQuestion(Question):
    """
    Manage questions with exact answers

    Automatic grading system
    """
    def __init__(self, load_dic=None):
        Question.__init__(self)



class ApproxQuestion(Question):
    """
    Manage questions with approximated answers considered correct

    Automatic grading system
    """
    def __init__(self, load_dic=None):
        Question.__init__(self)



class CodeQuestion(Question):
    """
    Manage questions with code as answers

    Semi-automatic grading system
    """
    def __init__(self, load_dic=None):
        Question.__init__(self)
