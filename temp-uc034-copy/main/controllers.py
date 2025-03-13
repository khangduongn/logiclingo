from .models import Classroom
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class ClassroomController:

    @staticmethod
    def inviteUsers(emails: str, classroomID: int, isStudent: bool):
        
        classroom = get_object_or_404(Classroom, classroomID=classroomID)
        invalid_emails = []

        for email in emails.split(","):

            email = email.strip()
            try:
                validate_email(email)
                success = classroom.sendEmail(email, classroom.classroomCode, isStudent)

                if not success:
                    invalid_emails.append(email)

            except ValidationError:
                invalid_emails.append(email)
                
        return invalid_emails