from django.shortcuts import render, get_object_or_404, redirect
from django.forms import formset_factory
from .forms import DynMCQTestInfoForm,DynMCQquestionForm,DynMCQanswerForm,Pass_DynMCQTestForm,DynMCQquestionForm_question,DynMCQTestInfoForm,DynMCQTestInfoForm_questions,Question_difficulty_form,MCQQuestion_difficulty_form,DynMCQTestInfoForm_launch,DynquestionForm,Pass_DynquestionTestForm
from .models import DynMCQInfo,DynMCQquestion,DynMCQanswer,Pass_DynMCQTest,Pass_DynMCQTest_Info,Dynquestion,Pass_DynquestionTest
import matplotlib.pyplot as plt
import numpy as np
import datetime
import time as tm
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User,Group,Permission
from django.urls import reverse


def register_view(request):
	"""Function to create a user on the app :
	Render the register page and retreive the informations of the user via the POST method
	Then it creates the user and assign the groups to the user.
	
	Returns the login/register page of the site when registered
	"""
	if request.method == 'POST':
		#Retrieve the informations of the user
		last_name = request.POST['last_name']
		first_name = request.POST['first_name']
		email = request.POST['email']
		username = request.POST['username']
		password = request.POST['password']
		function = request.POST['function']
		group1 = request.POST['group1']
		group2 = request.POST['group2']
		#If the username is already taken, we display an error message and we refresh the page
		if User.objects.filter(username=username).exists():
			messages.info(request,'Username taken')
			return redirect('tests:register')
		#Same for email
		elif User.objects.filter(email=email).exists():
			messages.info(request,'Email already used')
			return redirect('tests:register')
		#Creates the user
		else:
			user = User.objects.create_user(username=username,password=password,last_name=last_name,first_name=first_name,email=email)
			#We assign the permissions to the user depending of the group
			if function == "Student":
				student = Group.objects.get(name='Student')
				user.groups.add(student)
			else:
				teacher = Group.objects.get(name='Teacher')
				user.groups.add(teacher)
			#Class group
			group_1 = Group.objects.get(name=group1)
			user.groups.add(group_1)
			if group2 != "None":
				group_2 = Group.objects.get(name=group2)
				user.groups.add(group_2)
			
			#We save the user and then render the login/register page of the app
			user.save()
			return redirect('/')
	else:
		return render(request,'register.html')

def login_view(request):
	"""Function to login on the app :
	Render the login page and retreive the informations of the user via the POST method
	Then it login the user on the app
	
	Returns the main page of the site
	"""
	if request.method == 'POST':
		#Retrive informations
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username,password=password)
		#If the user exists, we login him and then returns the main page of the site
		if user is not None:
			login(request,user)
			return redirect('/')
		#Else we display an error message and refresh the page
		else:
			messages.info(request,'Invalid user')
			return redirect('tests:login')
	else:
		return render(request,'login.html')
		
def logout_view(request):
	"""Function to logout the user then render the login/register page
	"""
	logout(request)
	return redirect('/')

@login_required
@permission_required('tests.can_create_test', raise_exception=True)
def test_create_view(request, *args, **kwargs):
	"""Function to render the page for managing test
	"""
	testlist_dynmcqtestinfo_all = DynMCQInfo.objects.all()

	context = {
		'testlist_dynmcqtestinfo_all':testlist_dynmcqtestinfo_all,
	}
	return render(request, 'manage_tests/test_create.html', context)

def DynMCQTest_menu_view(request):
	"""Function to create a DynMCQInfo test
	Render the menu page for the created test
	"""
	#Form of DynMCQTestInfo
	form = DynMCQTestInfoForm(request.POST or None)
	if form.is_valid():
		form.save()
		form = DynMCQTestInfoForm()
	
	#Get the tests
	DynMCQTestInfo_list_all = DynMCQInfo.objects.all()
			
	context = {
		'form': form,
		'DynMCQTestInfo_list_all' : DynMCQTestInfo_list_all,
	}
	return render(request, 'manage_tests/menu_dynmcqtest.html',context)
	
def Manage_questions_view(request):
	"""Function to manage the questions (DynMCQquestion and Dynquestion)
	Render the the manage page for questions
	"""
	#Get the questions
	DynMCQquestions = DynMCQquestion.objects.all()
	Dynquestions = Dynquestion.objects.all()
			
	context = {
		'DynMCQquestions' : DynMCQquestions,
		'Dynquestions' : Dynquestions,
	}
	return render(request, 'manage_tests/manage_questions.html',context)
	
def DynMCQquestion_select_menu_view(request, input_id_test):
	"""Function to put questions in the test if there are not questions in the test
	Returns the page to manage the test
	"""
	#Get the test informations
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	empty = False
	DynMCQquestionTestList = []
	DynquestionTestList = []
	#If there are questions in the test
	if(DynMCQTestInfo.questions != ""):
		num_questions = get_questions(DynMCQTestInfo.questions)#Get id number of the questions

		mcq_questions = num_questions[0]
		normal_questions = num_questions[1]
		#We get the question instances for both type of question in two list
		for i in range(len(mcq_questions)):
			DynMCQQuestion = DynMCQquestion.objects.get(q_num = mcq_questions[i])
			DynMCQquestionTestList.append(DynMCQQuestion)
		for i in range(len(normal_questions)):
			DynQuestion = Dynquestion.objects.get(q_num = normal_questions[i])
			DynquestionTestList.append(DynQuestion)

	form = []
	#If there are not questions in the test, we display the form to put questions in the test
	if len(DynMCQquestionTestList) == 0 and len(DynquestionTestList) == 0:
		empty = True
		QuestionsSet = formset_factory(DynMCQTestInfoForm_questions, extra = 2)#Two form for both question types
		#Three mandatory properties for formset 
		data = {
			'form-TOTAL_FORMS': 2,
			'form-INITIAL_FORMS': '0',
			'form-MAX_NUM_FORMS': '',
		}
	
		form = QuestionsSet()#Formset
		choices = []#Choice for DynMCQquestion
		choices2 = []#Choice for Dynquestion
		DynMCQquestions = DynMCQquestion.objects.all()
		Dynquestions = Dynquestion.objects.all()
		#Filling the choice for DynMCQquestion with [q_num,q_text] for each questions (q_text is displayed and q_num is the returned value)
		for question in DynMCQquestions:
			list = []
			list.append(int(question.q_num))
			list.append(question.q_text)
			choices.append(list)
		form[0].fields['questions'].choices = choices
		#Same for Dynquestion
		for question in Dynquestions:
			list = []
			list.append(int(question.q_num))
			list.append(question.q_text)
			choices2.append(list)
		form[1].fields['questions'].choices = choices2
		
		if request.method == 'POST':
			#Same code for method POST to put the data in the app
			form = QuestionsSet(request.POST)
			choices = []
			choices2 = []
			DynMCQquestions = DynMCQquestion.objects.all()
			Dynquestions = Dynquestion.objects.all()
			for question in DynMCQquestions:
				list = []
				list.append(int(question.q_num))
				list.append(question.q_text)
				choices.append(list)
			form[0].fields['questions'].choices = choices
			for question in Dynquestions:
				list = []
				list.append(int(question.q_num))
				list.append(question.q_text)
				choices2.append(list)
			form[1].fields['questions'].choices = choices2
		
			#If form is valid, we save the questions in the test
			if form.is_valid():
				test = form[0].save(commit = False)
				test2 = form[1].save(commit = False)
				DynMCQTestInfo.questions = "a" + test.questions + "b" + test2.questions #Save the questions as "a[MCQ_ids,...]b[Normal_question_ids,...]" in the test
				DynMCQTestInfo.save()
				
				empty = False
				#Then get the questions to display it on the page
				num_questions = get_questions(DynMCQTestInfo.questions)

				mcq_questions = num_questions[0]
				normal_questions = num_questions[1]
				for i in range(len(mcq_questions)):
					DynMCQQuestion = DynMCQquestion.objects.get(q_num = mcq_questions[i])
					DynMCQquestionTestList.append(DynMCQQuestion)
				for i in range(len(normal_questions)):
					DynQuestion = Dynquestion.objects.get(q_num = normal_questions[i])
					DynquestionTestList.append(DynQuestion)
			
	context = {
		'DynMCQquestionTestList': DynMCQquestionTestList,
		'DynquestionTestList': DynquestionTestList,
		'DynMCQTestInfo': DynMCQTestInfo,
		'form': form,
		'empty':empty,
	}
	return render(request, 'manage_tests/selectmenu_dynmcqtest.html',context)
	
def Question_reallocation_view(request, input_id_test):
	"""Function to reallocate the questions in the test.
	Display the form for filling the questions in the test.
	Returns the page for reallocate questions
	"""
	#Get the test info
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	
	#Get the actual questions
	num_questions = get_questions(DynMCQTestInfo.questions)
	empty = True

	DynMCQquestionTestList = []
	DynquestionTestList = []
	
	mcq_questions = num_questions[0]
	normal_questions = num_questions[1]
	#We put the questions in a list
	for i in range(len(mcq_questions)):
		DynMCQQuestion = DynMCQquestion.objects.get(q_num = mcq_questions[i])
		DynMCQquestionTestList.append(DynMCQQuestion)
	for i in range(len(normal_questions)):
		DynQuestion = Dynquestion.objects.get(q_num = normal_questions[i])
		DynquestionTestList.append(DynQuestion)
				
	QuestionsSet = formset_factory(DynMCQTestInfoForm_questions, extra = 2)
	#Three mandatory properties for formset 
	data = {
		'form-TOTAL_FORMS': 2,
		'form-INITIAL_FORMS': '0',
		'form-MAX_NUM_FORMS': '',
	}
	
	form = QuestionsSet()#Formset
	choices = []#Choice for DynMCQquestion
	choices2 = []#Choice for Dynquestion
	DynMCQquestions = DynMCQquestion.objects.all()
	Dynquestions = Dynquestion.objects.all()
	#Filling the choice for DynMCQquestion with [q_num,q_text] for each questions (q_text is displayed and q_num is the returned value)
	for question in DynMCQquestions:
		list = []
		list.append(int(question.q_num))
		list.append(question.q_text)
		choices.append(list)
	form[0].fields['questions'].choices = choices
	#Same for Dynquestion
	for question in Dynquestions:
		list = []
		list.append(int(question.q_num))
		list.append(question.q_text)
		choices2.append(list)
	form[1].fields['questions'].choices = choices2
	
	if request.method == 'POST':
		#Same code for method POST to put the data in the app
		form = QuestionsSet(request.POST)
		choices = []
		choices2 = []
		DynMCQquestions = DynMCQquestion.objects.all()
		Dynquestions = Dynquestion.objects.all()
		for question in DynMCQquestions:
			list = []
			list.append(int(question.q_num))
			list.append(question.q_text)
			choices.append(list)
		form[0].fields['questions'].choices = choices
		for question in Dynquestions:
			list = []
			list.append(int(question.q_num))
			list.append(question.q_text)
			choices2.append(list)
		form[1].fields['questions'].choices = choices2
		
		#If form is valid, we save the questions in the test
		if form.is_valid():
			test = form[0].save(commit = False)
			test2 = form[1].save(commit = False)
			DynMCQTestInfo.questions = "a" + test.questions + "b" + test2.questions #Save the questions as "a[MCQ_ids,...]b[Normal_question_ids,...]" in the test
			DynMCQTestInfo.save()
			
			empty = False
			num_questions = get_questions(DynMCQTestInfo.questions)

			#Then get the questions to display it on the page
			mcq_questions = num_questions[0]
			normal_questions = num_questions[1]
			DynMCQquestionTestList = []
			DynquestionTestList = []
			for i in range(len(mcq_questions)):
				DynMCQQuestion = DynMCQquestion.objects.get(q_num = mcq_questions[i])
				DynMCQquestionTestList.append(DynMCQQuestion)
			for i in range(len(normal_questions)):
				DynQuestion = Dynquestion.objects.get(q_num = normal_questions[i])
				DynquestionTestList.append(DynQuestion)
			
	context = {
		'DynMCQquestionTestList': DynMCQquestionTestList,
		'DynquestionTestList': DynquestionTestList,
		'DynMCQTestInfo': DynMCQTestInfo,
		'form': form,
		'empty':empty,
	}
	return render(request, 'manage_tests/question_reallocation.html',context)

def get_questions(questions):
	"""Function the extract the question ids of the test
	Parameter : 
		questions (str) : questions of the test for example : a[1,5,6]b[1,9,11] or a[4,5]b or ab[4,9,7]
	Returns :
		num_questions (list) : list of two list, num_questions[0] contains id_questions for MCQquestions and num_questions[1] contains id_questions for Normal questions
	"""
	num_questions = []
	#Case where there are both MCQ and normal questions in the test so questions as a[1,5,6]b[1,9,11]
	if "]b[" in questions:
		num_questions = questions.split("]b[")
		num_questions[0] = num_questions[0].replace("a","")
		num_questions[1] = num_questions[1].replace("b","")
		num_questions[0] = num_questions[0].replace("[","")
		num_questions[1] = num_questions[1].replace("]","")
		num_questions[0] = num_questions[0].replace("'","")
		num_questions[1] = num_questions[1].replace("'","")
		num_questions[0] = num_questions[0].split(",")
		num_questions[1] = num_questions[1].split(",")
	else:
		posA = questions.find("a")
		str = questions
		str = str.replace("a","")
		str = str.replace("b","")
		str = str.replace("[","")
		str = str.replace("]","")
		str = str.replace("'","")
		listquestions = str.split(",")
		list = []
		#Case where there are only normal questions in the test so questions as ab[4,9,7]
		if(questions[posA+1] == "b"):
			num_questions.append(list)
			num_questions.append(listquestions)
		#Case where there are only MCQ questions in the test so questions as a[4,5]b
		else :
			num_questions.append(listquestions)
			num_questions.append(list)
	return num_questions	#Returns [[1,5,6],[1,9,11]], [[],[4,9,7]], [[4,5],[]] in each different cases
	
def DynMCQquestion_create_view(request, input_q_num):
	"""Function to create a DynMCQquestion
	Return the page to create a DynMCQquestion
	"""
	#Get the question
	DynMCQquestionTest = get_object_or_404(DynMCQquestion, q_num = input_q_num)
	#Get the answers of the questions
	DynMCQanswerTest = DynMCQanswer.objects.filter(q_num = input_q_num)
	DynMCQanswerTest_List = []
	empty_question = True
	empty_answer = True
	form = 0
	#If the question is not filled, we display the form
	if DynMCQquestionTest.q_text == "":
		form = DynMCQquestionForm(request.POST, instance = DynMCQquestionTest)
		if form.is_valid():
			form.save()
			form = DynMCQquestionForm()
			empty_question = False
	#If the question is filled, we check if there are answers in the questions to display it
	else:
		empty_question = False
		for instance in DynMCQanswerTest:
			DynMCQanswerTest_List.append(instance)
		if len(DynMCQanswerTest_List) != 0:
			empty_answer = False
			
	context = {
		'form': form,
		'empty_question': empty_question,
		'empty_answer': empty_answer,
		'DynMCQquestionTest' : DynMCQquestionTest,
		'DynMCQanswerTest_List':DynMCQanswerTest_List,
	}
	return render(request, 'manage_tests/test_create_dynmcqquestion.html',context)
	
def Dynquestion_create_view(request, input_q_num):
	"""Function to create a Dynquestion
	Return the page to create a Dynquestion
	"""
	#Get the question
	DynquestionTest = get_object_or_404(Dynquestion, q_num = input_q_num)
	empty_question = True
	form = 0
	#If the question is not filled, we display the form 
	if DynquestionTest.q_text == "":
		form = DynquestionForm(request.POST, instance = DynquestionTest)
		if form.is_valid():
			form.save()
			form = DynquestionForm()
			empty_question = False
			# Update the weight matrix by creating a new column with default values
	else:
		empty_question = False
			
	context = {
		'form': form,
		'empty_question': empty_question,
		'DynquestionTest' : DynquestionTest,
	}
	return render(request, 'manage_tests/test_create_dynquestion.html',context)
	
def Add_difficulty_view(request,input_q_num):
	"""Function to add the difficulty to a DynMCQquestion question
	Returns the page to add the difficulty
	"""
	#Get the question
	DynMCQquestionTest = get_object_or_404(DynMCQquestion, q_num = input_q_num)
	empty = True
	DifficultySet = formset_factory(MCQQuestion_difficulty_form, extra = 5)
	#Three mandatory properties for formset
	data = {
		'form-TOTAL_FORMS': 5,
		'form-INITIAL_FORMS': '0',
		'form-MAX_NUM_FORMS': '',
	}
	
	form = DifficultySet()#Formset
	
	for theme in form:
		choices = []
		for i in range(5):
			list = []
			list.append(i)
			list.append(i)
			choices.append(list)
		theme.fields['difficulty'].choices = choices #Filling the choices for theme/difficulty as [theme,difficulty]
	
	#Same code for method POST
	if request.method == 'POST':
		form = DifficultySet(request.POST)
		
		for theme in form:
			choices = []
			for i in range(5):
				list = []
				list.append(i)
				list.append(i)
				choices.append(list)
			theme.fields['difficulty'].choices = choices #Assignation des choix
	
		#If form is valid, we save the difficulty for the questions
		if form.is_valid():
			the_difficulty = ""
			for theme in form:
				the_theme = theme.save(commit=False)
				the_difficulty += the_theme.difficulty
			DynMCQquestionTest.difficulty = the_difficulty
			DynMCQquestionTest.save()
			empty = False
			
	context = {
		'form' : form,
		'DynMCQquestionTest' : DynMCQquestionTest,
		'empty' : empty,
	}
	return render(request, 'manage_tests/mcqquestion_difficulty.html',context)
	
def Add_difficulty_question_view(request,input_q_num):
	"""Function to add the difficulty to a Dynquestion question
	Returns the page to add the difficulty
	"""
	#Get the question
	DynquestionTest = get_object_or_404(Dynquestion, q_num = input_q_num)
	empty = True
	DifficultySet = formset_factory(Question_difficulty_form, extra = 5)
	
	#Three mandatory properties for formset
	data = {
		'form-TOTAL_FORMS': 5,
		'form-INITIAL_FORMS': '0',
		'form-MAX_NUM_FORMS': '',
	}
	
	form = DifficultySet()

	for theme in form:
		choices = []
		for i in range(5):
			list = []
			list.append(i)
			list.append(i)
			choices.append(list)
		theme.fields['difficulty'].choices = choices #Filling the choices for theme/difficulty as [theme,difficulty]
		
	#Same code for method POST
	if request.method == 'POST':
		form = DifficultySet(request.POST)
		
		for theme in form:
			choices = []
			for i in range(5):
				list = []
				list.append(i)
				list.append(i)
				choices.append(list)
			theme.fields['difficulty'].choices = choices
	
		#If form is valid, we save the difficulty for the questions
		if form.is_valid():
			the_difficulty = ""
			for theme in form:
				the_theme = theme.save(commit=False)
				the_difficulty += the_theme.difficulty
			DynquestionTest.difficulty = the_difficulty
			DynquestionTest.save()
			empty = False
			
	context = {
		'form' : form,
		'DynquestionTest' : DynquestionTest,
		'empty' : empty,
	}
	return render(request, 'manage_tests/question_difficulty.html',context)
		
	
def DynMCQanswer_create_view(request, input_q_num):
	"""Function to create the answers of a DynMCQquestion
	Returns the page for create answers
	"""
	#Get the question
	DynMCQquestionTest = get_object_or_404(DynMCQquestion, q_num = input_q_num)
	
	empty_answer = True
	
	#Get the answers of the question 
	DynMCQanswerTest = DynMCQanswer.objects.filter(q_num = input_q_num)
	DynMCQanswerTest_List = []
	for instance in DynMCQanswerTest:
		DynMCQanswerTest_List.append(instance)
		
	if len(DynMCQanswerTest_List) != 0:
		empty_answer = False
	
	nb_answers = DynMCQquestionTest.nb_ans
	
	form = 0
	
	#If there are not answers in the test, we display the formset of the answers
	if empty_answer == True:
		#We crate a formset of nb_answers forms of DynMCQanswerForm
		DynMCQanswerSet = formset_factory(DynMCQanswerForm, extra = int(nb_answers))
		
		#Three mandatory properties for formset
		data = {
			'form-TOTAL_FORMS': int(nb_answers),
			'form-INITIAL_FORMS': '0',
			'form-MAX_NUM_FORMS': '',
		}
	
		form = DynMCQanswerSet()#Formset
		
		if request.method == 'POST':
			form = DynMCQanswerSet(request.POST)
			if form.is_valid():
				answer_count = 1
				#Filling automaticaly q_num, ans_num of each answers
				for instance in form:
					dynMCQanswer = instance.save(commit=False)
					dynMCQanswer.q_num = input_q_num
					dynMCQanswer.ans_num = answer_count
					answer_count += 1
					dynMCQanswer.save()
					empty_answer = False
					#We get the answers to display it
					DynMCQanswerTest = DynMCQanswer.objects.filter(q_num = input_q_num)
					DynMCQanswerTest_List = []
					for instance in DynMCQanswerTest:
						DynMCQanswerTest_List.append(instance)
				form = DynMCQanswerSet()
			
	context = {
		'form' : form,
		'DynMCQquestionTest' : DynMCQquestionTest,
		'DynMCQanswerTest_List' : DynMCQanswerTest_List,
		'empty_answer' : empty_answer,
	}
	return render(request, 'manage_tests/test_create_dynmcqanswer.html',context)
	
def DynMCQTest_pass_menu_view(request, input_id_test):
	"""Function to start to pass a test
	Returns the page to start a test
	"""
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	empty_passdynMCQtest = True
	#We get the attempts of the user
	Pass_DynMCQInfo_filter = Pass_DynMCQTest_Info.objects.filter(id_test=input_id_test,id_student=request.user.username)
	Pass_DynMCQInfo_List = []
	Pass_DynMCQInfo = []
	for instance in Pass_DynMCQInfo_filter:
		Pass_DynMCQInfo_List.append(instance)
	#We get the number of attempts of the user
	nb_pass_test = len(Pass_DynMCQInfo_List)
	
	#We test if a pass_test has already been created
	if nb_pass_test > 0:
		#If yes, we test if the pass_test is filled
		if Pass_DynMCQTest.objects.filter(id_test = input_id_test,id_student = request.user.username,attempt = nb_pass_test).exists() or Pass_DynquestionTest.objects.filter(id_test = input_id_test,id_student = request.user.username,attempt = nb_pass_test).exists():
			#In that case, we need to create a new pass_test instance
			empty_passdynMCQtest = True
		else:
			#Else, we display the actual attempt
			Pass_DynMCQInfo = get_object_or_404(Pass_DynMCQTest_Info, id_test=input_id_test, id_student = request.user.username,attempt = nb_pass_test)
			empty_passdynMCQtest = False
	
	if empty_passdynMCQtest:
		#We create a new attempt for passing the test
		passdynmcqtest = Pass_DynMCQTest_Info(id_test=input_id_test,id_student=request.user.username,attempt = nb_pass_test+1,mark = 0)
		passdynmcqtest.save()
		empty_passdynMCQtest = False
		Pass_DynMCQInfo = get_object_or_404(Pass_DynMCQTest_Info, id_test=input_id_test, id_student = request.user.username,attempt = nb_pass_test+1)
			
	context = {
		'DynMCQTestInfo' : DynMCQTestInfo,
		'empty_passdynMCQtest' : empty_passdynMCQtest,
		'Pass_DynMCQInfo' : Pass_DynMCQInfo,
	}
	return render(request, 'pass_tests/menu_pass_dynmcqtest.html',context)

def DynMCQtest_pass_view(request,input_id_test, input_id_student, input_attempt):
	"""Function to pass a test
	Return the page to pass a test
	"""
	#Get the test
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	#Get the pass_test
	Pass_DynMCQInfo = get_object_or_404(Pass_DynMCQTest_Info, id_test=input_id_test, id_student = input_id_student, attempt = input_attempt)
	#Get the number of the questions

	# Apply algorithm for the student
	num_questions = get_questions(DynMCQTestInfo.questions)
	
	#Computing less time to complete the tests
	release_time = get_date(DynMCQTestInfo.release_time)
	limit_time = add_time(release_time,DynMCQTestInfo.time)
	now = get_date(str(datetime.datetime.today()))
	delta = compare_date(now,limit_time)
	
	DynMCQquestionTestList = []
	DynquestionTestList = []
	
	mcq_questions = num_questions[0]
	normal_questions = num_questions[1]
	
	#We get the questions
	for i in range(len(mcq_questions)):
		DynMCQQuestion = DynMCQquestion.objects.get(q_num = mcq_questions[i])
		DynMCQquestionTestList.append(DynMCQQuestion)
	for i in range(len(normal_questions)):
		DynQuestion = Dynquestion.objects.get(q_num = normal_questions[i])
		DynquestionTestList.append(DynQuestion)
	
	nb_mcq_questions = len(mcq_questions)
	nb_normal_questions = len(normal_questions)
	
	double_type_question = False
	if nb_mcq_questions > 0 and nb_normal_questions > 0:
		double_type_question = True
	
	form_mcq_answers = []
	form_normal_answers = []
	
	#For MCQ questions 
	if(nb_mcq_questions > 0):
		#We create a formset of nb_mcq_questions of Pass_DynMCQTestForm
		PassDynMCQTestSet = formset_factory(Pass_DynMCQTestForm, extra = int(nb_mcq_questions))
		#Three mandatory properties for formset
		data = {
			'form-TOTAL_FORMS': int(nb_mcq_questions),
			'form-INITIAL_FORMS': '0',
			'form-MAX_NUM_FORMS': '',
		}
		
		form_mcq_answers = PassDynMCQTestSet()#Formset
		#We get the answers of each questions and we put them in the choices for checkbox
		i = 0
		for ans in form_mcq_answers:
			choices = []
			DynMCQanswers = DynMCQanswer.objects.filter(q_num = mcq_questions[i])
			#Get the answers in list ('returned value','displayed text') for each answers
			for answer in DynMCQanswers:
				list = []
				list.append(answer.ans_num)
				list.append(answer.ans_text)
				choices.append(list)
			ans.fields['r_ans'].choices = choices #Filling the choices as list of [ans_num,ans_text]
			i += 1
			
		#Same code for method POST
		if request.method == 'POST':
			form_mcq_answers = PassDynMCQTestSet(request.POST)
			i = 0
			for ans in form_mcq_answers:
				choices = []
				DynMCQanswers = DynMCQanswer.objects.filter(q_num = mcq_questions[i])
				for answer in DynMCQanswers:
					list = []
					list.append(answer.ans_num)
					list.append(answer.ans_text)
					choices.append(list)
				ans.fields['r_ans'].choices = choices
				i += 1
		
			if form_mcq_answers.is_valid():
				question_count = 0
				Pass_DynMCQInfo.time = datetime.datetime.today()
				#Filling automaticaly fields
				for instance in form_mcq_answers:
					pass_dynMCQtest = instance.save(commit=False)
					pass_dynMCQtest.id_test = input_id_test
					pass_dynMCQtest.id_student = input_id_student
					pass_dynMCQtest.q_num = mcq_questions[question_count]
					pass_dynMCQtest.attempt = input_attempt
					#We get the right answers of the question
					right_answers = DynMCQanswer.objects.filter(q_num = mcq_questions[question_count], right_ans = 1)
					num_right_answers = []
					for ans in right_answers:
						num_right_answers.append(ans.ans_num)
					#We check if the answer is right
					if check_answer(pass_dynMCQtest.r_ans,num_right_answers):
						Pass_DynMCQInfo.mark += 1
						# here we need to add the answer in the weight matrix
					Pass_DynMCQInfo.save()
					question_count += 1
					pass_dynMCQtest.save()
					
				if double_type_question is False:
					#Compare limit time with released time
					time_left = compare_date(get_date(str(datetime.datetime.today())),limit_time)
					#If time left > 30 sec we put a penalty of 1 point every minute
					if time_left < -0.5:
						min_left = str(time_left).split(".")
						Pass_DynMCQInfo.mark += int(min_left[0])
						if(Pass_DynMCQInfo.mark < 0):
							Pass_DynMCQInfo.mark = 0
						Pass_DynMCQInfo.save()
					return redirect('/')
	
	#For normal questions
	if(nb_normal_questions > 0):
		#We create a formset of nb_normal_questions of Pass_DynquestionTestForm
		PassDynquestionTestSet = formset_factory(Pass_DynquestionTestForm, extra = int(nb_normal_questions))
		#Three mandatory properties for formset
		data = {
			'form-TOTAL_FORMS': int(nb_normal_questions),
			'form-INITIAL_FORMS': '0',
			'form-MAX_NUM_FORMS': '',
		}
		
		form_normal_answers = PassDynquestionTestSet()
			
		if request.method == 'POST':
			form_normal_answers = PassDynquestionTestSet(request.POST)
		
			if form_normal_answers.is_valid():
				question_count = 0
				Pass_DynMCQInfo.time = datetime.datetime.today()
				#Filling automaticaly fields
				for instance in form_normal_answers:
					if question_count < len(normal_questions):
						pass_dynMCQtest = instance.save(commit=False)
						pass_dynMCQtest.id_test = input_id_test
						pass_dynMCQtest.id_student = input_id_student
						pass_dynMCQtest.q_num = normal_questions[question_count]
						pass_dynMCQtest.attempt = input_attempt
						#We get the right answer of the question
						question = Dynquestion.objects.get(q_num = normal_questions[question_count])
						right_ans = str(question.r_text)
						student_ans = str(pass_dynMCQtest.r_answer)
						#We check if the answer is right
						if student_ans.lower() == right_ans.lower():
							Pass_DynMCQInfo.mark += 1
						Pass_DynMCQInfo.save()
						question_count += 1
						pass_dynMCQtest.save()
						
				#Compare limit time with released time
				time_left = compare_date(get_date(str(datetime.datetime.today())),limit_time)
				#If time left > 30 sec we put a penalty of 1 point every minute
				if time_left < -0.5:
					min_left = str(time_left).split(".")
					Pass_DynMCQInfo.mark += int(min_left[0])
					if(Pass_DynMCQInfo.mark < 0):
						Pass_DynMCQInfo.mark = 0
					Pass_DynMCQInfo.save()
				return redirect('/')
				
	context = {
		'Pass_DynMCQInfo' : Pass_DynMCQInfo,
		'DynMCQTestInfo':DynMCQTestInfo,
		'form_mcq_answers': form_mcq_answers,
		'form_normal_answers':form_normal_answers,
		'DynMCQquestionTestList':DynMCQquestionTestList,
		'DynquestionTestList' : DynquestionTestList,
		'nb_normal_questions':nb_normal_questions,
		'nb_mcq_questions':nb_mcq_questions,
		'release_time':release_time,
		'limit_time':limit_time,
		'delta':delta,
	}
	return render(request, 'pass_tests/dynMCQtest_pass.html', context)

def check_answer(stu_answer,num_right_answers):
	'''Funtion to check if the answer of the user is right or not
	Parameter :
		stu_answer (string) : answer of the user ([ids_answer],[...]])
		num_right_answers (list) : list of right answer ids
		
	Return :
		right_answer (Bool) : True if right else False
	'''
	right_answer = True
	num_right_answers.sort()
	stu_num_answer = []
	#We extract the answer ids of the string stu_answer
	i = 0
	while i < len(stu_answer):
		if stu_answer[i].isdigit():
			stu_num_answer.append(int(stu_answer[i]))
		i += 1	
	stu_num_answer.sort()
	if(len(num_right_answers) != len(stu_num_answer)):
		right_answer = False
	else:
		#We compare each list of answers
		i = 0
		while i < len(num_right_answers):
			if(num_right_answers[i] != stu_num_answer[i]):
				right_answer = False
			i += 1
	return right_answer
			
	
def pass_dynMCQtest_display_view(request,input_id_test,input_id_student,input_attempt):
	"""Function to display a pass test
	Returns the page of the pass test
	"""
	#Get the info
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	Pass_DynMCQInfo = get_object_or_404(Pass_DynMCQTest_Info, id_test=input_id_test, id_student = input_id_student,attempt = input_attempt)
	Pass_DynMCQtest = Pass_DynMCQTest.objects.filter(id_test = input_id_test, id_student = input_id_student,attempt = input_attempt)
	Pass_Dynquestiontest = Pass_DynquestionTest.objects.filter(id_test = input_id_test, id_student = input_id_student,attempt = input_attempt)
	#Get the questions of the test
	num_questions = get_questions(DynMCQTestInfo.questions)
	nb_questions = len(num_questions[0]) + len(num_questions[1])
	Pass_DynMCQtest_List = []
	Pass_Dynquestiontest_List = []
	for instance in Pass_DynMCQtest:
		Pass_DynMCQtest_List.append(instance)
	for instance in Pass_Dynquestiontest:
		Pass_Dynquestiontest_List.append(instance)
	context = {
		'DynMCQTestInfo' : DynMCQTestInfo,
		'Pass_DynMCQInfo' : Pass_DynMCQInfo,
		'Pass_DynMCQtest_List': Pass_DynMCQtest_List,
		'Pass_Dynquestiontest_List' : Pass_Dynquestiontest_List,
		'nb_questions':nb_questions,
	}
	return render(request, 'manage_tests/pass_dynMCQtest_display.html', context)
	
def DynMCQtest_display_view(request, input_id_test):
	"""Function to display a DynMCQInfo test
	Return the page of the displayed DynMCQInfo test
	"""
	#Get the info
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	num_questions = get_questions(DynMCQTestInfo.questions)
	mcq_questions = num_questions[0]
	normal_questions = num_questions[1]
	
	DynMCQquestions_List = []
	Dynquestions_List = []
	#Get the questions
	for i in range(len(normal_questions)):
		DynQuestion = Dynquestion.objects.get(q_num = normal_questions[i])
		Dynquestions_List.append(DynQuestion)
	
	for i in range(len(mcq_questions)):
		DynMCQQuestion = DynMCQquestion.objects.get(q_num = mcq_questions[i])
		DynMCQquestions_List.append(DynMCQQuestion)
	
	#Get the answers for mcq questions
	DynMCQanswers = []
	for i in range(len(mcq_questions)):
		theDynMCQanswers = DynMCQanswer.objects.filter(q_num = int(mcq_questions[i]))
		for ans in theDynMCQanswers:
			DynMCQanswers.append(ans)
		
	#We order the questions and the answers in a same list to properly display it
	Questions_Answers_List = []
	for question in DynMCQquestions_List:
		Questions_Answers_List.append(question)
		DynMCQanswers = DynMCQanswer.objects.filter(q_num = question.q_num)
		for answer in DynMCQanswers:
			Questions_Answers_List.append(answer)
			
	context = {
		'DynMCQquestions_List':DynMCQquestions_List,
		'DynMCQTestInfo':DynMCQTestInfo,
		'Questions_Answers_List': Questions_Answers_List,
		'Dynquestions_List':Dynquestions_List,
	}
	return render(request, 'manage_tests/dynmcqtest_display.html', context)
	
def Edit_DynMCQquestion_view(request,input_q_num):
	"""Function to edit a DynMCQquestion question
	Return the page to edit the DynMCQquestion question
	"""
	#Get the question
	DynMCQquestionTest = get_object_or_404(DynMCQquestion, q_num = input_q_num)
	
	#Form with the same instance to edit it
	form = DynMCQquestionForm_question(request.POST, instance = DynMCQquestionTest)
	if form.is_valid():
		form.save()
		form = DynMCQquestionForm_question(instance = DynMCQquestionTest)
			
	context = {
		'form': form,
		'DynMCQquestionTest':DynMCQquestionTest,
	}
	return render(request, 'manage_tests/edit_dynMCQquestion.html', context)
	
def Edit_Dynquestion_view(request,input_q_num):
	"""Function to edit a Dynquestion question
	Return the page to edit the Dynquestion question
	"""
	#Get the question
	DynquestionTest = get_object_or_404(Dynquestion, q_num = input_q_num)
	
	#Form with the same instance to edit it
	form = DynquestionForm(request.POST, instance = DynquestionTest)
	if form.is_valid():
		form.save()
		form = DynquestionForm(instance = DynquestionTest)
			
	context = {
		'form': form,
		'DynquestionTest':DynquestionTest,
	}
	return render(request, 'manage_tests/edit_dynquestion.html', context)
	
def Edit_DynMCQanswer_view(request,input_q_num,input_ans_num):
	"""Function to edit a DynMCQanswer answer
	Return the page to edit the DynMCQanswer question
	"""
	#Get the question and the answer
	DynMCQquestionTest = get_object_or_404(DynMCQquestion, q_num = input_q_num)
	DynMCQanswerTest = get_object_or_404(DynMCQanswer, q_num = input_q_num, ans_num = input_ans_num)
	
	#Form with the same instance to edit it
	form = DynMCQanswerForm(request.POST, instance = DynMCQanswerTest)
	if form.is_valid():
		form.save()
		form = DynMCQanswerForm(instance = DynMCQanswerTest)
			
	context = {
		'form': form,
		'DynMCQquestionTest':DynMCQquestionTest,
		'DynMCQanswerTest' : DynMCQanswerTest,
	}
	return render(request, 'manage_tests/edit_dynMCQanswer.html', context)
	
def Delete_DynMCQquestion_view(request,input_q_num):
	"""Function to delete a DynMCQquestion question
	Return the page of managing questions
	"""
	#Get the question
	DynMCQquestionTest = get_object_or_404(DynMCQquestion, q_num = input_q_num)
	
	#Delete the question
	DynMCQquestionTest.delete()
	
	#Get the question answers and delete each answers
	answers = DynMCQanswer.objects.filter(q_num = input_q_num)
	answers_list = []
	for instance in answers :
			answers_list.append(instance)
	for instance in answers_list :
		instance.delete()
			
	#Get the questions to display it
	DynMCQquestions = DynMCQquestion.objects.all()		
	Dynquestions = Dynquestion.objects.all()	
	
	context = {
		'Dynquestions': Dynquestions,
		'DynMCQquestions': DynMCQquestions,
	}
	return render(request, 'manage_tests/manage_questions.html', context)
	
def Delete_Dynquestion_view(request,input_q_num):
	"""Function to delete a Dynquestion question
	Return the page of managing questions
	"""
	#Get the question
	DynquestionTest = get_object_or_404(Dynquestion, q_num = input_q_num)
	
	#Delete the question
	DynquestionTest.delete()
			
	#Get the questions to display it
	DynMCQquestions = DynMCQquestion.objects.all()
	Dynquestions = Dynquestion.objects.all()		
	
	context = {
		'DynMCQquestions': DynMCQquestions,
		'Dynquestions': Dynquestions,
	}
	return render(request, 'manage_tests/manage_questions.html', context)
	
def Delete_DynMCQanswer_view(request,input_q_num,input_ans_num):
	"""Function to delete a DynMCQanswer answer
	Return the page to manage the question
	"""
	#Get the question and the answer 
	DynMCQquestionTest = get_object_or_404(DynMCQquestion,q_num = input_q_num)
	DynMCQanswerTest = get_object_or_404(DynMCQanswer,q_num = input_q_num, ans_num = input_ans_num)
	
	#Get the number of answers
	nb_answers = int(DynMCQquestionTest.nb_ans)
	answer_num = int(input_ans_num) + 1
	
	#Delete the answer
	DynMCQanswerTest.delete()
	
	#Change the number of answers
	tmp_nb_ans = int(DynMCQquestionTest.nb_ans) - 1
	DynMCQquestionTest.nb_ans = str(tmp_nb_ans)
	DynMCQquestionTest.save()
	
	#We move the number of the answers
	while answer_num <= nb_answers : 
		tmp_answer = get_object_or_404(DynMCQanswer,q_num = input_q_num,ans_num = answer_num)
		tmp_answer.ans_num -= 1
		tmp_answer.save()
		answer_num += 1
	
	#We get the answers to display them
	the_DynMCQanswer = DynMCQanswer.objects.filter(q_num = input_q_num)
	DynMCQanswerTest_List = []
	for instance in the_DynMCQanswer :
		DynMCQanswerTest_List.append(instance)
	empty_question = False
	empty_answer = False
			
	context = {
		'DynMCQquestionTest' : DynMCQquestionTest,
		'DynMCQanswerTest_List' : DynMCQanswerTest_List,
		'empty_question' : empty_question,
		'empty_answer' : empty_answer,
	}
	return render(request, 'manage_tests/test_create_dynmcqquestion.html', context)
	
def Add_DynMCQquestion_view(request):	
	"""Function to add a DynMCQquestion question
	Returns the page to manage questions
	"""
	#Creating the new question
	DynamicMCQquestion = DynMCQquestion.objects.create()
	DynamicMCQquestion.save()
	
	#Get all the questions to display it
	DynMCQquestions = DynMCQquestion.objects.all()
	Dynquestions = Dynquestion.objects.all()
	
	context = {
		'DynMCQquestions' : DynMCQquestions,
		'Dynquestions' : Dynquestions,
	}

	return render(request, 'manage_tests/manage_questions.html',context)
	
def Add_Dynquestion_view(request):
	"""Function to add a Dynquestion question
	Returns the page to manage questions
	"""
	#Creating the new question
	Dynamicquestion = Dynquestion.objects.create()
	Dynamicquestion.save()
	
	#Get all the questions to display it
	DynMCQquestions = DynMCQquestion.objects.all()
	Dynquestions = Dynquestion.objects.all()
	
	context = {
		'DynMCQquestions' : DynMCQquestions,
		'Dynquestions' : Dynquestions,
	}

	return render(request, 'manage_tests/manage_questions.html',context)
	
def Add_DynMCQanswer_view(request,input_q_num):
	"""Function to add a DynMCQanswer answer
	Returns the page to add a new answer
	"""
	#Get the question
	DynMCQquestionTest = get_object_or_404(DynMCQquestion, q_num = input_q_num)
	
	add_answer = False
	
	#Get the new number of answers
	nb_answers = int(DynMCQquestionTest.nb_ans) + 1
	
	#New form for the answer
	form = DynMCQanswerForm(request.POST)
	if form.is_valid():
		the_answer = form.save(commit = False)
		the_answer.q_num = input_q_num
		the_answer.ans_num = nb_answers
		the_answer.save()
		#We change the number of answers
		DynMCQquestionTest.nb_ans = int(nb_answers)
		DynMCQquestionTest.save()
		add_answer = True
			
	context = {
		'add_answer':add_answer,
		'nb_answers' : nb_answers,
		'form': form,
		'DynMCQquestionTest':DynMCQquestionTest,
	}
	return render(request, 'manage_tests/add_dynMCQanswer.html', context)

@login_required
@permission_required('tests.can_see_test', raise_exception=True)
def pass_testslist_teacher_view(request):
	"""Function to display all the pass_test
	Returns the page with displayed pass_test
	"""
	pass_dynMCQtest_all = Pass_DynMCQTest_Info.objects.all()
	
	context = {
		'pass_dynMCQtest_all': pass_dynMCQtest_all,
	}
	return render(request, 'manage_tests/pass_tests_list_teacher.html', context)

@login_required
@permission_required('tests.can_see_test', raise_exception=True)
def tests_list_teacher_view(request):
	"""Function to display all the test
	Returns the page with displayed test
	"""
	testlist_dynmcqtestinfo_all = DynMCQInfo.objects.all()

	context = {
		'testlist_dynmcqtestinfo_all':testlist_dynmcqtestinfo_all,
	}
	return render(request, 'manage_tests/tests_list_teacher.html', context)

@login_required
@permission_required('tests.can_pass_test', raise_exception=True)
def tests_list_student_view(request):
	"""Function to display the available test to pass
	Returns the page of available test to pass
	"""
	#Get the tests
	testlist_dynmcqtestinfo_all = DynMCQInfo.objects.all()
	testlist_dynmcqtestinfo_user = []
	
	#We compare the groups of each test with the groups of the user to check if the user can pass the test
	user_groups = request.user.groups.all()
	test_groups = ""
	for test in testlist_dynmcqtestinfo_all:
		test_groups = test.activated_for
		test_groups = test_groups.replace("'","")
		test_groups = test_groups.replace("[","")
		test_groups = test_groups.replace("]","")
		test_groups = test_groups.split(',')
		for test_group in test_groups:
			for user_group in user_groups:
				if(str(test_group) == str(user_group)):
					testlist_dynmcqtestinfo_user.append(test)

	context = {
		'testlist_dynmcqtestinfo_user' : testlist_dynmcqtestinfo_user,
	}
	return render(request, 'pass_tests/tests_list_student.html', context)


def tests_history_view(request):
	"""Function to display the pass test of the user
	Returns the page of displayed pass test of the users
	"""
	#Get all pass_test
	pass_dynMCQtest_all = Pass_DynMCQTest_Info.objects.all()
	pass_dynMCQtest_user = []
	for test in pass_dynMCQtest_all:
		#Get all pass_test of the user
		if test.id_student == request.user.username:
			pass_dynMCQtest_user.append(test)
	context = {
		'pass_dynMCQtest_user': pass_dynMCQtest_user,
	}
	return render(request, 'pass_tests/tests_history.html', context)


@login_required
@permission_required('tests.can_see_stats', raise_exception=True)
def dashboard_view(request):
	"""Function to display all available test to get statistics on them
	Returns the page of displayed available test to get statistics
	"""
	testlist_dynmcqtest = DynMCQInfo.objects.all()
	context = {
		'testlist_dynmcqtest': testlist_dynmcqtest
	}
	return render(request, 'manage_tests/dashboard.html', context)
	
@login_required
@permission_required('tests.can_see_test', raise_exception=True)
def launch_view(request):
	"""Function to display all the test that can be launch
	Returns the page with displayed test that can be launch
	"""
	testlist_dynmcqtest = DynMCQInfo.objects.all()
	context = {
		'testlist_dynmcqtest': testlist_dynmcqtest
	}
	return render(request, 'manage_tests/launch_test.html', context)	


def launch_specific_dynmcq_view(request, input_id_test):
	"""Function to launch a test in order to get the test available for users in a specific group
	Returns the page to launch a test
	"""
	#Get the test
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	empty = True
	#Get the question ids
	num_questions = get_questions(DynMCQTestInfo.questions)
	
	if DynMCQTestInfo.activated_for != "":
		empty = False
	
	mcq_questions = num_questions[0]
	normal_questions = num_questions[1]
	
	DynMCQquestions_List = []
	Dynquestions_List = []
	#Get the questions
	for i in range(len(normal_questions)):
		DynQuestion = Dynquestion.objects.get(q_num = normal_questions[i])
		Dynquestions_List.append(DynQuestion)
	
	for i in range(len(mcq_questions)):
		DynMCQQuestion = DynMCQquestion.objects.get(q_num = mcq_questions[i])
		DynMCQquestions_List.append(DynMCQQuestion)
		
	#Get the answers
	DynMCQanswers = []
	for i in range(len(mcq_questions)):
		theDynMCQanswers = DynMCQanswer.objects.filter(q_num = int(mcq_questions[i]))
		for ans in theDynMCQanswers:
			DynMCQanswers.append(ans)
		
	#We order the questions and the answers in a same list to display it properly
	Questions_Answers_List = []
	for question in DynMCQquestions_List:
		Questions_Answers_List.append(question)
		DynMCQanswers = DynMCQanswer.objects.filter(q_num = question.q_num)
		for answer in DynMCQanswers:
			Questions_Answers_List.append(answer)
	
	#We get all existing groups
	group_names = []
	groups = Group.objects.all()
	for group in groups:
		if(group.name != "Teacher" and group.name != "Student"):
			group_names.append(group)
	
	#We create a form for filling groups and the time for completing the test
	form = DynMCQTestInfoForm_launch()
	choices = []
	for group in group_names:
		list = []
		list.append(group.name)
		list.append(group.name)
		choices.append(list)
	form.fields['activated_for'].choices = choices#Fillings group choices
	
	#Same code for method POST
	if request.method == 'POST':
		form = DynMCQTestInfoForm_launch(request.POST, instance = DynMCQTestInfo)
		choices = []
		for group in group_names:
			list = []
			list.append(group.name)
			list.append(group.name)
			choices.append(list)
		form.fields['activated_for'].choices = choices
	
		if form.is_valid():
			form.save()
			empty = False
			form = DynMCQTestInfoForm_launch()
			
	context = {
		'DynMCQquestions_List':DynMCQquestions_List,
		'DynMCQTestInfo':DynMCQTestInfo,
		'Questions_Answers_List': Questions_Answers_List,
		'Dynquestions_List':Dynquestions_List,
		'form': form,
		'empty':empty,
	}
	return render(request, 'manage_tests/launch_specific_dynmcq_test.html', context)	

def in_launch_specific_dynmcq_view(request, input_id_test):
	"""Function to display the launched test page with timer decreasing
	Returns the page of the launched test
	"""
	#Get the test
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	
	#Saving release time
	DynMCQTestInfo.release_time = datetime.datetime.today()
	DynMCQTestInfo.save()
	
	num_questions = get_questions(DynMCQTestInfo.questions)
	
	time = get_time(DynMCQTestInfo.time)
	
	mcq_questions = num_questions[0]
	normal_questions = num_questions[1]
	
	DynMCQquestions_List = []
	Dynquestions_List = []
	#Get questions
	for i in range(len(normal_questions)):
		DynQuestion = Dynquestion.objects.get(q_num = normal_questions[i])
		Dynquestions_List.append(DynQuestion)
	
	for i in range(len(mcq_questions)):
		DynMCQQuestion = DynMCQquestion.objects.get(q_num = mcq_questions[i])
		DynMCQquestions_List.append(DynMCQQuestion)
	
	#Get answers
	DynMCQanswers = []
	for i in range(len(mcq_questions)):
		theDynMCQanswers = DynMCQanswer.objects.filter(q_num = int(mcq_questions[i]))
		for ans in theDynMCQanswers:
			DynMCQanswers.append(ans)
		
	#We order the questions and the answers in a same list to display it properly
	Questions_Answers_List = []
	for question in DynMCQquestions_List:
		Questions_Answers_List.append(question)
		DynMCQanswers = DynMCQanswer.objects.filter(q_num = question.q_num)
		for answer in DynMCQanswers:
			Questions_Answers_List.append(answer)
		
	context = {
		'DynMCQquestions_List':DynMCQquestions_List,
		'DynMCQTestInfo':DynMCQTestInfo,
		'Questions_Answers_List': Questions_Answers_List,
		'Dynquestions_List':Dynquestions_List,
		'time' : time,
	}
	return render(request, 'manage_tests/in_launch_specific_dynmcq_test.html', context)
	
def in_launch_mcq_stop_test(request, input_id_test):
	"""Function to stop a launched test
	Returns the main page of the app
	"""
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	stop_mcq_test(DynMCQTestInfo)
	return redirect('/')
	
def stop_mcq_test(DynMCQTestInfo):
	"""Function to reset the test : the groups and the release time of the test
	Parameter :
		DynMCQTestInfo (DynMCQInfo instance) : launched test
	"""
	DynMCQTestInfo.activated_for = ""
	DynMCQTestInfo.time = ""
	DynMCQTestInfo.save()
	
def get_time(time):
	"""Function to extract min and sec from time
	Parameter :
		time (string) : time "min:sec" (5:30)
	Return :
		the_time (float) : minute expressed 2,5 => 2 min 30 sec
	""" 
	timer = time.split(':')
	min = timer[0]
	sec = int(timer[1])/60
	sec = str(sec)
	sec = sec[1:]
	the_time = min + sec
	return the_time
	
def get_date(date):
	"""Function to get the time
	Parameter :
		date (str) : expressed like 2009-01-06 15:08:24.789150
	Return :
		(list) : [h,min,sec]
	"""
	time_date = date.split(".")
	time_date = time_date[0].split(" ")
	time_date = time_date[1].split(":")
	return [int(time_date[0]),int(time_date[1]),int(time_date[2])]
	
def add_time(date,time):
	"""Function to add a certain time to another time
	Parameter :
		date (list) : [h,min,sec]
		time (str) : "min:sec"
	Return :
		(list) : [h,min,sec]
	"""
	timer = time.split(":")
	if(len(timer)==2):
		h = int(date[0])
		min = int(timer[0])+int(date[1])
		sec = int(timer[1])+int(date[2])
	if(len(timer)==3):
		h = int(timer[0])+int(date[0])
		min = int(timer[1])+int(date[1])
		sec = int(timer[2])+int(date[2])
	if(sec >= 60):
		min += 1
		sec -= 60
	if(min >= 60):
		h += 1
		min -= 60
		if h >= 24:
			h -= 24
	return [h,min,sec]
	
def compare_date(date1,date2):
	"""Function to extract the difference between two time
	Parameter :
		date1, date2 (list) : [h,min,sec]
	Return :
		min (float) : delta time expressed in minutes
	"""
	h = date2[0] - date1[0]
	min = date2[1] - date1[1]
	sec = date2[2] - date1[2]
	h *= 3600
	min *= 60
	time = h + min + sec
	min = time /60
	return min
	
def statistics_view(request, input_id_test):
	"""Function to get the statistics on a specific test
	Return the page of the statistics
	"""
	#Get the info
	DynMCQTestInfo = get_object_or_404(DynMCQInfo, id_test=input_id_test)
	PassDynMCQInfo = Pass_DynMCQTest_Info.objects.filter(id_test = input_id_test)
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
	
	#Computing min / max marks
	note_plus_basse = Note_plus_basse(marks_list)
	note_plus_haute = Note_plus_haute(marks_list)

	#Computing average mark
	moyenne_mcqtest = Moyenne(marks_list)
	nb_test = len(PassDynMCQInfo_List)
	
	#Computing Q1 and Q3
	q1 = Q1(marks_list)
	q3 = Q3(marks_list)

    #Computing median
	m = Mediane(marks_list)
		
	#Computing frequences
	total_freq = Frequences(statistiques_notes,PassDynMCQInfo_List)
	
	#Computing questions statistics
	stats_question = Statistique_question(DynMCQTestInfo)
	
	#Questions statistics percentages
	pourcentage_question = Pourcentage_stats_question(stats_question,PassDynMCQInfo_List)
		
	total_statistics_question = []
	i = 0
	while i < len(stats_question):
		total_statistics_question.append((stats_question[i],pourcentage_question[i]))
		i += 1
	
	#Creating graphs
	GraphsQuestions(stats_question,int(nb_questions))
	GraphsNote(total_freq,int(nb_questions))
	GraphsBoxplot(marks_list)

	context = {
		'DynMCQTestInfo':DynMCQTestInfo,
		'PassDynMCQInfo_List': PassDynMCQInfo_List,
		'moyenne_mcqtest' : moyenne_mcqtest,
		'nb_test' : nb_test,
		'note_plus_haute' : note_plus_haute,
		'note_plus_basse' : note_plus_basse,
		'q1' : q1,
		'q3' : q3,
		'mediane' : m,
		'total_statistics_question' : total_statistics_question,
		'total_freq' : total_freq,
		'nb_questions':nb_questions,
	}
	return render(request, 'manage_tests/statistics.html', context)
	
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
	moyenne /= len(marks_list)
	moyenne="%.2f" % moyenne
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
	if len(marks_list)%4 == 0:
		q1=marks_list[len(marks_list)//4-1]
	else:
		q1=marks_list[len(marks_list)//4]
	return q1
	
def Q3(marks_list):
	"""Function to compute the third quarter of the mark list
	Parameter :
		marks_list (list) : list of the pass test marks
	Return :
		q3 (float) : third quarter
	"""
	marks_list.sort()
	if len(marks_list)%4 == 0:
		q3=marks_list[3*len(marks_list)//4-1]
	else:
		q3=marks_list[3*len(marks_list)//4]
	return q3
	
def Mediane(marks_list):
	"""Function to compute the median of the mark list
	Parameter :
		marks_list (list) : list of the pass test marks
	Return :
		m (int) : median
	"""
	marks_list.sort()
	if len(marks_list)%2 == 0:
		m=((marks_list[(len(marks_list)-1)//2]+marks_list[len(marks_list)//2])/2)
	else:
		m = marks_list[len(marks_list)//2]
	return m
	
def Frequences(statistiques_notes,PassDynMCQInfo_List):
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
		total_freq.append((temp_freq,som_freq))
	return total_freq
	
def Statistique_question(DynMCQTestInfo):
	"""Function to compute the statistics for each questions of the test
	Parameter :
		DynMCQTestInfo (DynMCQTest instance) : the test instance
	Return :
		stats_question (list) : list of occurences of good answers for each questions
	"""
	#Get questions
	num_questions = get_questions(DynMCQTestInfo.questions)
	stats_question = []
	mcq_question = num_questions[0]
	normal_questions = num_questions[1]
	i = 0
	while i < int(len(mcq_question) + len(normal_questions)):
		stats_question.append(0)
		i += 1
		
	#Get pass tests
	passdynmcqtest = Pass_DynMCQTest.objects.filter(id_test = DynMCQTestInfo.id_test)
	passdynquestiontest = Pass_DynquestionTest.objects.filter(id_test = DynMCQTestInfo.id_test)
	passdynmcqtest_List = []
	passdynquestiontest_List = []
	for instance in passdynmcqtest:
		passdynmcqtest_List.append(instance)
	for instance in passdynquestiontest:
		passdynquestiontest_List.append(instance)
	
	#For DynMCQanswer
	for passdynmcq in passdynmcqtest_List:
		tmp_dynmcqtest = DynMCQanswer.objects.filter(q_num = passdynmcq.q_num, right_ans = 1)
		num_right_answers = []
		for ans in tmp_dynmcqtest:
			num_right_answers.append(ans.ans_num)
		#If good answer, incrementing stats_question of the question
		if check_answer(passdynmcq.r_ans,num_right_answers):
			index = 0
			for i in range(len(mcq_question)):
				if(passdynmcq.q_num == mcq_question[i]):
					index = i
			stats_question[index] += 1
	#For Dynquestion
	for passdynquestion in passdynquestiontest_List:
		dynquestion = Dynquestion.objects.get(q_num = passdynquestion.q_num)
		right_answer = dynquestion.r_text
		student_answer = passdynquestion.r_answer
		#If good answer, incrementing stats_question of the question
		if right_answer.lower() == student_answer.lower():
			index = 0
			for i in range(len(normal_questions)):
				if(passdynquestion.q_num == normal_questions[i]):
					index = i + len(mcq_question)
			stats_question[index] += 1
	return stats_question
	
def Pourcentage_stats_question(stats_question,PassDynMCQInfo_List):
	"""Function to compute the percentages statistics for each questions of the test
	Parameter :
		stats_question (list) : list of occurences of good answers for each questions
		PassDynMCQInfo_List (list) : list of pass test instance
	Return :
		pourcentage_question (list) : percentage of good answers for each questions
	"""
	pourcentage_question = []
	for stat in stats_question:
		pourcentage = 100*stat/len(PassDynMCQInfo_List)
		pourcentage = "%.2f" % pourcentage
		pourcentage_question.append(pourcentage)
	return pourcentage_question
	
def GraphsQuestions(stats_question, nb_q):
	"""Function to create a graph to display statistics on questions
	Parameter :
		stats_question (list) : list of occurences of good answers for each questions
		nb_q (int) : number of questionss
	"""
	plt.rcdefaults()
	fig, ax = plt.subplots()

	questions = []
	i = 1
	while i <= nb_q:
		questions.append("q"+str(i))
		i += 1
	y_pos = np.arange(len(stats_question))
	performance = stats_question

	ax.barh(y_pos, performance, align='center')
	ax.set_yticks(y_pos)
	ax.set_yticklabels(questions)
	ax.invert_yaxis()
	ax.set_xlabel('Bonnes réponses')
	ax.set_title('Stats Questions')
	plt.savefig('./pages/static/images/GraphsQuestions.png')
	
def GraphsNote(total_freq,nb_q):
	"""Function to create a graph to display statistics on marks
	Parameter :
		total_freq (list) : list of frequences of the test
		nb_q (int) : number of questionss
	"""
	labels = []
	i = 0
	while i <= nb_q:
		labels.append(str(i)+"/"+str(nb_q))
		i += 1
	sizes = []
	for q in total_freq:
		sizes.append(q[0])
	fig, ax = plt.subplots()
	ax.pie(sizes, labels=labels, autopct='%1.1f%%',shadow=True, startangle=90)
	ax.axis('equal')
	ax.set_title('Statistiques des notes')
	plt.savefig('./pages/static/images/GraphsNote.png')
	
def GraphsBoxplot(marks_list):
	"""Function to create a boxplot to display statistics on marks
	Parameter :
		marks_list (list) : list of the pass test marks
	"""
	data = marks_list
	fig, ax = plt.subplots()
	ax.boxplot(data,vert=False,)
	ax.set_title('Boxplot du test')
	plt.savefig('./pages/static/images/GraphsBoxplot.png')
	



