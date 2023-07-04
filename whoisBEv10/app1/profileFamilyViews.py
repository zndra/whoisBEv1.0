import json
from django.http import HttpResponse

from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *


def userFamilyDel(request):
    jsons = json.loads(request.body)
    if (reqValidation(jsons, {"familyId", }) == False):
        resp = {}
        resp["responseCode"] = 550
        resp["responseText"] = "Field-үүд дутуу"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    try:
        familyId = jsons["familyId"]
        myCon = connectDB()
        familyCursor = myCon.cursor()
        familyCursor.execute(
            'delete from "f_userFamily" WHERE "id" = %s', (familyId,))
        myCon.commit()
        familyCursor.close()
        
    except Exception as e:
        response = {
            "responseCode": 551,
            "responseText": "Баазын алдаа"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
    finally:
        disconnectDB(myCon)

    response = {
        "responseCode": 200,
        "responseText": "Гэр бүлийн гишүүн амжилттай устгалаа"
    }

    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")
#   def userFamilyDel(request):
