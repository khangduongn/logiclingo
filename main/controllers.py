from .models import Classroom, Question, Topic, Exercise
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

class TopicController:

    @staticmethod
    def createNewTopic(topicName: str, topicDescription: str, topicNote: str, classroom):
        
        topicName = topicName.strip()
        topicDescription = topicDescription.strip()
        topicNote = topicNote.strip()

        #check if the topic name, desc, and note are not empty
        if topicName and topicDescription and topicNote:
            return Topic.objects.create(
                topicName=topicName,
                topicDescription=topicDescription,
                topicNote=topicNote, 
                classroom=classroom
            )
    
    @staticmethod
    def modifyTopic(topicID: int, topicName: str, topicDescription: str, topicNote: str):
        # Get the topic object
        topic = get_object_or_404(Topic, topicID=topicID)
        
        # Validate inputs
        topicName = topicName.strip()
        topicDescription = topicDescription.strip()
        topicNote = topicNote.strip()
        
        # Check if the topic name, desc, and note are not empty
        if not (topicName and topicDescription and topicNote):
            raise ValueError("Topic name, description, and note cannot be empty.")
        
        # Update the topic fields
        topic.topicName = topicName
        topic.topicDescription = topicDescription
        topic.topicNote = topicNote
        topic.save()
        
        return topic

    @staticmethod
    def deleteTopic(topicID: int):
        topic = get_object_or_404(Topic, topicID=topicID)
        topic.delete()
        return True
    
class ExerciseController:

    @staticmethod
    def createNewExercise(exerciseName: str, exerciseDescription: str, topic):
        
        exerciseName = exerciseName.strip()
        exerciseDescription = exerciseDescription.strip()

        #check if the exercise name and description are not empty
        if exerciseName and exerciseDescription:
            return Exercise.objects.create(
                exerciseName=exerciseName,
                exerciseDescription=exerciseDescription, 
                topic=topic
            )

        else:
            return None
        
class QuestionController:

    @staticmethod
    def createNewQuestion(questionType: str, questionPrompt: str, correctAnswer: str, exercise):
        
        questionPrompt = questionPrompt.strip()
        correctAnswer = correctAnswer.strip()

        #check if the question prompt and correct answer are not empty
        if questionPrompt and correctAnswer:
            return Question.objects.create(
                questionType=questionType,
                questionPrompt=questionPrompt,
                correctAnswer=correctAnswer,
                exercise=exercise
            )

        else:
            return None