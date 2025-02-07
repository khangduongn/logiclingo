from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import ClassroomForm
from .models import Classroom

def index(request):

    createClassroomForm = ClassroomForm()

    if request.method == 'POST':
        createClassroomForm = ClassroomForm(request.POST)
        if createClassroomForm.is_valid():
            newClassroom = createClassroomForm.save()  
            return redirect('classroom', id=newClassroom.id)

    return render(request, 'index.html', {'form': createClassroomForm})


def classroom(request, id):
    classroom = get_object_or_404(Classroom, id=id)
    return render(request, 'classroom.html', {'classroom': classroom})