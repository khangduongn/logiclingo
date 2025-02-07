from django import forms
from .models import Classroom

class ClassroomForm(forms.ModelForm):

    preexisting = forms.BooleanField(required=False, label="Default Roadmap")

    class Meta:
        model = Classroom
        fields = ['className', 'startDate', 'endDate']  
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