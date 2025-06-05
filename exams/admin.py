from django.contrib import admin
from .models import Exam, Question

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'created_by')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]

admin.site.register(Exam, ExamAdmin)
admin.site.register(Question)
