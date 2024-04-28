from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class UserRegistrationform(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','password1','password2')
        
        
class UserProfileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture','date_of_birth','location','user_type']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }
        
class DashboardForm(forms.Form):
    text = forms.CharField(max_length=100,label="")
 
class AssignmentForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(queryset=User.objects.filter(userprofile__user_type='Student'))
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date','students']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),}