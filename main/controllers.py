from .models import Classroom, Question, Topic, Exercise, Answer
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import csv
import io

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
    
    @staticmethod
    def importTopicsFromCSV(file, classroom):
        """
        Import topics from a CSV file with optional questions
        CSV format can include:
        - Basic topic fields (topicName, topicDescription, topicNote)
        - Optional exercise fields (exerciseName, exerciseDescription)
        - Optional question fields (questionType, questionPrompt, correctAnswer)
        
        Returns a tuple of (success_count, exercise_count, question_count, error_rows, errors)
        """
        success_count = 0  # Topics
        exercise_count = 0
        question_count = 0
        error_rows = []
        errors = []
        
        # Check if file is a CSV
        if not file.name.endswith('.csv'):
            errors.append("File must be a CSV file")
            return success_count, exercise_count, question_count, error_rows, errors
            
        # Try to decode the file
        try:
            file_data = file.read().decode('utf-8')
        except UnicodeDecodeError:
            errors.append("Unable to read the file. Please ensure it's a valid CSV file with UTF-8 encoding.")
            return success_count, exercise_count, question_count, error_rows, errors
            
        csv_data = io.StringIO(file_data)
        
        try:
            reader = csv.DictReader(csv_data)
            
            # Validate header row
            required_fields = ['topicName', 'topicDescription', 'topicNote']
            header = reader.fieldnames
            
            if not header:
                errors.append("CSV file appears to be empty")
                return success_count, exercise_count, question_count, error_rows, errors
                
            missing_fields = [field for field in required_fields if field not in header]
            if missing_fields:
                errors.append(f"CSV file is missing required columns: {', '.join(missing_fields)}")
                return success_count, exercise_count, question_count, error_rows, errors
            
            # Check for optional exercise and question fields
            has_exercises = all(field in header for field in ['exerciseName', 'exerciseDescription'])
            has_questions = all(field in header for field in ['questionType', 'questionPrompt', 'correctAnswer'])
            
            # Process rows
            current_topic = None
            current_exercise = None
            
            for row_num, row in enumerate(reader, start=2):  # Start from 2 to account for header row
                try:
                    # Extract row data
                    topic_name = row.get('topicName', '').strip()
                    topic_description = row.get('topicDescription', '').strip()
                    topic_note = row.get('topicNote', '').strip()
                    
                    exercise_name = row.get('exerciseName', '').strip() if has_exercises else ''
                    exercise_description = row.get('exerciseDescription', '').strip() if has_exercises else ''
                    
                    question_type = row.get('questionType', '').strip() if has_questions else ''
                    question_prompt = row.get('questionPrompt', '').strip() if has_questions else ''
                    correct_answer = row.get('correctAnswer', '').strip() if has_questions else ''
                    
                    # If we have a topic name, create a new topic (or reuse existing if unchanged)
                    if topic_name and topic_description and topic_note:
                        # Create new topic
                        current_topic = Topic.objects.create(
                            topicName=topic_name,
                            topicDescription=topic_description,
                            topicNote=topic_note,
                            classroom=classroom
                        )
                        success_count += 1
                        current_exercise = None  # Reset current exercise since we have a new topic
                    
                    # If we have an exercise and a valid current topic, create the exercise
                    if has_exercises and exercise_name and exercise_description and current_topic:
                        current_exercise = Exercise.objects.create(
                            exerciseName=exercise_name,
                            exerciseDescription=exercise_description,
                            topic=current_topic
                        )
                        exercise_count += 1
                    
                    # If we have question data and a valid current exercise, create the question
                    if has_questions and question_type and question_prompt and correct_answer and current_exercise:
                        # Validate question type
                        valid_question_types = [choice[0] for choice in Question.QUESTION_TYPES]
                        if question_type not in valid_question_types:
                            error_rows.append(f"Row {row_num}: Invalid question type '{question_type}'. Must be one of {', '.join(valid_question_types)}")
                            continue
                            
                        # Create question
                        Question.objects.create(
                            questionType=question_type,
                            questionPrompt=question_prompt,
                            correctAnswer=correct_answer,
                            exercise=current_exercise
                        )
                        question_count += 1
                    
                except Exception as e:
                    error_rows.append(f"Row {row_num}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"Error processing CSV file: {str(e)}")
            
        return success_count, exercise_count, question_count, error_rows, errors

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
    def createNewQuestion(questionType: str, questionPrompt: str, correctAnswer: str, exercise=None, instructor=None, is_saved=False):
        
        questionPrompt = questionPrompt.strip()
        correctAnswer = correctAnswer.strip()

        #check if the question prompt and correct answer are not empty
        if questionPrompt and correctAnswer:
            return Question.objects.create(
                questionType=questionType,
                questionPrompt=questionPrompt,
                correctAnswer=correctAnswer,
                exercise=exercise,
                created_by=instructor,
                is_saved=is_saved
            )

        else:
            return None
            
    @staticmethod
    def saveQuestion(questionType: str, questionPrompt: str, correctAnswer: str, instructor):
        """Creates a saved question without assigning it to an exercise"""
        return QuestionController.createNewQuestion(
            questionType=questionType,
            questionPrompt=questionPrompt,
            correctAnswer=correctAnswer,
            exercise=None,
            instructor=instructor,
            is_saved=True
        )
        
    @staticmethod
    def getSavedQuestions(instructor):
        """Get all saved questions for an instructor"""
        return Question.objects.filter(created_by=instructor, is_saved=True)
        
    @staticmethod
    def addQuestionToExercise(questionID: int, exerciseID: int):
        """Add a saved question to an exercise by creating a copy"""
        question = get_object_or_404(Question, questionID=questionID)
        exercise = get_object_or_404(Exercise, exerciseID=exerciseID)
        
        # Create a copy of the question for this exercise
        new_question = Question.objects.create(
            questionType=question.questionType,
            questionPrompt=question.questionPrompt,
            correctAnswer=question.correctAnswer,
            exercise=exercise,
            created_by=question.created_by,
            is_saved=False
        )
        
        # Also copy any answers if this is a multiple choice question
        if question.questionType == 'multiple_choice':
            for answer in question.answers.all():
                Answer.objects.create(
                    question=new_question,
                    answer=answer.answer,
                    correct=answer.correct
                )
                
        return new_question