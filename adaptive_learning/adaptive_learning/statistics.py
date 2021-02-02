"""
function that will use all the information of the statistique.py file
function have to work for a test and a student result

Moyenne
Note_plus_basse
Note_plus_haute
Median
Q1
Q3
Frequence
"""

def statistics_view(request, input_id_test):
    """Function to get the statistics on a specific test
    Return the page of the statistics
    """
    # Get the info
    DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
    PassDynMCQInfo = PassDynMCQTestInfo.objects.filter(id_test=input_id_test)
    num_questions = get_questions(DynMCQTestInfo.questions)
    nb_questions = len(num_questions[0]) + len(num_questions[1])

    PassDynMCQInfo_List = []
    for instance in PassDynMCQInfo:
        PassDynMCQInfo_List.append(instance)
    marks_list = []

    statistiques_notes = []
    i = 0
    while i <= int(nb_questions):
        statistiques_notes.append(0)
        i += 1

    for instance in PassDynMCQInfo_List:
        statistiques_notes[instance.mark] += 1
        marks_list.append(instance.mark)

    # Computing min / max marks
    note_plus_basse = Note_plus_basse(marks_list)
    note_plus_haute = Note_plus_haute(marks_list)

    # Computing average mark
    moyenne_mcqtest = Moyenne(marks_list)
    nb_test = len(PassDynMCQInfo_List)

    # Computing Q1 and Q3
    q1 = Q1(marks_list)
    q3 = Q3(marks_list)

    # Computing median
    m = Mediane(marks_list)

    # Computing frequences
    total_freq = Frequences(statistiques_notes, PassDynMCQInfo_List)

    # Computing questions statistics
    stats_question = Statistique_question(DynMCQTestInfo)

    # Questions statistics percentages
    pourcentage_question = Pourcentage_stats_question(stats_question,
                                                      PassDynMCQInfo_List)

    total_statistics_question = []
    i = 0
    while i < len(stats_question):
        total_statistics_question.append(
            (stats_question[i], pourcentage_question[i]))
        i += 1

    # Creating graphs
    GraphsQuestions(stats_question, int(nb_questions))
    GraphsNote(total_freq, int(nb_questions))
    GraphsBoxplot(marks_list)

    context = {
        'DynMCQTestInfo': DynMCQTestInfo,
        'PassDynMCQInfo_List': PassDynMCQInfo_List,
        'moyenne_mcqtest': moyenne_mcqtest,
        'nb_test': nb_test,
        'note_plus_haute': note_plus_haute,
        'note_plus_basse': note_plus_basse,
        'q1': q1,
        'q3': q3,
        'mediane': m,
        'total_statistics_question': total_statistics_question,
        'total_freq': total_freq,
        'nb_questions': nb_questions,
    }
    return render(request, 'manage_tests/statistics.html', context)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
Moyenne
Note_plus_basse
Note_plus_haute
Median
Q1
Q3
Frequence
"""

def Moyenne(marks_list):
    """Function to compute the average of the mark list
    Parameter :
        marks_list (list) : list of the pass test marks
    Return :
        moyenne (float) : average
    """
    moyenne = 0
    for mark in marks_list:
        moyenne += mark
        # print("moyenne",moyenne)
    moyenne /= len(marks_list)
    # print("moyennetype",type(moyenne))
    moyenne = float("%.2f" % moyenne)
    # print("moyennetype",type(moyenne))
    return moyenne


def Note_plus_basse(marks_list):
    """Function to compute the minimal mark of the mark list
    Parameter :
        marks_list (list) : list of the pass test marks
    Return :
        note_plus_basse (int) : minimal mark
    """
    note_plus_basse = 1000
    for mark in marks_list:
        if mark < note_plus_basse:
            note_plus_basse = mark
    return note_plus_basse


def Note_plus_haute(marks_list):
    """Function to compute the maximal mark of the mark list
    Parameter :
        marks_list (list) : list of the pass test marks
    Return :
        note_plus_haute (int) : maximal mark
    """
    note_plus_haute = 0
    for mark in marks_list:
        if mark > note_plus_haute:
            note_plus_haute = mark
    return note_plus_haute


def Q1(marks_list):
    """Function to compute the first quarter of the mark list
    Parameter :
        marks_list (list) : list of the pass test marks
    Return :
        q1 (float) : first quarter
    """
    marks_list.sort()
    if len(marks_list) % 4 == 0:
        q1 = marks_list[len(marks_list) // 4 - 1]
    else:
        q1 = marks_list[len(marks_list) // 4]
    return q1


def Q3(marks_list):
    """Function to compute the third quarter of the mark list
    Parameter :
        marks_list (list) : list of the pass test marks
    Return :
        q3 (float) : third quarter
    """
    marks_list.sort()
    if len(marks_list) % 4 == 0:
        q3 = marks_list[3 * len(marks_list) // 4 - 1]
    else:
        q3 = marks_list[3 * len(marks_list) // 4]
    return q3


def Mediane(marks_list):
    """Function to compute the median of the mark list
    Parameter :
        marks_list (list) : list of the pass test marks
    Return :
        m (int) : median
    """
    marks_list.sort()
    if len(marks_list) % 2 == 0:
        m = ((marks_list[(len(marks_list) - 1) // 2] + marks_list[
            len(marks_list) // 2]) / 2)
    else:
        m = marks_list[len(marks_list) // 2]
    return m


def Frequences(statistiques_notes, PassDynMCQInfo_List):
    """Function to compute the frequences of the marks
    Parameter :
        statistiques_notes (list) : list of occurences of each marks
    Return :
        total_freq (list) : list of frequences of each marks
    """
    total_freq = []
    somme_freq = 0
    for note in statistiques_notes:
        temp_freq = 100 * note / len(PassDynMCQInfo_List)
        somme_freq += temp_freq
        temp_freq = "%.2f" % temp_freq
        som_freq = "%.2f" % somme_freq
        total_freq.append((temp_freq, som_freq))
    return total_freq


def Statistique_question(DynMCQTestInfo):
    """Function to compute the statistics for each questions of the test
    Parameter :
        DynMCQTestInfo (DynMCQTest instance) : the test instance
    Return :
        stats_question (list) : list of occurences of good answers
        for each questions
    """
    # Get questions
    num_questions = get_questions(DynMCQTestInfo.questions)
    stats_question = []
    mcq_question = num_questions[0]
    normal_questions = num_questions[1]
    i = 0
    while i < int(len(mcq_question) + len(normal_questions)):
        stats_question.append(0)
        i += 1

    # Get pass tests
    passdynmcqtest = PassDynMCQTest.objects.filter(
        id_test=DynMCQTestInfo.id_test)
    passdynquestiontest = PassDynquestionTest.objects.filter(
        id_test=DynMCQTestInfo.id_test)
    passdynmcqtest_List = []
    passdynquestiontest_List = []
    for instance in passdynmcqtest:
        passdynmcqtest_List.append(instance)
    for instance in passdynquestiontest:
        passdynquestiontest_List.append(instance)

    # For DynMCQanswer
    for passdynmcq in passdynmcqtest_List:
        tmp_dynmcqtest = DynMCQanswer.objects.filter(q_num=passdynmcq.q_num,
                                                     right_ans=1)
        num_right_answers = []
        for ans in tmp_dynmcqtest:
            num_right_answers.append(ans.ans_num)
        # If good answer, incrementing stats_question of the question
        if check_answer(passdynmcq.r_ans, num_right_answers):
            index = 0
            for i in range(len(mcq_question)):
                if (passdynmcq.q_num == mcq_question[i]):
                    index = i
            stats_question[index] += 1
    # For Dynquestion
    for passdynquestion in passdynquestiontest_List:
        dynquestion = Dynquestion.objects.get(q_num=passdynquestion.q_num)
        right_answer = dynquestion.r_text
        student_answer = passdynquestion.r_answer
        # If good answer, incrementing stats_question of the question
        if right_answer.lower() == student_answer.lower():
            index = 0
            for i in range(len(normal_questions)):
                if (passdynquestion.q_num == normal_questions[i]):
                    index = i + len(mcq_question)
            stats_question[index] += 1
    return stats_question


def Pourcentage_stats_question(stats_question, PassDynMCQInfo_List):
    """Function to compute the percentages statistics for each questions
    of the test
    Parameter :
        stats_question (list) : list of occurences of good answers
        for each questions
        PassDynMCQInfo_List (list) : list of pass test instance
    Return :
        pourcentage_question (list) : percentage of good answers
        for each questions
    """
    pourcentage_question = []
    for stat in stats_question:
        pourcentage = 100 * stat / len(PassDynMCQInfo_List)
        pourcentage = "%.2f" % pourcentage
        pourcentage_question.append(pourcentage)
    return pourcentage_question
