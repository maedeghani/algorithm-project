from django.contrib import admin
from django.urls import path
from analysis.views import detect_cheating, home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),  # مسیر ادمین
    path('detect-cheating/<str:quiz_id>/<str:question_id>/', detect_cheating, name='detect_cheating'),
]