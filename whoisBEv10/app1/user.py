from django.http import HttpResponse
import json
import psycopg2
PGdbname = "sandbox"
PGuser = "postgres"
PGhost="127.0.0.1"
PGpassword="sandbox"
PGport="5432"
def connectDB():

    con = psycopg2.connect(
        dbname =PGdbname,
        user =PGuser,
        host=PGhost,
        password=PGpassword,
        port=PGport,   
    )
    return con
#   connectDB

def disconnectDB(con):
    if(con):
        con.close()
#   disconnectDB


def userListView(request):    
    myCon = connectDB()
    userCursor = myCon.cursor()
    # Ganzo - query yanzlah
    userCursor.execute('select * from "User"'
                         ' ORDER BY id ASC')
    columns = userCursor.description
    response = [{columns[index][0]:column for index, column in enumerate(
        value)} for value in userCursor.fetchall()]

    userCursor.close()        
    disconnectDB(myCon)
    # try:
    #     myCon = connectDB()
    #     userCursor = myCon.cursor()
    #     # Ganzo - query yanzlah
    #     userCursor.execute("select * from 'user'"
    #                         "ORDER BY id ASC")
    #     columns = userCursor.description
    #     response = [{columns[index][0]:column for index, column in enumerate(
    #         value)} for value in aimagCursor.fetchall()]

    #     userCursor.close()        
    # except Exception as e:
    #     response = {}
    #     response["hariu"] = "hello"
    #     response["surguuli"] = "Mandakh"
    # finally:
    #     disconnectDB(myCon)
    # response = {}
    # response["hariu"] = "hello"
    # response["surguuli"] = "Mandakh"

    responseJSON = json.dumps(response)
    return HttpResponse(responseJSON,content_type="application/json")
    