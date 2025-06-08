from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from exams.models import Exam
from .models import StudentResponse

@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()

    if request.method == 'POST':
        for question in questions:
            answer_text = request.POST.get(f'answer_{question.id}')
            if answer_text:
                StudentResponse.objects.update_or_create(
                    student=request.user,
                    question=question,
                    defaults={'answer_text': answer_text}
                )
        return redirect('response:thank_you')

    return render(request, 'responses/take_exam.html', {'exam': exam, 'questions': questions})

@login_required
def thank_you(request):
    return render(request, 'responses/ending.html')