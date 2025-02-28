from django.shortcuts import render, get_object_or_404, redirect
from .forms import ClassroomForm, StudentForm, InstructorForm, JoinClassroomForm
from .models import Classroom, Student, Instructor, User
from django.contrib.auth import login
from django.contrib import messages
from .controllers import ClassroomController
from django.contrib.auth.decorators import login_required


def is_student(user):
    return hasattr(user, 'student')

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
            newClassroom = createClassroomForm.save()  
            newClassroom.instructors.add(request.user.instructor)
            return redirect('classroom', id=newClassroom.classroomID)

    return render(request, 'create_classroom.html', {'form': createClassroomForm})

@login_required
def classroom(request, id):

    classroom = get_object_or_404(Classroom, classroomID=id)

    #if the user is in the classroom, then let them see the classroom
    if (classroom.instructors.filter(userID=request.user.userID).exists() or
        classroom.students.filter(userID=request.user.userID).exists()):
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

    if request.method == 'POST':

        student_emails = request.POST.get('student_emails')
        instructor_emails = request.POST.get('instructor_emails')

        if student_emails:
            ClassroomController.inviteUsers(student_emails, id, True)
        else:
            ClassroomController.inviteUsers(instructor_emails, id, False)
            
        return render(request, 'classroom_settings.html', {'message': 'Emails Sent!'})
    
    return render(request, 'classroom_settings.html', {'message': ''})

@login_required
def join_classroom(request):
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            classroom_id = request.POST.get('classroom_id')
            classroom = get_object_or_404(Classroom, classroomID=classroom_id)
               
            classroom.students.add(request.user.student)
            
            messages.success(request, f"Welcome to {classroom.instructorName}'s classroom!")
            return redirect('index')
        
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            classroom_code = form.cleaned_data['classroom_code']
            try:
                classroom = Classroom.objects.get(classroomCode=classroom_code)
                return render(request, 'confirm_join_classroom.html', {
                    'classroom': classroom,
                    'student': request.user.student
                })
            except Classroom.DoesNotExist:
                form.add_error('classroom_code', "Classroom not found. Please check the code and try again.")
    else:
        form = JoinClassroomForm()
    
    return render(request, 'join_classroom.html', {'form': form})