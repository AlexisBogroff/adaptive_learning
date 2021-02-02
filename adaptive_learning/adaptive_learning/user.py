"""
Functions for managing users:
"""
import json
from adaptive_learning import settings



def get_school_mail_domain(school_name):
    """
    Get the school mail corresponding to
    the school name provided

    Args:
        school_name

    returns:
        the school mail domain
    """
    # Retrieve the school domain server from table file
    tab_schools = load_table_schools_info()
    school_mail_address = tab_schools[school_name]['mail_domain']
    return school_mail_address


def extract_mail_domain(mail_address):
    """
    Extract the mail domain from a mail
    address

    Args:
        mail_address

    returns:
        the mail domain
    """
    mail_domain = mail_address.split('@')[1]
    return mail_domain


def load_table_schools_info():
    """
    Returns the content of the json file
    in a dictionary
    """
    with open(settings.__PATH_TAB_SCHOOLS_INFOS__, 'r') as f_schools:
        table_schools_info = json.load(f_schools)

    return table_schools_info


def student_is_from_this_school(student_mail, school_name):
    """
    Controls that the student is a member of
    the school

    It tries to match the student mail domain
    with the mail domain of the specified school

    Args:
        student_mail
        school_name

    returns:
        bool
    """
    student_mail_domain = extract_mail_domain(student_mail)
    school_mail_domain = get_school_mail_domain(school_name)
    return student_mail_domain == school_mail_domain



class User:
    """
    Manage user
    """
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.mail = ''

    def __str__(self):
        return "{} {}: {}".format(self.first_name, self.last_name, self.mail)



class Teacher(User):
    """
    Manage teacher
    """
    def __init__(self, first_name, last_name):
        User.__init__(self, first_name, last_name)



class Student(User):
    """
    Manage student
    """
    pass


class StudentCertified(Student):
    """
    Manage student that is logged through its school student id
    """
    pass


class StudentIndependent(Student):
    """
    Manage student that is not logged through its school
    """
    pass


class Admin(User):
    """
    Manage admin
    """
    pass
