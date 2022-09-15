from django.urls import path

from . import views

urlpatterns = [
    path('', views.SpaView.as_view(), name='spa'),
]
