from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Classroom)
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Question)
admin.site.register(Answer)