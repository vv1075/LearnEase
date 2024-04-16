from django.urls import path
from . import views


urlpatterns = [
    path('',views.home,name="home"),
    path('login/', auth_views.LoginView.as_view(template_name = "learneaseapp/login.html"),name='login'),
    
] 