"""
Interact with db
"""
import json
from . import settings
from . import funcs


def _extract_sample(id, data):
    """
    Extract the specific sample

    Hopefully returns a singleton (a list with only one element).

    Args:
        id: the id of elemnt to extract
        data: a list containing dictionaries, the latter having the key 'id'.

    data = [
        {'id': 123, 'foo1': 'bar1'},
        {'id': 433, 'foo2': 'bar2'},
        ...
    ]

    Returns:
        a list of the matching samples
    """
    samples = [sample for sample in data if sample['id'] == id]
    return samples


def is_empty(data):
    """
    Check that input contains an element

    Args:
        data (list)
    """
    if data:
        return False
    else:
        return True


def get_single_elem(list_):
    """ Get the first and only element of a list """
    return list_[0]


def is_single(data):
    """
    Check data contains a single sample

    Args:
        data (list)
    """
    if len(data) == 1:
        return True
    else:
        return False


def load_table(f_path):
    """
    Loads data from a text file

    Returns:
        the whole file content in a list

    TODO: add a method to load only part of the file
    """
    with open(f_path, 'r') as library:
        table = [json.loads(row) for row in library]
    return table


def show_table(table, fields):
    """
    Display a table

    Implementation is currently for command-line use

    Args:
        fields: list of fields to display
    """
    for row in table:
        text = [(key, row[key]) for key in fields]
        print(*text)


def select_exams():
    """ Display the list of exams stored in db """
    table = load_table(f_path=settings.__PATH_EXAMS__)
    show_table(table, ['title', 'id'])


def show_questions():
    """ Display the list of questions stored in db """
    table = load_table(f_path=settings.__PATH_QUESTIONS__)
    show_table(table, ['text', 'id'])


def retrieve_sample_from_table(id_sample, path_table):
    """
    Retrieve unique sample from table given its id

    Args:
        id_sample: the id of the sample to retrieve
        path_table: the path to the table containing the sample

    Returns:
        dictionary containing the unique sample
    """
    table = load_table(f_path=path_table)
    extracted = _extract_sample(id_sample, table)

    if is_empty(extracted):
        raise ValueError("Missing sample id {}".format(id_sample))

    if not is_single(extracted):
        raise ValueError("Duplicate sample ids {}".format(id_sample))

    sample_unique = get_single_elem(extracted)
    return sample_unique
