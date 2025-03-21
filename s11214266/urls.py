from django.urls import path
from . import views

urlpatterns = [
    path('chin/', views.index, name="index"),
]