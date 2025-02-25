from django.urls import path
from . import views

urlpatterns = [
    path('create_classroom/', views.create_classroom, name='create_classroom'),
    path('classroom/<int:id>/', views.classroom, name='classroom'),
    path('create_student/', views.create_student, name='create_student'),
    path('create_instructor/', views.create_instructor, name='create_instructor'),
    path('student/<int:id>/', views.student, name='student'),
    path('instructor/<int:id>/', views.instructor, name='instructor'),
    path('classroom/<int:id>/settings', views.classroom_settings, name='classroom_settings'),
]