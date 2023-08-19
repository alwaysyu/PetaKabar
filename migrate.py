import joblib
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
import re
import string
from flair.models import SequenceTagger
from flair.data import Sentence
import time
from datetime import datetime
import locale

newsscrapped = []

try:
    cnx = mysql.connector.connect(user='admin', password='admin', database = 'Petakabar')
    cursor = cnx.cursor()
    cursor.execute("SELECT ID, berita_date, berita_desc FROM berita where berita_topik_id = 6")
    myresult = cursor.fetchall()
    for row in myresult:
        newsscrapped.append(row)

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor.close()
    cnx.close()

iter_through = ['bencana', 'ekonomi', 'kecelakaan', 'kesehatan', 'kriminalitas', 'olahraga']
iter = 6
batch_iter = 1
batch_size = 128

# print(newsscrapped[127])

# tagged = joblib.load('D:/Repository/PetaKabar/whowherewhen/all_tagged_'+ iter_through[x-1] + '_' + str(batch_iter) + '.pkl')
# print('*'*40)
# print(tagged[-1])

rng = int(len(newsscrapped)/batch_size)
remainder = len(newsscrapped) - rng*batch_size

print(rng, remainder)

all_tagged = []
for i in range(int(len(newsscrapped)/batch_size)):
    print(i+1, i*batch_size)
    tagged = joblib.load('D:/Repository/PetaKabar/whowherewhen/all_tagged_'+ iter_through[iter-1] + '_' + str(i+1) + '.pkl')
    # # check
    # print(tagged[0])
    # print(newsscrapped[i*batch_size])
    for x in range(len(tagged)):
        all_tagged.append(tagged[x])

if remainder > 0:
    tagged = joblib.load('D:/Repository/PetaKabar/whowherewhen/all_tagged_'+ iter_through[iter-1] + '_' + str(rng+1) + '.pkl')
    # # check
    print(remainder, len(tagged))
    # print(tagged[0])
    # print(newsscrapped[i*batch_size])
    for x in range(len(tagged)):
        all_tagged.append(tagged[x])

joblib.dump(all_tagged, 'D:/Repository/PetaKabar/whowherewhen/complete_tagged_'+ iter_through[iter-1] + '.pkl')

