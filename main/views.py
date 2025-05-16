from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from .models import *
from django.contrib.auth import login
from django.contrib import messages
from .controllers import *
from django.contrib.auth.decorators import login_required
import csv, io


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

    if is_in_classroom(request.user, classroom):
        topics = classroom.topics.all()
        return render(request, 'classroom.html', {
            'classroom': classroom,
            'topics': topics
        })
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

    message = ''
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type', '')
        
        if form_type == 'access_settings':
            open_value = request.POST.get('open') == 'true'
            classroom.open = open_value
            classroom.save()
            message = 'Classroom access settings updated successfully!'
            
        elif form_type == 'invite_students':
            student_emails = request.POST.get('student_emails')
            if student_emails:
                invalid_emails = ClassroomController.inviteUsers(student_emails, id, True)
                
                emails = [email.strip() for email in student_emails.split(',')]
                for email in emails:
                    if email and email not in invalid_emails:
                        InvitedStudent.objects.get_or_create(classroom=classroom, email=email)
                
                if invalid_emails:
                    message = "Emails Sent! The following email addresses were unable to be reached: " + ", ".join(invalid_emails)
                else:
                    message = "Invitations sent successfully!"
        
        elif form_type == 'invite_instructors':
            instructor_emails = request.POST.get('instructor_emails')
            if instructor_emails:
                invalid_emails = ClassroomController.inviteUsers(instructor_emails, id, False)
                if invalid_emails:
                    message = "Emails Sent! The following email addresses were unable to be reached: " + ", ".join(invalid_emails)
                else:
                    message = "Invitations sent successfully!"
    
    invited_students = InvitedStudent.objects.filter(classroom=classroom).order_by('-created_at')
    
    return render(request, 'classroom_settings.html', {
        'message': message, 
        'classroomID': id,
        'classroom': classroom,
        'invited_students': invited_students
    })

@login_required
def join_classroom(request):
    if request.method == 'POST':
        if 'confirm' in request.POST:
            classroom_id = request.POST.get('classroom_id')
            classroom = get_object_or_404(Classroom, classroomID=classroom_id)
            
            if is_student(request.user) and not classroom.open:
                invited = InvitedStudent.objects.filter(
                    classroom=classroom, 
                    email=request.user.email
                ).exists()
                
                if not invited:
                    messages.error(request, "You are not invited to this classroom.")
                    return redirect('index')
            
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
                
                if is_student(request.user) and not classroom.open:
                    invited = InvitedStudent.objects.filter(
                        classroom=classroom, 
                        email=request.user.email
                    ).exists()
                    
                    if not invited:
                        form.add_error('classroom_code', "You are not invited to this classroom.")
                        return render(request, 'join_classroom.html', {'form': form})
                
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
    
    if is_student(request.user) and not classroom.open:
        invited = InvitedStudent.objects.filter(
            classroom=classroom, 
            email=request.user.email
        ).exists()
        
        if not invited:
            messages.error(request, "You are not invited to this classroom.")
            return redirect('index')
    
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
    if is_student(request.user):
        return redirect('index')
    
    classroom = get_object_or_404(Classroom, classroomID=classroomID)
    form = TopicForm()  

    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topicName = form.cleaned_data['topicName']
            topicDescription = form.cleaned_data['topicDescription']
            topicNote = form.cleaned_data['topicNote']

            topic = TopicController.createNewTopic(topicName, topicDescription, topicNote, classroom, request.user.instructor)

            if topic:
                return redirect('topic', classroomID=classroomID, topicID=topic.topicID)

    return render(request, 'create_topic.html', {'form': form, 'classroomID': classroomID})

@login_required
def topic(request, classroomID, topicID):
    topic = get_object_or_404(Topic, topicID=topicID)
    return render(request, 'topic.html', {
        'topic': topic, 
        'classroomID': classroomID,
        'is_student': is_student(request.user)
    })
    
@login_required
def add_existing_topics(request, classroomID):
    if is_student(request.user):
        return redirect('index')

    classroom = get_object_or_404(Classroom, classroomID=classroomID)
    available_topics = Topic.objects.filter(created_by=request.user.instructor).exclude(classrooms=classroom)

    form = AddExistingTopicsForm()
    form.fields['topics'].queryset = available_topics
    
    if request.method == 'POST':
        form = AddExistingTopicsForm(request.POST)
        form.fields['topics'].queryset = available_topics 

        if form.is_valid():
            for topic in form.cleaned_data['topics']:
                topic.classrooms.add(classroom)
            return redirect('classroom', id=classroomID)
        
    return render(request, 'add_existing_topics.html', {
        'form': form,
        'classroom': classroom,
        'no_existing_topics': not form.fields['topics'].queryset.exists(),
    })

def create_question(request, classroomID, topicID, exerciseID):
    if is_student(request.user):
        return redirect('index')
    
    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    form = QuestionForm()  

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            questionType = form.cleaned_data['questionType']
            questionPrompt = form.cleaned_data['questionPrompt']
            correctAnswer = form.cleaned_data['correctAnswer']

            question = QuestionController.createNewQuestion(questionType, questionPrompt, correctAnswer, exercise, request.user.instructor)

            if question:
                return redirect('question', classroomID=classroomID, topicID=topicID, exerciseID=exerciseID, questionID=question.questionID)

    return render(request, 'create_question.html', {'form': form, 'classroomID': classroomID, 'topicID': topicID, 'exerciseID': exerciseID})

@login_required
def question(request, classroomID, topicID, exerciseID, questionID):
    question = get_object_or_404(Question, questionID=questionID)
    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)

    if not question.exercises.filter(exerciseID=exerciseID).exists():
        messages.error(request, "This question does not belong to this exercise.")
        return redirect('exercise', classroomID=classroomID, topicID=topicID, exerciseID=exerciseID)

    if is_student(request.user):
        form = AnswerForm()
        if request.method == 'POST':
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.cleaned_data['answer']
                correct = answer.strip().lower() == question.correctAnswer.strip().lower()

                answer_result = "correct" if correct else "incorrect"

                Answer.objects.create(
                    question=question,
                    user=request.user,
                    answer=answer,
                    correct=correct
                )
                
                exercise_questions = exercise.questions.all().order_by('order')
                
                current_index = None
                for i, q in enumerate(exercise_questions):
                    if q.questionID == question.questionID:
                        current_index = i
                        break
                
                if current_index is not None and current_index + 1 < len(exercise_questions):
                    next_question = exercise_questions[current_index + 1]
                    return redirect('question', 
                                  classroomID=classroomID, 
                                  topicID=topicID, 
                                  exerciseID=exerciseID, 
                                  questionID=next_question.questionID)
                else:
                    return render(request, 'exercise_complete.html', {
                        'classroomID': classroomID,
                        'topicID': topicID,
                        'exerciseID': exerciseID,
                        'exercise': exercise
                    })
       
        return render(request, 'question_student_view.html', {
            'question': question, 
            'form': form, 
            'classroomID': classroomID, 
            'topicID': topicID, 
            'exerciseID': exerciseID
        })

    return render(request, 'question.html', {
        'question': question, 
        'classroomID': classroomID, 
        'topicID': topicID, 
        'exerciseID': exerciseID
    })

@login_required
def modify_question(request, classroomID, topicID, exerciseID, questionID):
    if is_student(request.user): 
        return redirect('index')
    question = get_object_or_404(Question, questionID=questionID)
    modifyQuestionForm = ModifyQuestionForm(instance=question)
    if request.method == 'POST':
        modifyQuestionForm = ModifyQuestionForm(request.POST, instance=question)
        if modifyQuestionForm.is_valid():
            modifyQuestionForm.save()
            return redirect('question', classroomID=classroomID, topicID=topicID, exerciseID=exerciseID, questionID=question.questionID)

    return render(request, 'modify_question.html', {'form': modifyQuestionForm, 'classroomID': classroomID, 'topicID': topicID, 'exerciseID': exerciseID, 'question': question})

@login_required
def create_exercise(request, classroomID, topicID):
    if is_student(request.user):
        return redirect('index')
    
    topic = get_object_or_404(Topic, topicID=topicID)
    form = ExerciseForm()

    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exerciseName = form.cleaned_data['exerciseName']
            exerciseDescription = form.cleaned_data['exerciseDescription']

            exercise = ExerciseController.createNewExercise(exerciseName, exerciseDescription, topic, request.user.instructor)

            return redirect('exercise', classroomID=classroomID, topicID=topicID, exerciseID=exercise.exerciseID)
        else:
            form = ExerciseForm()
    
    return render(request, 'create_exercise.html', {'form': form, 'classroomID': classroomID, 'topicID': topicID})

@login_required
def exercise(request, classroomID, topicID, exerciseID):
    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    return render(request, 'exercise.html', {'exercise': exercise, 'classroomID': classroomID, 'topicID': topicID})

@login_required
def modify_exercise(request, classroomID, topicID, exerciseID):
    if is_student(request.user): 
        return redirect('index')
    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    modifyExerciseForm = ModifyExerciseForm(instance=exercise)
    if request.method == 'POST':
        modifyExerciseForm = ModifyExerciseForm(request.POST, instance=exercise)
        if modifyExerciseForm.is_valid():
            modifyExerciseForm.save()
            return redirect('exercise', classroomID=classroomID, topicID=topicID, exerciseID=exercise.exerciseID)

    return render(request, 'modify_exercise.html', {'form': modifyExerciseForm, 'classroomID': classroomID, 'topicID': topicID, 'exercise': exercise})

@login_required
def edit_topic(request, classroomID, topicID):
    if is_student(request.user):
        return redirect('index')
    
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic_name = form.cleaned_data['topicName']
            topic_description = form.cleaned_data['topicDescription']
            topic_note = form.cleaned_data['topicNote']
            
            try:
                TopicController.modifyTopic(topicID, topic_name, topic_description, topic_note)
                messages.success(request, 'Topic updated successfully!')
                return redirect('topic', classroomID=classroomID, topicID=topicID)
            except Exception as e:
                messages.error(request, str(e))
                return render(request, 'edit_topic.html', {
                    'form': form,
                    'classroomID': classroomID,
                    'topicID': topicID
                })
    else:
        topic = get_object_or_404(Topic, topicID=topicID)
        form = TopicForm(instance=topic)
    
    return render(request, 'edit_topic.html', {
        'form': form,
        'classroomID': classroomID,
        'topicID': topicID
    })

@login_required
def delete_topic(request, classroomID, topicID):
    if is_student(request.user):
        return redirect('index')
    
    topic = get_object_or_404(Topic, topicID=topicID)
    
    if request.method == 'POST':
        try:
            TopicController.deleteTopic(topicID)
            messages.success(request, 'Topic deleted successfully!')
            return redirect('classroom', id=classroomID)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('topic', classroomID=classroomID, topicID=topicID)
    
    return render(request, 'delete_topic.html', {
        'classroomID': classroomID,
        'topicID': topicID,
        'topic': topic
    })

@login_required
def add_existing_exercises(request, classroomID, topicID):
    if is_student(request.user):
        return redirect('index')

    topic = get_object_or_404(Topic, topicID=topicID)
    available_exercises = Exercise.objects.filter(created_by=request.user.instructor).exclude(topics=topic)

    form = AddExistingExercisesForm()
    form.fields['exercises'].queryset = available_exercises
    
    if request.method == 'POST':
        form = AddExistingExercisesForm(request.POST)
        form.fields['exercises'].queryset = available_exercises 

        if form.is_valid():
            for exercise in form.cleaned_data['exercises']:
                exercise.topics.add(topic)
            return redirect('topic', classroomID=classroomID, topicID=topicID)
        
    return render(request, 'add_existing_exercises.html', {
        'form': form,
        'topic': topic,
        'classroomID': classroomID,
        'no_existing_exercises': not form.fields['exercises'].queryset.exists(),
    })

@login_required
def import_questions(request, classroomID, topicID, exerciseID):
    if is_student(request.user):
        return redirect('index')
    
    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    form = ImportQuestionForm()
    preview_data = []

    VALID_TYPES = dict(Question.QUESTION_TYPES).keys()

    if request.method == 'POST':
        if 'confirm' in request.POST:
            preview_data = request.session.get('preview_questions', [])
            created = 0
            for row in preview_data:
                if row['valid']:
                    QuestionController.createNewQuestion(
                        row['questionType'],
                        row['questionPrompt'],
                        row['correctAnswer'],
                        exercise,
                        request.user.instructor
                    )
                    created += 1
            messages.success(request, f"{created} question(s) successfully imported.")
            request.session.pop('preview_questions', None)
            return redirect('exercise', classroomID=classroomID, topicID=topicID, exerciseID=exerciseID)
        else:
            form = ImportQuestionForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['csv_file']
                try:
                    csv_file = file.read().decode('utf-8')
                    io_string = io.StringIO(csv_file)
                    reader = csv.DictReader(io_string)

                    for row in reader:
                        type = row.get("questionType", "").strip()
                        prompt = row.get("questionPrompt", "").strip()
                        answer = row.get("correctAnswer", "").strip()

                        entry = {
                            "questionType": type,
                            "questionPrompt": prompt,
                            "correctAnswer": answer,
                            "valid": True,
                            "error": ""
                        }

                        if not type or not prompt or not answer:
                            entry['valid'] = False
                            entry['error'] = "Missing required fields"
                        elif type not in VALID_TYPES:
                            entry['valid'] = False
                            entry['error'] = f"Invalid questionType: '{type}'"
                        elif Question.objects.filter(
                            questionType=type, 
                            questionPrompt=prompt, 
                            correctAnswer=answer, 
                            exercises=exercise
                        ).exists():
                            entry['valid'] = False
                            entry['error'] = "Prompt already exists in exercise"
                        
                        preview_data.append(entry)

                    request.session['preview_questions'] = preview_data

                except Exception as e:
                    messages.error(request, "Error reading CSV file")
                    return redirect(request.path)
    has_valid = any(row['valid'] for row in preview_data)
    return render(request, 'import_questions.html', {
        'form': form,
        'preview_data': preview_data,
        'has_valid': has_valid,
        'classroomID': classroomID,
        'topicID': topicID,
        'exerciseID': exerciseID
    })

@login_required
def import_exercises(request, classroomID, topicID):
    if is_student(request.user):
        return redirect('index')

    topic = get_object_or_404(Topic, topicID=topicID)
    form = ImportExerciseForm() 
    preview_data = None
    has_valid = False
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            preview_data = request.session.get('exercise_preview_data', [])
            count = ExerciseController.createExercisesFromPreview(preview_data, topic)
            if count > 0:
                messages.success(request, f'Successfully imported {count} exercises!')
            else:
                messages.warning(request, 'No valid exercises were found to import.')
            if 'exercise_preview_data' in request.session:
                del request.session['exercise_preview_data']
            return redirect('topic', classroomID=classroomID, topicID=topicID)
            
        elif 'csv_file' in request.FILES:
            form = ImportExerciseForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'Please upload a CSV file.')
                else:
                    preview_data, has_valid = ExerciseController.importExercisesFromCSV(csv_file, topic)
                    request.session['exercise_preview_data'] = preview_data
    
    return render(request, 'import_exercises.html', {
        'form': form,
        'preview_data': preview_data,
        'has_valid': has_valid,
        'classroomID': classroomID,
        'topicID': topicID,
        'topic': topic
    })

def save_question(request, classroomID):
    if is_student(request.user):
        return redirect('index')
    
    form = SaveQuestionForm()
    
    if request.method == 'POST':
        form = SaveQuestionForm(request.POST)
        if form.is_valid():
            question_type = form.cleaned_data['questionType']
            question_prompt = form.cleaned_data['questionPrompt']
            correct_answer = form.cleaned_data['correctAnswer']
            
            question = QuestionController.saveQuestion(
                question_type, 
                question_prompt, 
                correct_answer, 
                request.user.instructor
            )
            
            if question:
                messages.success(request, 'Question saved successfully!')
                return redirect('saved_questions', classroomID=classroomID)
            else:
                messages.error(request, 'Failed to save question.')
    
    return render(request, 'save_question.html', {
        'form': form,
        'classroomID': classroomID
    })

@login_required
def saved_questions(request, classroomID):
    if is_student(request.user):
        return redirect('index')
    
    classroom = get_object_or_404(Classroom, classroomID=classroomID)
    saved_questions = QuestionController.getSavedQuestions(request.user.instructor)
    
    return render(request, 'saved_questions.html', {
        'classroom': classroom,
        'saved_questions': saved_questions,
        'classroomID': classroomID
    })

@login_required
def add_existing_questions(request, classroomID, topicID, exerciseID):
    if is_student(request.user):
        return redirect('index')

    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    available_questions = Question.objects.filter(created_by=request.user.instructor).exclude(exercises=exercise)

    form = AddExistingQuestionsForm()
    form.fields['questions'].queryset = available_questions
    
    if request.method == 'POST':
        form = AddExistingQuestionsForm(request.POST)
        form.fields['questions'].queryset = available_questions 

        if form.is_valid():
            for question in form.cleaned_data['questions']:
                question.exercises.add(exercise)
            return redirect('exercise', classroomID=classroomID, topicID=topicID, exerciseID=exerciseID)
        
    return render(request, 'add_existing_questions.html', {
        'form': form,
        'exercise': exercise,
        'classroomID': classroomID,
        'topicID': topicID,
        'no_existing_questions': not form.fields['questions'].queryset.exists(),
    })

@login_required
def add_question_to_exercise(request, classroomID, questionID):
    if is_student(request.user):
        return redirect('index')
    
    question = get_object_or_404(Question, questionID=questionID, created_by=request.user.instructor)
    form = AddQuestionToExerciseForm(classroom_id=classroomID)
    
    if request.method == 'POST':
        form = AddQuestionToExerciseForm(request.POST, classroom_id=classroomID)
        if form.is_valid():
            exercise = form.cleaned_data['exercise']
            
            new_question = QuestionController.addQuestionToExercise(questionID, exercise.exerciseID)
            
            if new_question:
                messages.success(request, 'Question added to exercise successfully!')
                return redirect('exercise', classroomID=classroomID, topicID=exercise.topic.topicID, exerciseID=exercise.exerciseID)
            else:
                messages.error(request, 'Failed to add question to exercise.')
    
    return render(request, 'add_question_to_exercise.html', {
        'form': form,
        'question': question,
        'classroomID': classroomID
    })

@login_required
def import_topics(request, classroomID):
    if is_student(request.user):
        return redirect('index')
    
    classroom = get_object_or_404(Classroom, classroomID=classroomID)
    
    if not classroom.instructors.filter(userID=request.user.userID).exists():
        messages.error(request, "You don't have permission to import topics for this classroom.")
        return redirect('classroom', id=classroomID)
    
    form = ImportTopicForm()
    preview_data = []
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            preview_data = request.session.get('preview_topics', [])
            created = 0
            for row in preview_data:
                if row['valid']:
                    TopicController.createNewTopic(
                        row['topicName'],
                        row['topicDescription'],
                        row['topicNote'],
                        classroom,
                        request.user.instructor
                    )
                    created += 1
            messages.success(request, f"{created} topic(s) successfully imported.")
            request.session.pop('preview_topics', None)
            return redirect('classroom', id=classroomID)
        else:
            form = ImportTopicForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['csv_file']
                try:
                    csv_file = file.read().decode('utf-8')
                    io_string = io.StringIO(csv_file)
                    reader = csv.DictReader(io_string)

                    for row in reader:
                        name = row.get("topicName", "").strip()
                        description = row.get("topicDescription", "").strip()
                        note = row.get("topicNote", "").strip()

                        entry = {
                            "topicName": name,
                            "topicDescription": description,
                            "topicNote": note,
                            "valid": True,
                            "error": ""
                        }

                        if not name or not description:
                            entry['valid'] = False
                            entry['error'] = "Missing required fields"
                        elif len(name) > 100:
                            entry['valid'] = False
                            entry['error'] = "Topic name is too long"
                        elif len(description) > 500:
                            entry['valid'] = False
                            entry['error'] = "Topic description is too long"
                        elif note and len(note) > 1000:
                            entry['valid'] = False
                            entry['error'] = "Topic note is too long"
                        elif Topic.objects.filter(
                            topicName=name,
                            classrooms=classroom
                        ).exists():
                            entry['valid'] = False
                            entry['error'] = "Topic name already exists in classroom"
                        
                        preview_data.append(entry)

                    request.session['preview_topics'] = preview_data

                except Exception as e:
                    messages.error(request, f"Error reading CSV file: {str(e)}")
                    return redirect(request.path)
    
    has_valid = any(row['valid'] for row in preview_data)
    return render(request, 'import_topics.html', {
        'form': form,
        'preview_data': preview_data,
        'has_valid': has_valid,
        'classroomID': classroomID,
        'classroom': classroom
    })

@login_required
def start_exercise(request, classroomID, topicID, exerciseID):
    if not is_student(request.user):
        return redirect('index')
    
    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    
    first_question = exercise.questions.order_by('order').first()
    
    if not first_question:
        messages.error(request, "This exercise has no questions.")
        return redirect('exercise', classroomID=classroomID, topicID=topicID, exerciseID=exerciseID)
    
    return redirect('question', 
                   classroomID=classroomID, 
                   topicID=topicID, 
                   exerciseID=exerciseID, 
                   questionID=first_question.questionID)

@login_required
def next_question(request, classroomID, topicID, exerciseID, questionID):
    if not is_student(request.user):
        return redirect('index')
    
    current_question = get_object_or_404(Question, questionID=questionID)
    exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
    
    next_question = Question.objects.filter(
        exercises=exercise,
        order__gt=current_question.order
    ).order_by('order').first()
    
    if next_question:
        return redirect('question', 
                       classroomID=classroomID, 
                       topicID=topicID, 
                       exerciseID=exerciseID, 
                       questionID=next_question.questionID)
    else:
        return render(request, 'exercise_complete.html', {
            'classroomID': classroomID,
            'topicID': topicID,
            'exerciseID': exerciseID,
            'exercise': exercise
        })
