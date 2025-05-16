from django import template
from main.models import Student, Instructor

register = template.Library()

@register.filter
def is_student(user):
    """Check if the user is a student"""
    return hasattr(user, 'student')

@register.filter
def is_instructor(user):
    """Check if the user is an instructor"""
    return hasattr(user, 'instructor')