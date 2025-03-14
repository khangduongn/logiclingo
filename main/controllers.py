from .models import Classroom, Question
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
    
class QuestionController:

    @staticmethod
    def createNewQuestion(questionType: str, questionPrompt: str, correctAnswer: str):
        
        questionPrompt = questionPrompt.strip()
        correctAnswer = correctAnswer.strip()

        #check if the question prompt and correct answer are not empty
        if questionPrompt and correctAnswer:
            return Question.objects.create(
                questionType=questionType,
                questionPrompt=questionPrompt,
                correctAnswer=correctAnswer
            )

        else:
            return None