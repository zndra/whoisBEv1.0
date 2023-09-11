import json
from django.http import HttpResponse
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
from django.db import connection
import json
import traceback


def uploadTemplateView(request):
    jsons = json.loads(request.body)

    required_fields = {"name", "tempTypeId", "catId", "file"}
    if reqValidation(jsons, required_fields) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    name = jsons['name']
    tempTypeId = jsons['tempTypeId']
    catId = jsons['catId']
    file = jsons['file']

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        if not myCon:
            raise Exception("Can not connect to the database")
    except Exception as e:
        resp = {
            "responseCode": 551,
            "responseText": "Баазын алдаа"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Check if tempTypeId exists in f_tempType table
    userCursor.execute(
        'SELECT * FROM "f_tempType" WHERE "id" = %s', (tempTypeId,))
    tempType = userCursor.fetchone()

    if not tempType:
        resp = {
            "responseCode": 556,
            "responseText": "Буруу tempTypeId"
        }
        userCursor.close()
        disconnectDB(myCon)
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Check if catId exists in f_catType table
    userCursor.execute(
        'SELECT * FROM "f_catType" WHERE "id" = %s', (catId,))
    catType = userCursor.fetchone()

    if not catType:
        resp = {
            "responseCode": 557,
            "responseText": "Буруу catId"
        }
        userCursor.close()
        disconnectDB(myCon)
        return HttpResponse(json.dumps(resp), content_type="application/json")

    userCursor.execute(
        'INSERT INTO "f_templates"("name", "tempTypeId", "catId", "file") '
        'VALUES(%s, %s, %s, %s) RETURNING "id"',
        (name, tempTypeId, catId, file))

    templateId = userCursor.fetchone()[0]

    myCon.commit()

    userCursor.close()
    disconnectDB(myCon)

    resp = {
        "responseCode": 200,
        "responseText": "Template нэмэгдлээ",
        "templateId": templateId
    }
    return HttpResponse(json.dumps(resp), content_type="application/json")

############################################################################
def userTemplates(request):
    jsons = json.loads(request.body)

    if reqValidation(jsons, {"userId", "name", "tempId"}) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    tempId = jsons['tempId']
    userId = jsons['userId']
    name = jsons['name']

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        if not myCon:
            raise Exception("Can not connect to the database")
    except Exception as e:
        resp = {
            "responseCode": 551,
            "responseText": "Баазын алдаа"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Check if the user exists
    userCursor.execute(
        'SELECT * FROM "f_user" WHERE "id" = %s', (userId,))
    user = userCursor.fetchone()

    if not user:
        resp = {
            "responseCode": 555,
            "responseText": "Хэрэглэгч олдсонгүй"
        }
        userCursor.close()
        disconnectDB(myCon)
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Check if the template exists
    userCursor.execute(
        'SELECT * FROM "f_templates" WHERE "id" = %s', (tempId,))
    template = userCursor.fetchone()

    if not template:
        resp = {
            "responseCode": 556,
            "responseText": "template олдсонгүй"
        }
        userCursor.close()
        disconnectDB(myCon)
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Insert the template
    userCursor.execute(
        'INSERT INTO "f_userTemplates"( "name", "userId", "tempId") '
        'VALUES (%s, %s, %s) '
        'RETURNING "id"',
        (name, userId, tempId))

    userTempId = userCursor.fetchone()[0]

    myCon.commit()

    userCursor.close()
    disconnectDB(myCon)

    resp = {
        "responseCode": 200,
        "responseText": "Template ашигласан",
        "userTempId": userTempId
    }
    return HttpResponse(json.dumps(resp), content_type="application/json")


###############################################################################
def userTempGet(request):
    jsons = json.loads(request.body)
    user_id = jsons.get('userId')
    if user_id is None:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    if request.method == 'GET':
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute(
            'SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
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
                'SELECT * FROM "f_userTemplates" WHERE "userId" = %s', (user_id,))
            columns = [column[0] for column in userCursor.description]
            response = [
                {columns[index]: column for index, column in enumerate(
                    value) if columns[index] not in []}
                for value in userCursor.fetchall()
            ]
            userCursor.close()
            disconnectDB(myCon)
            responseJSON = {"tempData": response}
            response = {
                "responseCode": 200,
                "responseText": "Амжилттай",
                **responseJSON
            }
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")

        else:
            resp = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

    response = {
        "responseCode": 200,
        "responseText": "Амжилттай",
        "tempData": {}
    }
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")


def tempGet(request):
    jsons = json.loads(request.body)
    user_id = jsons.get('id')
    if user_id is None:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    if request.method == 'GET':
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute(
            'SELECT * FROM "f_templates" WHERE "id" = %s', (user_id,))
        columns = [column[0] for column in userCursor.description]
        response = [
            {columns[index]: column for index, column in enumerate(
                value) if columns[index] not in []}
            for value in userCursor.fetchall()
        ]
        userCursor.close()
        disconnectDB(myCon)

        if not response:
            resp = {
                "responseCode": 555,
                "responseText": "Тэмплэт олдсонгүй"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        responseJSON = {"tempData": response}
        response = {
            "responseCode": 200,
            "responseText": "Амжилттай",
            **responseJSON
        }
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")



###############################################################################
def tempListView(request):
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT * FROM f_templates ORDER BY id ASC')
    columns = userCursor.description
    response = [{columns[index][0]: column for index, column in enumerate(value)} for value in userCursor.fetchall()]
    userCursor.close()
    disconnectDB(myCon)
    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")
################################################################################

def userTempListView(request):
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT * FROM "f_userTemplates" ORDER BY id ASC')
    columns = [column[0] for column in userCursor.description]
    response = [
        {columns[index]: column for index, column in enumerate(value) if columns[index] not in []}
        for value in userCursor.fetchall()
    ]
    userCursor.close()
    disconnectDB(myCon)
    if response:
        responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    else:
        responseJSON = json.dumps({}, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")
###########################################################################


def getUserAllInfo(request):
    jsons = json.loads(request.body)
    user_id = jsons.get('id')
    user_name = jsons.get('userName')

    required_fields = ["id", "userName"]
    if request.method == 'GET':
        if not (reqValidation(jsons, required_fields) or user_id or user_name):
            resp = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        try:
            myCon = connectDB()
            userCursor = myCon.cursor()

            if user_id:
                userCursor.execute('SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
            elif user_name:
                userCursor.execute('SELECT * FROM "f_user" WHERE "userName" = %s', (user_name,))
                user = userCursor.fetchone()
                if user:
                    user_id = user[0]  # Get the ID from the fetched user

            if not user_id:
                response = {
                    "responseCode": 555,
                    "responseText": "Хэрэглэгч олдсонгүй"
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")

            response = {
                "responseCode": 200,
                "responseText": "Амжилттай"
            }

            columns = [column[0] for column in userCursor.description]
            
            # Fetch user data
            userCursor.execute('SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
            user = userCursor.fetchone()
            undsen_data = {
                columns[index]: column for index, column in enumerate(user)
            }
            response['undsen'] = undsen_data if undsen_data else {}

            # Fetch education data
            userCursor.execute('SELECT * FROM "f_userEdu" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
            columns = [column[0] for column in userCursor.description]
            edu_data = []
            for row in userCursor.fetchall():
                edu_data.append({
                    columns[index]: column for index, column in enumerate(row)
                })
            response['education'] = edu_data

            # Fetch family data
            userCursor.execute('SELECT * FROM "f_userFamily" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
            columns = [column[0] for column in userCursor.description]
            family_data = []
            for row in userCursor.fetchall():
                family_data.append({
                    columns[index]: column for index, column in enumerate(row)
                })
            response['family'] = family_data

            # Fetch additional information data
            userCursor.execute(
                'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id" = %s', (user_id,))
            columns = [column[0] for column in userCursor.description]
            nemelt_row = userCursor.fetchone()
            nemelt_data = {
                columns[index]: column for index, column in enumerate(nemelt_row)
            } if nemelt_row else {}
            response['nemelt'] = nemelt_data

            # Fetch skill data
            userCursor.execute(
                'SELECT * FROM "f_skill" WHERE "userId" = %s', (user_id,))
            columns = [column[0] for column in userCursor.description]
            skill_data = {
                columns[index]: column for index, column in enumerate(userCursor.fetchone())
            } if userCursor.rowcount > 0 else {}
            response['skill'] = skill_data

            # Fetch social data
            userCursor.execute('SELECT * FROM "f_userSocial" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
            columns = [column[0] for column in userCursor.description]
            social_data = []
            for row in userCursor.fetchall():
                social_data.append({
                    columns[index]: column for index, column in enumerate(row)
                })
            response['social'] = social_data

            # Fetch work data
            userCursor.execute('SELECT * FROM "f_userWork" WHERE "user_id" = %s AND "deldate" IS NULL', (user_id,))
            columns = [column[0] for column in userCursor.description]
            work_data = []
            for row in userCursor.fetchall():
                work_data.append({
                    columns[index]: column for index, column in enumerate(row)
                })
            response['work'] = work_data

            userCursor.close()
            disconnectDB(myCon)

            response = json.dumps(response, cls=DjangoJSONEncoder)
            return HttpResponse(response, content_type="application/json")

        except Exception as e:
            traceback.print_exc()  # Print the exception traceback
            response = {
                "responseCode": 555,
                "responseText": "Алдаа гарлаа"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")





################################################################
def tempDel(request):
    jsons = json.loads(request.body)
    if reqValidation(jsons, {"templateId"}) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    try:
        templateId = jsons["templateId"]
        myCon = connectDB()
        templateCursor = myCon.cursor()

        templateCursor.execute(
            'DELETE FROM "f_templates" WHERE "id" = %s', (templateId,)
        )

        if templateCursor.rowcount == 0:
            response = {
                "responseCode": 552,
                "responseText": "Template олдсонгүй"
            }
            templateCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        myCon.commit()
        templateCursor.close()
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
        "responseText": "Template устгагдлаа"
    }
    return HttpResponse(json.dumps(response), content_type="application/json")

#################################################################################
def userTempDel(request):
    jsons = json.loads(request.body)
    if reqValidation(jsons, {"templateId"}) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    try:
        templateId = jsons["templateId"]
        myCon = connectDB()
        templateCursor = myCon.cursor()

        templateCursor.execute(
            'DELETE FROM "f_userTemplates" WHERE "id" = %s', (templateId,)
        )

        if templateCursor.rowcount == 0:
            response = {
                "responseCode": 552,
                "responseText": "Template олдсонгүй"
            }
            templateCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        myCon.commit()
        templateCursor.close()
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
        "responseText": "Template устгагдлаа"
    }
    return HttpResponse(json.dumps(response), content_type="application/json")

###############################################################################
# def uploadTemplateView(request):
#     jsons = json.loads(request.body)

#     required_fields = {"name", "tempTypeId", "catId", "file", "userId"}
#     if reqValidation(jsons, required_fields) == False:
#         resp = {
#             "responseCode": 550,
#             "responseText": "Field-үүд дутуу"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     name = jsons['name']
#     tempTypeId = jsons['tempTypeId']
#     catId = jsons['catId']
#     file = jsons['file']
#     userId = jsons['userId']

#     try:
#         myCon = connectDB()
#         userCursor = myCon.cursor()

#         if not myCon:
#             raise Exception("Can not connect to the database")
#     except Exception as e:
#         resp = {
#             "responseCode": 551,
#             "responseText": "Баазын алдаа"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     # Check if user exists in f_user table
#     userCursor.execute(
#         'SELECT * FROM "f_user" WHERE "id" = %s', (userId,))
#     user = userCursor.fetchone()

#     if not user:
#         resp = {
#             "responseCode": 555,
#             "responseText": "Хэрэглэгч олдсонгүй"
#         }
#         userCursor.close()
#         disconnectDB(myCon)
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     # Check if tempTypeId exists in f_tempType table
#     userCursor.execute(
#         'SELECT * FROM "f_tempType" WHERE "id" = %s', (tempTypeId,))
#     tempType = userCursor.fetchone()

#     if not tempType:
#         resp = {
#             "responseCode": 556,
#             "responseText": "Буруу tempTypeId"
#         }
#         userCursor.close()
#         disconnectDB(myCon)
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     # Check if catId exists in f_catType table
#     userCursor.execute(
#         'SELECT * FROM "f_catType" WHERE "id" = %s', (catId,))
#     catType = userCursor.fetchone()

#     if not catType:
#         resp = {
#             "responseCode": 557,
#             "responseText": "Буруу catId"
#         }
#         userCursor.close()
#         disconnectDB(myCon)
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     userCursor.execute(
#         'INSERT INTO "f_templates"("name", "tempTypeId", "catId", "file", "userId") '
#         'VALUES(%s, %s, %s, %s, %s) RETURNING "id"',
#         (name, tempTypeId, catId, file, userId))

#     templateId = userCursor.fetchone()[0]

#     myCon.commit()

#     userCursor.close()
#     disconnectDB(myCon)

#     resp = {
#         "responseCode": 200,
#         "responseText": "Template нэмэгдлээ",
#         "templateId": templateId
#     }
#     return HttpResponse(json.dumps(resp), content_type="application/json")





############ NEW TEMP FUNCTIONS #########################################
# from datetime import datetime

# def userTemplates(request):
#     jsons = json.loads(request.body)

#     if reqValidation(jsons, {"userId", "name", "tempId"}) == False:
#         resp = {
#             "responseCode": 550,
#             "responseText": "Field-үүд дутуу"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     tempId = jsons['tempId']
#     userId = jsons['userId']
#     name = jsons['name']

#     try:
#         myCon = connectDB()
#         userCursor = myCon.cursor()

#         if not myCon:
#             raise Exception("Can not connect to the database")
#     except Exception as e:
#         resp = {
#             "responseCode": 551,
#             "responseText": "Баазын алдаа"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     # Check if the user exists
#     userCursor.execute(
#         'SELECT * FROM "f_user" WHERE "id" = %s', (userId,))
#     user = userCursor.fetchone()

#     if not user:
#         resp = {
#             "responseCode": 555,
#             "responseText": "Хэрэглэгч олдсонгүй"
#         }
#         userCursor.close()
#         disconnectDB(myCon)
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     # Check if the template exists and is not marked as deleted
#     userCursor.execute(
#         'SELECT * FROM "f_templates" WHERE "id" = %s AND "deldate" IS NULL', (tempId,))
#     template = userCursor.fetchone()

#     if not template:
#         resp = {
#             "responseCode": 556,
#             "responseText": "Template олдсонгүй"
#         }
#         userCursor.close()
#         disconnectDB(myCon)
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     # Insert the template
#     userCursor.execute(
#         'INSERT INTO "f_userTemplates"( "name", "userId", "tempId") '
#         'VALUES (%s, %s, %s) '
#         'RETURNING "id"',
#         (name, userId, tempId))

#     userTempId = userCursor.fetchone()[0]

#     myCon.commit()

#     userCursor.close()
#     disconnectDB(myCon)

#     resp = {
#         "responseCode": 200,
#         "responseText": "Template ашигласан",
#         "userTempId": userTempId
#     }
#     return HttpResponse(json.dumps(resp), content_type="application/json")

#############################################
# def userTempGet(request):
#     jsons = json.loads(request.body)
#     user_id = jsons.get('userId')
    
#     if user_id is None:
#         resp = {
#             "responseCode": 550,
#             "responseText": "Field-үүд дутуу"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     if request.method == 'GET':
#         myCon = connectDB()
#         userCursor = myCon.cursor()
#         userCursor.execute(
#             'SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
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
#             # Modify the SQL query to include deldate logic
#             userCursor.execute(
#                 'SELECT * FROM "f_userTemplates" WHERE "userId" = %s AND "deldate" IS NULL', (user_id,))
#             columns = [column[0] for column in userCursor.description]
#             response = [
#                 {columns[index]: column for index, column in enumerate(
#                     value) if columns[index] not in []}
#                 for value in userCursor.fetchall()
#             ]
#             userCursor.close()
#             disconnectDB(myCon)
#             responseJSON = {"tempData": response}
#             response = {
#                 "responseCode": 200,
#                 "responseText": "Амжилттай",
#                 **responseJSON
#             }
#             return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")

#         else:
#             resp = {
#                 "responseCode": 551,
#                 "responseText": "Баазын алдаа"
#             }
#             return HttpResponse(json.dumps(resp), content_type="application/json")

#     response = {
#         "responseCode": 200,
#         "responseText": "Амжилттай",
#         "tempData": {}
#     }
#     return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")
########################
# def tempGet(request):
#     jsons = json.loads(request.body)
#     user_id = jsons.get('id')
#     if user_id is None:
#         resp = {
#             "responseCode": 550,
#             "responseText": "Field-үүд дутуу"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     if request.method == 'GET':
#         myCon = connectDB()
#         userCursor = myCon.cursor()
#         # Modify the SQL query to include deldate logic
#         userCursor.execute(
#             'SELECT * FROM "f_templates" WHERE "id" = %s AND "deldate" IS NULL', (user_id,))
#         columns = [column[0] for column in userCursor.description]
#         response = [
#             {columns[index]: column for index, column in enumerate(
#                 value) if columns[index] not in []}
#             for value in userCursor.fetchall()
#         ]
#         userCursor.close()
#         disconnectDB(myCon)

#         if not response:
#             resp = {
#                 "responseCode": 555,
#                 "responseText": "Тэмплэт олдсонгүй"
#             }
#             return HttpResponse(json.dumps(resp), content_type="application/json")

#         responseJSON = {"tempData": response}
#         response = {
#             "responseCode": 200,
#             "responseText": "Амжилттай",
#             **responseJSON
#         }
#         return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")

###################################
# def tempDel(request):
#     jsons = json.loads(request.body)
#     if reqValidation(jsons, {"templateId"}) == False:
#         resp = {
#             "responseCode": 550,
#             "responseText": "Field-үүд дутуу"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     try:
#         templateId = jsons["templateId"]
#         myCon = connectDB()
#         templateCursor = myCon.cursor()

#         # Update the DELDATE column instead of physically deleting the row
#         templateCursor.execute(
#             'UPDATE "f_templates" SET "deldate" = NOW() WHERE "id" = %s', (templateId,)
#         )

#         if templateCursor.rowcount == 0:
#             response = {
#                 "responseCode": 552,
#                 "responseText": "Template олдсонгүй"
#             }
#             templateCursor.close()
#             disconnectDB(myCon)
#             return HttpResponse(json.dumps(response), content_type="application/json")

#         myCon.commit()
#         templateCursor.close()
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
#         "responseText": "Template устгагдлаа"
#     }
#     return HttpResponse(json.dumps(response), content_type="application/json")
################################
# def userTempDel(request):
#     jsons = json.loads(request.body)
#     if reqValidation(jsons, {"templateId"}) == False:
#         resp = {
#             "responseCode": 550,
#             "responseText": "Field-үүд дутуу"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")

#     try:
#         templateId = jsons["templateId"]
#         myCon = connectDB()
#         templateCursor = myCon.cursor()

#         # Update the DELDATE column instead of physically deleting the row
#         templateCursor.execute(
#             'UPDATE "f_userTemplates" SET "deldate" = NOW() WHERE "id" = %s', (templateId,)
#         )

#         if templateCursor.rowcount == 0:
#             response = {
#                 "responseCode": 552,
#                 "responseText": "Template олдсонгүй"
#             }
#             templateCursor.close()
#             disconnectDB(myCon)
#             return HttpResponse(json.dumps(response), content_type="application/json")

#         myCon.commit()
#         templateCursor.close()
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
#         "responseText": "Template устгагдлаа"
#     }
#     return HttpResponse(json.dumps(response), content_type="application/json")
