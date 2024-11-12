import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
from datetime import date
def userSocial(request):
    jsons = json.loads(request.body)
    user_id = jsons['id']

    if request.method == 'GET':
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute(
            'SELECT * FROM "f_userSocial" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
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
                'SELECT * FROM "f_userSocial" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
            columns = [column[0] for column in userCursor.description]
            response = [
                {columns[index]: column for index, column in enumerate(
                    value) if columns[index] not in []}
                for value in userCursor.fetchall()
            ]
            userCursor.close()
            disconnectDB(myCon)
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
        "socialData": {} 
    }
    return HttpResponse(json.dumps(response), content_type="application/json")
###########################################################################

def userSocialUp(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "user_id", "app", "site"]
    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Буруу хүсэлт"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
    
    id = int(jsons['id'])
    user_id = int(jsons['user_id'])
    app = jsons['app']
    site = jsons['site']
    
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        userCursor.execute(
            'SELECT * FROM "f_userSocial" WHERE "id" = %s AND "user_id" = %s AND "deldate" IS NULL', (id, user_id))
        user = userCursor.fetchone()

        if not user:
            response = {
                "responseCode": 555,
                "responseText": "Хэрэглэгчийн мэдээлэл олдсонгүй"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        if app == user[2] and site == user[3]:
            response = {
                "responseCode": 557,
                "responseText": "App болон site тэнцүү байна"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        userCursor.execute(
            'UPDATE "f_userSocial" SET "app" = %s, "site" = %s WHERE "id" = %s AND "user_id" = %s AND "deldate" IS NULL', (app, site, id, user_id))
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

#########################################################
def userSocialIn(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "app", "site"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    app = jsons['app']
    site = jsons['site']

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
            userCursor.execute('INSERT INTO "f_userSocial" ("user_id", "app", "site") VALUES (%s, %s, %s)',
                               (user_id, app, site))

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


def userSocialDel(request):
    jsons = json.loads(request.body)
    required_fields = ["socialId"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    socialId = jsons['socialId']
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute(
            'SELECT * FROM "f_userSocial" WHERE "id" = %s AND "deldate" IS NULL', (socialId,))
        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "Хаяг олдсонгүй"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            socialId = jsons["socialId"]
            myCon = connectDB()
            socialcursor = myCon.cursor()
            socialcursor.execute('UPDATE "f_userSocial" SET "deldate" = %s WHERE "id" = %s AND "deldate" IS NULL',
            (date.today(), socialId,))
            myCon.commit()
            socialcursor.close()
        
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
        "responseText": "Цахим хаяг устлаа"
    }

    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")

    ############### NEW SOCIAL FUNCTIONS 


# def userSocialDel(request):
#     if request.method != 'POST':
#         response = {
#             "responseCode": 400,
#             "responseText": "Bad Request"
#         }
#         return HttpResponse(json.dumps(response), content_type="application/json")

#     try:
#         jsons = json.loads(request.body)
#         required_fields = ["socialId"]

#         if not reqValidation(jsons, required_fields):
#             response = {
#                 "responseCode": 550,
#                 "responseText": "Field-үүд дутуу"
#             }
#             return HttpResponse(json.dumps(response), content_type="application/json")

#         socialId = jsons['socialId']

#         myCon = connectDB()
#         socialCursor = myCon.cursor()
#         socialCursor.execute(
#             'SELECT * FROM "f_userSocial" WHERE "id" = %s AND "deldate" IS NULL', (socialId,))
#         user = socialCursor.fetchone()

#         if not user:
#             response = {
#                 "responseCode": 555,
#                 "responseText": "Цахим хаяг олдсонгүй"
#             }
#             return HttpResponse(json.dumps(response), content_type="application/json")
        
#         socialCursor.execute(
#             'UPDATE "f_userSocial" SET "deldate" = %s WHERE "id" = %s AND "deldate" IS NULL',
#             (date.today(), socialId,)
#         )
#         myCon.commit()

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
#         "responseText": "Цахим хаяг устгагдлаа"
#     }

#     return HttpResponse(json.dumps(response), content_type="application/json")
##############
# def userSocial(request):
#     jsons = json.loads(request.body)
#     user_id = jsons['id']

#     if request.method == 'GET':
#         myCon = connectDB()
#         userCursor = myCon.cursor()
#         userCursor.execute(
#             'SELECT * FROM "f_userSocial" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
#         user = userCursor.fetchone()

#         if not user:
#             resp = {
#                 "responseCode": 555,
#                 "responseText": "Хэрэглэгч олдсонгүй"
#             }
#             userCursor.close()
#             disconnectDB(myCon)
#             return HttpResponse(json.dumps(resp), content_type="application/json")

#         elif user:
#             userCursor.execute(
#                 'SELECT * FROM "f_userSocial" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
#             columns = [column[0] for column in userCursor.description]
#             response = [
#                 {columns[index]: column for index, column in enumerate(
#                     value) if columns[index] not in []}
#                 for value in userCursor.fetchall()
#             ]
#             userCursor.close()
#             disconnectDB(myCon)
#             # Extract the first element from the response list
#             responseJSON = response
#             response = {
#                 "responseCode": 200,
#                 "responseText": "Амжилттай",
#                 "socialData": responseJSON
#             }
#             return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder, default=str), content_type="application/json")

#         else:
#             resp = {
#                 "responseCode": 551,
#                 "responseText": "Баазын алдаа"
#             }
#             return HttpResponse(json.dumps(resp), content_type="application/json")

#     response = {
#         "responseCode": 200,
#         "responseText": "Амжилттай",
#         "socialData": {}  # Add an empty "data" field in the response
#     }
#     return HttpResponse(json.dumps(response), content_type="application/json")
#########################
# def userSocialUp(request):
#     jsons = json.loads(request.body)
#     required_fields = ["id", "user_id", "app", "site"]
#     if not reqValidation(jsons, required_fields):
#         response = {
#             "responseCode": 550,
#             "responseText": "Буруу хүсэлт"
#         }
#         return HttpResponse(json.dumps(response), content_type="application/json")
    
#     id = int(jsons['id'])
#     user_id = int(jsons['user_id'])
#     app = jsons['app']
#     site = jsons['site']
    
#     try:
#         myCon = connectDB()
#         userCursor = myCon.cursor()

#         userCursor.execute(
#             'SELECT * FROM "f_userSocial" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
#         user = userCursor.fetchall()
#         userCursor.execute(
#             'SELECT id FROM "f_userSocial" WHERE "id" = %s AND "deldate" IS NULL', (id,))
#         idk = userCursor.fetchone()
#         if not user:
#             response = {
#                 "responseCode": 555,
#                 "responseText": "Хэрэглэгчийн мэдээлэл олдсонгүй"
#             }
#             userCursor.close()
#             disconnectDB(myCon)
#             return HttpResponse(json.dumps(response), content_type="application/json")

#         # Check if the provided ID matches the ID in the userSocial table
#         if not idk:  # Assuming the ID is the first column in the query
#             response = {
#                 "responseCode": 556,
#                 "responseText": "ID таарсангүй"
#             }
#             userCursor.close()
#             disconnectDB(myCon)
#             return HttpResponse(json.dumps(response), content_type="application/json")

#         # Check if the app and site values are different from the old data
#         if app == user[2] and site == user[3]:  # Assuming app is the third column and site is the fourth column
#             response = {
#                 "responseCode": 557,
#                 "responseText": "App болон site тэнцүү байна"
#             }
#             userCursor.close()
#             disconnectDB(myCon)
#             return HttpResponse(json.dumps(response), content_type="application/json")
#         # Update the app and site values in the userSocial table
#         userCursor.execute('UPDATE "f_userSocial" SET "app" = %s, "site" = %s WHERE "id" = %s AND "user_id" = %s AND "deldate" IS NULL',(app, site, id,user_id))
#         myCon.commit()
#         userCursor.close()
#         disconnectDB(myCon)
#     except Exception as e:
#         error_message = traceback.format_exc()  # Get the traceback message
#         response = {
#             "responseCode": 551,
#             "responseText": f"Баазын алдаа: {error_message}"
#         }
#         return HttpResponse(json.dumps(response), content_type="application/json")

#     response = {
#         "responseCode": 200,
#         "responseText": "Амжилттай солигдлоо"
#     }
#     return HttpResponse(json.dumps(response), content_type="application/json")