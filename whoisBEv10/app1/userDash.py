import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *

def getDashboardInfoView(request):
    if request.method == "GET" or request.method == "POST":
        jsons = checkJson(request)
        if reqValidation(jsons, {"user_id"}) == False:        
            resp = aldaaniiMedegdel(550, "Field дутуу байна.")
            return HttpResponse(json.dumps(resp), content_type="application/json")
        userId = jsons.get('user_id')

        conn = None
        try:
            conn = connectDB()
            cur = conn.cursor()
            cur.execute(
                """SELECT balance, "userName", "firstName" FROM "f_user" WHERE "id" = %s""", [userId,])
            user = cur.fetchone()
            dansniiUldegdel = user[0]
            userName = user[1]
            lastName = user[2]
            if not dansniiUldegdel:
                response = aldaaniiMedegdel(553, "Бүртгэлгүй хэрэглэгч байна.")
            response = {
                "responseCode": 200,
                "responseText": "Амжилттай хэрэглэгчийн мэдээллийг илгээлээ.",
                "dansniiUldegdel": dansniiUldegdel,
                "userName": userName,
                "lastName": lastName
            }
            cur.close()
        
        except Exception as e:
            response = aldaaniiMedegdel(580, "Баазын алдаа.")
        finally:
            if conn is not None:                
                disconnectDB(conn)
    else:
        response = aldaaniiMedegdel(400, "Хүлээн авах боломжгүй хүсэлт байна.")
    return HttpResponse(json.dumps(response), content_type="application/json")
################################################################################

def insertComplainView(request):
    jsonsData = json.loads(request.body)
    response = {}
    if (reqValidation(jsonsData, {"id", "text"}) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна.")
        responseJSON = json.dumps(response)
        return HttpResponse(responseJSON, content_type="application/json")
    user_id = jsonsData["id"]
    text = jsonsData["text"]
    try:
        # db холболт
        myCon = connectDB()
        userCursor = myCon.cursor()
        # user_id-гаар нь хайгаад бүх мэдээллийн авах
        userCursor.execute("""INSERT INTO "f_complain"("userId", text) VALUES(%s, %s)""", (user_id, text,))
        myCon.commit()
        # db salalt
        userCursor.close()
        disconnectDB(myCon)
    except Exception as e:
        response = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(response), content_type="application/json")
    finally:
        disconnectDB(myCon)
    response = aldaaniiMedegdel(200, "Амжилттай бүртгэгдлээ.")
    return HttpResponse(json.dumps(response), content_type="application/json")
#################################################################################   

def getComplainView(request):
    jsonsData = json.loads(request.body)
    response = {}
    user_id = jsonsData["id"]
    text = jsonsData["text"]
    try:
        # db холболт
        myCon = connectDB()
        userCursor = myCon.cursor()
        # user_id-гаар нь хайгаад бүх мэдээллийн авах
        userCursor.execute("""SELECT * FROM f_complain""")
        columns = [column[0] for column in userCursor.description]
        data = userCursor.fetchall()
        for i in range(0, len(data)):
            diki = {}
            for j in range(0, len(data[i])):
                diki[columns[j]] = data[i][j]
            data[i] = diki
        # data = list(data)
        myCon.commit()
        # db salalt
        userCursor.close()
        disconnectDB(myCon)
    except Exception as e:
        response = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(response), content_type="application/json")
    finally:
        disconnectDB(myCon)
    response = aldaaniiMedegdel(200, "Амжилттай бүртгэгдлээ.")
    response["data"] = data
    return HttpResponse(json.dumps(response), content_type="application/json")
#################################################################################   
