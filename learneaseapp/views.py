from django.shortcuts import render, HttpResponse, redirect, get_object_or_404 
from .forms import UserRegistrationform, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Assignment, Submission, Grade
from .forms import AssignmentForm, SubmissionForm, GradeForm
from django.views import generic
from .forms import *
from .models import *
import requests

# Create your views here.
def home(request):
    return render(request,'learneaseapp/home.html')



def registration(request):
    if request.method == "POST":
        user_form = UserRegistrationform(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return HttpResponse("<h1>Registration successfully</h1>")
        
        
    else:
        user_form = UserRegistrationform()
        profile_form = UserProfileForm()
        
    return render(request,'learneaseapp/register.html',{'user_form': user_form, 'profile_form': profile_form,})

@login_required
def profile(request):
    try:
        profile = request.user.userprofile
        profile_picture = profile.profile_picture.url
    except UserProfile.DoesNotExist:
        # If UserProfile does not exist for the user, create a new one
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'learneaseapp/profile.html', {'form': form, 'profile': profile,'profile_picture': profile_picture})
