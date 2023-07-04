import traceback
import json
from django.http import HttpResponse
from datetime import date
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
import json
from django.db import connection
import pytz
import datetime

def userEduDel(request):
    jsons = json.loads(request.body)
    if (reqValidation(jsons, {"id", }) == False):
        resp = {}
        resp["responseCode"] = 550
        resp["responseText"] = "Field-үүд дутуу"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    try:
        edu_id = jsons["id"]
        myCon = connectDB()
        familyCursor = myCon.cursor()
        familyCursor.execute(
            'delete from "f_userEdu" WHERE "id" = %s', (edu_id,))
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
        "responseText": "Боловсролын мэдээлэл амжилттай устгагдлаа."
    }

    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")
####################################################################################
def userEduUp(request):
    jsons = json.loads(request.body)
    required_fields = ["user_id", "education", "direction",
                       "elssenOn", "duussanOn"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['user_id']
    education = jsons['education']
    direction = jsons['direction']
    elssenOn = jsons['elssenOn']
    duussanOn = jsons['duussanOn']

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        userCursor.execute(
            'SELECT * FROM "f_userEdu" WHERE "user_id" = %s', (user_id,))
        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "Хэрэглэгч олдсонгүй"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        userCursor.execute('UPDATE "f_userEdu" SET "education" = %s,"direction" = %s,"elssenOn" = %s, "duussanOn" = %s WHERE "user_id" = %s',
                           (education, direction, elssenOn, duussanOn, user_id,))
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

###############################################################################################


def userEduInsert(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "education", "direction", "elssenOn", "duussanOn"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    education = jsons['education']
    direction = jsons['direction']
    elssenOn = jsons['elssenOn']
    duussanOn = jsons['duussanOn']

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
            'INSERT INTO "f_userEdu" ("education", "direction", "elssenOn", "duussanOn","user_id") VALUES (%s, %s, %s, %s, %s)',
            (education, direction, elssenOn, duussanOn, user_id))
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)

        response = {
            "responseCode": 200,
            "responseText": "Амжилттай бүртгэгдлээ"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    except Exception as e:
        error_message = traceback.format_exc()
        # Print the detailed error message for debugging purposes
        print(error_message)

        response = {
            "responseCode": 551,
            "responseText": "Баазын алдаа: " + str(e)
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

################################################################################################


def userEduGet(request):
    jsons = json.loads(request.body)
    user_id = jsons['user_id']    
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute(
        'SELECT * FROM "f_userEdu" WHERE "user_id" = %s', (user_id,))
    user = userCursor.fetchone()

    if not user:
        resp = {
            "responseCode": 555,
            "responseText": "Хэрэглэгч олдсонгүй"
        }
        userCursor.close()
        disconnectDB(myCon)
        return HttpResponse(json.dumps(resp), content_type="application/json")

    elif user:
        userCursor.execute(
            'SELECT * FROM "f_userEdu" WHERE "user_id" = %s', (user_id,))
        columns = [column[0] for column in userCursor.description]
        response = [
            {columns[index]: column for index, column in enumerate(
                value) if columns[index] not in []}
            for value in userCursor.fetchall()
        ]
        userCursor.close()
        disconnectDB(myCon)
        # Extract the first element from the response list
        responseJSON = response
        response = {
            "responseCode": 200,
            "responseText": "Амжилттай",
            "eduData": responseJSON
        }
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder, default=str), content_type="application/json")

    else:
        resp = {
            "responseCode": 551,
            "responseText": "Баазын алдаа"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

######################################################################################


def userSocial(request):
    jsons = json.loads(request.body)
    user_id = jsons['id']

    if request.method == 'GET':
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute(
            'SELECT * FROM "f_userSocial" WHERE "user_id" = %s', (user_id,))
        user = userCursor.fetchone()

        if not user:
            resp = {
                "responseCode": 555,
                "responseText": "Хэрэглэгч олдсонгүй"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")

        elif user:
            userCursor.execute(
                'SELECT * FROM "f_userSocial" WHERE "user_id" = %s', (user_id,))
            columns = [column[0] for column in userCursor.description]
            response = [
                {columns[index]: column for index, column in enumerate(
                    value) if columns[index] not in []}
                for value in userCursor.fetchall()
            ]
            userCursor.close()
            disconnectDB(myCon)
            # Extract the first element from the response list
            responseJSON = response
            response = {
                "responseCode": 200,
                "responseText": "Амжилттай",
                "socialData": responseJSON
            }
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder, default=str), content_type="application/json")

        else:
            resp = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

    response = {
        "responseCode": 200,
        "responseText": "Амжилттай",
        "socialData": {}  # Add an empty "data" field in the response
    }
    return HttpResponse(json.dumps(response), content_type="application/json")
###########################################################################