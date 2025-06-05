from django.contrib import admin
from .models import StudentResponse, Note

class StudentResponseAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'is_flagged', 'last_modified')
    list_filter = ('is_flagged', 'last_modified')
    search_fields = ('student__username', 'question__text', 'answer_text')

admin.site.register(StudentResponse, StudentResponseAdmin)
admin.site.register(Note)
