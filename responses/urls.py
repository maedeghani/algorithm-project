from django.urls import path
from . import views

app_name = 'response'

urlpatterns = [
    path('take_exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('thank_you/', views.thank_you, name='thank_you'),
]