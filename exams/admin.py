from django.contrib import admin
from .models import Exam, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text',)  # فقط فیلدهای موجود در مدل شما
    show_change_link = True


class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'created_by', 'question_count')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]

    # اضافه کردن تعداد سوالات به لیست نمایش
    def question_count(self, obj):
        return obj.questions.count()

    question_count.short_description = 'تعداد سوالات'

    # ذخیره سازنده آزمون به صورت خودکار
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Exam, ExamAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'exam', 'short_text')
    search_fields = ('text', 'exam__title')
    raw_id_fields = ('exam',)

    # نمایش متن کوتاه برای سوالات طولانی
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    short_text.short_description = 'متن کوتاه'


admin.site.register(Question, QuestionAdmin)