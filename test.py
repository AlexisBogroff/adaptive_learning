"""
Main test file for adaptive learning engine
"""
import unittest
from unittest.mock import patch
from adaptive_learning import user, funcs, db
from adaptive_learning.questionnaires import exam
from adaptive_learning.questionnaires.exam import Exam
from adaptive_learning.questionnaires.question import Question, \
    create_question, McqQuestion
from adaptive_learning.questionnaires.answer import Answer, McqAnswer

class AnswerTestCase(unittest.TestCase):
    """
    Test methods of parent class Answer
    """

    @patch('adaptive_learning.funcs.get_input', return_value='Debug answer')
    def setUp(self, mock_input_text):
        """
        make a simple answer with the value 'Debug answer'
        """
        self.answer = Answer()

        """
        an answer in dict format to be exportable
        """
        self.ANSWER_DICT = {'text': 'Debug answer'}


    @patch('adaptive_learning.funcs.get_input', return_value='Debug answer')
    def test__init__(self, mock_input_text):
        """
        check that an answer is correctly create, check all it's attribute
        """
        obtained = self.answer._text
        expected = 'Debug answer'
        self.assertEqual(obtained, expected)


    def test_make_exportable(self):
        """
        check that an answer is able to be set in dict format to export in the database
        """
        obtained = self.answer.make_exportable()
        expected = self.ANSWER_DICT
        self.assertEqual(obtained, expected)


    def test_load(self):
        """
        check that an answer can be load from the database
        """
        self.answer.load(load_dic=self.ANSWER_DICT)
        obtained = self.ANSWER_DICT['text']
        expected = self.answer._text
        self.assertEqual(obtained, expected)


class McqAnswerTestCase(unittest.TestCase):
    """
    Test the creation and loading of an McqAnswer
    """
    @patch('adaptive_learning.funcs.get_input', return_value='Debug answer') # mock_input_text
    @patch('adaptive_learning.funcs.input_bool', side_effect=(True,True)) # mock_input_bool
    def setUp(self, mock_input_text,mock_input_bool):
        """
        make a simple MCQ answer with the value ('Debug answer', 'True', 'True')
        """
        self.answer_create = McqAnswer()
        """
        make the dict representation of our question to test load and make_exportable
        """
        self.MCQ_ANSWER_DICT = {'text': 'Debug answer',
                                'is_correct': True,
                                'use_answer': True}
        """
        load a simple MCQ answer with the value ('Debug answer', 'True', 'True')
        """
        self.answer_load = McqAnswer(load_dic=self.MCQ_ANSWER_DICT)


    def test__init__create(self):
        """
        check that an MCQ answer can be properly create
        """
        obtained = self.answer_create
        expected = self.MCQ_ANSWER_DICT

        self.assertEqual(obtained._text, expected['text'])
        self.assertEqual(obtained._is_correct,expected['is_correct'])
        self.assertEqual(obtained._use_answer,expected['use_answer'])

    def test__init__load(self):
        """
        check that an MCQ answer can be properly load
        """
        obtained = self.answer_load
        expected = self.MCQ_ANSWER_DICT

        self.assertEqual(obtained._text, expected['text'])
        self.assertEqual(obtained._is_correct,expected['is_correct'])
        self.assertEqual(obtained._use_answer,expected['use_answer'])

    def test_make_exportable(self):
        """
        check that an MCQ answer can change format to be exported in the database
        """
        obtained = self.answer_create.make_exportable()
        expected = self.MCQ_ANSWER_DICT
        self.assertEqual(obtained, expected)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ExamTestCase(unittest.TestCase):
    """
    Test the creation of an exam

    TODO: add tests for functions related to the .save method
    """

    INPUT_EXAM=('Title debug exam',         # exam text
                'Description debug exam',   # exam description
                'mcq',                      # question type
                'Debug question text',      # question text
                'keyword1, keyword2',       # question keywords
                'Debug answer',             # answer text
                'True',                     # is_correct
                'Yes',                      # use_answer
                'No')                       # compose new answer ?

    @patch('adaptive_learning.funcs.generate_uuid', return_value='40a8610b-93cc-4cb1-841f-6d9c68361ad0') # mock_input_id
    @patch('builtins.input', side_effect=INPUT_EXAM)
    def setUp(self, mock_input_id, mock_inputs):
        self.exam = Exam()
        # example of default properties of an exam
        self.EXAM_DICT = {
            'id': '40a8610b-93cc-4cb1-841f-6d9c68361ad0',
            'title': 'Title debug exam',
            'description': 'Description debug exam',
            'randomize_questions': True,
            'auto_rebase_grade': True,
            'grade_base': 20,
            'questions': [],
        }

#     """
#     Test the creation of an exam
#     """
    def test__init_id_type(self):
        obtained = self.exam
        expected = self.EXAM_DICT
        self.assertEqual(obtained._id, expected['id'])
        self.assertEqual(obtained._title, expected['title'])
        self.assertEqual(obtained._description, expected['description'])
        self.assertEqual(obtained._randomize_questions, expected['randomize_questions'])
        self.assertEqual(obtained._auto_rebase_grade, expected['auto_rebase_grade'])
        self.assertEqual(obtained._grade_base, expected['grade_base'])
        self.assertEqual(obtained._randomize_questions, expected['randomize_questions'])
        self.assertIsNotNone(obtained._questions)


    def test_make_exportable(self):
        # Controls that:
        # - it returns a dictionary with the expected structure
        # - the following keys are included in the exportable (sort of dump)
        # - the corresponding values are correctly matching
        obtained = self.exam.make_exportable()
        expected = self.EXAM_DICT
        self.assertEqual(obtained['id'], expected['id'])
        self.assertEqual(obtained['title'], expected['title'])
        self.assertEqual(obtained['description'], expected['description'])
        self.assertEqual(obtained['randomize_questions'],expected['randomize_questions'])
        self.assertEqual(obtained['auto_rebase_grade'],expected['auto_rebase_grade'])
        self.assertEqual(obtained['grade_base'],expected['grade_base'])

    EXAM_DICT_LOAD = {
        'id': '40a8610b-93cc-4cb1-841f-6d9c68361ad0',
        'title': 'Title debug exam',
        'description': 'Description debug exam',
        'randomize_questions': True,
        'auto_rebase_grade': True,
        'grade_base': 20,
        'questions': [],
    }


    # @patch('adaptive_learning.db.retrieve_sample_from_table', return_value=TABLE_EXAMS_LONG)
    @patch('adaptive_learning.db.retrieve_sample_from_table', return_value=EXAM_DICT_LOAD)
    @patch('adaptive_learning.questionnaires.question.load_question', return_value=[])
    def test_load_exam(self, mock_input_exam, mock_input_question):
        # Almost duplicate of test_retrieve_exam_from_table
        self.exam.load_exam(exam_id=self.EXAM_DICT['id'])
        obtained = self.exam
        expected = self.EXAM_DICT
        self.assertEqual(obtained._id, expected['id'])
        self.assertEqual(obtained._title, expected['title'])
        self.assertEqual(obtained._description, expected['description'])
        self.assertEqual(obtained._randomize_questions,expected['randomize_questions'])
        self.assertEqual(obtained._auto_rebase_grade,expected['auto_rebase_grade'])
        self.assertEqual(obtained._grade_base,expected['grade_base'])
        self.assertEqual(obtained._questions,expected['questions'])



    def test_set_auto_rebase_grade_from_existing(self):
        self.exam.set_auto_rebase_grade_from_existing(self.EXAM_DICT)
        obtained = self.exam._auto_rebase_grade
        expected = self.EXAM_DICT['auto_rebase_grade']
        self.assertEqual(obtained, expected)


    def test_set_description_from_existing(self):
        self.exam.set_description_from_existing(self.EXAM_DICT)
        obtained = self.exam._description
        expected = self.EXAM_DICT['description']
        self.assertEqual(obtained, expected)


    def test_set_grade_base_from_existing(self):
        self.exam.set_grade_base_from_existing(self.EXAM_DICT)
        obtained = self.exam._grade_base
        expected = self.EXAM_DICT['grade_base']
        self.assertEqual(obtained, expected)


    def test_set_id_from_existing(self):
        self.exam.set_id_from_existing(self.EXAM_DICT)
        obtained = self.exam._id
        expected = self.EXAM_DICT['id']
        self.assertEqual(obtained, expected)

    @patch('builtins.input', return_value='new exam title')
    def test_set_title_from_input(self, mock_input):
        self.exam.set_title_from_input()
        self.assertEqual(self.exam._title, 'new exam title')
        # Restore default parameters
        self.setUp()


    @patch('builtins.input', return_value='new exam desc')
    def test_create_description_from_input(self, mock_input):
        self.exam.set_title_from_input()
        self.assertEqual(self.exam._title, 'new exam desc')
        # Restore default parameters
        self.setUp()


    @patch('builtins.input', return_value='False')
    def test_set_randomize_questions_from_input(self, mock_input):
        self.exam.set_randomize_questions_from_input()
        self.assertEqual(self.exam._randomize_questions, False)
        # Restore default parameters
        self.setUp()


    @patch('builtins.input', return_value='False')
    def test_set_auto_rebase_grade_from_input(self, mock_input):
        self.exam.set_auto_rebase_grade_from_input()
        self.assertEqual(self.exam._auto_rebase_grade, False)
        # Restore default parameters
        self.setUp()


    @patch('builtins.input', return_value='10')
    def test_set_grade_base_from_input(self, mock_input):
        self.exam.set_grade_base_from_input()
        self.assertEqual(self.exam._grade_base, 10)
        # Restore default parameters
        self.setUp()


    def test_set_randomize_questions_from_existing(self):
        self.exam.set_randomize_questions_from_existing(self.EXAM_DICT)
        obtained = self.exam._randomize_questions
        expected = self.EXAM_DICT['randomize_questions']
        self.assertEqual(obtained, expected)
        # Restore default parameters
        self.setUp()


    def test_set_title_from_existing(self):
        self.exam.set_title_from_existing(self.EXAM_DICT)
        obtained = self.exam._title
        expected = self.EXAM_DICT['title']
        self.assertEqual(obtained, expected)
        # Restore default parameters
        self.setUp()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class FuncsTestCase(unittest.TestCase):
    """
    Test the functions of general order
    """

    def test_cast_when_bool(self):
        obtained = funcs.cast('True', bool)
        expected = True
        self.assertEqual(obtained, expected)


    def test_cast_when_int(self):
        obtained = funcs.cast('12', int)
        expected = 12
        self.assertEqual(obtained, expected)


    def test_cast_when_float(self):
        obtained = funcs.cast('12', float)
        expected = 12.
        self.assertEqual(obtained, expected)


    def test_cast_when_not_possible(self):
        with self.assertRaises(TypeError) as context:
            funcs.cast('12', bool)

        expected = "The value: 12, of type <class 'str'>, " \
                   "cannot be casted into type: <class 'bool'>"
        self.assertTrue(expected in str(context.exception))

#     """
#     Can't find function from funcs package
#     """

class DbTestCase(unittest.TestCase):


    def test__extract_sample(self):
        """
        missing the _extract_sample function in db
        """
        data = [
            {'id': 123, 'foo1': 'bar1'},
            {'id': 433, 'foo2': 'bar2'},
        ]
        obtained = db._extract_sample(id=433, data=data)
        expected = [{'id': 433, 'foo2': 'bar2'}]
        self.assertEqual(obtained, expected)


    def test_get_single_elem(self):
        """
        missing the _extract_sample function in db
        """
        obtained = db.get_single_elem([4])
        expected = 4
        self.assertEqual(obtained, expected)


    def test_is_single_when_duplicate_found(self):
        table = [
            {'id':12, 'title': 'foo'},
            {'id':12, 'title': 'foobar'},
        ]
        obtained = db.is_single(table)
        self.assertFalse(obtained)


    def test_is_single_when_single_found(self):
        table = [
            {'id':12, 'title': 'foobar'},
        ]
        obtained = db.is_single(table)
        self.assertTrue(obtained)


    def test_is_empty_when_not_found(self):
        table = []
        obtained = db.is_empty(table)
        self.assertTrue(obtained)


    def test_is_empty_when_found(self):
        table = [
            {'id':12, 'title': 'foobar'},
        ]
        obtained = db.is_empty(table)
        self.assertFalse(obtained)


    TABLE_EXAMS_SHORT = [
        {'title': '', 'id': 'c85779fd', 'questions': [...]},
        {'title': '', 'id': '327e93a3', 'questions': [...]},
    ]
    @patch('adaptive_learning.db.load_table', return_value=TABLE_EXAMS_SHORT)
    def test_retrieve_sample_from_table(self, mock_table):
        obtained = db.retrieve_sample_from_table(id_sample='c85779fd',
                                                    path_table='')
        expected = {'title': '', 'id': 'c85779fd', 'questions': [...]}
        self.assertEqual(obtained, expected)


    TABLE_EMPTY = []
    @patch('adaptive_learning.db.load_table', return_value=TABLE_EMPTY)
    def test_retrieve_sample_from_table_when_is_empty(self, mock_table):
        with self.assertRaises(ValueError) as context:
            db.retrieve_sample_from_table(id_sample='c85779fd',
                                                    path_table='')
        self.assertTrue('Missing sample id c85779fd' in str(context.exception))


    TABLE_DUPLICATES = [
        {'title': '', 'id': 'c85779fd', 'questions': [...]},
        {'title': '', 'id': 'c85779fd', 'questions': [...]},
    ]
    @patch('adaptive_learning.db.load_table', return_value=TABLE_DUPLICATES)
    def test_retrieve_sample_from_table_when_duplicates(self, mock_table):
        with self.assertRaises(ValueError) as context:
            db.retrieve_sample_from_table(id_sample='c85779fd',
                                                    path_table='')
        self.assertTrue('Duplicate sample ids c85779fd' in str(context.exception))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class QuestionTestCase(unittest.TestCase):
    """
    Test the manipulations on questions and answers
    (create, amend, delete, launch, etc.)
    """
    @patch('adaptive_learning.funcs.generate_uuid', return_value='8148773d-773f-42a8-977a-4cbbcee752c1') # mock_input_id
    @patch('builtins.input', side_effect=('Debug question text', 'keyword1, keyword2')) # mock_input_text_keywords
    @patch('adaptive_learning.funcs.get_input', return_value='Debug answer')
    def setUp(self, mock_input_id, mock_input_text_keywords, mock_input_answer_text):
        """
        create a simple question with the attribute :
        """
        self.question = Question()
        """
        create a simple answer
        """
        self.answer = Answer()
        """
        dict format of our question
        """
        self.QUESTION_DICT = {
            'id': '8148773d-773f-42a8-977a-4cbbcee752c1',
            'text': 'Debug question text',
            'keywords': 'keyword1, keyword2',
            'use_question': True,
            'nb_points': 1.,
            'difficulty': 1,
            'answers': [],
        }

    def test__init__(self):
        """
        check the creation of a question
        """
        obtained = self.question
        expected = self.QUESTION_DICT
        self.assertEqual(obtained._id, expected['id'])
        self.assertEqual(obtained._text, expected['text'])
        self.assertEqual(obtained._keywords, expected['keywords'])
        self.assertEqual(obtained._use_question, expected['use_question'])
        self.assertEqual(obtained._nb_points, expected['nb_points'])
        self.assertEqual(obtained._difficulty, expected['difficulty'])
        self.assertEqual(obtained._answers, expected['answers'])


    # make exportable don't take the answer of the question in the database
    def test_make_exportable(self):
        """
        check that a question can be change to dict format
        """
        obtained = self.question.make_exportable()
        expected = self.QUESTION_DICT
        del expected['answers']
        self.assertEqual(obtained, expected)


    def test_load(self):
        """
        check that a load from the database can be change in a proper Question object
        from dict to Question
        """
        self.question.load(self.QUESTION_DICT)
        obtained = self.question
        expected = self.QUESTION_DICT
        self.assertEqual(obtained._id, expected['id'])
        self.assertEqual(obtained._text, expected['text'])
        self.assertEqual(obtained._keywords, expected['keywords'])
        self.assertEqual(obtained._use_question, expected['use_question'])
        self.assertEqual(obtained._nb_points, expected['nb_points'])
        self.assertEqual(obtained._difficulty, expected['difficulty'])
        self.assertEqual(obtained._answers, expected['answers'])


class McqQuestionTestCase(unittest.TestCase):
    """
    Test the manipulations with McqQuestion
    MCQ question need to have an answer
    """
    INPUT_MCQ_QUESTION = ('Debug question text',  # question text
                          'keyword1, keyword2',   # question keywords
                          'Debug answer',         # answer text
                          'True',                 # is_correct
                          'Yes',                  # use_answer
                          'No')                   # compose new answer ?

    INPUT_ANSWER = (
        'Debug answer',  # text
        'True',           # is_correct
        'Yes',            # use_answer
        'No',            # compose new answer ?
        # 'Text answer 2',  # text
        # 'False',          # is_correct
        # 'No',             # use_answer
        # 'No',             # compose new answer ?
    )


#     # @patch('builtins.input', side_effect=ONE_ANSWER)

    @patch('adaptive_learning.funcs.generate_uuid', return_value='8148773d-773f-42a8-977a-4cbbcee752c1') # mock_input_id
    @patch('builtins.input', side_effect=(INPUT_MCQ_QUESTION)) # mock_input
    def setUp(self,mock_input_id, mock_input):
        self.mcq_question = McqQuestion()
        self.MCQ_QUESTION_DICT = {
            'id': '8148773d-773f-42a8-977a-4cbbcee752c1',
            'type': 'mcq',
            'text': 'Debug question text',  #ONE_ANSWER[0]
            'keywords': 'keyword1, keyword2',  #ONE_ANSWER[1]
            'use_question': True,
            'nb_points': 1.,
            'difficulty': 1,
            'notif_correct_answers': True,
            'notif_num_exact_answers': False,
            'randomize_answers_order': True,
            'answers': [],
        }

    def test__init__(self):
        """
        check the creation of a MCQ question
        """
        obtained = self.mcq_question
        expected = self.MCQ_QUESTION_DICT
        self.assertEqual(obtained._id, expected['id'])
        self.assertEqual(obtained._type, expected['type'])
        self.assertEqual(obtained._text, expected['text'])
        self.assertEqual(obtained._keywords, expected['keywords'])
        self.assertEqual(obtained._use_question, expected['use_question'])
        self.assertEqual(obtained._nb_points, expected['nb_points'])
        self.assertEqual(obtained._difficulty, expected['difficulty'])
        self.assertEqual(obtained._notif_correct_answers, expected['notif_correct_answers'])
        self.assertEqual(obtained._notif_num_exact_answers, expected['notif_num_exact_answers'])
        # self.assertEqual(obtained._answers, expected['answers'])


    @patch('builtins.input', side_effect=INPUT_ANSWER)
    def test_add_answers(self, mock_inputs):
        self.assertEqual(self.mcq_question._answers[0]._text, 'Debug answer')
        self.assertTrue(self.mcq_question._answers[0]._is_correct)
        self.assertTrue(self.mcq_question._answers[0]._use_answer)


    INPUT_CREATE_QUESTION= ('mcq',) + INPUT_MCQ_QUESTION # type of the question + data to create a new question

    @patch('builtins.input', side_effect=INPUT_CREATE_QUESTION) # mock_inputs
    def test_create_question(self, mock_inputs):
        # mcq_q = create_question()
        obtained = create_question()
        expected = self.MCQ_QUESTION_DICT
        self.assertEqual(obtained._type, expected['type'])
        self.assertEqual(obtained._text, expected['text'])
        self.assertEqual(obtained._keywords, expected['keywords'])
        self.assertEqual(obtained._use_question, expected['use_question'])
        self.assertEqual(obtained._nb_points, expected['nb_points'])
        self.assertEqual(obtained._notif_correct_answers,expected['notif_correct_answers'])
        self.assertEqual(obtained._answers[0]._text, 'Debug answer')
        self.assertTrue(obtained._answers[0]._is_correct)
        self.assertTrue(obtained._answers[0]._use_answer)


    def test_load(self):
        self.mcq_question.load(self.MCQ_QUESTION_DICT)
        obtained = self.mcq_question
        expected = self.MCQ_QUESTION_DICT
        self.assertEqual(obtained._id, expected['id'])
        self.assertEqual(obtained._text, expected['text'])
        self.assertEqual(obtained._keywords, expected['keywords'])
        self.assertEqual(obtained._use_question, expected['use_question'])
        self.assertEqual(obtained._nb_points, expected['nb_points'])
        self.assertEqual(obtained._difficulty, expected['difficulty'])


    def test_make_exportable(self):
        obtained = self.mcq_question.make_exportable()
        expected = self.MCQ_QUESTION_DICT
        del obtained['answers']
        del expected['answers']
        self.assertEqual(obtained, expected)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class UserMethodsTestCase(unittest.TestCase):
    """
    Test the user methods
    TODO: test user rights
    """
    def test_extract_mail_domain(self):
        expected_domain = 'univ-paris1.fr'
        mail_address = 'test_mail-pi@univ-paris1.fr'
        obtained_domain = user.extract_mail_domain(mail_address)
        self.assertEqual(expected_domain, obtained_domain)


    def test_get_school_mail_domain(self):
        school_mail_domain_1 = user.get_school_mail_domain('paris1')
        school_mail_domain_2 = user.get_school_mail_domain('esilv')
        self.assertEqual(school_mail_domain_1, 'univ-paris1.fr')
        self.assertEqual(school_mail_domain_2, 'edu.devinci.fr')


    def test_student_is_from_this_school(self):
        school_name = 'paris1'
        student_mail = 'stu_1@univ-paris1.fr'
        is_from_this_school = user.student_is_from_this_school(
            student_mail,
            school_name)
        self.assertTrue(is_from_this_school)





if __name__ == '__main__':
    unittest.main()
