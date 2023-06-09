from django.http import HttpResponse
# from django.http import JsonResponse
import json

# Create your views here.
def zuu(request):
    response = {}
    response["hariu"] = "hello"
    response["surguuli"] = "Mandakh"
    responseJSON = json.dumps(response)
    return HttpResponse(responseJSON,content_type="application/json")
    # return JsonResponse({'response': responseJSON})