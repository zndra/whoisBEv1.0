from django.http import HttpResponse
import json
from whoisBEv10.settings import *
from django.core.serializers.json import DjangoJSONEncoder
import pytz
from django.utils import timezone
# ...
def userListView(request):
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('SELECT * FROM "user" ORDER BY id ASC')
    columns = userCursor.description
    response = [{columns[index][0]: column for index, column in enumerate(value)} for value in userCursor.fetchall()]
    userCursor.close()
    disconnectDB(myCon)
    # Convert timezone-aware time objects to timezone-naive time objects
    for item in response:
        if 'created_at' in item:
            item['created_at'] = item['created_at'].astimezone(pytz.utc).replace(tzinfo=None)
    responseJSON = json.dumps(response, cls=DjangoJSONEncoder, default=str)
    return HttpResponse(responseJSON, content_type="application/json")

###################################################################
def userLoginView(request):
    jsons = json.loads(request.body)
    myName = jsons['name']
    myPass = jsons['pass']
    passs = mandakhHash(myPass)
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('select count(id) as too from "user"'
                         ' where "userName"=\''+ myName+ '\' '
                         ' and "pass"=\''+ passs+ '\''
                         )    
    columns = userCursor.description
    response = [{columns[index][0]:column for index, column in enumerate(
        value)} for value in userCursor.fetchall()]    
    userCursor.close()        
    disconnectDB(myCon)

    responseCode = 0
    responseText = 'Буруу нэр/нууц үг'
    if response[0]['too'] != 0:
        responseCode = 200
        responseText = 'Зөв нэр/нууц үг байна хөгшөөн'
    resp = {}
    resp["responseCode"] = responseCode
    resp["responseText"] = responseText

    return  HttpResponse(json.dumps(resp),content_type="application/json")    
###################################################
def userRegisterView(request):
    jsons = json.loads(request.body)
    firstName = jsons['firstName']
    lastName = jsons['lastName']
    email = jsons['email']
    password = jsons['pass']
    username = jsons['userName']
    
    # Check if email or username already exist in the database
    if emailExists(email):
        response = {
            "responseCode": 400,
            "responseText": "Email already exists"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
    
    if userNameExists(username):
        response = {
            "responseCode": 400,
            "responseText": "Username already exists"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    # Proceed with user registration if email and username are unique
    myCon = connectDB()
    userCursor = myCon.cursor()
    passs = mandakhHash(password)
    userCursor.execute('INSERT INTO "user"("firstName", "lastName", "email", "pass", "userName", "deldate", "usertypeid") VALUES(%s, %s, %s, %s, %s, %s, %s)',
                       (firstName, lastName, email, passs, username, None, 2))
    myCon.commit()
    userCursor.close()
    disconnectDB(myCon)
    
    response = {
        "responseCode": 200,
        "responseText": "User registered successfully"
    }

    return HttpResponse(json.dumps(response), content_type="application/json")