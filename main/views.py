from django.shortcuts import render, get_object_or_404, redirect
from .forms import ClassroomForm, StudentForm, InstructorForm, JoinClassroomForm, ConfirmJoinClassroomForm
from .models import Classroom, Student, Instructor, User
from django.contrib.auth import login
from django.contrib import messages
from .controllers import ClassroomController
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

        if student_emails:
            ClassroomController.inviteUsers(student_emails, id, True)
        else:
            ClassroomController.inviteUsers(instructor_emails, id, False)
            
        return render(request, 'classroom_settings.html', {'message': 'Emails Sent!', 'classroomID': id})
    
    return render(request, 'classroom_settings.html', {'message': '', 'classroomID': id})

@login_required
def join_classroom(request):
    if request.method == 'POST':
        form = ConfirmJoinClassroomForm(request.POST)
        
        if form.is_valid():
            classroom_id = form.cleaned_data['classroom_id']
            classroom = get_object_or_404(Classroom, classroomID=classroom_id)
            
            classroom.students.add(request.user.student)
            messages.success(request, f"Welcome to {classroom.instructorName}'s classroom!")
            return redirect('index')

    form = JoinClassroomForm()
    return render(request, 'join_classroom.html', {'form': form})


@login_required
def confirm_join_classroom(request):
    classroom_code = request.GET.get('classroom_code')

    if not classroom_code:
        messages.error(request, "Invalid classroom link.")
        return redirect('index')

    try:
        classroom = Classroom.objects.get(classroomCode=classroom_code)
    except Classroom.DoesNotExist:
        messages.error(request, "Classroom not found.")
        return redirect('index')

    form = ConfirmJoinClassroomForm(initial={'classroom_id': classroom.classroomID})

    return render(request, 'confirm_join_classroom.html', {
        'classroom': classroom,
        'form': form
    })