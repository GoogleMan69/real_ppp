from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="homec"),
    path('logout/', views.logout, name="logout"),
    path('users/', views.users, name="users"),  # Add the trailing slash here
    path('user_ins/', views.user_ins, name="user_ins"),  # <-- Add this line

]