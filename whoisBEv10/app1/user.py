from    django.http                  import HttpResponse,HttpResponseServerError
from    django.core.serializers.json import DjangoJSONEncoder
from    whoisBEv10.settings          import *
from    django.db                    import connection
import  pytz
import  json



# ene debug uyed ajillah yostoi
def userListView(request):
    myCon      = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT * FROM "f_user" ORDER BY id ASC')
    columns    = userCursor.description
    response   = [{columns[index][0]: column for index,
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
    if( reqValidation( jsons, {"name","pass",} ) == False):
        resp = {}
        resp["responseCode"] = 550
        resp["responseText"] = "Field-үүд дутуу"        
        return HttpResponse(json.dumps(resp), content_type="application/json")
    myName = jsons['name']
    myPass = jsons['pass']
    try:
        myCon      = connectDB()
        userCursor = myCon.cursor()    
        userCursor.execute("SELECT \"id\",\"userName\",\"firstName\",\"lastName\",\"email\" "
                        " FROM f_user"
                        " WHERE " 
                        " deldate IS NULL AND "
                        " pass = %s AND "
                        " \"isVerified\" = true AND "
                        " \"userName\" = %s ",
                        (                     
                        myPass, 
                        myName, 
                        ))    
        columns  = userCursor.description
        response = [{columns[index][0]: column for index, column in enumerate(value)} for value in userCursor.fetchall()]
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

    if len(response)>0:
        responseCode = 200
        responseText = 'Зөв нэр/нууц үг байна хөгшөөн'
        responseData = response[0]
    resp = {}
    resp["responseCode"]     = responseCode
    resp["responseText"]     = responseText
    resp["userData"]         = responseData
    resp["Сургууль"]         = {}
    resp["Сургууль"]["Нэр"]  = "Мандах"
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
    lastName  = jsons['lastName']
    email     = jsons['email']
    password  = jsons['pass']
    username  = jsons['userName']

    try:
        myCon      = connectDB()
        userCursor = myCon.cursor()

        if emailExists(email):
            resp = {
                "responseCode": 400,
                "responseText": "Email already exists"
            }
            return HttpResponse(json.dumps(resp), content_type="application/json")

        if userNameExists(username):
            resp = {
                "responseCode": 400,
                "responseText": "Username already exists"
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
    otp = createCodes(6)
    otp = str(otp)  # Convert OTP to string
    userCursor.execute(
        'INSERT INTO "f_user"("firstName", "lastName", "email", "pass", "userName", "deldate", "usertypeid") '
        'VALUES(%s, %s, %s, %s, %s, %s, %s) RETURNING "id"',  # Replace "userId" with the correct column name
        (firstName, lastName, email, hashed_password, username, None, 2,))

    # Fetch the user ID from the returned row
    userId = userCursor.fetchone()[0]

    # Update the "f_otp" table with the user ID and OTP
    userCursor.execute(
        'INSERT INTO "f_otp"("userId", "value") VALUES(%s, %s)',
        (userId, otp))

    myCon.commit()

    # Send email verification email
    myVerifyEmailLink = verifyEmailLink + otp
    myMailContent     = verifyEmailContent + "Холбоос: " + myVerifyEmailLink
    sendMail(email, verifyEmailSubject, myMailContent)

    # Close the userCursor and disconnect from the database
    userCursor.close()
    disconnectDB(myCon)

    # Return success response
    resp = {
        "responseCode": 200,
        "responseText": "User registered successfully"
    }
    return HttpResponse(json.dumps(resp), content_type="application/json")


######################################################################################
def verifyEmailView(request, otp):
    try:
        myCon      = connectDB()
        userCursor = myCon.cursor()

        # Retrieve the user ID associated with the provided OTP
        userCursor.execute('SELECT "userId" FROM "f_otp" WHERE "value" = %s', (otp,))
        result = userCursor.fetchone()
        
        if result:
            userId = result[0]
            # Update the user's isVerified flag to True in the f_user table
            userCursor.execute('UPDATE "f_user" SET "isVerified" = TRUE WHERE "id" = %s', (userId,))
            myCon.commit()
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse("Email verification successful")
        else:
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse("Invalid or expired OTP")
    except Exception as e:
        return HttpResponse("An error occurred during email verification")
###################################################################################

# Verify email view
def verifyEmailView(request, otp):
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        # Retrieve the user ID associated with the provided OTP
        userCursor.execute('SELECT "userId" FROM "f_otp" WHERE "value" = %s', (otp,))
        result = userCursor.fetchone()
        
        if result:
            userId = result[0]
            # Update the user's isVerified flag to True in the f_user table
            userCursor.execute('UPDATE "f_user" SET "isVerified" = TRUE WHERE "id" = %s', (userId,))
            myCon.commit()
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse("Email verification successful")
        else:
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse("Invalid or expired OTP")
    except Exception as e:
        return HttpResponse("An error occurred during email verification")
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
                "responseText": "success"
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
    required_fields = ["id", "pas"]
    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Invalid request body"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
    
    id  = jsons['id']
    pas = jsons['pas']

    try:
        myCon      = connectDB()
        userCursor = myCon.cursor()
        
        # Check if the user exists
        userCursor.execute('SELECT * FROM "f_user" WHERE "id" = %s', (id,))
        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")
        
        # Update the password
        userCursor.execute('UPDATE "f_user" SET "pass" = %s WHERE "id" = %s', (pas, id))
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)
        
    except Exception as e:
        response = {
            "responseCode": 551,
            "responseText": "Database error"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    response = {
        "responseCode": 200,
        "responseText": "Password changed successfully"
    }
    return HttpResponse(json.dumps(response), content_type="application/json")

#######################################################################################
#CreateCv


def userNemeltGet(request):
   jsons   = json.loads(request.body)
   user_id = jsons['user_id']
   if request.method == 'GET':
       myCon = connectDB()
       userCursor = myCon.cursor()
       userCursor.execute('SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id"= %s',(user_id,) )
       user = userCursor.fetchone()
       if not user:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")
       elif user:
            userCursor.execute('SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id"= %s',(user_id,) )
            columns = [column[0] for column in userCursor.description]
   
            response = [
                    {columns[index]: column for index, column in enumerate(value)}
                     for value in userCursor.fetchall()
                  ]
            userCursor.close()
            disconnectDB(myCon)
       
            responseJSON = json.dumps((response), cls=DjangoJSONEncoder, default=str)
            return HttpResponse(responseJSON, content_type="application/json")
       else:
           response = {
            "responseCode": 551,
            "responseText": "Database error"
        }
           return HttpResponse(json.dumps(response), content_type="application/json") 
       
####################################################################
def userNemeltUpdate(request):
    jsons = json.loads(request.body)
    required_fields = ["user_id", "regDug", "torsonOgnoo", "dugaar", "huis", "irgenshil", "ysUndes", "hayg", "hobby"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id     = jsons['user_id']
    regDug      = jsons['regDug']
    torsonOgnoo = jsons['torsonOgnoo']
    dugaar      = jsons['dugaar']
    huis        = jsons['huis']
    irgenshil   = jsons['irgenshil']
    ysUndes     = jsons['ysUndes']
    hayg        = jsons['hayg']
    hobby       = jsons['hobby']

    try:
        myCon      = connectDB()
        userCursor = myCon.cursor()

        userCursor.execute('SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id" = %s', (user_id,))
        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
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
            "responseText": "Changed successfully"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    except Exception as e:
        response = {
            "responseCode": 551,
            "responseText": "Database error"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")


  
###########################################################
def userNemeltInsert(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "regDug", "torsonOgnoo", "dugaar", "huis", "irgenshil", "ysUndes", "hayg", "hobby"]

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

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute('SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")
        
        userCursor.execute('SELECT * FROM "f_userNemeltMedeelel" WHERE "user_id" = %s', (user_id,))
        user = userCursor.fetchone()
        if user:
            response = {
                "responseCode": 400,
                "responseText": "User already exists"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        userCursor.execute('INSERT INTO "f_userNemeltMedeelel" ("regDug", "torsonOgnoo", "dugaar", "huis", "irgenshil", "ysUndes", "hayg", "hobby", "user_id") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (regDug, torsonOgnoo, dugaar, huis, irgenshil, ysUndes, hayg, hobby, user_id))
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)

        response = {
            "responseCode": 200,
            "responseText": "Inserted successfully"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    except Exception as e:
        response = {
            "responseCode": 551,
            "responseText": "Database error"
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
    if( reqValidation(jsonsData, {"newPassword", "email"} ) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна")        
        return HttpResponse(json.dumps(resp), content_type="application/json")
    
    email       = jsonsData["email"]
    newPassword = jsonsData["newPassword"]
    verifyCode  = createCodes(10) # Batalgaajuulakh codenii urt ni 10
    
    try:
        myCon      = connectDB()
        userCursor = myCon.cursor()
        # email баталгаажсан нь DB дээр бйагаа эсэхийг уншиж байна. 
        userCursor.execute('SELECT * FROM "f_user" WHERE  "email" = %s AND  "isVerified" = true', (email,))
        user = userCursor.fetchone()
        print(user)
        # Хэрэглэч байгаа үгүйг шалгах
        if not user:
            resp = aldaaniiMedegdel(553, "Уг email хаягтай хэрэглэгч олдсонгүй.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # Email илгээх
        mailSubject = "Баталгаажуулах код"
        mailContent = f"Нууц үг сэргээх баталгаажуулах код:\n\n{verifyCode}"
        sendMail(email, mailSubject, mailContent)
        # newPass-ийг өөрчлөх
        userCursor.execute('UPDATE "f_user" SET "newPass" = %s WHERE "email" = %s', (newPassword, email))
        # verifyCode-ийг өөрчлөх
        userCursor.execute('UPDATE "f_user" SET "verifyCode" = %s WHERE "email" = %s', (verifyCode, email))
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
    if( reqValidation(jsonsData, {"verifyCode"} ) == False):
        resp = aldaaniiMedegdel(550, "Field дутуу байна")  
        return HttpResponse(json.dumps(resp), content_type="application/json")
    
    verifyCode = jsonsData["verifyCode"]
    
    try:
        myCon      = connectDB()
        userCursor = myCon.cursor()
        # email баталгаажсан болон verifyCode нь DB дээр бйагаа эсэхийг уншиж байна. 
        userCursor.execute('SELECT * FROM "f_user" WHERE "verifyCode" = %s', (verifyCode,))
        user = userCursor.fetchone()
        # verifyCode нь таарахгүй бол алдааны мэдээлэл дамжуулан
        if not user:   
            resp = aldaaniiMedegdel(553,"Баталгаажуулах код таарсангүй.")
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # pass-аа өөрчлөх
        user = list(user)
        userCursor.execute('UPDATE "f_user" SET "pass" = %s WHERE "verifyCode" = %s', (str(user[len(user)-2]), verifyCode))
        myCon.commit()
        userCursor.close()
    # Баазтай холбоо тасрах үед
    except Exception as e:
        resp = {}
        resp = aldaaniiMedegdel(551,"Баазын алдаа")        
        return HttpResponse(json.dumps(resp), content_type="application/json")
    finally:
        disconnectDB(myCon)
    resp = aldaaniiMedegdel(200,"Амжилттай хэрэглэгчийн нууц үгийг шинэчлэлээ")
    return HttpResponse(json.dumps(resp), content_type="application/json")
#########################################################################
def userEduUp(request):
            jsons = json.loads(request.body)
            required_fields = ["user_id", "haana", "elssen", "duussan", "togssonMergejil"]
        
            if not reqValidation(jsons, required_fields):
                response = {
                    "responseCode": 550,
                    "responseText": "Field-үүд дутуу"
                }
                return HttpResponse(json.dumps(response), content_type="application/json")
        
            user_id         = jsons['user_id']
            haana           = jsons['haana']
            elssen          = jsons['elssen']
            duussan         = jsons['duussan']
            togssonMergejil = jsons['togssonMergejil']
        
            try:
                myCon      = connectDB()
                userCursor = myCon.cursor()
        
                userCursor.execute('SELECT * FROM "f_userEdu" WHERE "user_id" = %s', (user_id,))
                user = userCursor.fetchone()
                if not user:
                    response = {
                        "responseCode": 555,
                        "responseText": "User not found"
                    }
                    userCursor.close()
                    disconnectDB(myCon)
                    return HttpResponse(json.dumps(response), content_type="application/json")
        
                userCursor.execute('UPDATE "f_userEdu" SET "haana" = %s,"elssen" = %s,"duussan" = %s, "togssonMergejil" = %s, "user_id" = %s',
                                   (haana, elssen, duussan, togssonMergejil, user_id,))
                myCon.commit()
                userCursor.close()
                disconnectDB(myCon)
        
                response = {
                    "responseCode": 200,
                    "responseText": "Changed successfully"
                }
                return HttpResponse(json.dumps(response), content_type="application/json")
        
            except Exception as e:
                response = {
                    "responseCode": 551,
                    "responseText": "Database error"
                }
                return HttpResponse(json.dumps(response), content_type="application/json")
###############################################################################################          
import traceback

def userEduInsert(request):
    jsons = json.loads(request.body)
    required_fields = ["id", "haana", "elssen", "duussan", "togssonMergejil"]

    if not reqValidation(jsons, required_fields):
        response = {
            "responseCode": 550,
            "responseText": "Field-үүд дутуу"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']
    haana  =  jsons['haana']
    elssen = jsons['elssen']
    duussan = jsons['duussan']
    togssonMergejil = jsons['togssonMergejil']

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute('SELECT * FROM "f_user" WHERE "id" = %s', (user_id,))
        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        userCursor.execute('SELECT * FROM "f_userEdu" WHERE "user_id" = %s', (user_id,))
        user = userCursor.fetchone()
        if user:
            response = {
                "responseCode": 400,
                "responseText": "User already exists"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        userCursor.execute(
            'INSERT INTO "f_userEdu" ("haana", "elssen", "duussan", "togssonMergejil","user_id") VALUES (%s, %s, %s, %s, %s)',
            (haana, elssen, duussan, togssonMergejil, user_id))
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)

        response = {
            "responseCode": 200,
            "responseText": "Inserted successfully"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    except Exception as e:
        error_message = traceback.format_exc()
        print(error_message)  # Print the detailed error message for debugging purposes

        response = {
            "responseCode": 551,
            "responseText": "Database error: " + str(e)
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

################################################################################################
def userEduGet(request):
   jsons   = json.loads(request.body)
   user_id = jsons['user_id']
   if request.method == 'GET':
       myCon = connectDB()
       userCursor = myCon.cursor()
       userCursor.execute('SELECT * FROM "f_userEdu" WHERE "user_id"= %s',(user_id,) )
       user = userCursor.fetchone()
       if not user:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")
       elif user:
            userCursor.execute('SELECT * FROM "f_userEdu" WHERE "user_id"= %s',(user_id,) )
            columns = [column[0] for column in userCursor.description]
   
            response = [
                    {columns[index]: column for index, column in enumerate(value)}
                     for value in userCursor.fetchall()
                  ]
            userCursor.close()
            disconnectDB(myCon)
       
            responseJSON = json.dumps((response), cls=DjangoJSONEncoder, default=str)
            return HttpResponse(responseJSON, content_type="application/json")
       else:
           response = {
            "responseCode": 551,
            "responseText": "Database error"
        }
           return HttpResponse(json.dumps(response), content_type="application/json") 
################################################################################################
def userSocial(request):
    jsons = json.loads(request.body)
    user_id = jsons['user_id']
    if request.method == "GET":
        myCon = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute('SELECT * FROM "f_userSocial" WHERE "user_id"= %s',(user_id,) )
        user = userCursor.fetchone()
        if not user:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")
        elif user:
             userCursor.execute('SELECT * FROM "f_userSocial" WHERE "user_id"= %s',(user_id,) )
             columns = [column[0] for column in userCursor.description]
  
             response = [
                     {columns[index]: column for index, column in enumerate(value)}
                      for value in userCursor.fetchall()
                   ]
             userCursor.close()
             disconnectDB(myCon)
      
             responseJSON = json.dumps((response), cls=DjangoJSONEncoder, default=str)
             return HttpResponse(responseJSON, content_type="application/json")
        else:
            response = {
             "responseCode": 551,
             "responseText": "Database error"
         }
            return HttpResponse(json.dumps(response), content_type="application/json") 
#############################################################################################
def userInfoUpdateView(request):
    jsons = json.loads(request.body)
    allowed_fields = ["id", "firstName", "lastName", "email", "userName"]

    if not any(field in jsons for field in allowed_fields):
        response = {
            "responseCode": 550,
            "responseText": "No valid fields provided for update"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    user_id = jsons['id']

    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        userCursor.execute('SELECT "isVerified" FROM "f_user" WHERE "id" = %s', (user_id,))
        result = userCursor.fetchone()

        if not result:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")

        is_verified = result[0]

        if not is_verified:
            response = {
                "responseCode": 556,
                "responseText": "User is not verified"
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
        if "email" in jsons:
            update_fields.append('"email"')
            update_values.append(jsons['email'])
        if "userName" in jsons:
            update_fields.append('"userName"')
            update_values.append(jsons['userName'])

        # Construct the SQL query
        update_query = 'UPDATE "f_user" SET ' + ', '.join([field + ' = %s' for field in update_fields]) + ' WHERE "id" = %s'
        update_values.append(user_id)

        userCursor.execute(update_query, tuple(update_values))
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)

        response = {
            "responseCode": 200,
            "responseText": "Changed successfully"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    except Exception as e:
        response = {
            "responseCode": 551,
            "responseText": "Database error"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
###################################################################################
def userInfoShowView(request):
   jsons   = json.loads(request.body)
   user_id = jsons['id']
   if request.method == 'GET':
       myCon = connectDB()
       userCursor = myCon.cursor()
       userCursor.execute('SELECT * FROM "f_user" WHERE "id"= %s',(user_id,) )
       user = userCursor.fetchone()
       if not user:
            response = {
                "responseCode": 555,
                "responseText": "User not found"
            }
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(response), content_type="application/json")
       elif user:
            userCursor.execute('SELECT * FROM "f_user" WHERE "id"= %s',(user_id,) )
            columns = [column[0] for column in userCursor.description]
   
            response = [
                    {columns[index]: column for index, column in enumerate(value)}
                     for value in userCursor.fetchall()
                  ]
            userCursor.close()
            disconnectDB(myCon)
       
            responseJSON = json.dumps((response), cls=DjangoJSONEncoder, default=str)
            return HttpResponse(responseJSON, content_type="application/json")
       else:
           response = {
            "responseCode": 551,
            "responseText": "Database error"
        }
           return HttpResponse(json.dumps(response), content_type="application/json") 
