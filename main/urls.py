from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('create_classroom/', views.create_classroom, name='create_classroom'),
    path('classroom/<int:id>/', views.classroom, name='classroom'),
    path('create_student/', views.create_student, name='create_student'),
    path('create_instructor/', views.create_instructor, name='create_instructor'),
    path('join-classroom/', views.join_classroom, name='join_classroom'),
    path('classroom/<int:id>/settings', views.classroom_settings, name='classroom_settings'),
    path('confirm-join/', views.confirm_join_classroom, name='confirm_join_classroom'),
    path('classroom/<int:classroomID>/add_existing_topics/', views.add_existing_topics, name='add_existing_topics'),
    path('classroom/<int:classroomID>/create_topic/', views.create_topic, name='create_topic'),
    path('classroom/<int:classroomID>/import_topics/', views.import_topics, name='import_topics'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/', views.topic, name='topic'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/edit/', views.edit_topic, name='edit_topic'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/delete/', views.delete_topic, name='delete_topic'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/exercise/<int:exerciseID>/add_existing_questions/', views.add_existing_questions, name='add_existing_questions'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/exercise/<int:exerciseID>/create_question/', views.create_question, name='create_question'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/exercise/<int:exerciseID>/import_questions/', views.import_questions, name='import_questions'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/exercise/<int:exerciseID>/question/<int:questionID>/', views.question, name='question'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/exercise/<int:exerciseID>/question/<int:questionID>/modify/', views.modify_question, name='modify_question'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/add_existing_exercises/', views.add_existing_exercises, name='add_existing_exercises'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/create_exercise/', views.create_exercise, name='create_exercise'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/exercise/<int:exerciseID>/', views.exercise, name='exercise'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/exercise/<int:exerciseID>/modify/', views.modify_exercise, name='modify_exercise'),
    path('classroom/<int:classroomID>/save_question/', views.save_question, name='save_question'),
    path('question/get_form/', views.get_question_form, name='get_question_form'),
    path('classroom/<int:classroomID>/saved_questions/', views.saved_questions, name='saved_questions'),
    path('classroom/<int:classroomID>/question/<int:questionID>/add_to_exercise/', views.add_question_to_exercise, name='add_question_to_exercise'),
    path('classroom/<int:classroomID>/topic/<int:topicID>/import_exercises/', views.import_exercises, name='import_exercises'),
]