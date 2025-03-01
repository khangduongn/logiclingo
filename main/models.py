from django.db import models
import string, random
from django.core.validators import MinLengthValidator
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.urls import reverse

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):

        if not username:
            raise ValueError("User must have a username")
        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Creates and saves a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    userID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=100, blank=False)
    lastName = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100,blank=False,unique=True)
    username = models.CharField(max_length=25, unique=True, blank=False)
    password = models.CharField(max_length=100, blank=False, validators=[MinLengthValidator(8)])
    feedback = models.CharField(max_length=200)

    #django fields (these are only here to make user authentication work properly in Django)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager() 

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'firstName', 'lastName']

class Student(User):
    numExercisesCompleted = models.IntegerField(default=0)
    numHoursSpent = models.IntegerField(default=0)
    daysStreak = models.IntegerField(default=0)
    streakToday = models.BooleanField(default=False)
    enrolled = models.BooleanField(default=True)

class Instructor(User):
    department = models.CharField(max_length=200)
    employed = models.BooleanField(default=True)

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

    def sendEmail(self, email: str, classroomCode: str, isStudent: bool):
        confirm_url = f"{settings.SITE_URL}{reverse('confirm_join_classroom')}?classroom_code={classroomCode}"

        if isStudent:
            subject = "Join Your LogicLingo Classroom"
            message = (
                f"You've been invited to join a LogicLingo classroom.\n\n"
                f"Join the LogicLingo classroom with the classroom code {classroomCode}\n"
                f"Click the link below to confirm your enrollment:\n{confirm_url}"
            )
        else:
            subject = "Instructor Classroom Invitation"
            message = (
                f"You've been invited to join a LogicLingo classroom as an instructor.\n\n"
                f"Join the LogicLingo classroom with the classroom code {classroomCode}\n\n"
                f"Click the link below to confirm your enrollment:\n{confirm_url}"
            )

        try:
            send_mail(
                subject,
                message,
                "logiclingo@drexel.edu",
                [email],
                fail_silently=False,
            )
            return True
        except:
            return False

    def __str__(self):
        return self.className
