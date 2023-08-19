# # from bencana.main.submodule.What import What as bencana_What
# # from bencana.main.submodule.WhoWhereWhen import WhoWhereWhen as bencana_3W
# # from datetime import datetime
# # import locale

# import pandas as pd
# # import re
# # import string
# # from sklearn.model_selection import train_test_split
# import joblib
# from flair.data import Sentence
# from flair.models import SequenceTagger
# from time import sleep

# def preprocessing(berita, result="l"):
#         s = str(berita)
#         # s = s.lower()
#         s = s.replace('\n', ' ')
#         s = s.replace('\r', ' ')
#         # s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
#         if result == "ll":
#                 tokens = [[token] for token in s.split(" ") if token != ""]
#                 # T = [t for t in tokens if (
#                 #     (t in excluded_words) or (t not in NLTK_StopWords))]
#         elif result == "asis":
#                 s = s.replace('  ', ' ')
#                 return s
#         else:
#                 tokens = [token for token in s.split(" ") if token != ""]
#                 # T = [t for t in tokens if (
#                 #     (t in excluded_words) or (t not in NLTK_StopWords))]
#         return tokens

# if __name__ == '__main__':  
#     # bencana_what = bencana_What()
#     # lst = ['hujan', 'bangunan', 'banjir', 'hujan_BAWWW', 'sungai', 'genangan', 'kemarin', 'banjir', 'pemerintah', 'hujan', 'banjir', 'genangan', 'bandung']
#     # q = bencana_what.save_to_mysql(1, lst)
#     # print(q)
#     # bencana_3w = bencana_3W()
#     # print(bencana_3w.get3W())
#     # locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
#     # x = "Kamis, 15 Des 2022 17:02"
#     # print(datetime.strptime(x, "%A, %d %b %Y %H:%M"))

#     news = pd.read_csv('perbandingan/berita-24-5.csv')

#     tag_pos = SequenceTagger.load("D:/Repository/PetaKabar/models/best-model.pt")

#     iter_through = ['bencana', 'ekonomi', 'kecelakaan', 'kesehatan', 'kriminalitas', 'olahraga']

#     x = 3
#     tagged = []
#     # batch = []
#     small_batch = []
#     batch_size = 32

#     berita = news[news['berita_topik_id'] == x]

#     print(iter_through[x-1])

#     batch_iter = 36
#     # for i in range((batch_iter-1)*batch_size, len(berita)):
#     for i in range((batch_iter-1)*batch_size, batch_iter*batch_size):
#         if len(small_batch) == batch_size:
#             # batch.append(small_batch)
#             tag_pos.predict(small_batch)
#             for j in range(len(small_batch)):
#                 # if j == 1136:
#                 #       tagged.append(joblib.load('D:/Repository/PetaKabar/whowherewhen/3_1136_tagged.pkl'))
#                 tagged.append(small_batch[j])
#             joblib.dump(tagged, 'D:/Repository/PetaKabar/whowherewhen/32_all_tagged_'+ iter_through[x-1] + '_' + str(batch_iter) + '.pkl')
#             small_batch = []
#             tagged = []
#             print("*"*30)
#             print(batch_iter)
#             sleep(10)
#             batch_iter += 1
#         # preprocessed_text = preprocessing(berita['berita_desc'].iloc[i], result='asis')
#         sentence = Sentence(preprocessing(berita['berita_desc'].iloc[i], result='asis'))
#         if i == 1136:
#               continue
#         small_batch.append(sentence)
#         print(i, str(len(sentence)))

#     if len(small_batch) != 0:
#         # batch.append(small_batch)
#         tag_pos.predict(small_batch)
#         for j in range(len(small_batch)):
#             if j+(batch_iter-1)*batch_size == 1136:
#                 tagged.append(joblib.load('D:/Repository/PetaKabar/whowherewhen/3_1136_tagged.pkl'))
#             tagged.append(small_batch[j])
#         joblib.dump(tagged, 'D:/Repository/PetaKabar/whowherewhen/32_all_tagged_'+ iter_through[x-1] + '_' + str(batch_iter) + '.pkl')
#         small_batch = []
#         tagged = []
#         batch_iter += 1

#     # # print("***")
#     # # sleep(10)
#     # # print("***")
from bencana.main.submodule.Summarization import Summarization as bencana_Summary

import time

# Start timer
start_time = time.time()

# Code to be timed
bencana_summary = bencana_Summary()
bencana_resultSummary = bencana_summary.get_summary()
print(bencana_resultSummary)
# End timer
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - start_time
print("Elapsed time: ", elapsed_time)