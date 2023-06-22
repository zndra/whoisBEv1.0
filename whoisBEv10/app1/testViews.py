from django.http import HttpResponse
from  whoisBEv10.settings import *
import json


# Create your views here.
def zuu(request):
    response = {}
    response["hariu"]    = "hello"
    response["surguuli"] = "Mandakh"
    response["usuhuu"]   = mandakhHash('usuhuu')
    responseJSON         = json.dumps(response)
    return HttpResponse(responseJSON,content_type="application/json")
    # return JsonResponse({'response': responseJSON})

def tavFactView(request):
    jsons = json.loads(request.body)    
    if( reqValidation( jsons, {"n","m"} ) == False):
        response = {}
        response["sol"]    = "Оролт буруу"
        responseJSON = json.dumps(response)
        return HttpResponse(responseJSON,content_type="application/json")
    n = int(jsons["n"])
    m = int(jsons["m"])
    hariu = n*m
    response = {}
    response["sol"]    = hariu
    responseJSON = json.dumps(response)
    return HttpResponse(responseJSON,content_type="application/json")
