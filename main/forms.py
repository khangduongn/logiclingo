from django import forms
from .models import Classroom, User, Student, Instructor
from django.core.validators import MinLengthValidator

class ClassroomForm(forms.ModelForm):

    preexisting = forms.BooleanField(required=False, label="Default Roadmap")

    class Meta:
        model = Classroom
        fields = ['className', 'startDate', 'endDate', 'instructorName']  
        widgets = {
            'startDate': forms.DateInput(attrs={'type': 'date'}),
            'endDate': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        startDate = cleaned_data.get("startDate")
        endDate = cleaned_data.get("endDate")

        if startDate and endDate and startDate > endDate:
            raise forms.ValidationError("Start date must be earlier than the end date.")

class UserForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(),
        validators=[MinLengthValidator(8)],
        error_messages={'min_length': 'Password must be at least 8 characters long.'}
    )

    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'username', 'password']

class StudentForm(UserForm):
    class Meta(UserForm.Meta):
        model = Student 

class InstructorForm(UserForm):
    class Meta(UserForm.Meta):
        model = Instructor
        fields = UserForm.Meta.fields + ['department']

class JoinClassroomForm(forms.Form):
    classroom_code = forms.CharField(max_length=5, label="Classroom Code", 
                                    widget=forms.TextInput(attrs={'placeholder': 'Enter classroom code'}))