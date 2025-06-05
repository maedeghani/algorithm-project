from django.contrib import admin
from .models import AnalysisResult

class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('exam', 'timestamp', 'algorithm_version')
    list_filter = ('timestamp', 'algorithm_version')

admin.site.register(AnalysisResult, AnalysisResultAdmin)
