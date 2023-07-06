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