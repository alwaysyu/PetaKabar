from operator import itemgetter
from typing import List
from nltk import tokenize
from nltk.corpus import stopwords
from yake import KeywordExtractor
import math
import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import re
import joblib
from keybert import KeyBERT
import scipy
import ssl
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import locale

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

kw_extractor = KeyBERT('distilbert-base-nli-mean-tokens')
embedder = SentenceTransformer('xlm-r-distilroberta-base-paraphrase-v1')
nltk.download('punkt')
NLTK_StopWords = stopwords.words('indonesian')


excluded_words = ["tempat", "waktu", "hari"]
NLTK_StopWords = stopwords.words('indonesian')
NLTK_StopWords.extend(["detik", "detikjatim", "detikjateng", "detikjabar", "detiksulsel", "detiksumbar", "detikbali",
                      "detikpapua", "detiksulteng", "detikmaluku", "detjatim", "detikcom", "allahumma", "aamiin", "allah", "bismillah"])
NLTK_StopWords.extend(["yg", "dg", "rt", "dgn", "ny", "d", 'klo',
                       'kalo', 'amp', 'biar', 'bikin', 'bilang',
                       'gak', 'ga', 'krn', 'nya', 'nih', 'sih',
                       'si', 'tau', 'tdk', 'tuh', 'utk', 'ya',
                       'jd', 'jgn', 'sdh', 'aja', 'n', 't',
                       'nyg', 'hehe', 'pen', 'u', 'nan', 'loh', 'rt',
                       '&amp', 'yah'])
NLTK_StopWords = set(NLTK_StopWords)


class QueryExpansion:
    def __init__(self) -> None:
        self.containerberita = []
        self.descberita = []
        self.idberita = []
        try:
            cnx = mysql.connector.connect(user='admin', password='admin', database = 'Petakabar')
            cursor = cnx.cursor()
            cursor.execute("SELECT ID, berita_desc FROM berita where berita_topik_id = 3 AND class_classification is null")
            myresult = cursor.fetchall()
            for row in myresult:
                self.containerberita.append(row)

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
        if(len(self.containerberita)>0):
            self.idberita, self.descberita = zip(*self.containerberita)

        #ini dapetnya pada darimana?
        # self.tfidf_vectorizer = joblib.load('dataset/qe/vectorizer.pkl')
        # self.tfidf_matrix = joblib.load('dataset/qe/tfidf_train.pkl')
        # self.df_train = pd.read_csv('dataset/qe/df_train.csv')
        # self.bow_list_what = joblib.load('dataset/qe/bow_kecelakaan.pkl')

        self.tfidf_vectorizer = joblib.load('D:/PetaKabar/kecelakaan/dataset/qe/vectorizer_new.pkl')
        self.tfidf_matrix = joblib.load('D:/PetaKabar/kecelakaan/dataset/qe/tfidf_train_new.pkl')
        self.df_train = pd.read_csv('D:/PetaKabar/kecelakaan/dataset/qe/df_train.csv')
        self.bow_list_what = joblib.load('D:/PetaKabar/kecelakaan/dataset/qe/bow_kecelakaan.pkl')
        # print("qe kecelakaan")


        # df_bow_what = pd.read_csv('dataset/qe/bow_what.csv')
        # self.bow_list_what = []
        # for i in range(0, df_bow_what.shape[0]):
        #     self.bow_list_what.append(df_bow_what.iloc[i, 1])

    def __preprocessing(self, berita: str):
        s = str(berita)
        s = s.lower()
        s = s.replace('\n', ' ')
        s = s.replace('\r', ' ')
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
        tokens = [token for token in s.split(" ") if token != ""]
        T = [t for t in tokens if (
            (t in excluded_words) or (t not in NLTK_StopWords))]
        return T

    # YAKE keyword extraction
    def __keyword_yake(self, hasilSearch: str) -> List[str]:
        keywordYake = []

        k_extractor = KeywordExtractor(lan="id", n=1, top=50)
        k_extractor2 = KeywordExtractor(lan="id", n=2, top=50)
        keywords = k_extractor.extract_keywords(text=hasilSearch)

        keywords.extend(k_extractor2.extract_keywords(text=hasilSearch))
        keywordYake = [x for x, y in keywords]

        # print('*'*120)
        # print('*'*120)
        # print("Keyword yake")
        # print(keywordYake)
        # print('*'*120)
        # print('*'*120)

        return keywordYake

    # Cari dok pertama Use data train
    def __cari_dokpertama(self, kueriAsli: str):
        kueriPre = self.__preprocessing(kueriAsli)
        kueriPre = " ".join(kueriPre)
        hasilSearch = []

        query_vec = self.tfidf_vectorizer.transform([kueriPre])
        results = cosine_similarity(self.tfidf_matrix, query_vec).reshape((-1))

        for i in results.argsort()[-5:][::-1]:
            hasilSearch.append(self.df_train.iloc[i, -2])

        hasilSearch = ". ".join(hasilSearch)

        return hasilSearch

    # TFIDF Keywords extraction
    def __keyword_tfidf(self, hasilSearch: str) -> List[str]:

        keywordtfidf = []
        keywordtfidf2 = []

        total_words = re.sub(r'[^\w]', ' ', hasilSearch)
        total_words = total_words.lower().split()
        #print (total_words)
        total_word_length = len(total_words)
        total_sentences = tokenize.sent_tokenize(hasilSearch)
        total_sent_len = len(total_sentences)

        tf_score = {}
        for each_word in total_words:
            #print (each_word)
            each_word = each_word.replace('.', '')
            if (each_word in excluded_words) or (each_word not in NLTK_StopWords):
                if each_word in tf_score:
                    tf_score[each_word] += 1
                else:
                    tf_score[each_word] = 1

        # Dividing by total_word_length for each dictionary element
        tf_score.update((x, y/int(total_word_length))
                        for x, y in tf_score.items())
        # print(tf_score)

        def check_sent(word, sentences):
            final = [all([w in x for w in word]) for x in sentences]
            sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
            return int(len(sent_len))

        idf_score = {}
        for each_word in total_words:
            #print (each_word)
            each_word = each_word.replace('.', '')
            if (each_word in excluded_words) or (each_word not in NLTK_StopWords):
                if each_word in idf_score:
                    idf_score[each_word] = check_sent(
                        each_word, total_sentences)
                else:
                    idf_score[each_word] = 1

        idf_score.update((x, math.log(int(total_sent_len)/y))
                         for x, y in idf_score.items())

        tf_idf_score = {
            key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}

        def get_top_n(dict_elem, n):
            result = dict(sorted(dict_elem.items(),
                          key=itemgetter(1), reverse=True)[:n])
            hasil = list(result.keys())

            return hasil

        keywordtfidf.append(get_top_n(tf_idf_score, 35))
        for i in range(len(keywordtfidf)):
            totalKw = 0
            totalKw = len(keywordtfidf[i])
            for j in range(totalKw):
                keywordtfidf2.append(keywordtfidf[i][j])

        # print('*'*120)
        # print('*'*120)
        # print("Keyword TFIDF")
        # print (keywordtfidf2)
        # print('*'*120)
        # print('*'*120)

        return keywordtfidf2

    # BERT keywords extraction
    def __keyword_bert(self, hasilSearch: str) -> List[str]:
        keywordbert = []
        keyword1 = kw_extractor.extract_keywords(hasilSearch, top_n=50, keyphrase_ngram_range=(1, 1))
        keyword2 = kw_extractor.extract_keywords(hasilSearch, top_n=50, keyphrase_ngram_range=(1, 2))

        for i in range(0, len(keyword1)):
            keywordbert.append(keyword1[i][0])
            keywordbert.append(keyword2[i][0])

        # print('*'*120)
        # print('*'*120)
        # print("Keyword Bert")
        # print(keywordbert)
        # print('*'*120)
        # print('*'*120)

        return keywordbert

    # Borda rangking
    def __rangking(self, keywordGabung: List[str], kueriAsli: str) -> List[str]:
        kandidatFinalCek = []
        kandidatFinalFix = []

        for i in keywordGabung:
            if (i not in kandidatFinalCek and i != 0):
                kandidatFinalCek.append(i)
        queries = [kueriAsli]
        query_embeddings = embedder.encode(queries)
        corpus_embeddings4 = embedder.encode(kandidatFinalCek)
        # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
        closest_n = 80
        for query, query_embedding in zip(queries, query_embeddings):
            distances = scipy.spatial.distance.cdist(
                [query_embedding], corpus_embeddings4, 'cosine')[0]
            results = zip(range(len(distances)), distances)
            results = sorted(results, key=lambda x: x[1])
            for idx, distance in results[0:closest_n]:
                kandidatFinalFix.append(kandidatFinalCek[idx])

        # print('*'*120)
        # print('*'*120)
        # print ('Kandidat Final Fix Rank: ', kandidatFinalFix)
        # print('*'*120)
        # print('*'*120)

        return kandidatFinalFix

    # Keyword bow
    def __keywordCustomBow(self, bowList: List[str], initialQuery: str) -> List[str]:
        cekDuplicate = []
        kandidatFix = []

        for i in bowList:
            if(i not in cekDuplicate and i != 0):
                cekDuplicate.append(i)

        queries = [initialQuery]
        query_embeddings = embedder.encode(queries)
        corpus_embeddings4 = embedder.encode(cekDuplicate)

        # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
        closest_n = 2200
        for _, query_embedding in zip(queries, query_embeddings):
            distances = scipy.spatial.distance.cdist(
                [query_embedding], corpus_embeddings4, 'cosine')[0]
            results = zip(range(len(distances)), distances)
            results = sorted(results, key=lambda x: x[1])
            for idx, distance in results[0:closest_n]:
                kandidatFix.append(cekDuplicate[idx])

        # print('*'*120)
        # print('*'*120)
        # print("Keyword BoW")
        # print('Kandidat BoW: ', kandidatFix)
        # print('*'*120)
        # print('*'*120)

        return kandidatFix

    # Prepare w data
    def __prepareWData(self, initial_query: str, bow_list: List[str]):
        hasilkandidat = []
        keywordGabung = []
        qeGabungan = []
        kueriFix = []

        hasilSearch = self.__cari_dokpertama(initial_query)
        # (ini yake + tfidf + bert) = qe statistik
        keywordYake = self.__keyword_yake(hasilSearch)
        keywordtfidf2 = self.__keyword_tfidf(hasilSearch) 
        keywordbert = self.__keyword_bert(hasilSearch) 
        # ini qe bow
        keywordBoW = self.__keywordCustomBow(bow_list, initial_query)

        for keyword1 in keywordYake:
            keywordGabung.append(keyword1)
        for keyword2 in keywordtfidf2:
            keywordGabung.append(keyword2)
        for keyword3 in keywordbert:
            keywordGabung.append(keyword3)

        # hasilrank = qe statistik
        hasilrank = self.__rangking(keywordGabung, initial_query)

        for word1 in hasilrank:
            kueriFix.append(word1)

        for word2 in keywordBoW:
            kueriFix.append(word2)

        for word3 in kueriFix:
            hasilkandidat.append(word3)

        kueriFix = [self.__preprocessing(i) for i in kueriFix]

        qeGabunganDelimiter = []

        for word4 in kueriFix:
            for subWord in word4:
                qeGabungan.append(subWord)
                qeGabunganDelimiter.append(subWord)

        qeGabunganDelimiter = list(dict.fromkeys(qeGabunganDelimiter))

        return qeGabunganDelimiter

    def getWhatFromText(self, initial_query: str):
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
        try :
            what_initial_query = initial_query

            what_query = self.__preprocessing(what_initial_query)
            what_query = " ".join(what_query)

            qeGabunganDelimiter = self.__prepareWData(
                what_query, self.bow_list_what)

            document_result = []

            for i in range(0, len(self.descberita)):
                hasilWhat = []

                for key in qeGabunganDelimiter:
                    cariW = re.findall(key, self.descberita[i])

                    if cariW:
                        hasilWhat.append(key)
                # print("selfberita=",self.dateberita[i])
                # print("TYPE selfberita-",type(self.dateberita[i]))
                # rep_date = self.dateberita[i].replace(" WIB","")
                # date_format = datetime.strptime(rep_date, "%A, %d %b %Y %H:%M")
                # print("dateformat", date_format)
                
                #save to sql
                self.save_to_mysql(self.idberita[i], hasilWhat)
                
                # document_result.append([self.titleberita[i], self.descberita[i], self.dateberita[i], hasilWhat])

            # writer = pd.DataFrame(document_result, columns=[
            #                     'title', 'description', 'time', 'what'], index=None)
            # writer.to_csv('result/4w/4w_news_db.csv', index=False, sep=',')
            return 'success'
        except:
            return 'error'

    def save_to_mysql(self, idberita, whatberita):
        try:
            conn = mysql.connector.connect(user='admin', password='admin', database = 'Petakabar')
            cur = conn.cursor()
            add_news = ("UPDATE berita "
                        "SET qe_what = %s "
                    "WHERE ID = %s"
                    )
            hasilstr = ""
            for x in range(len(whatberita)):
                hasilstr = hasilstr + whatberita[x]
                if x < len(whatberita)-1:
                    hasilstr = hasilstr + ", "
            data_news = (hasilstr, idberita)
            cur.execute(add_news, data_news)
            conn.commit()            
            cur.close()
            conn.close()

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)