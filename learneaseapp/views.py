from django.shortcuts import render, HttpResponse,  redirect, get_object_or_404
from .forms import UserRegistrationform, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Assignment, Submission, Grade
from .forms import AssignmentForm, SubmissionForm, GradeForm
from django.views import generic
from .forms import *
from .models import *
from youtubesearchpython import VideosSearch
import requests
from django.db.models import Max
from django.db.models import F
import json
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.conf import settings
from .models import QuizSubmissionStatus
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
            return redirect('login')
            #return HttpResponse("<h1>Registration successfully</h1>")
        
        
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
            request.session['profile_updated'] = True
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'learneaseapp/update_profile.html',{'form':form})

def books(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check if it's an Ajax request
            form = DashboardForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data['text']
                url = "https://www.googleapis.com/books/v1/volumes?q=" + text
                r = requests.get(url)
                if r.status_code == 200:
                    answer = r.json()
                    result_list = []
                    if 'items' in answer:
                        for item in answer['items'][:10]:
                            volume_info = item.get('volumeInfo', {})
                            result_dict = {
                                'title': volume_info.get('title'),
                                'subtitle': volume_info.get('subtitle'),
                                'description': volume_info.get('description'),
                                'count': volume_info.get('pageCount'),
                                'categories': volume_info.get('categories'),
                                'rating': volume_info.get('pageRating'),
                                'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail'),
                                'preview': volume_info.get('previewLink'),
                            }
                            result_list.append(result_dict)
                    else:
                        result_list = []  # No items found
                    return JsonResponse({'results': result_list})
                else:
                    return JsonResponse({'error': 'Failed to fetch data from Google Books API'}, status=500)
            else:
                return JsonResponse({'error': 'Form is not valid'}, status=400)
        else:
            form = DashboardForm(request.POST)
            context = {'form': form}
            return render(request, "learneaseapp/books.html", context)
    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, "learneaseapp/books.html", context)
    
def save_book(request):
    if request.method == "POST":
        title = request.POST.get('title')
        subtitle = request.POST.get('subtitle')
        description = request.POST.get('description')
        count = request.POST.get('count')
        categories = request.POST.get('categories')
        rating = request.POST.get('rating')
        thumbnail = request.POST.get('thumbnail')
        preview = request.POST.get('preview')
 
        SavedBook.objects.create(
            title=title,
            subtitle=subtitle,
            description=description,
            count=count,
            categories=categories,
            thumbnail=thumbnail,
            preview=preview
        )
        return redirect('saved_books')
    else:
        return redirect('books')

def saved_books(request):
    saved_books = SavedBook.objects.all()
    context = {'saved_books': saved_books}
    return render(request, 'learneaseapp/saved_books.html',context)
    
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

def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '')  # Use get() method to safely retrieve 'text' parameter
        video = VideosSearch(text, limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input': text,
                'title': i['title'],
                'duration': i['duration'],
                'thumbnails': i['thumbnails'][0]['url'],
                'channel': i['channel']['name'],
                'link': i['link'],
                'views': i['viewCount']['short'],
                'published': i['publishedTime']   
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict)
        context = {
            'form': form,
            'results': result_list
        }
        return render(request, 'learneaseapp/youtube.html', context)
    else:
        form = DashboardForm()
        context = {'form': form}
        return render(request, "learneaseapp/youtube.html", context)

@login_required
def course_list(request):
    if request.user.userprofile.user_type == "Professor":
        courses = Course.objects.filter(created_by=request.user)
    else:
        courses = Course.objects.all()  # or logic for student view

    course_data = []

    quizzes_data = []
    try:
        response = requests.get(f"{QUIZ_SERVICE_URL}/quizzes")
        if response.status_code == 200:
            quizzes_data = response.json()
    except Exception as e:
        print("Quiz fetch failed:", e)

    if quizzes_data is None:
        quizzes_data = []

    for course in courses:
        assignments = Assignment.objects.filter(course=course)
        quizzes = [q for q in quizzes_data if q.get('course_id') == str(course.id)]

        assignment_list = [
            {"title": a.title, "description": a.description, "due_date": str(a.due_date) if a.due_date else "N/A"}
            for a in assignments
        ]

        course_data.append({
            "course": {"id": course.id, "name": course.name},
            "assignments": assignment_list,
            "quizzes": quizzes
        })

    return render(request, 'learneaseapp/course_list.html', {
        'course_data': course_data,
        'course_data_json': json.dumps(course_data, cls=DjangoJSONEncoder)
    })

@login_required
def create_course(request):
    if request.user.userprofile.user_type != "Professor":
        return redirect("course_list")

    if request.method == "POST":
        name = request.POST.get("name")
        Course.objects.create(name=name, created_by=request.user)
        messages.success(request, "Course created successfully!")
        return redirect("course_list")

    return render(request, 'learneaseapp/create_course.html')
@login_required
def create_assignment(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.user.userprofile.user_type != 'Professor':
        return redirect('assignment_list', course_id=course_id)

    students = User.objects.filter(userprofile__user_type='Student')  # Filter students
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.created_by = request.user
            assignment.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('assignment_list', course_id=course_id)
    else:
        form = AssignmentForm()
    return render(request, 'learneaseapp/create_assignment.html', {'form': form, 'course': course, 'students': students})

@login_required
def assignment_list(request, course_id):
    course = Course.objects.get(id=course_id)
    assignments = Assignment.objects.filter(course_id=course_id).annotate(latest_grade_id=Max('grade__score'))
    
    
    if request.user.userprofile.user_type == 'Student':
        submissions = Submission.objects.filter(student=request.user)
        grades = Grade.objects.filter(student=request.user)
        submitted_assignments = {submission.assignment_id: submission for submission in submissions}
        return render(request, 'learneaseapp/assignment_list.html', {'assignments': assignments, 'grades': grades, 'course': course, 'submitted_assignments': submitted_assignments})
    else:
        return render(request, 'learneaseapp/assignment_list.html', {'assignments': assignments, 'course': course})
                                                            
@login_required
def submit_assignment(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    if request.user.userprofile.user_type != 'Student':
        return redirect('assignment_list', course_id=assignment.course.id)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            return redirect('assignment_list', course_id=assignment.course.id)
    else:
        form = SubmissionForm()
    return render(request, 'learneaseapp/submit_assignment.html', {'form': form, 'assignment': assignment})

def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    assignment = submission.assignment
    
    # Check if the user is a professor and has the authority to grade the submission
    if request.user.userprofile.user_type != 'Professor' or assignment.created_by != request.user:
        return redirect('assignment_list', course_id=assignment.course.id)  # Redirect back to assignment list if unauthorized
    
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.assignment = assignment
            grade.student = submission.student
            grade.graded_by = request.user  # Assign the current user as the grader
            grade.save()
            # Redirect to the assignment details page after grading
            return redirect('grade_assignment_list', assignment_id=assignment.id)
    else:
        form = GradeForm()
    
    return render(request, 'learneaseapp/grade_submission.html', {'form': form, 'submission': submission, 'assignment': assignment})

def grade_assignment_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    course = assignment.course
    grades = Grade.objects.filter(student=request.user)
    
    # Annotate the latest grade ID for the assignment
    latest_grade_id = assignment.grade_set.aggregate(Max('id'))['id__max']
    
    # Fetch the latest grade object if the latest grade ID exists
    latest_grade = None
    if latest_grade_id:
        latest_grade = Grade.objects.get(id=latest_grade_id)
    
    assignments = Assignment.objects.filter(course=course).annotate(latest_grade=Max('grade__score'))
    return render(request, 'learneaseapp/grade_assignment_list.html', {'assignment': assignment, 'submissions': submissions, 'assignments': assignments,'grades': grades, 'latest_grade': latest_grade})

def notes(request):
    if request .method =="POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notess(user=request.user,title = request.POST['title'],description = request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully!")
        return redirect('notes')
    else:
        form = NotesForm()
        notes = Notess.objects.filter(user=request.user)
        context = {'notes':notes,'form':form}
        return render(request,'learneaseapp/notes.html',context)
    
def delete_note(request,pk=None):
    Notess.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailsView(generic.DetailView):
    model = Notess  



QUIZ_SERVICE_URL = "http://10.21.179.82:8080"
from .models import UserProfile, QuizAssignment
@login_required
def quiz_list(request):
    quizzes = []
    try:
        response = requests.get(f"{QUIZ_SERVICE_URL}/quizzes")
        if response.status_code == 200:
            quizzes = response.json()
    except Exception as e:
        print("Error fetching quizzes:", e)
        quizzes = []

    assignments = QuizAssignment.objects.all()
    students = User.objects.filter(userprofile__user_type='Student')
    courses = Course.objects.all()  # ✅ include for AI quiz modal

    if request.user.userprofile.user_type == 'Student':
        assigned_quiz_ids = [a.quiz_id for a in assignments if request.user in a.assigned_students.all()]
        quizzes = [q for q in quizzes if q.get('id') in assigned_quiz_ids]

        for quiz in quizzes:
            submission = QuizSubmissionRecord.objects.filter(student=request.user, quiz_id=quiz['id']).order_by('-submitted_at').first()
            if submission:
                if submission.score is not None:
                    quiz['can_take'] = submission.quiz_last_updated < quiz.get('last_updated', 0)
                    quiz['score_info'] = f"{submission.score} / {submission.max_score}"
                else:
                    quiz['can_take'] = True
                    quiz['score_info'] = None
            else:
                quiz['can_take'] = True
                quiz['score_info'] = None

    elif request.user.userprofile.user_type == 'Professor':
        #  Show saved and draft quizzes for professors
        quizzes = [q for q in quizzes if q.get('status') in ['saved', 'draft']]

    return render(request, 'learneaseapp/quiz_list.html', {
        'quizzes': quizzes,
        'students': students,
        'courses': courses  # required for dropdown in modal
    })

@login_required
def create_quiz(request, course_id=None):  # ✅ Accept course_id from URL
    if request.user.userprofile.user_type != 'Professor':
        return redirect('quiz_list')

    students = User.objects.filter(userprofile__user_type='Student')
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        quiz_title = request.POST.get('quiz_title')
        questions = []
        total_questions = int(request.POST.get('total_questions'))

        for i in range(total_questions):
            question_text = request.POST.get(f'question_{i}')
            options = [
                request.POST.get(f'option_{i}_1'),
                request.POST.get(f'option_{i}_2'),
                request.POST.get(f'option_{i}_3'),
                request.POST.get(f'option_{i}_4'),
            ]
            correct = int(request.POST.get(f'correct_{i}', 0))
            marks = int(request.POST.get(f'marks_{i}', 1))

            questions.append({
                'text': question_text,
                'options': options,
                'correct': correct,
                'marks': marks
            })

        quiz_data = {
            "title": quiz_title,
            "questions": questions,
            "course_id": str(course.id)
        }

        response = requests.post(f"{QUIZ_SERVICE_URL}/quizzes", json=quiz_data)

        if response.status_code == 200:
            created_quiz = response.json()
            quiz_id = created_quiz['id']
            assignment = QuizAssignment.objects.create(quiz_id=quiz_id, course=course)
            selected_students = request.POST.getlist('assigned_students')
            assignment.assigned_students.set(User.objects.filter(id__in=selected_students))
            messages.success(request, "Quiz created and assigned!")
            return redirect('quiz_list_by_course', course_id=course.id)

    return render(request, 'learneaseapp/create_quiz.html', {
        'students': students,
        'course': course
    })

@login_required
def quiz_detail(request, quiz_id):
    response = requests.get(f"{QUIZ_SERVICE_URL}/quizzes/{quiz_id}")
    if response.status_code == 200:
        quiz = response.json()
        students = User.objects.filter(userprofile__user_type='Student')

        if request.method == "POST":
            quiz_title = request.POST.get('quiz_title')
            total_questions = int(request.POST.get('total_questions', len(quiz.get('questions', []))))
            updated_questions = []

            for i in range(total_questions):
                question = {
                    'text': request.POST.get(f'question_text_{i}'),
                    'options': [
                        request.POST.get(f'option_{i}_1'),
                        request.POST.get(f'option_{i}_2'),
                        request.POST.get(f'option_{i}_3'),
                        request.POST.get(f'option_{i}_4'),
                    ],
                    'correct': int(request.POST.get(f'correct_{i}', 0)),
                    'marks': int(request.POST.get(f'marks_{i}', 1))
                }
                updated_questions.append(question)

            updated_quiz = {
                "id": quiz['id'],
                "title": quiz_title,
                "questions": updated_questions,
                "course_id": quiz.get("course_id"),  # Include this to keep link
                "status": quiz.get("status", "saved")
            }

            requests.put(f"{QUIZ_SERVICE_URL}/quizzes/{quiz_id}", json=updated_quiz)

            #  Course handling for assignment
            course_id = quiz.get("course_id")
            course_obj = None
            if course_id:
                try:
                    course_obj = Course.objects.get(id=course_id)
                except Course.DoesNotExist:
                    course_obj = None

            assignment = QuizAssignment.objects.filter(quiz_id=quiz_id).first()

            if assignment:
                # Update student assignments
                selected_students = request.POST.getlist('assigned_students')
                assignment.assigned_students.set(User.objects.filter(id__in=selected_students))
            else:
                # Create new assignment if it doesn’t exist
                assignment = QuizAssignment.objects.create(
                    quiz_id=quiz_id,
                    course=course_obj
                )
                selected_students = request.POST.getlist('assigned_students')
                assignment.assigned_students.set(User.objects.filter(id__in=selected_students))

            messages.success(request, "Quiz updated successfully!")
            return redirect('quiz_list_by_course', course_id=course_id)

        # 🧠 Add current student assignment info for template
        assignment = QuizAssignment.objects.filter(quiz_id=quiz_id).first()
        assigned_students = assignment.assigned_students.all() if assignment else []

        return render(request, "learneaseapp/quiz_detail.html", {
            "quiz": quiz,
            "students": students,
            "assigned_students": assigned_students
        })

    return HttpResponse("Quiz not found", status=404)  
@login_required
def quiz_take(request, quiz_id):
    response = requests.get(f"{QUIZ_SERVICE_URL}/quizzes/{quiz_id}")
    quiz = response.json()

    if request.method == "POST":
        answers = []
        for i in range(len(quiz['questions'])):
            selected = request.POST.get(f'question_{i}', -1)
            try:
                selected = int(selected)
            except ValueError:
                selected = -1
            answers.append(selected)

        submission = {
            "quiz_id": quiz_id,
            "answers": answers
        }

        # Submit answers to Go backend
        requests.post(f"{QUIZ_SERVICE_URL}/quizzes/{quiz_id}/submit", json=submission)

        # ✅ Fetch score response from Go
        result = requests.get(f"{QUIZ_SERVICE_URL}/quizzes/{quiz_id}/results").json()

        # ✅ Save submission to Django DB for score display
        from .models import QuizSubmissionRecord
        QuizSubmissionRecord.objects.create(
            student=request.user,
            quiz_id=quiz_id,
            quiz_title=quiz.get("title", ""),
            score=result.get("score", 0),
            max_score=result.get("max", 0),
            quiz_last_updated=quiz.get("last_updated", 0)
        )

        return redirect(f"/quizzes/{quiz_id}/results/")

    return render(request, 'learneaseapp/quiz_take.html', {'quiz': quiz})
@login_required
def quiz_results(request, quiz_id):
    try:
        response = requests.get(f"{QUIZ_SERVICE_URL}/quizzes/{quiz_id}")
        quiz = response.json()
        quiz_title = quiz['title']  # ✅ Extract title

        result_response = requests.get(f"{QUIZ_SERVICE_URL}/quizzes/{quiz_id}/results")
        result = result_response.json()
    except Exception as e:
        print("Error fetching quiz or result:", e)
        result = {"score": "Error", "max": "--"}
        quiz_title = "Quiz"

    return render(request, 'learneaseapp/quiz_result.html', {'result': result, 'quiz_title': quiz_title})
@login_required
def delete_quiz(request, quiz_id):
    if request.user.userprofile.user_type != 'Professor':
        return redirect('quiz_list')

    assignment = QuizAssignment.objects.filter(quiz_id=quiz_id).first()
    course_id = assignment.course.id if assignment else None

    QuizAssignment.objects.filter(quiz_id=quiz_id).delete()
    response = requests.delete(f"{QUIZ_SERVICE_URL}/quizzes/{quiz_id}")
    if response.status_code == 200:
        messages.success(request, "Quiz deleted successfully!")
    else:
        messages.error(request, "Failed to delete quiz.")

    if course_id:
        return redirect('quiz_list_by_course', course_id=course_id)
    else:
        return redirect('quiz_list')
@login_required
def quiz_submissions_list(request):
    if request.user.userprofile.user_type != 'Professor':
        return redirect('quiz_list')

    submissions = QuizSubmissionRecord.objects.all().order_by('-id')
    return render(request, 'learneaseapp/quiz_submissions_list.html', {'submissions': submissions})


@login_required
def quiz_submissions_json(request):
    if request.user.userprofile.user_type != 'Professor':
        return JsonResponse([], safe=False)

    data = []
    records = QuizSubmissionRecord.objects.all()
    for record in records:
        data.append({
            "student": record.student.username,
            "quiz_title": record.quiz_title,
            "score": record.score,
            "max_score": record.max_score,
        })
    return JsonResponse(data, safe=False)

@login_required

def course_details_json(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    #  Get assignments for this course
    assignments = Assignment.objects.filter(course=course)
    assignment_data = [{'title': a.title, 'description': a.description} for a in assignments]

    #  Get quizzes linked to this course using QuizAssignment model
    quiz_assignments = QuizAssignment.objects.filter(course=course)

    # Fetch quiz titles from Go backend
    response = requests.get(f"{QUIZ_SERVICE_URL}/quizzes")
    quiz_titles = {}
    if response.status_code == 200:
        for quiz in response.json():
            quiz_titles[quiz['id']] = quiz.get('title')

    quiz_data = []
    for qa in quiz_assignments:
        title = quiz_titles.get(qa.quiz_id, f"Quiz {qa.quiz_id}")
        quiz_data.append({'title': title})

    return JsonResponse({
        'assignments': assignment_data,
        'quizzes': quiz_data
    })

@login_required
def quiz_list_by_course(request, course_id):
    quizzes = []
    try:
        response = requests.get(f"{QUIZ_SERVICE_URL}/quizzes")
        if response.status_code == 200:
            quizzes = response.json()
    except Exception as e:
        print("Error fetching quizzes:", e)
        quizzes = []

    assignments = QuizAssignment.objects.all()
    students = User.objects.filter(userprofile__user_type='Student')

    #  Get the specific course object
    course = get_object_or_404(Course, id=course_id)

    # Filter quizzes by course_id
    quizzes = [q for q in quizzes if str(q.get('course_id')) == str(course_id)]

    if request.user.userprofile.user_type == 'Student':
        assigned_quiz_ids = list(
            QuizAssignment.objects.filter(assigned_students=request.user)
            .values_list('quiz_id', flat=True)
        )

        quizzes = [q for q in quizzes if q.get('id') in assigned_quiz_ids]

        for quiz in quizzes:
            submission = QuizSubmissionRecord.objects.filter(
                student=request.user, quiz_id=quiz['id']
            ).order_by('-submitted_at').first()

            if submission:
                quiz['can_take'] = submission.quiz_last_updated < quiz.get('last_updated', 0)
                quiz['score_info'] = f"{submission.score} / {submission.max_score}"
            else:
                quiz['can_take'] = True
                quiz['score_info'] = None

    return render(request, 'learneaseapp/quiz_list.html', {
        'quizzes': quizzes,
        'students': students,
        'course': course,  # ✅ pass selected course (not courses list)
        'courses': Course.objects.all()
    })

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course, Assignment, Grade, QuizSubmissionRecord, QuizAssignment

@login_required
def course_performance_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # If user is student -> show only their performance
    if request.user.userprofile.user_type == 'Student':
        students = [request.user]
    else:
        # Professors see all students
        students = User.objects.filter(userprofile__user_type='Student')

    performance_data = []

    for student in students:
        # Assignments
        student_submissions = Submission.objects.filter(assignment__course=course, student=student)
        assignment_total_score = Grade.objects.filter(student=student, assignment__course=course).aggregate(score=Sum('score'))['score'] or 0
        assignment_total_possible = student_submissions.count() * 100  # assuming each is 100 marks

        assignment_percentage = (assignment_total_score / assignment_total_possible * 100) if assignment_total_possible else 0

        # Quizzes
        quiz_assignments = QuizAssignment.objects.filter(course_id=course_id, assigned_students=student)
        quiz_total_score = 0
        quiz_total_possible = 0

        for quiz_assignment in quiz_assignments:
            submission = QuizSubmissionRecord.objects.filter(student=student, quiz_id=quiz_assignment.quiz_id).first()
            if submission:
                quiz_total_score += submission.score
                quiz_total_possible += submission.max_score

        quiz_percentage = (quiz_total_score / quiz_total_possible * 100) if quiz_total_possible else 0

        # Overall
        overall_score = assignment_total_score + quiz_total_score
        overall_possible = assignment_total_possible + quiz_total_possible
        overall_percentage = (overall_score / overall_possible * 100) if overall_possible else 0

        performance_data.append({
            'student': student,
            'assignment_score': assignment_total_score,
            'assignment_total': assignment_total_possible,
            'assignment_percent': round(assignment_percentage, 2),
            'quiz_score': quiz_total_score,
            'quiz_total': quiz_total_possible,
            'quiz_percent': round(quiz_percentage, 2),
            'overall_score': overall_score,
            'overall_total': overall_possible,
            'overall_percent': round(overall_percentage, 2),
        })

    return render(request, 'learneaseapp/course_performance.html', {
        'course': course,
        'performance_data': performance_data,
        'is_professor': request.user.userprofile.user_type == 'Professor',
    })