import traceback
import json
from django.http import HttpResponse
from datetime import date
from django.http import HttpResponse, HttpResponseServerError
from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *
from django.db import connection
import pytz
import json


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
    myPass = mandakhHash(myPass)
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute("SELECT \"id\",\"userName\",\"firstName\",\"lastName\",\"email\" "
                           " FROM f_user"
                           " WHERE "
                           " deldate IS NULL AND "
                           " pass = %s AND "
                           " \"userName\" = %s ",
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

#   userLoginView end


def userRegisterView(request):
    jsons = json.loads(request.body)

    # Validate request body
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

        if not myCon:
            raise Exception("Can not connect to the database")
    except Exception as e:
        resp = {
            "responseCode": 551,
            "responseText": "Баазын алдаа"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    hashed_password = mandakhHash(password) 
    userCursor.execute(
        'INSERT INTO "f_user"("firstName", "lastName", "email", "pass", "userName", "deldate", "usertypeid") '
        'VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING "id"',
        (firstName, lastName, email, hashed_password, username, None, 2,))


    userId = userCursor.fetchone()[0]

    # Add user ID to other tables
    userCursor.execute(
        'INSERT INTO "f_userEdu"("user_id") VALUES(%s)',
        (userId,))

    userCursor.execute(
        'INSERT INTO "f_userFamily"("user_id") VALUES(%s)',
        (userId,))

    userCursor.execute(
        'INSERT INTO "f_userNemeltMedeelel"("user_id") VALUES(%s)',
        (userId,))

    userCursor.execute(
        'INSERT INTO "f_userSkill"("user_id") VALUES(%s)',
        (userId,))

    userCursor.execute(
        'INSERT INTO "f_userSocial"("user_id") VALUES(%s)',
        (userId,))

    userCursor.execute(
        'INSERT INTO "f_userWork"("user_id") VALUES(%s)',
        (userId,))

    myCon.commit()

    # Close the userCursor and disconnect from the database
    userCursor.close()
    disconnectDB(myCon)

    # Return success response
    resp = {
        "responseCode": 200,
        "responseText": "Амжилттай бүртгэгдлээ"
    }
    return HttpResponse(json.dumps(resp), content_type="application/json")



######################################################################################

# Verify email view
def verifyEmailView(request, otp):
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        # Retrieve the user ID associated with the provided OTP
        userCursor.execute(
            'SELECT "userId" FROM "f_otp" WHERE "value" = %s', (otp,))
        result = userCursor.fetchone()

        if result:
            userId = result[0]
            # Update the user's isVerified flag to True in the f_user table
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

#### Change password #####


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
# CreateCv


def userNemeltGet(request):
    jsons = json.loads(request.body)
    user_id = jsons['user_id']
    if request.method == 'GET':
        try:
            myCon = connectDB()
            userCursor = myCon.cursor()
            userCursor.execute(
                'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id"= %s', (user_id,))
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
                userCursor.execute(
                    'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id"= %s', (user_id,))
                columns = [column[0] for column in userCursor.description]

                response = [
                    {columns[index]: column for index, column in enumerate(value)}for value in userCursor.fetchall()
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
        except:
            response = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")


####################################################################


def userNemeltUpdate(request):
    jsons = json.loads(request.body)
    required_fields = ["user_id", "regDug", "torsonOgnoo",
                       "dugaar", "huis", "irgenshil", "ysUndes", "hayg", "hobby"]
    if request.method == 'POST':
        if not reqValidation(jsons, required_fields):
            response = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")

        user_id = jsons['user_id']
        regDug = jsons['regDug']
        torsonOgnoo = jsons['torsonOgnoo']
        dugaar = jsons['dugaar']
        huis = jsons['huis']
        irgenshil = jsons['irgenshil']
        ysUndes = jsons['ysUndes']
        hayg = jsons['hayg']
        hobby = jsons['hobby']

        try:
            myCon = connectDB()
            userCursor = myCon.cursor()

            userCursor.execute(
                'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id" = %s', (user_id,))
            user = userCursor.fetchone()
            if not user:
                response = {
                    "responseCode": 555,
                    "responseText": "Хэрэглэгч олдсонгүй"
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")

            userCursor.execute('UPDATE "f_userNemeltMedeelel" SET "regDug" = %s,"torsonOgnoo" = %s,"dugaar" = %s, "huis" = %s,"irgenshil" = %s,"ysUndes" = %s,"hayg" = %s,"hobby" = %s WHERE "user_id" = %s',
                               (regDug, torsonOgnoo, dugaar, huis, irgenshil, ysUndes, hayg, hobby, user_id,))
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
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

###########################################################


def userNemeltInsert(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "regDug", "torsonOgnoo", "dugaar",
                       "huis", "irgenshil", "ysUndes", "hayg", "hobby"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    regDug = jsons['regDug']
    torsonOgnoo = jsons['torsonOgnoo']
    dugaar = jsons['dugaar']
    huis = jsons['huis']
    irgenshil = jsons['irgenshil']
    ysUndes = jsons['ysUndes']
    hayg = jsons['hayg']
    hobby = jsons['hobby']
    if request.method == 'POST':
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
                'SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id" = %s', (user_id,))
            user = userCursor.fetchone()
            if user:
                response = {
                    "responseCode": 400,
                    "responseText": "Бүртгэлтэй хэрэглэгч байна."
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")
            if regDugExist(regDug):
                resp = {
                    "responseCode": 400,
                    "responseText": "Бүртгэлтэй хэрэглэгчийн id байна."
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")
            userCursor.execute('INSERT INTO "f_userNemeltMedeelel" ("regDug", "torsonOgnoo", "dugaar", "huis", "irgenshil", "ysUndes", "hayg", "hobby", "user_id") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                               (regDug, torsonOgnoo, dugaar, huis, irgenshil, ysUndes, hayg, hobby, user_id))
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
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
 #########################################################################


# response буцаахад ашиглах
def aldaaniiMedegdel(code, tailbar):
    resp = {}
    resp["responseCode"] = code
    resp["responseText"] = tailbar
    return resp
#############################################################

# response буцаахад ашиглах


def resetPasswordView(request):
    jsonsData = json.loads(request.body)
    resp = {}
    # Хэрэв мэдээлэл дутуу байвал алдааны мэдээлэл дамжуулах
    if (reqValidation(jsonsData, {"newPassword", "email"}) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна")
        return HttpResponse(json.dumps(resp), content_type="application/json")

    email = jsonsData["email"]
    newPassword = jsonsData["newPassword"]
    verifyCode = createCodes(10)  # Batalgaajuulakh codenii urt ni 10

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        # email баталгаажсан нь DB дээр бйагаа эсэхийг уншиж байна.
        userCursor.execute(
            'SELECT * FROM "f_user" WHERE  "email" = %s AND  "isVerified" = true', (email,))
        user = userCursor.fetchone()
        print(user)
        # Хэрэглэч байгаа үгүйг шалгах
        if not user:
            resp = aldaaniiMedegdel(
                553, "Уг email хаягтай хэрэглэгч олдсонгүй.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # Email илгээх
        mailSubject = "Баталгаажуулах код"
        mailContent = f"Нууц үг сэргээх баталгаажуулах код:\n\n{verifyCode}"
        sendMail(email, mailSubject, mailContent)
        # newPass-ийг өөрчлөх
        userCursor.execute(
            'UPDATE "f_user" SET "newPass" = %s WHERE "email" = %s', (newPassword, email))
        # verifyCode-ийг өөрчлөх
        userCursor.execute(
            'UPDATE "f_user" SET "verifyCode" = %s WHERE "email" = %s', (verifyCode, email))
        myCon.commit()
        userCursor.close()

    except Exception as e:
        resp = {}
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
    resp = {}
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
            'SELECT * FROM "f_user" WHERE "verifyCode" = %s', (verifyCode,))
        user = userCursor.fetchone()
        # verifyCode нь таарахгүй бол алдааны мэдээлэл дамжуулан
        if not user:
            resp = aldaaniiMedegdel(553, "Баталгаажуулах код таарсангүй.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # pass-аа өөрчлөх
        user = list(user)
        userCursor.execute('UPDATE "f_user" SET "pass" = %s WHERE "verifyCode" = %s', (str(
            user[len(user)-2]), verifyCode))
        myCon.commit()
        userCursor.close()
    # Баазтай холбоо тасрах үед
    except Exception as e:
        resp = {}
        resp = aldaaniiMedegdel(551, "Баазын алдаа")
        return HttpResponse(json.dumps(resp), content_type="application/json")
    finally:
        disconnectDB(myCon)
    resp = aldaaniiMedegdel(
        200, "Амжилттай хэрэглэгчийн нууц үгийг шинэчлэлээ")
    return HttpResponse(json.dumps(resp), content_type="application/json")
#########################################################################


def userEduUp(request):
    jsons = json.loads(request.body)
    required_fields = ["user_id", "Боловсрол", "Эрдмийн зэрэг",
                       "Албан тушаал", "Албан байгууллагын нэр"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['user_id']
    haana = jsons['Боловсрол']
    elssen = jsons['Эрдмийн зэрэг']
    duussan = jsons['Албан тушаал']
    togssonMergejil = jsons['Албан байгууллагын нэр']

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

        userCursor.execute('UPDATE "f_userEdu" SET "Боловсрол" = %s,"Эрдмийн зэрэг" = %s,"Албан тушаал" = %s, "Албан байгууллагын нэр" = %s WHERE "user_id" = %s',
                           (haana, elssen, duussan, togssonMergejil, user_id,))
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
    required_fields = ["id", "Боловсрол", "Эрдмийн зэрэг",
                       "Албан тушаал", "Албан байгууллагын нэр"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    haana = jsons['Боловсрол']
    elssen = jsons['Эрдмийн зэрэг']
    duussan = jsons['Албан тушаал']
    togssonMergejil = jsons['Албан байгууллагын нэр']

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
            'SELECT * FROM "f_userEdu" WHERE "user_id" = %s', (user_id,))
        user = userCursor.fetchone()
        if user:
            response = {
                "responseCode": 400,
                "responseText": "Бүртгэлтэй хэрэглэгч байна."
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        userCursor.execute(
            'INSERT INTO "f_userEdu" ("Боловсрол", "Эрдмийн зэрэг", "Албан тушаал", "Албан байгууллагын нэр","user_id") VALUES (%s, %s, %s, %s, %s)',
            (haana, elssen, duussan, togssonMergejil, user_id))
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

    if request.method == 'GET':
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
            responseJSON = response[0]
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

    response = {
        "responseCode": 200,
        "responseText": "Амжилттай",
        "eduData": {}  # Add an empty "data" field in the response
    }
    return HttpResponse(json.dumps(response), content_type="application/json")
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
            responseJSON = response[0]
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


def userSocialUp(request):
    jsons = json.loads(request.body)

    # Validate request body
    required_fields = ["id", "app", "oldsite", "newsite"]
    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Буруу хүсэлт"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    id = jsons['id']
    app = jsons['app']
    oldsite = jsons['oldsite']
    newsite = jsons['newsite']

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        # Check if the user exists
        userCursor.execute(
            'SELECT * FROM "f_userSocial" WHERE "user_id" = %s AND "app" = %s AND "site" = %s', (id, app, oldsite))
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
            'UPDATE "f_userSocial" SET "site" = %s WHERE "user_id" = %s AND "app" = %s', (newsite, id, app))
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
    ##############################################################


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


def userTurshlaga(request):
    jsons = json.loads(request.body)
    user_id = jsons['id']
    if request.method == "GET":
        myCon = connectDB()
        userCursor = myCon.cursor()

        userCursor.execute(
            'SELECT * FROM "f_userWork" WHERE "user_id"= %s', (user_id,))

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
                'SELECT * FROM "f_userWork" WHERE "user_id"= %s', (user_id,))
            columns = [column[0] for column in userCursor.description]

            response = [
                {columns[index]: column for index, column in enumerate(value)}
                for value in userCursor.fetchall()
            ]
            userCursor.close()
            disconnectDB(myCon)
            responseJSON = response[0]
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
#############################################################################################


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
        userCursor.execute('SELECT * FROM "f_userWork" WHERE "user_id" = %s AND "ajil" = %s',
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
        userCursor.execute('UPDATE "f_userWork" SET "ajil" = %s, "company"  = %s, "ehelsen" =%s,  "duussan"=%s WHERE "user_id" = %s AND "ajil"=%s',
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
    ##############################################################


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
#################################################################


def userFamilyGet(request):
    jsons = json.loads(request.body)
    user_id = jsons['user_id']
    if request.method == 'GET':
        try:
            myCon = connectDB()
            userCursor = myCon.cursor()
            userCursor.execute(
                'SELECT * FROM "f_userFamily" WHERE "user_id"= %s', (user_id,))
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
                userCursor.execute(
                    'SELECT * FROM "f_userFamily" WHERE "user_id"= %s', (user_id,))
                columns = [column[0] for column in userCursor.description]

                response = [
                    {columns[index]: column for index, column in enumerate(value)}for value in userCursor.fetchall()
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

        except:
            response = {
                "responseCode": 551,
                "responseText": "Баазын алдаа"
            }
            return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
############################################################################

#   Хэрэглэгчийн id-г илгээхэд бүх чадваруудыг list хэлбэрээр илгээх функц.


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
#################################################################################

# Profile-ийнн чадвар дээр хадгалах дарахад table-д мэдээлэл оруулж мөн шинэчлэх.


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
    # allInfo = []
    # allInfo = allInfoDic(user)
    allInfo = []
    for data in user:
        data = list(data)
        chadvar = {}
        chadvar["id"] = data[0]
        chadvar["chadvariinNer"] = data[1]
        chadvar["chadvariinTuvshin"] = data[2]
        allInfo.append(chadvar)
    # def allInfoDic(user):
    #     allInfo = []
    #     for data in user:
    #         data = list(data)
    #         chadvar = {}
    #         chadvar["id"] = data[0]
    #         chadvar["chadvariinNer"] = data[1]
    #         chadvar["chadvariinTuvshin"] = data[2]
    #         allInfo.append(chadvar)
    #     return allInfo
    # "skills" not in jsonsData
    print(skills)
    for data in skills:
        # print(list(data))
        print(data)
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
            print(id)
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
            # allInfo = allInfoDic(user)
            ustgasan += 1
    userCursor.close()
    disconnectDB(myCon)
    response = aldaaniiMedegdel(
        200, "Амжилттай чадварын тухай мэдээллүүдийг шинэчлэлээ.")
    response["ustgasan"] = ustgasan
    response["nemsen"] = nemsen
    return HttpResponse(json.dumps(response), content_type="application/json")
#################################################################################


def getTransactionLog(request):
    if request.method == "GET":
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
                """SELECT * FROM "f_transactionLog" WHERE "from" = %s OR "to" = %s""", [userId, userId])
            logData = cur.fetchall()
            if logData is not None:
                desc = cur.description
                payLoad = [
                    {desc[index][0]: columnn.isoformat() if isinstance(
                        columnn, date) else columnn for index, columnn in enumerate(value)}
                    for value in logData
                ]

            resp = {
                "responseCode": 200,
                "responseText": "Амжилттай",
                "data": payLoad if payLoad else []
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        except Exception as e:
            resp = {
                "responseCode": 500,
                "responseText": "Алдаа",
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


def makeTransaction(request):
    if request.method == "POST":
        jsons = checkJson(request)

        if reqValidation(jsons, {"from", "target", "amount"}) == False:
            resp = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        userId = jsons.get('from')
        targetUserId = jsons.get('target')
        amount = jsons.get('amount')

        conn = None
        try:
            conn = connectDB()
            cur = conn.cursor()

            cur.execute(
                """SELECT balance FROM "f_user" WHERE id = %s""", [userId])
            balance = cur.fetchone()

            if balance is None and balance[0] < 0:
                resp = {
                    "responseCode": 500,
                    "responseText": "uldegdel hureltssengui eeee.",
                    "data": balance
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")

            cur.execute(
                "UPDATE f_user SET balance = balance + %s WHERE id = %s RETURNING id, balance", [amount, targetUserId])
            targetData = cur.fetchone()
            cur.execute(
                "UPDATE f_user SET balance = balance - %s WHERE id = %s RETURNING id, balance", [amount, userId])
            fromData = cur.fetchone()
            cur.execute("""INSERT INTO "f_transactionLog"(amount, balance, "from", "to") VALUES (%s, %s, %s, %s)""",
                        [amount, fromData[1], userId, targetUserId])
            conn.commit()

            resp = {
                "responseCode": 200,
                "responseText": "ok.",
                "data": {
                    'from': fromData,
                    'target': targetData,
                }
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        except Exception as e:
            resp = {
                "responseCode": 500,
                "responseText": "aldaa.",
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
    #######################


def userFamilyInsert(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "henBoloh", "ner", "dugaar"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    henBoloh = jsons['henBoloh']
    ner = jsons['ner']
    dugaar = jsons['dugaar']

    if request.method == 'POST':
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

            userCursor.execute('INSERT INTO "f_userFamily" ("henBoloh", "ner", "dugaar", "user_id") VALUES (%s, %s, %s, %s)',
                               (henBoloh, ner, dugaar, user_id))
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
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
#####################


def userFamilyUpdate(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "henBoloh", "ner", "dugaar"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    henBoloh = jsons['henBoloh']
    ner = jsons['ner']
    dugaar = jsons['dugaar']
    if request.method == 'POST':
        try:
            myCon = connectDB()
            userCursor = myCon.cursor()

            userCursor.execute(
                'SELECT * FROM "f_userFamily" WHERE "user_id" = %s', (user_id,))
            user = userCursor.fetchone()
            if not user:
                response = {
                    "responseCode": 555,
                    "responseText": "Хэрэглэгч олдсонгүй"
                }
                userCursor.close()
                disconnectDB(myCon)
                return HttpResponse(json.dumps(response), content_type="application/json")

            userCursor.execute('UPDATE "f_userFamily" SET "henBoloh" = %s, "ner" = %s, dugaar= %s WHERE "user_id" = %s',
                               (henBoloh, ner, dugaar, user_id))
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
    else:
        response = {
            "responseCode": 400,
            "responseText": "Хүлээн авах боломжгүй хүсэлт байна.",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    ################################################################################


def uploadTemplateView(request):
    jsons = json.loads(request.body)

    # Validate request body
    if reqValidation(jsons, {"name", "tempId", "catId", "file"}) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    name = jsons['name']
    date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    tempId = jsons['tempId']
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

    userCursor.execute(
        'INSERT INTO "f_templates"("name", "date", "tempId", "catId", "file", "userId") '
        'VALUES(%s, %s, %s, %s, %s, %s) RETURNING "id"',
        (name, date, tempId, catId, file, userId))

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


def userTemplatesGet(request):
    jsons = json.loads(request.body)

    if reqValidation(jsons, {"tempId", "tempType"}) == False:
        resp = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(resp), content_type="application/json")

    date = date.today().strftime("%d-%m-%Y")
    tempType = jsons['tempType']
    userId = jsons['userId']
    tempId = jsons['tempId']

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

    userCursor.execute(
        'INSERT INTO "f_userTemplates"("date", "tempType", "userId", "tempId") '
        'VALUES (%s, %s, %s, %s) '
        'RETURNING "id"',
        (date, tempType, userId, tempId))

    templateId = userCursor.fetchone()[0]

    myCon.commit()

    userCursor.close()
    disconnectDB(myCon)

    resp = {
        "responseCode": 200,
        "responseText": "Template ашигласан",
        "templateId": templateId
    }
    return HttpResponse(json.dumps(resp), content_type="application/json")

###############################################################################


def tempListView(request):
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT * FROM  f_templates ORDER BY id ASC')
    columns = userCursor.description
    response = [{columns[index][0]: column for index,
                 column in enumerate(value)} for value in userCursor.fetchall()]
    userCursor.close()
    disconnectDB(myCon)
    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")


def userTempListView(request):
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT * FROM "f_userTemplates" ORDER BY id ASC')
    columns = userCursor.description
    response = [{columns[index][0]: column for index,
                 column in enumerate(value)} for value in userCursor.fetchall()]
    userCursor.close()
    disconnectDB(myCon)
    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")


#   Хэрэглэгчийн id-г илгээхэд бүх чадваруудыг list хэлбэрээр илгээх функц.
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
            'SELECT "id", "skill" FROM "f_skill" WHERE "userId" = %s', (user_id,))
        user = userCursor.fetchone()
        # Хэрэглэч байгаа үгүйг шалгах
        if not user:
            text = ""
            userCursor.execute(
                'INSERT INTO "f_skill"("userId", "skill") VALUES(%s, %s) RETURNING "id"', (user_id, text,))
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
#################################################################################

#   Хэрэглэгчийн id болон чадварыг илгээхэд update хийж илгээнэ.


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
            'SELECT "id", "skill" FROM "f_skill" WHERE "userId" = %s', (user_id,))
        user = userCursor.fetchone()
        # Хэрэглэч байгаа үгүйг шалгах
        if not user:
            text = ""
            userCursor.execute(
                'INSERT INTO "f_skill"("userId", "skill") VALUES(%s, %s) RETURNING "id"', (user_id, skill,))
            idd = userCursor.fetchone()
            myCon.commit()
            resp = aldaaniiMedegdel(
                553, "Хэрэглэгчийн чадварын тухай мэдээллийг шинээр үүсгэлээ.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        userCursor.execute(
            'UPDATE "f_skill" SET "skill" = %s WHERE "userId" = %s', (skill, int(user_id),))
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
#################################################################################


def getTransactionLog(request):
    if request.method == "GET":
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
                """SELECT * FROM "f_transactionLog" WHERE "from" = %s OR "to" = %s""", [userId, userId,])
            logData = cur.fetchall()
            cur.execute(
                """SELECT balance FROM "f_user" WHERE "id" = %s""", [userId,])
            dansniiUldegdel = cur.fetchall()
            if not dansniiUldegdel:
                response = aldaaniiMedegdel(553, "Бүртгэлгүй хэрэглэгч байна.")
                cur.close()
                disconnectDB(conn)
                return HttpResponse(json.dumps(response), content_type="application/json")
            resp = {
                "responseCode": 200,
                "responseText": "Амжилттай дансны мэдээлэл харлаа.",
                # "data": payLoad if payLoad else [],
                "dansniiUldegdel": dansniiUldegdel[0][0]
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        except Exception as e:
            resp = {
                "responseCode": 588,
                "responseText": "Бүртгэлгүй хэрэглэгч байна",
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


def makeTransaction(request):
    if request.method == "POST":
        jsons = checkJson(request)

        if reqValidation(jsons, {"from", "target", "amount",}) == False:
            resp = {
                "responseCode": 550,
                "responseText": "Field-үүд дутуу"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")
        
        userId = jsons.get('from')
        targetUserId = jsons.get('target')
        amount = jsons.get('amount')
        conn = None
        try:
            conn = connectDB()
            cur = conn.cursor()
            cur.execute("""SELECT balance, "userName" FROM "f_user" WHERE id = %s""", [userId,])
            user = cur.fetchone()
            fromBalance = user[0]
            userName = user[1]
            cur.execute("""SELECT balance FROM "f_user" WHERE "userName" = %s""", [targetUserId,])
            targetBalance = cur.fetchone()[0]

            if fromBalance is None or targetBalance is None: 
                resp = {
                    "responseCode": 588,
                    "responseText": "Хэрэглэгчийн мэдээлэл олдсонгүй .",
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")
            
            if targetBalance is None or fromBalance < int(amount):
                resp = {
                    "responseCode": 555,
                    "responseText": "Таны дансны үлдэгдэл хүрэлцэхгүй байна.",
                    "data": fromBalance
                }
                return HttpResponse(json.dumps(resp), content_type="application/json")

            cur.execute("""UPDATE f_user SET balance = balance + %s WHERE "userName" = %s RETURNING "userName", balance""", [amount, targetUserId])
            targetData = cur.fetchone()
            conn.commit()
            cur.execute("""UPDATE f_user SET balance = balance - %s WHERE "userName" = %s RETURNING "userName", balance""", [amount, userName])
            fromData = cur.fetchone()
            cur.execute("""INSERT INTO "f_transactionLog"(amount, balance, "from", "to") VALUES (%s, %s, %s, %s)""",
                        [int(amount), int(fromData[1]), userName, targetUserId])
            conn.commit()
        
            cur.execute("""SELECT "from", balance, amount, "date"  FROM "f_transactionLog" WHERE "from" = 'usuhuu' OR "to" = 'usuhuu' ORDER BY "date" DESC LIMIT 5""")
            fromDate = cur.fetchall()
            fromDate[0] = list(fromDate[0])
            fromDate[1] = list(fromDate[1])
            fromDate[2] = list(fromDate[2])
            fromDate[3] = list(fromDate[3])
            fromDate[4] = list(fromDate[4])
            # print(fromDate)
            myData = []
            for i in range(0, 5):
                datas = {}
                datas["userName"] = fromDate[i][0]
                datas["balance"] = fromDate[i][1]
                datas["amount"] = fromDate[i][2]
                datas["date"] = str(fromDate[i][3])
                myData.append(datas)
            # print(fromDate)
#             "henees": usuhuu, FROM
#             "balance": 1000,BALANCE
#             "mungu": 100,AMOUNT
#             "date": 2023.12.12,DATE
#             "utga": "sdf"/
            resp = {
                "responseCode": 200,
                "responseText": "Амжилттай шилжлээ.",  
                "data" : {
                    'from': fromData,
                    'target': targetData,
                    'gvilgee': myData
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
