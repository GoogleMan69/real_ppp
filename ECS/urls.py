from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="homec"),
    path('logout/', views.logout, name="logout"),
    path('users/', views.users, name="users"),  # Add the trailing slash here
]