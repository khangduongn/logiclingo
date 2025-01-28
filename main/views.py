from django.shortcuts import render
from django.http import HttpResponse
from .forms import ClassroomForm
from .models import Classroom

def index(request):
    classrooms = Classroom.objects.all()

    if request.method == 'POST':
        createClassroomForm = ClassroomForm(request.POST)
        if createClassroomForm.is_valid():
            createClassroomForm.save()  
            createClassroomForm = ClassroomForm()

    else:
        createClassroomForm = ClassroomForm()

    return render(request, 'index.html', {'form': createClassroomForm, 'classrooms': classrooms})
