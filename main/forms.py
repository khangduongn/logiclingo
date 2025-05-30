from django import forms
from .models import *
from django.core.validators import MinLengthValidator

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

class ConfirmJoinClassroomForm(forms.Form):
    classroom_id = forms.IntegerField(widget=forms.HiddenInput())
    confirm = forms.CharField(initial="yes", widget=forms.HiddenInput())

class TopicForm(forms.ModelForm):
    
    class Meta:
        model = Topic
        fields = ['topicName', 'topicDescription', 'topicNote']  
        widgets = {
            'topicName': forms.TextInput(attrs={'maxlength': '100'}),
            'topicDescription': forms.Textarea(attrs={'maxlength': '500', 'rows': 4}),
            'topicNote': forms.Textarea(attrs={'maxlength': '1000', 'rows': 4}),
        }

class QuestionForm(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ['questionType', 'questionPrompt', 'correctAnswer']  
        widgets = {
            'questionPrompt': forms.Textarea(attrs={
                'maxlength': '1000', 
                'rows': 4,
                'class': 'logical-symbols-input'
            }),
            'correctAnswer': forms.Textarea(attrs={
                'maxlength': '500', 
                'rows': 2,
                'class': 'logical-symbols-input'
            }),
        }

class ModifyQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['questionType', 'questionPrompt', 'correctAnswer']
        widgets = {
            'questionPrompt': forms.Textarea(attrs={
                'maxlength': '1000', 
                'rows': 4,
                'class': 'logical-symbols-input'
            }),
            'correctAnswer': forms.Textarea(attrs={
                'maxlength': '500', 
                'rows': 2,
                'class': 'logical-symbols-input'
            }),
        }

class SaveQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['questionType', 'questionPrompt', 'correctAnswer']
        widgets = {
            'questionPrompt': forms.Textarea(attrs={
                'maxlength': '1000', 
                'rows': 4,
                'class': 'logical-symbols-input'
            }),
            'correctAnswer': forms.Textarea(attrs={
                'maxlength': '500', 
                'rows': 2,
                'class': 'logical-symbols-input'
            }),
        }

class AddQuestionToExerciseForm(forms.Form):
    exercise = forms.ModelChoiceField(
        queryset=Exercise.objects.none(),
        empty_label="Select an exercise",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        classroom_id = kwargs.pop('classroom_id', None)
        super(AddQuestionToExerciseForm, self).__init__(*args, **kwargs)
        
        if classroom_id:
            # Get all exercises in the classroom
            exercises = Exercise.objects.filter(
                topic__classroom__classroomID=classroom_id
            ).order_by('topic__topicName', 'exerciseName')
            
            self.fields['exercise'].queryset = exercises

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['exerciseName', 'exerciseDescription']
        widgets = {
            'exerciseName': forms.TextInput(attrs={'maxlength': '200'}),
            'exerciseDescription': forms.Textarea(attrs={'maxlength': '1000', 'rows': 4}),
        }

class ModifyExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['exerciseName', 'exerciseDescription']
        widgets = {
            'exerciseName': forms.TextInput(attrs={'maxlength': '200'}),
            'exerciseDescription': forms.Textarea(attrs={'maxlength': '1000', 'rows': 4}),
        }

class AddExistingTopicsForm(forms.Form):
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

class AddExistingExercisesForm(forms.Form):
    exercises = forms.ModelMultipleChoiceField(
        queryset=Exercise.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

class AddExistingQuestionsForm(forms.Form):
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

class AnswerForm(forms.Form):
    answer = forms.CharField(
        widget=forms.Textarea(attrs={
            'maxlength': '500',
            'rows': 2,
            'class': 'logical-symbols-input'
        }), 
        required=True
    )

    def clean_answer(self):
        answer = self.cleaned_data['answer'].strip()
        if not answer:
            raise forms.ValidationError("Your answer cannot be empty")
        return answer

class ImportQuestionForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV file")

class ImportExerciseForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV file")

class ImportTopicForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file containing topic data. Required columns: topicName, topicDescription, topicNote (optional)',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )