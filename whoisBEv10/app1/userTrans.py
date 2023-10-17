import traceback
import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
from django.db import connection
import pytz
import datetime


def getTransactionLog(request):
    if request.method == "GET" or request.method == "POST":
        jsons = checkJson(request)
        if reqValidation(jsons, {"user_id"}) == False:
            resp = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        userId = jsons.get('user_id')

        conn = None
        try:
            conn = connectDB()
            cur = conn.cursor()
            cur.execute(
                """SELECT balance FROM "f_user" WHERE "id" = %s""", [userId,])
            dansniiUldegdel = cur.fetchall()
            cur.execute(
                """SELECT "userName" FROM "f_user" WHERE "id" = %s""", [userId,])
            name = cur.fetchone()[0]
            if not dansniiUldegdel:
                response = aldaaniiMedegdel(553, "Бүртгэлгүй хэрэглэгч байна.")
            else:
                cur.execute("""select * from \"f_transactionLog\" where "from"=%s or "to"=%s """, [name, name])
                columns = cur.description
                guilgee = [{columns[index][0]: column for index, column in enumerate(
                    value)} for value in cur.fetchall()]                
                
                for i in range(0, len(guilgee)):
                    guilgee[i]['date']=str(guilgee[i]['date'])
                response = {
                    "responseCode": 200,
                    "responseText": "Амжилттай дансны мэдээлэл харлаа.",
                    "dansniiUldegdel": dansniiUldegdel[0][0],
                    "guilgee": guilgee
                }
            cur.close()
        
        except Exception as e:
            response = {
                "responseCode": 588,
                "responseText": "Баазын алдаа",
                # "data": str(e)
            }
        finally:
            if conn is not None:                
                disconnectDB(conn)
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }        
    return HttpResponse(json.dumps(response), content_type="application/json")


def makeTransactionView(request):
    if request.method == "POST":
        jsons = checkJson(request)
        if reqValidation(jsons, {"from", "target", "amount",}) == False:
            resp = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        userId = jsons["from"]
        targetUserName = jsons["target"]
        amount = jsons["amount"]
        try:
            conn = connectDB()
            cur = conn.cursor()
            cur.execute("""SELECT balance, "userName" FROM "f_user" WHERE "id" = %s""", [userId,])
            user = cur.fetchone()
            fromBalance = user[0]
            userName = user[1]
            name = user[1]
            cur.execute("""SELECT balance FROM "f_user" WHERE "userName" = %s""", [targetUserName,])
            targetBalance = cur.fetchone()[0]
       
            if fromBalance is None or targetBalance is None: 
                resp = {
                    "responseCode": 588,
                    "responseText": "Хэрэглэгчийн мэдээлэл олдсонгүй .",
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")
            if ((targetBalance is None) or (fromBalance < int(amount)) or (0 > int(amount))):
                resp = {
                    "responseCode": 555,
                    "responseText": "Таны дансны үлдэгдэл хүрэлцэхгүй байна.",
                    "data": fromBalance
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")
            cur.execute("""UPDATE f_user SET balance = balance + %s WHERE "userName" = %s RETURNING "userName", balance""", [amount, targetUserName,])
          
            targetData = cur.fetchone()
         
            conn.commit()
            cur.execute("""UPDATE f_user SET balance = balance - %s WHERE "userName" = %s RETURNING "userName", balance""", [amount, userName,])
            fromData = cur.fetchone()
            cur.execute("""INSERT INTO "f_transactionLog"(amount, balance, "from", "to") VALUES (%s, %s, %s, %s)""",
                        [int(amount), int(fromData[1]), userName, targetUserName,])
            conn.commit()
            resp = {
                "responseCode": 200,
                "responseText": "Амжилттай шилжлээ.",  
                "data" : {
                    'from': fromData,
                    'target': targetData
                }
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        except Exception as e:
            resp = {
                "responseCode": 500,
                "responseText": "Алдаа гарлаа",
                "data" : str(e)
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        finally:
            if conn is not None:
                disconnectDB(conn)
    else:
        resp = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
    ##### admin make transaction

def adminTransactionView(request):
    if request.method == "POST":
        jsons = checkJson(request)
        if reqValidation(jsons, {"target", "amount"}) == False:
            resp = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        targetUserName = jsons["target"]
        amount = jsons["amount"]
        try:
            conn = connectDB()
            cur = conn.cursor()
            cur.execute("""SELECT balance FROM "f_user" WHERE "userName" = %s""", [targetUserName])
            targetBalance = cur.fetchone()

            if targetBalance is None:
                resp = {
                    "responseCode": 588,
                    "responseText": "Хэрэглэгчийн мэдээлэл олдсонгүй .",
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")

            cur.execute("""UPDATE f_user SET balance = balance + %s WHERE "userName" = %s RETURNING "userName", balance""",
                        [amount, targetUserName])
            targetData = cur.fetchone()

            cur.execute("""INSERT INTO "f_adminTransactionLog" (amount, balance, "to") VALUES (%s, %s, %s)""",
                        [int(amount), int(targetBalance[0]), targetUserName])
            conn.commit()

            resp = {
                "responseCode": 200,
                "responseText": "Амжилттай шилжлээ.",
                "data": {
                    'target': targetData
                }
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        except Exception as e:
            resp = {
                "responseCode": 500,
                "responseText": "Алдаа гарлаа",
                "data": str(e)
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        finally:
            if conn is not None:
                disconnectDB(conn)

    else:
        resp = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

#########admin transaction log
def getAdminTransactionLog(request):
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT * FROM "f_adminTransactionLog" ORDER BY id ASC')
    columns = userCursor.description
    response = [{columns[index][0]: column for index,
                 column in enumerate(value)} for value in userCursor.fetchall()]
    userCursor.close()
    disconnectDB(myCon)
    for item in response:
        if 'created_at' in item:
            item['created_at'] = item['created_at'].astimezone(
                pytz.utc).replace(tzinfo=None)
    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")

