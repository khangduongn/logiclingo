from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('create_classroom/', views.create_classroom, name='create_classroom'),
    path('classroom/<int:id>/', views.classroom, name='classroom'),
    path('create_student/', views.create_student, name='create_student'),
    path('create_instructor/', views.create_instructor, name='create_instructor'),
    path('classroom/<int:classroomID>/create_question/', views.create_question, name='create_question'),
    path('classroom/<int:classroomID>/question/<int:questionID>/', views.question, name='question'),
    path('join-classroom/', views.join_classroom, name='join_classroom'),
    path('classroom/<int:id>/settings', views.classroom_settings, name='classroom_settings'),
    path('confirm-join/', views.confirm_join_classroom, name='confirm_join_classroom'),
    path('classroom/<int:classroomID>/question/<int:questionID>/modify/', views.modify_question, name='modify_question'),

]