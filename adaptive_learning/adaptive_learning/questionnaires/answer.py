"""
Manage answers
"""
from .. import funcs


class Answer:
    """
    Class to manage answers
    """
    def __init__(self):
        self._text = funcs.get_input("Enter the answer text")


    def make_exportable(self):
        """ Make a dictionary containing the settings """
        return {'text': self._text}


    def load(self, load_dic):
        """ Load settings from existing answer """
        self._text = load_dic['text']



class McqAnswer(Answer):
    """
    Manage MCQ answers
    """
    def __init__(self, load_dic=None):
        if load_dic:
            self.load(load_dic)
        else:
            Answer.__init__(self)
            self._is_correct = funcs.input_bool("Is correct?")
            self._use_answer = funcs.input_bool("Use answer?")


    def make_exportable(self):
        """ Make a dictionary containing the settings """
        exportable = super().make_exportable()
        exportable['is_correct'] = self._is_correct
        exportable['use_answer'] = self._use_answer
        return exportable


    def load(self, load_dic):
        """ Load settings from existing answer """
        super().load(load_dic=load_dic)
        self._is_correct = bool(load_dic['is_correct'])
        self._use_answer = bool(load_dic['use_answer'])



class DevAnswer(Answer):
    """
    Manage answers with development
    """



class ExactAnswer(Answer):
    """
    Manage exact answers
    """



class ApproxAnswer(Answer):
    """
    Manage approximated answers considered correct
    """



class CodeAnswer(Answer):
    """
    Manage answers as code
    """
