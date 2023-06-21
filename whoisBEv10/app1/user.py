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
    passs      = mandakhHash(password)
    userCursor.execute('INSERT INTO "f_user"("firstName", "lastName", "email", "pass", "userName", "deldate", "usertypeid") VALUES(%s, %s, %s, %s, %s, %s, %s)',
                       (firstName, lastName, email, passs, username, None, 2))
    myCon.commit()
    userCursor.close()
    disconnectDB(myCon)

    # Send email verification email
    mail_subject = "Email Verification"
    mail_content = f"Dear {firstName},\n\nThank you for registering. Please click the following link to verify your email:\n\nhttp://whois.mandakh.org/profile/"
    sendMail(email, mail_subject, mail_content)

    # Return success response
    resp = {}
    resp["responseCode"] = 200
    resp["responseText"] = "User registered successfully"
    return HttpResponse(json.dumps(resp), content_type="application/json")

def forgetPass(request):
    jsons = json.loads(request.body)
    email = jsons['email']
    if request.method == 'POST':
        if runQuery == ('SELECT email FROM f_user WHERE email=%s', (email)):
            sendMail(email, 
                     'Reset Password',
                     'https://www.facebook.com/recover/initiate/?ldata=AWe3DyZjElBs5PGSw6BbaSjaPZm49o3OoUm7YM5HvpnAeNfxn-6QADMiYkZP0JDAohjE5d8M_2f8fGwFyMICZhAQX1ehnOiC4xur9Lqn7QqrTPld7YQqzfaDA9EE1xQBwWhQ26A-vXt07-h3qZkn6uCgNxKSaURadprdJ9aQqvjypi8SqPus5wyasseqpnYqgb_k_T-mgxm2E30qlG_s0SQa_3lGdbKdm0ibnh1aYEPMWdVVwLq5J3U9ExYVBnKWWSJfJvZHpCCAPdTApc6jIc9t'
                     )

        response = {
            "responseCode": 555,
            "responseText": ""
        }
    return HttpResponse(json.dumps(response), content_type="application/json")

#### Change password #####
def changePass(request):
    jsons = json.loads(request.body)
    id    = jsons['id']
    pas   = jsons['pas']
    # pa = mandakhHash(pas)
    ## a = "UPDATE user SET pass=%s WHERE id = %s", id, pa
    # a = "UPDATE \"f_user\" SET pass=%s WHERE id = %s" % (pa,id)
    # b = runQuery("SELECT * FROM \"user\" WHERE id = %s"%(id))
    
    if id==0:
        myCon      = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute('select count(id) from "f_user"'
                       ' where "id"=\'' + id + '\' ')
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)
        response = {
            "responseCode": 555,
            "responseText": "user not found"
            }
        return HttpResponse(json.dumps(response), content_type="application/json")
    else:
        myCon      = connectDB()
        userCursor = myCon.cursor()
        userCursor.execute('update "user"'
                           ' set "pass"=\'' + pas + '\''
                       ' where "id"=\'' + id + '\' ')
        myCon.commit()
        userCursor.close()
        disconnectDB(myCon)
        response = {
            "responseCode": 200,
            "responseText": "Change password successfully"
            }
        return HttpResponse(json.dumps(response), content_type="application/json")

#######################################################################################