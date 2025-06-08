from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ExamForm, QuestionForm
from .models import Question, Answer, Exam
from django.contrib.auth.decorators import login_required


@login_required
def create_exam(request):
    if not request.User.is_instructor:
        return HttpResponseForbidden("Only instructors can create exams.")

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            return redirect('exams:add_question', exam_id=exam.id)
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

    # فقط instructors اجازه افزودن سؤال دارند
    if not request.user.is_authenticated or not getattr(request.user, 'is_instructor', False):
        return HttpResponseForbidden("فقط اساتید می‌توانند سوال اضافه کنند")

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam_id = exam_id  # استفاده مستقیم از exam_id
            question.save()
            return redirect('exams:add_question', exam_id=exam_id)
    else:
        form = QuestionForm()
    questions = Question.objects.filter(exam_id=exam_id)

    return render(request, 'exams/add_question.html', {'exam_id': exam_id, 'form': form, 'questions': questions})


@login_required
def questions_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()

    if request.method == 'POST':
        for question in questions:
            answer_text = request.POST.get(f'answer_{question.id}')
            if answer_text:
                Answer.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'answer_text': answer_text}
                )
        return redirect('exams:thank_you')

    return render(request, 'exams/questions.html', {'exam': exam, 'questions': questions})


@login_required
def thank_you_view(request):
    return render(request, 'responses/ending.html')
