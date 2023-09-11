import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
from datetime import date

# def userTurshlaga(request):
#     jsons = json.loads(request.body)
#     user_id = jsons['id']
#     if request.method == "GET":
#         myCon = connectDB()
#         userCursor = myCon.cursor()

#         userCursor.execute(
#             'SELECT * FROM "f_userWork" WHERE "user_id"= %s', (user_id,))

#         user = userCursor.fetchone()
#         if not user:
#             response = {
#                 "responseCode": 555,
#                 "responseText": "Хэрэглэгч олдсонгүй"
#             }
#             userCursor.close()
#             disconnectDB(myCon)
#             return HttpResponse(json.dumps(response), content_type="application/json")

#         elif user:
#             userCursor.execute(
#                 'SELECT * FROM "f_userWork" WHERE "user_id"= %s', (user_id,))
#             columns = [column[0] for column in userCursor.description]

#             response = [
#                 {columns[index]: column for index, column in enumerate(value)}
#                 for value in userCursor.fetchall()
#             ]
#             userCursor.close()
#             disconnectDB(myCon)
#             responseJSON = response
#             response = {
#                 "responseCode": 200,
#                 "responseText": "Амжилттай",
#                 "TurshlagaData": responseJSON
#             }

#             responseJSON = json.dumps(
#                 (response), cls=DjangoJSONEncoder, default=str)
#             return HttpResponse(responseJSON, content_type="application/json")

#         else:
#             response = {
#                 "responseCode": 551,
#                 "responseText": "Баазын алдаа"
#             }
#             return HttpResponse(json.dumps(response), content_type="application/json")
######################################################################################
# def userTurshlagaDel(request):
#     jsons = json.loads(request.body)
#     if (reqValidation(jsons, {"workId", }) == False):
#         resp = {}
#         resp["responseCode"] = 550
#         resp["responseText"] = "Field-үүд дутуу"
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#     try:
#         workId = jsons["workId"]
#         myCon = connectDB()
#         familyCursor = myCon.cursor()
#         familyCursor.execute(
#             'delete from "f_userWork" WHERE "id" = %s', (workId,))
#         myCon.commit()
#         familyCursor.close()
        
#     except Exception as e:
#         response = {
#             "responseCode": 551,
#             "responseText": "Баазын алдаа"
#         }
#         return HttpResponse(json.dumps(response), content_type="application/json")
#     finally:
#         disconnectDB(myCon)

#     response = {
#         "responseCode": 200,
#         "responseText": "Ажлын туршлага амжилттай устгалаа"
#     }

#     responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
#     return HttpResponse(responseJSON, content_type="application/json")
#########################################################################
def userTurshlagaIn(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "ajil", "company", "duussan", "ehelsen"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    ajil = jsons['ajil']
    company = jsons['company']
    ehelsen = jsons['ehelsen']
    duussan = jsons['duussan']

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
        if user:
            userCursor.execute('INSERT INTO "f_userWork" ("user_id", "ajil", "company", "ehelsen","duussan") VALUES (%s, %s, %s,%s, %s)',
                               (user_id, ajil, company, ehelsen, duussan))

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
    ##########################################################################
# def userTurshlagaUp(request):
#     jsons = json.loads(request.body)

#     # Validate request body
#     required_fields = ["id", "oldAjil", "ajil",
#                        "company", "ehelsen", "duussan"]
#     if not reqValidation(jsons, required_fields):
#         response = {
#             "responseCode": 550,
#             "responseText": "Буруу хүсэлт"
#         }
#         return HttpResponse(json.dumps(response), content_type="application/json")

#     id = jsons['id']
#     ajil = jsons['ajil']
#     company = jsons['company']
#     ehelsen = jsons['ehelsen']
#     duussan = jsons['duussan']
#     oldAjil = jsons["oldAjil"]

#     try:
#         myCon = connectDB()
#         userCursor = myCon.cursor()

#         # Check if the user exists
#         userCursor.execute('SELECT * FROM "f_userWork" WHERE "user_id" = %s AND "ajil" = %s',
#                            (id, oldAjil))
#         user = userCursor.fetchone()
#         if not user:
#             response = {
#                 "responseCode": 555,
#                 "responseText": "Мэдээлэл буруу байна"
#             }
#             userCursor.close()
#             disconnectDB(myCon)

#             return HttpResponse(json.dumps(response), content_type="application/json")

#         # Update the password
#         userCursor.execute('UPDATE "f_userWork" SET "ajil" = %s, "company"  = %s, "ehelsen" =%s,  "duussan"=%s WHERE "user_id" = %s AND "ajil"=%s',
#                            (ajil, company, ehelsen, duussan, id, oldAjil))
#         myCon.commit()
#         userCursor.close()
#         disconnectDB(myCon)

#     except Exception as e:
#         response = {
#             "responseCode": 551,
#             "responseText": "Баазын алдаа"
#         }
#         return HttpResponse(json.dumps(response), content_type="application/json")

#     response = {
#         "responseCode": 200,
#         "responseText": "Амжилттай солигдлоо"
#     }
#     return HttpResponse(json.dumps(response), content_type="application/json")
    #################### NEW WORK FUNCTIONS 


def userTurshlaga(request):
    jsons = json.loads(request.body)
    user_id = jsons['id']
    if request.method == "GET":
        myCon = connectDB()
        userCursor = myCon.cursor()

        userCursor.execute(
            'SELECT * FROM "f_userWork" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))

        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "Хэрэглэгч олдсонгүй"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        elif user:
            userCursor.execute(
                'SELECT * FROM "f_userWork" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
            columns = [column[0] for column in userCursor.description]

            response = [
                {columns[index]: column for index, column in enumerate(value)}
                for value in userCursor.fetchall()
            ]
            userCursor.close()
            disconnectDB(myCon)
            responseJSON = response
            response = {
                "responseCode": 200,
                "responseText": "Амжилттай",
                "TurshlagaData": responseJSON
            }

            responseJSON = json.dumps(
                (response), cls=DjangoJSONEncoder, default=str)
            return HttpResponse(responseJSON, content_type="application/json")

        else:
            response = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")



def userTurshlagaDel(request):
    # Ensure that the request method is POST
    if request.method != 'POST':
        response = {
            "responseCode": 400,
            "responseText": "Bad Request"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    try:
        jsons = json.loads(request.body)
        required_fields = ["workId"]

        if not reqValidation(jsons, required_fields):
            response = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")

        workId = jsons['workId']

        myCon = connectDB()
        workCursor = myCon.cursor()

        # Check if the workId exists and is not deleted
        workCursor.execute(
            'SELECT * FROM "f_userWork" WHERE "id" = %s AND "deldate" IS NULL', (workId,))
        work = workCursor.fetchone()

        if not work:
            response = {
                "responseCode": 555,
                "responseText": "Ажлын туршлаг олдсонгүй"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
        
        # Soft delete the work record by setting the 'deldate'
        workCursor.execute(
            'UPDATE "f_userWork" SET "deldate" = %s WHERE "id" = %s AND "deldate" IS NULL',
            (date.today(), workId,)
        )
        myCon.commit()

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
        "responseText": "Ажлын туршлаг амжилттай устгалаа"
    }

    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")




def userTurshlagaUp(request):
    jsons = json.loads(request.body)

    # Validate request body
    required_fields = ["id", "oldAjil", "ajil",
                       "company", "ehelsen", "duussan"]
    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Буруу хүсэлт"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    id = jsons['id']
    ajil = jsons['ajil']
    company = jsons['company']
    ehelsen = jsons['ehelsen']
    duussan = jsons['duussan']
    oldAjil = jsons["oldAjil"]

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        # Check if the user exists
        userCursor.execute('SELECT * FROM "f_userWork" WHERE "user_id" = %s AND "ajil" = %s AND "deldate" IS NULL',
                           (id, oldAjil))
        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "Мэдээлэл буруу байна"
            }
            userCursor.close()
            disconnectDB(myCon)

            return HttpResponse(json.dumps(response), content_type="application/json")

        # Update the password
        userCursor.execute('UPDATE "f_userWork" SET "ajil" = %s, "company"  = %s, "ehelsen" =%s,  "duussan"=%s WHERE "user_id" = %s AND "ajil"=%s AND "deldate" IS NULL',
                           (ajil, company, ehelsen, duussan, id, oldAjil))
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)

    except Exception as e:
        response = {
            "responseCode": 551,
            "responseText": "Баазын алдаа"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    response = {
        "responseCode": 200,
        "responseText": "Амжилттай солигдлоо"
    }
    return HttpResponse(json.dumps(response), content_type="application/json")
