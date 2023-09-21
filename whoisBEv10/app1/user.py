import traceback
import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
from django.db import connection
import pytz
import datetime

# ene debug uyed ajillah yostoi
def userListView(request):
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT * FROM "f_user" ORDER BY id ASC')
    columns = userCursor.description
    response = [{columns[index][0]: column for index,
                 column in enumerate(value)} for value in userCursor.fetchall()]
    userCursor.close()
    disconnectDB(myCon)
# Convert timezone-aware time objects to timezone-naive time objects
    for item in response:
        if 'created_at' in item:
            item['created_at'] = item['created_at'].astimezone(
                pytz.utc).replace(tzinfo=None)
    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")
#   userListView

def userLoginView(request):
    jsons = json.loads(request.body)
    if (reqValidation(jsons, {"name", "pass", }) == False):
        resp = {}
        resp["responseCode"] = 550
        resp["responseText"] = "Field-үүд дутуу"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    myName = jsons['name']
    myPass = jsons['pass']
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute("SELECT \"id\",\"userName\",\"firstName\",\"lastName\",\"email\" "
                   "FROM f_user "
                   "WHERE "
                   "deldate IS NULL AND "
                   "pass = %s AND "
                   "\"isVerified\" = true AND "
                   "\"userName\" = %s",
                   (
                       myPass,
                       myName,
                   ))

        columns = userCursor.description
        response = [{columns[index][0]: column for index, column in enumerate(
            value)} for value in userCursor.fetchall()]
        userCursor.close()
    except Exception as e:
        resp = {}
        resp["responseCode"] = 551
        resp["responseText"] = "Баазын алдаа"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    finally:
        disconnectDB(myCon)
    responseCode = 521  # login error
    responseText = 'Буруу нэр/нууц үг'
    responseData = []

    if len(response) > 0:
        responseCode = 200
        responseText = 'Зөв нэр/нууц үг байна хөгшөөн'
        responseData = response[0]
    resp = {}
    resp["responseCode"] = responseCode
    resp["responseText"] = responseText
    resp["userData"] = responseData
    resp["Сургууль"] = {}
    resp["Сургууль"]["Нэр"] = "Мандах"
    resp["Сургууль"]["Хаяг"] = "3-р хороолол"

    return HttpResponse(json.dumps(resp), content_type="application/json")

#   userLoginView end#########################################################
# def userRegisterView(request):
#     jsons = json.loads(request.body)
#     # Validate request body
#     if reqValidation(jsons, {"firstName", "lastName", "email", "pass", "userName"}) == False:
#         resp = {
#             "responseCode": 550,
#             "responseText": "Field-үүд дутуу"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#     firstName = jsons['firstName']
#     lastName = jsons['lastName']
#     email = jsons['email']
#     password = jsons['pass']
#     username = jsons['userName']
#     try:
#         myCon = connectDB()
#         userCursor = myCon.cursor()

#         if emailExists(email):
#             resp = {
#                 "responseCode": 400,
#                 "responseText": "Бүртгэлтэй email байна."
#             }
#             return HttpResponse(json.dumps(resp), content_type="application/json")

#         if userNameExists(username):
#             resp = {
#                 "responseCode": 400,
#                 "responseText": "Бүртгэлтэй хэрэглэгчийн нэр байна."
#             }
#             return HttpResponse(json.dumps(resp), content_type="application/json")

#         if not myCon:
#             raise Exception("Can not connect to the database")
#     except Exception as e:
#         resp = {
#             "responseCode": 551,
#             "responseText": "Баазын алдаа"
#         }
#         return HttpResponse(json.dumps(resp), content_type="application/json")
#     userCursor.execute(
#         'INSERT INTO "f_user"("firstName", "lastName", "email", "pass", "userName", "deldate", "usertypeid") '
#         'VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING "id"',
#         (firstName, lastName, email, password, username, None, 2,))
#     userId = userCursor.fetchone()[0]
#     # Add user ID to other tables
#     current_date = datetime.date.today()
#     date = current_date.strftime("%m/%d/%Y")
#     userCursor.execute(
#         'INSERT INTO "f_userNemeltMedeelel"("user_id", "huis", "torsonOgnoo") VALUES(%s,%s,%s)',
#         (userId,1,date))
#     myCon.commit()
#     # Close the userCursor and disconnect from the database
#     userCursor.close()
#     disconnectDB(myCon)

#     # Return success response
#     resp = {
#         "responseCode": 200,
#         "responseText": "Амжилттай бүртгэгдлээ"
#     }
#     return HttpResponse(json.dumps(resp), content_type="application/json")
######################################
def userRegisterView(request):
    jsons = json.loads(request.body)
    if reqValidation(jsons, {"firstName", "lastName", "email", "pass", "userName"}) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    firstName = jsons['firstName']
    lastName = jsons['lastName']
    email = jsons['email']
    password = jsons['pass']
    username = jsons['userName']

    try:
        myCon = connectDB()
        if not myCon:
            raise Exception("Can not connect to the database")

        userCursor = myCon.cursor()

        if emailExists(email):
            resp = {
                "responseCode": 400,
                "responseText": "Бүртгэлтэй email байна."
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        if userNameExists(username):
            resp = {
                "responseCode": 400,
                "responseText": "Бүртгэлтэй хэрэглэгчийн нэр байна."
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        userCursor.execute(
            'INSERT INTO "f_user"("firstName", "lastName", "email", "pass", "userName", "deldate", "usertypeid") '
            'VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING "id"',
            (firstName, lastName, email, password, username, None, 2,))
        userId = userCursor.fetchone()[0]

        current_date = datetime.date.today()
        date = current_date.strftime("%m/%d/%Y")
        userCursor.execute(
            'INSERT INTO "f_userNemeltMedeelel"("user_id", "huis", "torsonOgnoo") VALUES(%s,%s,%s)',
            (userId, 1, date))

        verification_code = createCodes(6)
        userCursor.execute(
            'INSERT INTO "f_otp"("userId", "value") VALUES(%s, %s)',
            (userId, verification_code)
        )
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)

        verifyEmailSubject = "WhoIs: Имэйл баталгаажуулах"
        verifyEmailContent = f"Та манай системд бүртгүүлсэн байна, {username}. \n\n Доорх холбоос дээр дарж бүртгэлээ баталгаажуулна уу!\n\n"
        verifyEmailLink = f"http://whois.mandakh.org/emailVerify/{verification_code}"

        sendMail(email, verifyEmailSubject, verifyEmailContent + verifyEmailLink)
        
        resp = {
            "responseCode": 200,
            "responseText": "Амжилттай бүртгэгдлээ. Баталгаажуулах имэйл илгээгдлээ.",
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    except Exception as e:
        print(f"Error: {str(e)}")  
        resp = {
            "responseCode": 551,
            "responseText": "Баазын алдаа"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")
######################################################################################

# Verify email view
def verifyEmailView(request, otp):
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute(
            'SELECT "userId" FROM "f_otp" WHERE "value" = %s', (otp,))
        result = userCursor.fetchone()

        if result:
            userId = result[0]
            userCursor.execute(
                'UPDATE "f_user" SET "isVerified" = TRUE WHERE "id" = %s', (userId,))
            myCon.commit()
            userCursor.close()
            disconnectDB(myCon)
            resp = {
                "responseCode": 200,
                "responseText": "Email амжилттай баталгаажлаа",
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        else:
            userCursor.close()
            disconnectDB(myCon)
            resp = {
                "responseCode": 400,
                "responseText": "Буруу эсвэл ашиглах боломжгүй холбоос байна",
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
    except Exception as e:
        resp = {
            "responseCode": 400,
            "responseText": "Баталгаажуулах үед алдаа гарлаа",
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

###################################################################################
# Flog
def fLog(request):
    f_log("test", "test")
    resp = {}
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute(
            'SELECT * FROM f_log')
        result = userCursor.fetchall()
        # table-д мэдээлэл байхгүй үед
        if not result:
            response = aldaaniiMedegdel(553, "Одоогоор мэдээлэл оруулаагүй байна.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")
        datas = []
        for data in result:
            data = list(data)
            chadvar = {}
            chadvar["id"] = data[0]
            chadvar["user_id"] = data[4]
            chadvar["request_body"] = data[1]
            chadvar["response_body"] = data[2]
            chadvar["ognoo"] = str(data[3])
            # print(data[3])
            # chadvar["ognoo"] = data[3]
            datas.append(chadvar)
        resp = aldaaniiMedegdel(
            200, "Амжилттай.")
        resp["data"] = datas
        if result:
            myCon.commit()
            userCursor.close()
            disconnectDB(myCon)
    except Exception as e:
        print("error")
        response = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(response), content_type="application/json")
    return HttpResponse(json.dumps(resp), content_type="application/json")
###################################################################################
# f_log
def f_log(request_body, response_body):
    print("1111111111111")
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute('INSERT INTO f_log(request_body, response_body, ognoo) VALUES(%s, %s, default)', (request_body, response_body))
        # result = userCursor.fetchall()
        # print(result)
        # if result:
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)
        print( "Амжилттай бүртгэгдлээ")
    except Exception as e:
        print ("Амжилтгүй")
        print(e)
###################################################################################


def forgetPass(request):
    jsons = json.loads(request.body)
    email = jsons['email']

    # Validate request body
    if reqValidation(jsons, {"email"}) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    if request.method == 'POST':
        try:
            # Check if the email exists in the database
            if runQuery('SELECT email FROM f_user WHERE email=%s', (email,)):
                sendMail(email,
                         'Reset Password',
                         'https://www.facebook.com/recover/initiate/?ldata=AWe3DyZjElBs5PGSw6BbaSjaPZm49o3OoUm7YM5HvpnAeNfxn-6QADMiYkZP0JDAohjE5d8M_2f8fGwFyMICZhAQX1ehnOiC4xur9Lqn7QqrTPld7YQqzfaDA9EE1xQBwWhQ26A-vXt07-h3qZkn6uCgNxKSaURadprdJ9aQqvjypi8SqPus5wyasseqpnYqgb_k_T-mgxm2E30qlG_s0SQa_3lGdbKdm0ibnh1aYEPMWdVVwLq5J3U9ExYVBnKWWSJfJvZHpCCAPdTApc6jIc9t'
                         )

            response = {
                "responseCode": 555,
                "responseText": "Амжилттай "
            }
        except Exception as e:
            response = {
                "responseCode": 551,
                "responseText": "Алдаа гарлаа"
            }

    return HttpResponse(json.dumps(response), content_type="application/json")

#### Change password ########################################################
def changePass(request):
    jsons = json.loads(request.body)

    # Validate request body
    required_fields = ["id", "oldpass", "newpass"]
    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Буруу хүсэлт"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    id = jsons['id']
    oldpass = jsons['oldpass']
    newpass = jsons['newpass']

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        # Check if the user exists
        userCursor.execute(
            'SELECT * FROM "f_user" WHERE "id" = %s AND "pass" = %s', (id, oldpass))
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
        userCursor.execute(
            'UPDATE "f_user" SET "pass" = %s WHERE "id" = %s', (newpass, id))
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
        "responseText": "Password амжилттай солигдлоо"
    }
    return HttpResponse(json.dumps(response), content_type="application/json")

#######################################################################################

# Солих нууц үгийг хадгалж авч имэйл рүү нь баталгаажуулах код илгээх функц
def resetPasswordView(request):
    jsonsData = json.loads(request.body)
    # Хэрэв мэдээлэл дутуу байвал алдааны мэдээлэл дамжуулах
    if (reqValidation(jsonsData, {"newPassword", "email"}) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна")
        return HttpResponse(json.dumps(resp), content_type="application/json")

    email = jsonsData["email"]
    newPassword = jsonsData["newPassword"]
    print(newPassword)
    verifyCode = createCodes(10)  # Batalgaajuulakh codenii urt ni 10

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        # email баталгаажсан нь DB дээр байгаа эсэхийг уншиж байна.
        userCursor.execute(
            'SELECT "id" FROM "f_user" WHERE  "email" = %s AND  "isVerified" = true', (email,))
        user = userCursor.fetchone()
        # Хэрэглэч байгаа үгүйг шалгах
        if (not user) or (user is None):
            resp = aldaaniiMedegdel(
                553, "Уг email хаягтай хэрэглэгч олдсонгүй.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        userId = user[0]
        # Email илгээх
        mailSubject = "Баталгаажуулах код"
        mailContent = f"Нууц үг сэргээх баталгаажуулах код:\n\n{verifyCode}"
        sendMail(email, mailSubject, mailContent)
        # verifyCode болон newPass-ийг өөрчлөх
        userCursor.execute(
            'SELECT * FROM "f_resetPassword" WHERE "userId" = %s', (userId,))
        user = userCursor.fetchone()
        # Хэрэв хүснэгтэнд байхгүй бол шинээр үүсгэх. Байвал өөрчлөх
        if (not user) or (user is None):
            userCursor.execute(
                'INSERT INTO "f_resetPassword" ("newPass", "verifyCode", "userId") VALUES (%s, %s, %s)', (str(newPassword), verifyCode, userId,))
        else:
            userCursor.execute(
                'UPDATE "f_resetPassword" SET "newPass" = %s, "verifyCode" = %s WHERE "userId" = %s', (str(newPassword), verifyCode, userId,))
        myCon.commit()
        userCursor.close()

    except Exception as e:
        resp = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(resp), content_type="application/json")
    finally:
        disconnectDB(myCon)
    resp = aldaaniiMedegdel(200, "Уг email рүү баталгаажуулах код илгээв")
    return HttpResponse(json.dumps(resp), content_type="application/json")
#############################################################

# Баталгаажуулах кодоор нууц үгээ сэргээх /email, verifyCode/
def verifyCodeView(request):
    jsonsData = json.loads(request.body)
    # Хэрэв мэдээлэл дутуу байвал алдааны мэдээлэл дамжуулах
    if (reqValidation(jsonsData, {"verifyCode"}) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна")
        return HttpResponse(json.dumps(resp), content_type="application/json")
    verifyCode = jsonsData["verifyCode"]
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        # email баталгаажсан болон verifyCode нь DB дээр бйагаа эсэхийг уншиж байна.
        userCursor.execute(
            'SELECT "userId", "newPass" FROM "f_resetPassword" WHERE "verifyCode" = %s', (verifyCode,))
        user = userCursor.fetchone()
        # verifyCode нь таарахгүй бол алдааны мэдээлэл дамжуулан
        if (not user) or (user is None):
            resp = aldaaniiMedegdel(553, "Баталгаажуулах код таарсангүй.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        userId = user[0]
        newPass = user[1]
        # verifyCode болон newPass-аа өөрчлөх
        resetVerify = str(createCodes(7))
        resetNewPass = str(createCodes(10))
        userCursor.execute(
            'UPDATE "f_user" SET "pass" = %s WHERE "id" = %s', (newPass, userId,))
        myCon.commit()
        userCursor.execute('UPDATE "f_resetPassword" SET "newPass" = %s, "verifyCode" = %s WHERE "verifyCode" = %s',
                           (resetNewPass, resetVerify, verifyCode,))
        myCon.commit()
        userCursor.close()
    # Баазтай холбоо тасрах үед
    except Exception as e:
        resp = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(resp), content_type="application/json")
    finally:
        disconnectDB(myCon)
    resp = aldaaniiMedegdel(
        200, "Амжилттай хэрэглэгчийн нууц үгийг шинэчлэлээ")
    return HttpResponse(json.dumps(resp), content_type="application/json")
#########################################################################

def userInfoUpdateView(request):
    jsons = json.loads(request.body)
    allowed_fields = ["id", "firstName", "lastName", "userName"]

    if not any(field in jsons for field in allowed_fields):
        response = {
            "responseCode": 550,
            "responseText": "Шинэчлэх хүчинтэй талбар байхгүй байна"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        userCursor.execute(
            'SELECT "isVerified", "userName" FROM "f_user" WHERE "id" = %s', (user_id,))
        result = userCursor.fetchone()

        if not result:
            response = {
                "responseCode": 555,
                "responseText": "Хэрэглэгч олдсонгүй"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        is_verified = result[0]
        response_json = {
            "userName": result[1]
        }

        if not is_verified:
            response = {
                "responseCode": 556,
                "responseText": "Хэрэглэгч баталгаажаагүй байна"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        update_fields = []
        update_values = []

        if "firstName" in jsons:
            update_fields.append('"firstName"')
            update_values.append(jsons['firstName'])
        if "lastName" in jsons:
            update_fields.append('"lastName"')
            update_values.append(jsons['lastName'])
        if "userName" in jsons:
            new_username = jsons['userName']
            if new_username != response_json["userName"] and userNameExists(new_username):
                response = {
                    "responseCode": 560,
                    "responseText": "Бүртгэлтэй хэрэглэгчийн нэр байна."
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")
            else:
                update_fields.append('"userName"')
                update_values.append(new_username)

        # Construct the SQL query
        update_query = 'UPDATE "f_user" SET ' + \
            ', '.join([field + ' = %s' for field in update_fields]
                      ) + ' WHERE "id" = %s'
        update_values.append(user_id)

        userCursor.execute(update_query, tuple(update_values))
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
###################################################################################

def userInfoShowView(request):
    jsons = json.loads(request.body)
    user_id = jsons['id']

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
                'SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
            columns = [column[0] for column in userCursor.description]
            response = [
                {columns[index]: column for index, column in enumerate(
                    value) if columns[index] not in ['verifyCode', 'newPass', 'deldate', 'pass']}
                for value in userCursor.fetchall()
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

        else:
            resp = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

    response = {
        "responseCode": 200,
        "responseText": "Амжилттай",
        "data": {}  # Add an empty "data" field in the response
    }
    return HttpResponse(json.dumps(response), content_type="application/json")

    #############################################################################

def getTransactionLog(request):
    if request.method == "GET" or request.method == "POST":
        jsons = checkJson(request)
        # 
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
                "responseText": "aldaa.",
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
##################################################################################
# Хэрэглэгчийн нэр, үлдэгдэл, нэрийг user_id-гаар нь авч илгээх  
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
##################################################################################
