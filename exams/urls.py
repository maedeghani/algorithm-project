from django.urls import path
from . import views
app_name = 'exams'
urlpatterns = [
    path('create/', views.create_exam, name='create_exam'),
    path('my/', views.my_exams, name='my_exams'),
    path('exam/<int:exam_id>/add_question/', views.add_question, name='add_question'),
    path('exam/<int:exam_id>/report/', views.exam_report, name='exam_report'),
    path('exam/<int:exam_id>/questions/', views.questions_view, name='exam_detail'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
]
