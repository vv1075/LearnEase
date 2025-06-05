from django.urls import path, re_path
from . import views


urlpatterns = [
    path('',views.home,name="home"),
    
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('books',views.books,name="books"),  
    path('save_book/', views.save_book, name='save_book'),
    path('saved_books/', views.saved_books, name='saved_books'),
    path('dictionary',views.dictionary,name="dictionary"),
    path('youtube',views.youtube,name="youtube"),
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/assignments/', views.assignment_list, name='assignment_list'),
    path('courses/<int:course_id>/assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('assignments/<int:assignment_id>/grade_list/', views.grade_assignment_list, name='grade_assignment_list'),
    path('submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('notes',views.notes,name="notes"),
    path('delete_note/<int:pk>', views.delete_note, name='delete-note'),
    path('notes_detail/<int:pk>', views.NotesDetailsView.as_view(), name='notes-detail'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('courses/<int:course_id>/quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/submissions/', views.quiz_submissions_list, name='quiz_submissions_list'),  # ✅ must come BEFORE the quiz_id path
    path('quizzes/<str:quiz_id>/take/', views.quiz_take, name='quiz_take'),
    path('quizzes/<str:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('quizzes/<str:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quizzes/<str:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/submissions/json/', views.quiz_submissions_json, name='quiz_submissions_json'),
    path('courses/<int:course_id>/quizzes/', views.quiz_list_by_course, name='quiz_list_by_course'),
    path('courses/<int:course_id>/details/', views.course_details_json, name='course_details_json'),
    path('courses/<int:course_id>/performance/', views.course_performance_view, name='course_performance'),


]
