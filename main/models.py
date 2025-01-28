from django.db import models
import string, random

# Create your models here.
class Classroom(models.Model):
    className = models.CharField(max_length=100)
    startDate = models.DateField()
    endDate = models.DateField()
    active = models.BooleanField(default=True)
    open = models.BooleanField(default=True)
    classroomCode = models.CharField(
        max_length=5,
        unique=True,        
        null=False,        
        blank=True       
    )

    def save(self, *args, **kwargs):
        #generate a unique random code
        if not self.classroomCode:
            while True:
                randomCode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                if not Classroom.objects.filter(classroomCode=randomCode).exists():
                    self.classroomCode = randomCode
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return self.className