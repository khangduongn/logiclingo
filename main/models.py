from django.db import models

# Create your models here.
class Classroom(models.Model):
    className = models.CharField(max_length=100)
