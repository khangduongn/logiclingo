from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import *
from django.contrib.auth import login
from django.contrib import messages
from .controllers import *
from django.contrib.auth.decorators import login_required


def is_student(user):
    return hasattr(user, 'student')

def is_in_classroom(user, classroom):
    return (classroom.instructors.filter(userID=user.userID).exists() or classroom.students.filter(userID=user.userID).exists())

@login_required
def index(request):

    user = request.user

    if not is_student(user): 
        return render(request, 'instructor.html', {'instructor': user.instructor})

    else:
        return render(request, 'student.html', {'student': user.student})

@login_required
def create_classroom(request):

    if is_student(request.user):
        return redirect('index')
    
    createClassroomForm = ClassroomForm()

    if request.method == 'POST':
        createClassroomForm = ClassroomForm(request.POST)
        if createClassroomForm.is_valid():
            newClassroom = createClassroomForm.save(commit=False)  
            newClassroom.instructorName = request.user.firstName + ' ' + request.user.lastName
            newClassroom.save() 
            newClassroom.instructors.add(request.user.instructor)
            return redirect('classroom', id=newClassroom.classroomID)

    return render(request, 'create_classroom.html', {'form': createClassroomForm})

@login_required
def classroom(request, id):

    classroom = get_object_or_404(Classroom, classroomID=id)

    #if the user is in the classroom, then let them see the classroom
    if is_in_classroom(request.user, classroom):
        return render(request, 'classroom.html', {'classroom': classroom})
    else:
        return redirect('index')

def create_student(request):

    createStudentForm = StudentForm()

    if request.method == 'POST':
        createStudentForm = StudentForm(request.POST)
        if createStudentForm.is_valid():
            newStudent = createStudentForm.save(commit=False)
            newStudent.set_password(createStudentForm.cleaned_data['password'])
            newStudent.save()
            login(request, newStudent)

            return redirect('index')

    return render(request, 'create_student.html', {'form': createStudentForm})

def create_instructor(request):

    createInstructorForm = InstructorForm()

    if request.method == 'POST':
        createInstructorForm = InstructorForm(request.POST)
        if createInstructorForm.is_valid():
            newInstructor = createInstructorForm.save()
            newInstructor.set_password(createInstructorForm.cleaned_data['password'])
            newInstructor.save()
            login(request, newInstructor)

            return redirect('index')

    return render(request, 'create_instructor.html', {'form': createInstructorForm})

@login_required
def classroom_settings(request, id):

    classroom = get_object_or_404(Classroom, classroomID=id)

    if is_student(request.user) or not is_in_classroom(request.user, classroom):
        return redirect('index')

    if request.method == 'POST':

        student_emails = request.POST.get('student_emails')
        instructor_emails = request.POST.get('instructor_emails')
        invalid_emails = []

        if student_emails:
            invalid_emails = ClassroomController.inviteUsers(student_emails, id, True)
        else:
            invalid_emails = ClassroomController.inviteUsers(instructor_emails, id, False)
            
        error = "The following email addresses were unable to be reached: " + ", ".join(invalid_emails)
        return render(request, 'classroom_settings.html', {'message': 'Emails Sent! ' + error, 'classroomID': id})
    
    return render(request, 'classroom_settings.html', {'message': '', 'classroomID': id})

@login_required
def join_classroom(request):
    if request.method == 'POST':
        if 'confirm' in request.POST:
            classroom_id = request.POST.get('classroom_id')
            classroom = get_object_or_404(Classroom, classroomID=classroom_id)
            if is_student(request.user):
                classroom.students.add(request.user.student)
            else:
                classroom.instructors.add(request.user.instructor)
            messages.success(request, f"Welcome to {classroom.instructorName}'s classroom!")
            return redirect('index')
        
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            classroom_code = form.cleaned_data['classroom_code']
            try:
                classroom = Classroom.objects.get(classroomCode=classroom_code)
                confirm_form = ConfirmJoinClassroomForm(initial={
                    'classroom_id': classroom.classroomID,
                    'confirm': 'yes'
                })
                return render(request, 'confirm_join_classroom.html', {
                    'classroom': classroom,
                    'form': confirm_form
                })
            except Classroom.DoesNotExist:
                form.add_error('classroom_code', "Classroom not found. Please check the code and try again.")
    else:
        form = JoinClassroomForm()
    
    return render(request, 'join_classroom.html', {'form': form})


@login_required
def confirm_join_classroom(request):
    classroom_code = request.GET.get('classroom_code')
    if not classroom_code:
        messages.error(request, "Invalid classroom link.")
        return redirect('index')
    
    classroom = get_object_or_404(Classroom, classroomCode=classroom_code)
    
    form = ConfirmJoinClassroomForm(initial={
        'classroom_id': classroom.classroomID,
        'confirm': 'yes'
    })
    
    return render(request, 'confirm_join_classroom.html', {
        'classroom': classroom,
        'form': form
    })

@login_required
def create_topic(request, classroomID):

    form = TopicForm()  

    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topicName = form.cleaned_data['topicName']
            topicDescription = form.cleaned_data['topicDescription']
            topicNote = form.cleaned_data['topicNote']

            topic = TopicController.createNewTopic(topicName, topicDescription, topicNote)

            if topic:
                return redirect('topic', classroomID=classroomID, topicID=topic.topicID)

    return render(request, 'create_topic.html', {'form': form, 'classroomID': classroomID})


@login_required
def topic(request, classroomID, topicID):

    topic = get_object_or_404(Topic, topicID=topicID)
    return render(request, 'topic.html', {'topic': topic, 'classroomID': classroomID})
    
  
def create_question(request, classroomID):
    # If the user is a student, redirect them back
    if is_student(request.user):
        return redirect('index')
    
    form = QuestionForm()  

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            questionType = form.cleaned_data['questionType']
            questionPrompt = form.cleaned_data['questionPrompt']
            correctAnswer = form.cleaned_data['correctAnswer']

            question = QuestionController.createNewQuestion(questionType, questionPrompt, correctAnswer)

            if question:
                return redirect('question', classroomID=classroomID, questionID=question.questionID)

    return render(request, 'create_question.html', {'form': form, 'classroomID': classroomID})


@login_required
def question(request, classroomID, questionID):

    question = get_object_or_404(Question, questionID=questionID)
    return render(request, 'question.html', {'question': question, 'classroomID': classroomID})
    

@login_required
def modify_question(request, classroomID, questionID):

    if is_student(request.user): 
        return redirect('index')
    question = get_object_or_404(Question, questionID=questionID)
    modifyQuestionForm = ModifyQuestionForm(instance=question)
    if request.method == 'POST':
        modifyQuestionForm = ModifyQuestionForm(request.POST, instance=question)
        if modifyQuestionForm.is_valid():
            modifyQuestionForm.save()
            return redirect('question', classroomID=classroomID, questionID=question.questionID)

    return render(request, 'modify_question.html', {'form': modifyQuestionForm, 'classroomID': classroomID, 'question': question})

@login_required
def create_exercise(request):
    if is_student(request.user):
        return redirect('index')

    if request.method == 'POST':
        form = ExerciseForm(request.POST)

    if form.is_valid():
        exercise = form.save(commit=False)
        exercise.created_by = request.user
        exercise.save()
        return redirect('exercise_detail', exerciseID=exercise.exerciseID)
    else:
        form = ExerciseForm()
    
    return render(request, 'create_exercise.html', {'form': form})


@login_required
def exercise(request, classroomID, exerciseID):

    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    return render(request, 'exercise.html', {'exercise': exercise, 'classroomID': classroomID})
    

@login_required
def modify_exercise(request, classroomID, exerciseID):

    if is_student(request.user): 
        return redirect('index')
    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    modifyExerciseForm = ModifyExerciseForm(instance=exercise)
    if request.method == 'POST':
        modifyExerciseForm = ModifyExerciseForm(request.POST, instance=exercise)
        if modifyExerciseForm.is_valid():
            modifyExerciseForm.save()
            return redirect('exercise', classroomID=classroomID, exerciseID=exercise.exerciseID)

    return render(request, 'modify_exercise.html', {'form': modifyExerciseForm, 'classroomID': classroomID, 'exercise': exercise})