from django.urls import path
from . import views

urlpatterns = [
    path('/noreach', views.index, name="default"),
]