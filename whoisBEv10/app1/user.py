from django.http import HttpResponse
import json

from whoisBEv10.settings import *

def userListView(request):    
    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('select * from "user"'
                         ' ORDER BY id ASC')
    columns = userCursor.description
    response = [{columns[index][0]:column for index, column in enumerate(
        value)} for value in userCursor.fetchall()]

    userCursor.close()        
    disconnectDB(myCon)

    responseJSON = json.dumps(response)
    return HttpResponse(responseJSON,content_type="application/json")

def userLoginView(request):
    # reqData = request.body
    jsons = json.loads(request.body)
    myName = jsons['name']
    myPass = jsons['pass']

    myCon = connectDB()
    userCursor = myCon.cursor()
    userCursor.execute('select count(id) as too from "user"'
                         ' where "userName"=\''+ myName+ '\' '
                         ' and "pass"=\''+ myPass+ '\''
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