from django.http import HttpResponse
import json

# Create your views here.
def zuu(request):
    response = {}
    response["hariu"] = "hello"
    response["surguuli"] = "Mandakh"
    responseJSON = json.dumps(response)
    return HttpResponse(responseJSON,content_type="application/json")