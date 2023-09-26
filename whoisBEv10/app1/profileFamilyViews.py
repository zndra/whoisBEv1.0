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
        current_datetime = datetime.now()
        familyCursor.execute(
            'UPDATE "f_userFamily" SET "deldate" = %s WHERE "id" = %s', (current_datetime, familyId))
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
########################################################
def userFamilyGet(request):
    jsons = json.loads(request.body)
    required_fields=["user_id"]
  
    if request.method == 'GET':
        if not reqValidation(jsons, required_fields):
            response = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
        user_id = jsons['user_id']
        try:
            myCon = connectDB()
            userCursor = myCon.cursor()
            userCursor.execute(
                'SELECT * FROM "f_userFamily" WHERE "user_id"= %s AND "deldate" IS NULL', (user_id,))
            user = userCursor.fetchone()
            if not user:
                response = {
                    "responseCode": 555,
                    "responseText": "Хэрэглэгч олдсонгүй"
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")
            if user:
                userCursor.execute(
                    'SELECT * FROM "f_userFamily" WHERE "user_id"= %s', (user_id,))
                columns = [column[0] for column in userCursor.description]

                response = [
                    {columns[index]: column for index, column in enumerate(value)}for value in userCursor.fetchall()
                ]

                userCursor.close()
                disconnectDB(myCon)
            responseJSON = response
            response = {
                "responseCode": 200,
                "responseText": "Амжилттай",
                "data": responseJSON
            }
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder, default=str), content_type="application/json")

        except:
            response = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

#####################################################
def userFamilyInsert(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "henBoloh", "ner", "dugaar"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    henBoloh = jsons['henBoloh']
    ner = jsons['ner']
    dugaar = jsons['dugaar']

    if request.method == 'POST':
        try:
            myCon = connectDB()
            userCursor = myCon.cursor()
            userCursor.execute(
                'SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
            user = userCursor.fetchone()
            if not user:
                response = {
                    "responseCode": 555,
                    "responseText": "Хэрэглэгч олдсонгүй"
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")

            userCursor.execute('INSERT INTO "f_userFamily" ("henBoloh", "ner", "dugaar", "user_id") VALUES (%s, %s, %s, %s)',
                               (henBoloh, ner, dugaar, user_id))
            myCon.commit()
            userCursor.close()
            disconnectDB(myCon)

            response = {
                "responseCode": 200,
                "responseText": "Амжилттай бүртгэгдлээ"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")

        except Exception as e:
            response = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
#########################################################################################


def userFamilyUpdate(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "henBoloh", "ner", "dugaar"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    henBoloh = jsons['henBoloh']
    ner = jsons['ner']
    dugaar = jsons['dugaar']
    if request.method == 'POST':
        try:
            myCon = connectDB()
            userCursor = myCon.cursor()

            userCursor.execute(
                'SELECT * FROM "f_userFamily" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
            user = userCursor.fetchone()
            if not user:
                response = {
                    "responseCode": 555,
                    "responseText": "Хэрэглэгч олдсонгүй"
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")

            userCursor.execute('UPDATE "f_userFamily" SET "henBoloh" = %s, "ner" = %s, dugaar= %s WHERE "user_id" = %s',
                               (henBoloh, ner, dugaar, user_id))
            myCon.commit()
            userCursor.close()
            disconnectDB(myCon)

            response = {
                "responseCode": 200,
                "responseText": "Амжилттай солигдлоо"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")

        except Exception as e:
            response = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")


