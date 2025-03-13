from django import template
from main.views import is_student

register = template.Library()

@register.filter(name='is_instructor')
def is_instructor(user):
    return not is_student(user)