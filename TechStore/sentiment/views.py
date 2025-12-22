# sentiment/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import predict_sentiment

@csrf_exempt
def sentiment_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)
    text = data.get("text")

    if not text:
        return JsonResponse({"error": "No text"}, status=400)

    result = predict_sentiment(text)
    return JsonResponse(result)
