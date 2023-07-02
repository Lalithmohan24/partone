from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# class RegisterForm(UserCreationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
#     password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
#     password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

#     class Meta:
#         model = User
#         fields = ['username', 'password1', 'password2']

class LogoutForm(forms.Form):
    pass  # No additional fields are needed for logout


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# class RegisterForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'password1', 'password2']

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
