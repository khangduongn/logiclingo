from django.contrib import admin
from .models import Classroom, Student, Instructor, User

# Register your models here.
admin.site.register(Classroom)
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(User)