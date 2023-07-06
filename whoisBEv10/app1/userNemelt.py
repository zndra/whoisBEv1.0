import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *




def userNemeltGet(request):
    jsons = json.loads(request.body)
    required_fields = ["user_id",]
   
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
                'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id"= %s', (user_id,))
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
                    'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id"= %s', (user_id,))
                columns = [column[0] for column in userCursor.description]

                response = [
                    {columns[index]: column for index, column in enumerate(value)}for value in userCursor.fetchall()
                ]
                userCursor.close()
                disconnectDB(myCon)

            # Extract the first element from the response list
            responseJSON = response[0]
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


####################################################################


def userNemeltUpdate(request):
    jsons = json.loads(request.body)
    required_fields = ["user_id", "regDug", "torsonOgnoo",
                       "dugaar", "huis", "irgenshil", "ysUndes", "hayg", "hobby"]
    if request.method == 'POST':
        if not reqValidation(jsons, required_fields):
            response = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")

        user_id = jsons['user_id']
        regDug = jsons['regDug']
        torsonOgnoo = jsons['torsonOgnoo']
        dugaar = jsons['dugaar']
        huis = jsons['huis']
        irgenshil = jsons['irgenshil']
        ysUndes = jsons['ysUndes']
        hayg = jsons['hayg']
        hobby = jsons['hobby']

        try:
            myCon = connectDB()
            userCursor = myCon.cursor()

            userCursor.execute(
                'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id" = %s', (user_id,))
            user = userCursor.fetchone()
            if not user:
                response = {
                    "responseCode": 555,
                    "responseText": "Хэрэглэгч олдсонгүй"
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")

            userCursor.execute('UPDATE "f_userNemeltMedeelel" SET "regDug" = %s,"torsonOgnoo" = %s,"dugaar" = %s, "huis" = %s,"irgenshil" = %s,"ysUndes" = %s,"hayg" = %s,"hobby" = %s WHERE "user_id" = %s',
                               (regDug, torsonOgnoo, dugaar, huis, irgenshil, ysUndes, hayg, hobby, user_id,))
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

###########################################################


def userNemeltInsert(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "regDug", "torsonOgnoo", "dugaar",
                       "huis", "irgenshil", "ysUndes", "hayg", "hobby"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    regDug = jsons['regDug']
    torsonOgnoo = jsons['torsonOgnoo']
    dugaar = jsons['dugaar']
    huis = jsons['huis']
    irgenshil = jsons['irgenshil']
    ysUndes = jsons['ysUndes']
    hayg = jsons['hayg']
    hobby = jsons['hobby']
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

            userCursor.execute(
                'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id" = %s', (user_id,))
            user = userCursor.fetchone()
            if user:
                response = {
                    "responseCode": 400,
                    "responseText": "Бүртгэлтэй хэрэглэгч байна."
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")
            if regDugExist(regDug):
                resp = {
                    "responseCode": 400,
                    "responseText": "Бүртгэлтэй хэрэглэгчийн id байна."
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")
            userCursor.execute('INSERT INTO "f_userNemeltMedeelel" ("regDug", "torsonOgnoo", "dugaar", "huis", "irgenshil", "ysUndes", "hayg", "hobby", "user_id") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                               (regDug, torsonOgnoo, dugaar, huis, irgenshil, ysUndes, hayg, hobby, user_id))
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