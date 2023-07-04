import json
from django.http import HttpResponse

from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *

def userTurshlagaDel(request):
    jsons = json.loads(request.body)
    if (reqValidation(jsons, {"workId", }) == False):
        resp = {}
        resp["responseCode"] = 550
        resp["responseText"] = "Field-үүд дутуу"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    try:
        workId = jsons["workId"]
        myCon = connectDB()
        familyCursor = myCon.cursor()
        familyCursor.execute(
            'delete from "f_userWork" WHERE "id" = %s', (workId,))
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
        "responseText": "Ажлын туршлага амжилттай устгалаа"
    }

    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")
    