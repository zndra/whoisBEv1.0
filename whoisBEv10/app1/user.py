from django.http import HttpResponse
import json
import psycopg2
from whoisBEv10.settings import DatabaseSettings

def connectDB():
    settings = DatabaseSettings()

    con = psycopg2.connect(
        dbname=settings.PGdbname,
        user=settings.PGuser,
        host=settings.PGhost,
        password=settings.PGpassword,
        port=settings.PGport,
    )
    return con

# ... rest of the code ...



def disconnectDB(con):
    if(con):
        con.close()


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

    responseJSON = json.dumps(response)
    return HttpResponse(responseJSON,content_type="application/json")
    