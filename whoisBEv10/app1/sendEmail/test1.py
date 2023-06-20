def runQuery(query):
    print(query)

id=10
pa="asd"

runQuery("UPDATE user SET pass=%s WHERE id = %s" % (pa,id))

