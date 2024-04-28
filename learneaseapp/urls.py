from django.urls import path
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
    path('courses/<int:course_id>/assignments/', views.assignment_list, name='assignment_list'),
    path('courses/<int:course_id>/assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
] 