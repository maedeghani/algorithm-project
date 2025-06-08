from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: redirect('signup')), 
    path('responses/', include('responses.urls')),
    path('exams/', include('exams.urls')),
 # ریدایرکت صفحه‌ی اصلی به signup
]
