import traceback
import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
from django.db import connection


def getUserSkillView(request):
    jsonsData = json.loads(request.body)
    response = {}
    if (reqValidation(jsonsData, {"user_id"}) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна.")
        responseJSON = json.dumps(response)
        return HttpResponse(responseJSON, content_type="application/json")
    user_id = jsonsData["user_id"]
    try:
        # db холболт
        myCon = connectDB()
        userCursor = myCon.cursor()
        # user_id-гаар нь хайгаад бүх мэдээллийн авах
        userCursor.execute(
            'SELECT "id", "chadvarNer", "s_Tuvshin" FROM "f_userSkill" WHERE "user_id" = %s', (user_id,))
        user = userCursor.fetchall()
        # Хэрэглэч байгаа үгүйг шалгах
        if not user:
            resp = aldaaniiMedegdel(
                553, "Тухайн хэрэглэгч одоогоор ур чадварын тухай мэдээлэл оруулаагүй байна.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # list хэлбэрээр авах
        skills = []
        for data in user:
            skills.append(list(data))
        # db salalt
        userCursor.close()
        disconnectDB(myCon)
    except Exception as e:
        response = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(response), content_type="application/json")
    finally:
        disconnectDB(myCon)
    allInfo = []
    for data in skills:
        # data = list(data)
        chadvar = {}
        chadvar["id"] = data[0]
        chadvar["chadvariinNer"] = data[1]
        chadvar["chadvariinTuvshin"] = data[2]
        allInfo.append(chadvar)

    response = aldaaniiMedegdel(
        200, "Амжилттай чадварын тухай мэдээллүүдийг илгээв.")
    response["skills"] = allInfo
    return HttpResponse(json.dumps(response), content_type="application/json")
######################################################################
def setUserSkillView(request):
    jsonsData = json.loads(request.body)
    response = {}
    user_id = jsonsData["user_id"]
    skills = jsonsData["skills"]
    ustgasan = 0
    nemsen = 0
    # db холболт
    myCon = connectDB()
    userCursor = myCon.cursor()
    # user_id-гаар нь хайгаад бүх мэдээллийн авах
    userCursor.execute(
        'SELECT * FROM "f_userSkill" WHERE "user_id" = %s', (user_id,))
    user = userCursor.fetchall()
    myCon.commit()
    # table-д ур чадвар байгаа үгүйг шалгах
    if not user:
        response = aldaaniiMedegdel(
            553, "Тухайн хэрэглэгч одоогоор ур чадварын тухай мэдээлэл оруулаагүй байна.")
        userCursor.close()
        disconnectDB(myCon)
        return HttpResponse(json.dumps(response), content_type="application/json")
    # list хэлбэрээр авах
    allInfo = []
    for data in user:
        data = list(data)
        chadvar = {}
        chadvar["id"] = data[0]
        chadvar["chadvariinNer"] = data[1]
        chadvar["chadvariinTuvshin"] = data[2]
        allInfo.append(chadvar)
    # "skills" not in jsonsData
    for data in skills:
        if not data["id"]:
            id = ""
        else:
            id = data["id"]
        if not data["chadvariinNer"]:
            name = ""
        else:
            name = data["chadvariinNer"]
        if not data["chadvariinTuvshin"]:
            tuvshin = ""
        else:
            tuvshin = data["chadvariinTuvshin"]
        # print(str(id) + ' ' + name + ' ' + tuvshin)
        if not id:
            userCursor.execute(
                'INSERT INTO "f_userSkill"("chadvarNer", "s_Tuvshin", "user_id") VALUES(%s, %s, %s) RETURNING "id"', (name, tuvshin, int(user_id),))
            id = userCursor.fetchone()[0]
            # print(id)
            myCon.commit()
            allInfo.append({"id": id, "chadvariinNer": name,
                           "chadvariinTuvshin": tuvshin})
            nemsen += 1
        elif (not tuvshin) or (not name):
            userCursor.execute(
                'DELETE FROM "f_userSkill" WHERE "id"= %s', (int(id),))
            myCon.commit()
            userCursor.execute(
                'SELECT * FROM "f_userSkill" WHERE "user_id" = %s', (user_id,))
            user = userCursor.fetchall()
            myCon.commit()
            allInfo = []
            for data in user:
                data = list(data)
                chadvar = {}
                chadvar["id"] = data[0]
                chadvar["chadvariinNer"] = data[1]
                chadvar["chadvariinTuvshin"] = data[2]
                allInfo.append(chadvar)
            ustgasan += 1
    userCursor.close()
    disconnectDB(myCon)
    response = aldaaniiMedegdel(
        200, "Амжилттай чадварын тухай мэдээллүүдийг шинэчлэлээ.")
    response["ustgasan"] = ustgasan
    response["nemsen"] = nemsen
    return HttpResponse(json.dumps(response), content_type="application/json")
###############################################################
def getSkillView(request):
    jsonsData = json.loads(request.body)
    response = {}
    if (reqValidation(jsonsData, {"id"}) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна.")
        responseJSON = json.dumps(resp)
        return HttpResponse(responseJSON, content_type="application/json")
    user_id = jsonsData["id"]
    try:
        # db холболт
        myCon = connectDB()
        userCursor = myCon.cursor()
        # user_id-гаар нь хайгаад бүх мэдээллийн авах
        userCursor.execute(
            'SELECT "id", "chadvarNer" FROM "f_skill" WHERE "userId" = %s', (user_id,))
        user = userCursor.fetchone()
        # Хэрэглэч байгаа үгүйг шалгах
        if not user:
            text = ""
            userCursor.execute(
                'INSERT INTO "f_skill"("userId", "chadvarNer") VALUES(%s, %s) RETURNING "id"', (user_id, text,))
            idd = userCursor.fetchone()
            myCon.commit()
            resp = aldaaniiMedegdel(
                553, "Хэрэглэгчийн чадварын тухай мэдээллийг шинээр үүсгэлээ.")
            resp["skill"] = text
            resp["id"] = idd[0]
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # db salalt
        userCursor.close()
        disconnectDB(myCon)
    except Exception as e:
        response = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(response), content_type="application/json")
    finally:
        disconnectDB(myCon)
    response = aldaaniiMedegdel(
        200, "Амжилттай чадварын тухай мэдээллүүдийг илгээв.")
    response["skill"] = user[1]
    response["id"] = user[0]
    return HttpResponse(json.dumps(response), content_type="application/json")
###############################################
def setSkillView(request):
    jsonsData = json.loads(request.body)
    response = {}
    if (reqValidation(jsonsData, {"id", "skill"}) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна.")
        responseJSON = json.dumps(resp)
        return HttpResponse(responseJSON, content_type="application/json")
    user_id = jsonsData["id"]
    skill = jsonsData["skill"]
    try:
        # db холболт
        myCon = connectDB()
        userCursor = myCon.cursor()
        # user_id-гаар нь хайгаад бүх мэдээллийн авах
        userCursor.execute(
            'SELECT "id", "chadvarNer" FROM "f_skill" WHERE "userId" = %s', (user_id,))
        user = userCursor.fetchone()
        # Хэрэглэч байгаа үгүйг шалгах
        if not user:
            text = ""
            userCursor.execute(
                'INSERT INTO "f_skill"("userId", "chadvarNer") VALUES(%s, %s) RETURNING "id"', (user_id, skill,))
            idd = userCursor.fetchone()
            myCon.commit()
            resp = aldaaniiMedegdel(
                553, "Хэрэглэгчийн чадварын тухай мэдээллийг шинээр үүсгэлээ.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        userCursor.execute(
            'UPDATE "f_skill" SET "chadvarNer" = %s WHERE "userId" = %s', (skill, int(user_id),))
        myCon.commit()
        # db salalt
        userCursor.close()
        disconnectDB(myCon)
    except Exception as e:
        response = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(response), content_type="application/json")
    finally:
        disconnectDB(myCon)
    response = aldaaniiMedegdel(
        200, "Амжилттай чадварын мэдээллийг шинэчлэлээ.")
    return HttpResponse(json.dumps(response), content_type="application/json")