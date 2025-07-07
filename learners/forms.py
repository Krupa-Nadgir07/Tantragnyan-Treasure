from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from . models import *
from crispy_forms.helper import FormHelper

PREPARING_FOR = (('Intern','Internship'),('Job','Full Time'))
# DOMAIN_CHOICES = (('Algorithms','Algorithms'),('Data Structures','Data Structures'),('C++','C++'),('Python','Python'),('Java','Java'),\
#                   ('C','C'),('Databases','Databases'),('Artificial Intelligence','Artificial Intelligence'))

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    class Meta:
        model = User
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class LearnerForm(forms.ModelForm):
    preparing_for = forms.ChoiceField(choices=PREPARING_FOR)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}))
    class Meta:
        model = Learners
        fields =['email_id','preparing_for', 'date_of_birth']
        # exclude = ['age', 'learner_since','user', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class CPAccountsForm(forms.ModelForm):
    class Meta:
        model = LearnerCpAccCreds
        fields = ['cp_username', 'password']
        labels = {
            'cp_username': 'CP username',  
            'password': 'Password',        
        }

class SignInForm(forms.Form):
    username_or_email = forms.CharField(label="Username or Email", max_length=150)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')
        # confirm_password = cleaned_data.get('confirm_password')

        if not username_or_email:
            raise forms.ValidationError("Username or email is required.")
        if not password:
            raise forms.ValidationError("Password is required.")
        
        return cleaned_data
