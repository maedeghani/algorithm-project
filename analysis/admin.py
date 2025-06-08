from django.contrib import admin
from .models import AnalysisResult

class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'timestamp', 'algorithm_version')
    list_filter = ('timestamp', 'algorithm_version')
    search_fields = ('exam__title', 'algorithm_version')
    ordering = ('-timestamp',)
admin.site.register(AnalysisResult, AnalysisResultAdmin)
