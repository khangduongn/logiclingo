from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('classroom/<int:id>/', views.classroom, name='classroom'),
]