from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_instructor = forms.BooleanField(required=False, label='Register as Instructor')
    is_student = forms.BooleanField(required=False, label='Register as Student')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_student', 'is_instructor']

    def clean(self):
        cleaned_data = super().clean()
        is_instructor = cleaned_data.get('is_instructor')
        is_student = cleaned_data.get('is_student')

        if is_student and is_instructor:
            raise forms.ValidationError('You cannot be both a student and an instructor')
        if not is_student and not is_instructor:
            raise forms.ValidationError('Please select either student or instructor role')

        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
