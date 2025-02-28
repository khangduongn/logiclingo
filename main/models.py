from django.db import models
import string, random
from django.core.validators import MinLengthValidator
from django.core.mail import send_mail

class User(models.Model):
    userID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=100, blank=False)
    lastName = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100,blank=False,unique=True)
    username = models.CharField(max_length=25, unique=True, blank=False)
    password = models.CharField(max_length=20, blank=False, validators=[MinLengthValidator(8)])
    feedback = models.CharField(max_length=200)
    # classrooms = models.ManyToManyField(Classroom, blank=True)

    class Meta:
        #this is abstract model
        abstract = True 

class Student(User):
    numExercisesCompleted = models.IntegerField(default=0)
    numHoursSpent = models.IntegerField(default=0)
    daysStreak = models.IntegerField(default=0)
    # classrooms = models.ManyToManyField(Classroom, related_name='students')
    streakToday = models.BooleanField(default=False)
    enrolled = models.BooleanField(default=True)

class Instructor(User):
    department = models.CharField(max_length=200)
    employed = models.BooleanField(default=True)

# Create your models here.
class Classroom(models.Model):
    classroomID = models.AutoField(primary_key=True)
    className = models.CharField(max_length=100)
    startDate = models.DateField()
    endDate = models.DateField()
    active = models.BooleanField(default=True)
    open = models.BooleanField(default=True)
    instructorName = models.CharField(max_length=200, blank=False, default="")
    instructors = models.ManyToManyField(Instructor, related_name='classrooms')
    students = models.ManyToManyField(Student, related_name='classrooms', blank=True)

    classroomCode = models.CharField(
        max_length=5,
        unique=True,        
        null=False,        
        blank=True       
    )

    def save(self, *args, **kwargs):
        if not self.classroomCode:
            while True:
                randomCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                if not Classroom.objects.filter(classroomCode=randomCode).exists():
                    self.classroomCode = randomCode
                    break

        super().save(*args, **kwargs)

    def sendEmail(self, email: str, classroomCode: int, isStudent: bool):
        
        if isStudent:
            send_mail(
                "LogicLingo Student Join Classroom",
                f"Join the LogicLingo classroom with the classroom code {classroomCode}",
                "logiclingo@drexel.edu",
                [email],
                fail_silently=False,
            )
        else:
            send_mail(
                "LogicLingo Instructor Join Classroom",
                f"Join the LogicLingo classroom with the classroom code {classroomCode}",
                "logiclingo@drexel.edu",
                [email],
                fail_silently=False,
            )

    def __str__(self):
        return self.className


    
