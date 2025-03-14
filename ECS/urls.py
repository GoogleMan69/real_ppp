from django.urls import path
from . import views

urlpatterns = [
    path('01/', views.index, name="index"),
]