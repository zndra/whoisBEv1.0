# import psycopg2
# PGdbname = "sandbox"
# PGuser = "postgres"
# PGhost="127.0.0.1"
# PGpassword="sandbox"
# PGport="5432"

# def connectDB():

#     con = psycopg2.connect(
#         dbname =PGdbname,
#         user =PGuser,
#         host=PGhost,
#         password=PGpassword,
#         port=PGport,   
#     )
#     return con
# #   connectDB

# def disconnectDB(con):
#     if(con):
#         con.close()
# #   disconnectDB

# myCon = connectDB()
# userCursor = myCon.cursor()
# # Ganzo - query yanzlah
# userCursor.execute('select * from "user"'
#                     ' ORDER BY id ASC')
# columns = userCursor.description
# response = [{columns[index][0]:column for index, column in enumerate(
#     value)} for value in userCursor.fetchall()]

# userCursor.close()        

# print(response)

# disconnectDB(myCon)
# print('Okey')