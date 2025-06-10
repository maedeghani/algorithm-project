from datetime import timedelta

from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import ExamForm, QuestionForm
from .models import Question, Answer, Exam
from django.contrib.auth.decorators import login_required


@login_required
def create_exam(request):
    if not request.user.is_authenticated or not getattr(request.user, 'is_instructor', False):
        return HttpResponseForbidden("فقط اساتید می‌توانند سوال اضافه کنند")

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            try:
                exam = form.save(commit=False)
                exam.created_by = request.user
                exam.save()
                try:
                    return redirect('exams:add_question', exam_id=exam.id)
                except:
                    # اگر مشکل در redirect بود
                    return redirect(f'/exams/{exam.id}/add-question/')
            except Exception as e:
                # لاگ خطا
                print(f"Error creating exam: {str(e)}")
                form.add_error(None, "خطا در ایجاد آزمون")
    else:
        form = ExamForm()
    return render(request, 'exams/create_exam.html', {'form': form})


@login_required
def my_exams(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'exams/my_exams.html', {'exams': exams})


@login_required
def exam_report(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    answers = Answer.objects.filter(question__exam=exam).select_related('user', 'question')
    return render(request, 'exams/exam_report.html', {'exam': exam, 'answers': answers})


@login_required
def add_question(request, exam_id):
    # بررسی instructor بودن کاربر
    if not request.user.is_authenticated or not getattr(request.user, 'is_instructor', False):
        return HttpResponseForbidden("فقط اساتید می‌توانند سوال اضافه کنند")

    exam, created = Exam.objects.get_or_create(
        id=exam_id,
        defaults={
            'created_by': request.user,
            'title': f'آزمون جدید {exam_id}',
            # سایر فیلدهای اجباری مدل Exam را اینجا اضافه کنید
            'description': 'توضیحات پیش‌فرض',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timedelta(hours=1)
        }
    )
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam  # همون exam_id مستقیم
            question.save()
            return redirect('exams:add_question', exam_id=exam.id)

    else:
        form = QuestionForm()

    # دریافت سوالات مربوط به این آزمون
    questions = Question.objects.filter(exam=exam).order_by('-id')

    return render(request, 'exams/add_question.html', {
        'exam': exam,  # فقط ارسال exam_id
        'form': form,
        'questions': questions,
    })


@login_required
def questions_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all().order_by('id')

    if request.method == 'POST':
        for question in questions:
            answer_text = request.POST.get(f'answer_{question.id}')
            if answer_text:
                Answer.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={
                        'answer_text': answer_text,
                        'submitted_at': timezone.now()
                    }
                )
        return redirect('exams:thank_you')
    user_answers = Answer.objects.filter(
        user=request.user,
        question__in=questions
    )
    answered_questions = {answer.question.id: answer.answer_text for answer in user_answers}
    return render(request, 'exams/questions.html', {
        'exam': exam,
        'questions': questions,
        'answered_questions': answered_questions,
    })


@login_required
def thank_you_view(request):
    return render(request, 'responses/ending.html')
