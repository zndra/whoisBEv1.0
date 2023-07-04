import json
from django.http import HttpResponse
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
from django.db import connection
import json

def uploadTemplateView(request):
    jsons = json.loads(request.body)

    if reqValidation(jsons, {"name", "tempTypeId", "catId", "file", "userId"}) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    name = jsons['name']
    tempTypeId = jsons['tempTypeId']
    catId = jsons['catId']
    file = jsons['file']
    userId = jsons['userId']

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

    # Check if user exists in f_user table
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

    userCursor.execute(
        'INSERT INTO "f_templates"("name", "tempTypeId", "catId", "file", "userId") '
        'VALUES(%s, %s, %s, %s, %s) RETURNING "id"',
        (name, tempTypeId, catId, file, userId))

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

    # Insert the template
    userCursor.execute(
        'INSERT INTO "f_userTemplates"( "name", "userId", "tempId") '
        'VALUES (%s, %s, %s) '
        'RETURNING "id"',
        (name, userId, tempId))

    tempId = userCursor.fetchone()[0]

    myCon.commit()

    userCursor.close()
    disconnectDB(myCon)

    resp = {
        "responseCode": 200,
        "responseText": "Template ашигласан",
        "tempId": tempId
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
                'SELECT * FROM "f_templates" WHERE "userId" = %s', (user_id,))
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
    user_id = jsons['id']

    if request.method == 'GET':
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

            elif user:
                userCursor.execute(
                    'SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
                columns = [column[0] for column in userCursor.description]
                response = {
                    "responseCode": 200,
                    "responseText": "Амжилттай",
                    **{
                        columns[index]: column for index, column in enumerate(user) if columns[index] not in ['verifyCode', 'newPass', 'deldate', 'pass']
                    }
                }

                userCursor.execute(
                    'SELECT * FROM "f_userEdu" WHERE "user_id" = %s', (user_id,))
                columns = [column[0] for column in userCursor.description]
                edu_data = {
                    columns[index]: column for index, column in enumerate(userCursor.fetchone())
                }
                response['education'] = edu_data

                userCursor.execute(
                    'SELECT * FROM "f_userFamily" WHERE "user_id" = %s', (user_id,))
                columns = [column[0] for column in userCursor.description]
                family_data = {
                    columns[index]: column for index, column in enumerate(userCursor.fetchone())
                }
                response['family'] = family_data

                userCursor.execute(
                    'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id" = %s', (user_id,))
                columns = [column[0] for column in userCursor.description]
                nemelt_data = {
                    columns[index]: column for index, column in enumerate(userCursor.fetchone())
                }
                response['nemelt_medeelel'] = nemelt_data

                userCursor.execute(
                    'SELECT * FROM "f_userSkill" WHERE "user_id" = %s', (user_id,))
                columns = [column[0] for column in userCursor.description]
                skill_data = {
                    columns[index]: column for index, column in enumerate(userCursor.fetchone())
                }
                response['skill'] = skill_data

                userCursor.execute(
                    'SELECT * FROM "f_userSocial" WHERE "user_id" = %s', (user_id,))
                columns = [column[0] for column in userCursor.description]
                social_data = {
                    columns[index]: column for index, column in enumerate(userCursor.fetchone())
                }
                response['social'] = social_data

                userCursor.execute(
                    'SELECT * FROM "f_userWork" WHERE "user_id" = %s', (user_id,))
                columns = [column[0] for column in userCursor.description]
                work_data = {
                    columns[index]: column for index, column in enumerate(userCursor.fetchone())
                }
                response['work'] = work_data

                userCursor.close()
                disconnectDB(myCon)

                response = json.dumps(response, cls=DjangoJSONEncoder)
                return HttpResponse(response, content_type="application/json")

        except Exception as e:
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

