# import mysql.connector
# from mysql.connector import errorcode
# try:
#     conn = mysql.connector.connect(user='admin', password='admin', database = 'Petakabar')
#     cur = conn.cursor()
#     query = ("SELECT * FROM topik")
#     cur.execute(query)
#     result = cur.fetchall()
#     print(result)
#     print(type(result))
#     for x in result:
#         print(x)
#         print(type(x))
#     conn.commit()            
#     cur.close()
#     conn.close()

# except mysql.connector.Error as err:
#     if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#         print("Something is wrong with your user name or password")
#     elif err.errno == errorcode.ER_BAD_DB_ERROR:
#         print("Database does not exist")
#     else:
#         print(err)

import torch

print(torch.version.cuda)
print(torch.cuda.is_available())
# print(torch.cuda.device_count())
# print(torch.cuda.current_device())