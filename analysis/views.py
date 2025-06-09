from django.http import JsonResponse
from .cheating_detection import generate_results_json
from django.http import HttpResponse

def detect_cheating(request, quiz_id, question_id):
    result = generate_results_json(quiz_id, "result.json", question_id)
    return JsonResponse(result)

def home(request):
    return HttpResponse("خوش آمدید به سیستم آزمون! برای بررسی تقلب، از آدرس /detect-cheating/<quiz_id>/<question_id>/ استفاده کنید.")