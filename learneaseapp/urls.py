from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name="home"),
    
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('books',views.books,name="books"),  
    path('dictionary',views.dictionary,name="dictionary"),
] 