from .models import Classroom
from django.shortcuts import get_object_or_404

class ClassroomController:

    @staticmethod
    def inviteUsers(emails: str, classroomID: int, isStudent: bool):
        
        classroom = get_object_or_404(Classroom, classroomID=classroomID)
        
        for email in emails.split(","):
            classroom.sendEmail(email, classroom.classroomCode, isStudent)