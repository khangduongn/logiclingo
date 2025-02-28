from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import ClassroomForm, StudentForm, InstructorForm, LoginForm, JoinClassroomForm
from .models import Classroom, Student, Instructor, User
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Classroom, Student, Instructor, User
from .controllers import ClassroomController

from .controllers import ClassroomController


def index(request):
    return render(request, 'index.html')

def create_classroom(request):
    createClassroomForm = ClassroomForm()

    if request.method == 'POST':
        createClassroomForm = ClassroomForm(request.POST)
        if createClassroomForm.is_valid():
            newClassroom = createClassroomForm.save()  
            return redirect('classroom', id=newClassroom.classroomID)

    return render(request, 'create_classroom.html', {'form': createClassroomForm})

def classroom(request, id):
    classroom = get_object_or_404(Classroom, classroomID=id)
    return render(request, 'classroom.html', {'classroom': classroom})

def student(request, id):
    student = get_object_or_404(Student, userID=id)
    return render(request, 'student.html', {'student': student})

def instructor(request, id):
    instructor = get_object_or_404(Instructor, userID=id)
    return render(request, 'instructor.html', {'instructor': instructor})

def create_student(request):

    createStudentForm = StudentForm()

    if request.method == 'POST':
        createStudentForm = StudentForm(request.POST)
        if createStudentForm.is_valid():
            newStudent = createStudentForm.save()
            return redirect('student', id=newStudent.userID)

    return render(request, 'create_student.html', {'form': createStudentForm})

def create_instructor(request):

    createInstructorForm = InstructorForm()

    if request.method == 'POST':
        createInstructorForm = InstructorForm(request.POST)
        if createInstructorForm.is_valid():
            newInstructor = createInstructorForm.save()
            return redirect('instructor', id=newInstructor.userID)

    return render(request, 'create_instructor.html', {'form': createInstructorForm})

def user_login(request):
    loginForm = LoginForm()
    if request.method == 'POST':
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            username = loginForm.cleaned_data['username']
            password = loginForm.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect('student', id=user.id)
            else:
                loginForm.add_error(None, "Invalid username or password")
    
    return render(request, 'login.html', {'form': loginForm})

def classroom_settings(request, id):

    if request.method == 'POST':

        student_emails = request.POST.get('student_emails')
        instructor_emails = request.POST.get('instructor_emails')

        if student_emails:
            ClassroomController.inviteUsers(student_emails, id, True)
        else:
            ClassroomController.inviteUsers(instructor_emails, id, False)
            
        return render(request, 'classroom_settings.html', {'message': 'Emails Sent!'})
    
    return render(request, 'classroom_settings.html', {'message': ''})

def join_classroom(request, student_id):
    student = get_object_or_404(Student, userID=student_id)
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            classroom_id = request.POST.get('classroom_id')
            classroom = get_object_or_404(Classroom, classroomID=classroom_id)
            
            student.enrolled = True
            student.save()
            
            classroom.students.add(student)
            
            messages.success(request, f"Welcome to {classroom.instructorLastName}'s classroom!")
            return redirect('student', id=student_id)
        
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            classroom_code = form.cleaned_data['classroom_code']
            try:
                classroom = Classroom.objects.get(classroomCode=classroom_code)
                return render(request, 'confirm_join_classroom.html', {
                    'classroom': classroom,
                    'student': student
                })
            except Classroom.DoesNotExist:
                form.add_error('classroom_code', "Classroom not found. Please check the code and try again.")
    else:
        form = JoinClassroomForm()
    
    return render(request, 'join_classroom.html', {'form': form, 'student': student})

def classroom_settings(request, id):

    if request.method == 'POST':

        student_emails = request.POST.get('student_emails')
        instructor_emails = request.POST.get('instructor_emails')

        if student_emails:
            ClassroomController.inviteUsers(student_emails, id, True)
        else:
            ClassroomController.inviteUsers(instructor_emails, id, False)
            
        return render(request, 'classroom_settings.html', {'message': 'Emails Sent!'})
    
    return render(request, 'classroom_settings.html', {'message': ''})