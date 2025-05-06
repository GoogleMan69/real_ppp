from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="homec"),
    path('logout/', views.logout, name="logout"),
]