from    django.http                  import HttpResponse
from    django.core.serializers.json import DjangoJSONEncoder
from    app1.sendEmail.sendEmail     import *
from    whoisBEv10.settings          import *
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
    if( reqValidation( jsons, {"firstName", "lastName", "email", "pass", "userName",} ) == False):
        resp = {}
        resp["responseCode"] = 550
        resp["responseText"] = "Field-үүд дутуу"        
        return HttpResponse(json.dumps(resp), content_type="application/json")

    firstName = jsons['firstName']
    lastName  = jsons['lastName']    
    email     = jsons['email']
    password  = jsons['pass']
    username  = jsons['userName']

    # Check if email or username already exist in the database
    try:
        myCon      = connectDB()
        userCursor = myCon.cursor()
        if emailExists(email):
            resp = {}
            resp["responseCode"] = 400
            resp["responseText"] = "Email already exists"
            return HttpResponse(json.dumps(resp), content_type="application/json")

        if userNameExists(username):
            resp = {}
            resp["responseCode"] = 400
            resp["responseText"] = "Username already exists"
            return HttpResponse(json.dumps(resp), content_type="application/json")

        # Check if the database is connected
        if not myCon:
            raise Exception("Can not connect database")
    except Exception as e:
        resp = {}
        resp["responseCode"] =  551
        resp["responseText"] = "Баазын алдаа"
        return HttpResponse(json.dumps(resp), content_type="application/json")

    # Proceed with user registration if email and username are unique
    # passs      = mandakhHash(password)
    userCursor.execute('INSERT INTO "f_user"("firstName", "lastName", "email", "pass", "userName", "deldate", "usertypeid") VALUES(%s, %s, %s, %s, %s, %s, %s)',
                       (firstName, lastName, email, password, username, None, 2))
    myCon.commit()
    userCursor.close()
    disconnectDB(myCon)

    # Send email verification email
    # Return success response
    otp = createCodes(6)  # Generate OTP
    myVerifyEmailLink = verifyEmailLink + otp
    myMailContent = verifyEmailContent+"Холбоос: "+myVerifyEmailLink
    sendMail(email, verifyEmailSubject, myMailContent)
    resp = {}
    resp["responseCode"] = 200
    resp["responseText"] = "User registered successfully"
    return HttpResponse(json.dumps(resp), content_type="application/json")
######################################################################################
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
    
    id = jsons['id']
    pas = jsons['pas']

    try:
        myCon = connectDB()
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


def userNemeltMedeelel(request):
   jsons = json.loads(request.body)
   user_id = jsons['user_id']
   try:
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
       else:
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
 
           
         
   except Exception as e:
        response = {
            "responseCode": 551,
            "responseText": "Database error"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
           
  #########################################################################
# def checkEmailExistence(request):
#     jsons = json.loads(request.body)
#     email = jsons['email']
    
#     exists = emailExists(email)
#     if exists:
#         otp = createCodes(6)  # Generate OTP
#         mail_subject = "Email Verification"
#         mail_content = f"Dear User,\n\nPlease click the following link to verify your email:\n\nhttp:whois.mandakh.org/signUpWar/{otp}/{email}"
#         sendMail(email, mail_subject, mail_content)
#         response = {
#             'success': True,
#             'message': 'Email verification email sent.'
#         }
#     else:
#         response = {
#             'success': False,
#             'message': 'Email does not exist.'
#         }
    
#     responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
#     return HttpResponse(responseJSON, content_type="application/json")
       
     # # response дамжуулах дугаар болон утгыг оноож өгөх функц
# def respUgukh(code, text):
#     resp["responseCode"] = code
#     resp["responseText"] = text        
# #############################################################    
# # DB tugsgukh kheseg
# def tasal():
#     userCursor.close()
#     disconnectDB(myCon)
# #############################################################    


# email, өөрчлөх кодыг аваад DB дээрээ хадгалаад otp code email рүү илгээнэ.
def resetPasswordView(request):
    jsonsData = json.loads(request.body) 
    resp = {}
    # Хэрэв мэдээлэл дутуу байвал алдааны мэдээлэл дамжуулах
    if( reqValidation(jsonsData, {"newPassword", "email"} ) == False):
        # def respUgukh("522", "Field дутуу байна"):
        resp["responseCode"] = "550"
        resp["responseText"] = "Field дутуу байна"        
        return HttpResponse(json.dumps(resp), content_type="application/json")
    
    email = jsonsData["email"]
    newPassword = jsonsData["newPassword"]
    verifyCode = createCodes(10) # Batalgaajuulakh codenii urt
    
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        # email баталгаажсан нь DB дээр бйагаа эсэхийг уншиж байна. 
        userCursor.execute('SELECT * FROM "f_user" WHERE  "email" = %s AND  "isVerified" = true', (email,))
        user = userCursor.fetchone()
        # Хэрэглэч байгаа үгүйг шалгах
        if not user:
            # respUgukh("523", "Уг email хаягтай хэрэглэгч олдсонгүй", resp)     
            resp["responseCode"] = "553"
            resp["responseText"] = "Уг email хаягтай хэрэглэгч олдсонгүй"
            # tasal()   
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # Email илгээх
        mail_subject = "Баталгаажуулах код"
        mail_content = f"Нууц үг сэргээх баталгаажуулах код:\n\n{verifyCode}"
        sendMail(email, mail_subject, mail_content)
        # newPass-ийг өөрчлөх
        userCursor.execute('UPDATE "f_user" SET "newPass" = %s WHERE "email" = %s', (newPassword, email))
        # myCon.commit()
        # verifyCode-ийг өөрчлөх
        userCursor.execute('UPDATE "f_user" SET "verifyCode" = %s WHERE "email" = %s', (verifyCode, email))
        myCon.commit()
        userCursor.close()
        
    except Exception as e:
        resp = {}
        resp["responseCode"] = 551
        resp["responseText"] = "Баазын алдаа"        
        return HttpResponse(json.dumps(resp), content_type="application/json")
    finally:
        disconnectDB(myCon)
    # tasal()   
    # respUgukh("200", "Уг email рүү баталгаажуулах код илгээв", resp)     
    resp["responseCode"] = "200"
    resp["responseText"] = "Уг email рүү баталгаажуулах код илгээв"
    return HttpResponse(json.dumps(resp), content_type="application/json")
#############################################################
       # Баталгаажуулах кодоор нууц үгээ сэргээх /email, verifyCode/
def verifyCodeView(request):
    jsonsData = json.loads(request.body)   
    resp = {}
    # Хэрэв мэдээлэл дутуу байвал алдааны мэдээлэл дамжуулах
    if( reqValidation(jsonsData, {"verifyCode"} ) == False):
        resp["responseCode"] = "550"
        resp["responseText"] = "Field дутуу байна"        
        return HttpResponse(json.dumps(resp), content_type="application/json")
    
    verifyCode = jsonsData["verifyCode"]
    
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()
        # email баталгаажсан болон verifyCode нь DB дээр бйагаа эсэхийг уншиж байна. 
        userCursor.execute('SELECT * FROM "f_user" WHERE "verifyCode" = %s', (verifyCode,))
        # print("helloooooo")
        user = userCursor.fetchone()
        # print(user)
        # myCon.commit()
        # verifyCode нь таарахгүй бол алдааны мэдээлэл дамжуулан
        if not user:   
            resp["responseCode"] = "553"
            resp["responseText"] = "Баталгаажуулах код таарсангүй."
            userCursor.close()
            disconnectDB(myCon)
            return HttpResponse(json.dumps(resp), content_type="application/json")
        # newPass = userCursor.execute('SELECT "newPass" FROM "f_user" WHERE "email" = %s', (email))
        # print(str(newPass))
        # pass-аа өөрчлөх
        user = list(user)
        userCursor.execute('UPDATE "f_user" SET "pass" = %s WHERE "verifyCode" = %s', (str(user[len(user)-3]), verifyCode))
        myCon.commit()
        userCursor.close()
    # Баазтай холбоо тасрах үед
    except Exception as e:
        resp = {}
        resp["responseCode"] = 551
        resp["responseText"] = "Баазын алдаа"        
        return HttpResponse(json.dumps(resp), content_type="application/json")
    finally:
        disconnectDB(myCon)
    resp["responseCode"] = "200"
    resp["responseText"] = "Амжилттай хэрэглэгчийн нууц үгийг шинэчлэлээ"
    return HttpResponse(json.dumps(resp), content_type="application/json")
#############################################################    
   
       