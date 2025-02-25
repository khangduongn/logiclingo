from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import ClassroomForm, StudentForm, InstructorForm
from .models import Classroom, Student, Instructor, User
from django.http import Http404

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

def login(request):
    loginForm = LoginForm()
    if request.method == 'POST':
        loginForm = LoginForm(request.POST)
        if loginForm.is_valid():
            username = loginForm.cleaned_data['username']
            password = loginForm.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('student') 
            else:
                loginForm.add_error(None, "Invalid username or password")

    
    return render(request, 'login.html', {'form': loginForm})