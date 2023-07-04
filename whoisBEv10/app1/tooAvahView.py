import json
from django.http import HttpResponse

from django.core.serializers.json import DjangoJSONEncoder
from whoisBEv10.settings import *


def tooAvah(request):
    try:
        myCon = connectDB()
        userCursor = myCon.cursor()

        query = '''
            SELECT COUNT(*) AS count, 'user_edu_count' AS count_type FROM "f_userEdu"
            UNION
            SELECT COUNT(*), 'user_count' AS count_type FROM "f_user"
            UNION
            SELECT COUNT(*), 'user_family_count' AS count_type FROM "f_userFamily"
            UNION
            SELECT COUNT(*), 'user_wallet_count' AS count_type FROM "f_transactionLog"
        '''

        userCursor.execute(query)
        results = userCursor.fetchall()

        columns = [column[0] for column in userCursor.description]

        response = []
        for result in results:
            response.append({columns[index]: column for index, column in enumerate(result)})

        userCursor.close()
        disconnectDB(myCon)

        response = {
            "responseCode": 200,
            "responseText": "Амжилттай",
            "data": response
        }

        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder, default=str), content_type="application/json")

    except Exception as e:
        response = {
            "responseCode": 551,
            "responseText": "Баазын алдаа"
        }
        return HttpResponse(json.dumps(response), content_type="application/json")