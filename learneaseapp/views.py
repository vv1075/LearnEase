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

@login_required
def update_profile(request):
    try:
        profile = request.user.userprofile 
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'learneaseapp/update_profile.html',{'form':form})

def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')  # Use get() method to safely retrieve 'text' parameter
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r= requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dict = {
                'title': answer['items'][i]['volumeInfo']['title'],
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': answer['items'][i]['volumeInfo'].get('description'),
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'rating': answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink'),
                 
            }
            result_list.append(result_dict)
            context = {
            'form': form,
            'results': result_list
            }
        return render(request, 'learneaseapp/books.html', context)
    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, "learneaseapp/books.html", context)
    
def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')  # Use get() method to safely retrieve 'text' parameter
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r= requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms
            }
        except:
            context = {
                'form':form,
                'input':''
            }
        return render(request,"learneaseapp/dictionary.html",context)    
    else:  
        form = DashboardForm()
        context = {'form':form}
    return render(request,"learneaseapp/dictionary.html",context)


                  