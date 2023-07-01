import joblib
from typing import List
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from gensim.test.utils import datapath
from gensim import models
from nltk.corpus import stopwords
import re
from nltk.tokenize import word_tokenize 
from gensim.models import Phrases


class What:
    def __init__(self) -> None:
        # Bagian LDA
        self.total_topics = 4
        self.number_words = 29
        self.lda_model = models.ldamodel.LdaModel.load(datapath('D:/PetaKabar/models/lda_model_kriminalitas/lda_model')) # Ambil Model LDA sesuai dengan topik
        self.topics = self.lda_model.show_topics(formatted = False, num_topics = self.total_topics, num_words = self.number_words)
        self.words = [word for i, topic in self.topics for word, weight in topic]

        self.newsscrapped = []
        try:
            cnx = mysql.connector.connect(user = 'root', password='', database = 'Petakabar')
            cursor = cnx.cursor()
            cursor.execute("SELECT ID, berita_desc, berita_title FROM berita where berita_topik_id = 5  AND class_classification is null") # adjust
            myresult = cursor.fetchall()
            for row in myresult:
                self.newsscrapped.append(row)

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

        self.idberita = []
        self.descberita = []
        self.titleberita = []
        for i in range(len(self.newsscrapped)):
            self.idberita.append(self.newsscrapped[i][0])
            self.descberita.append(self.newsscrapped[i][1])
            self.titleberita.append(self.newsscrapped[i][2])
        
        self.stopwords_add = pd.read_csv("D:/PetaKabar/datasets/stopwords_add.txt", names= ["stopwords"], header = None)

    def __preprocessing(self, berita: str):
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
        NLTK_StopWords.extend(self.stopwords_add["stopwords"][0].split(' '))
        NLTK_StopWords = set(NLTK_StopWords)
        s = str(berita)
        s = s.lower()
        s = s.replace('\n', ' ')
        s = s.replace('\r', ' ')
        s = re.sub(r'[^a-zA-Z\s]', ' ', s)
        tokens = [token for token in s.split(" ") if token != ""]
        T = [t for t in tokens if (t not in NLTK_StopWords)]
        T = (' '.join(T))
        T = re.sub(r"\d+", "", s)
        T = word_tokenize(T)
        T = [token for token in T if len(token) > 2]
        return T
    
    def getWhat(self):
        try:
            for x in range(0, len(self.descberita)):
                text = self.__preprocessing(self.descberita[x])
                self.descberita[x] = text
            for x in range(0, len(self.titleberita)):
                text = self.__preprocessing(self.titleberita[x])
                self.titleberita[x] = text

            bigram = Phrases(self.descberita, min_count=1)
            for idx in range(len(self.descberita)):
                for token in bigram[self.descberita[idx]]:
                    if '_' in token:
                        # Token is a bigram, add to document.
                        self.descberita[idx].append(token)
                        word1, word2 = token.split("_")
                        dont_remove = ('kereta', 'bencana', 'gempa', 'tsunami', 'meletus', 'getaran', 'vulkanik', 'meledak', 'ledakan', 'kebakaran',
                            'terbakar', 'banjir', 'abrasi', 'amblas', 'kekeringan', 'puting', 'beliung', 'angin', 'anjlok', 'pergerakan', 'tumbang',
                            'kencang', 'petir', 'lebat', 'hujan', 'longsor', 'genangan', 'meteor', 'meluap', 'dagang', 'berita', 'perdagangan', 'ekonomi',
                            'miliar', 'neraca', 'impor', 'resesi', 'persen', 'perekonomian', 'keuangan', 'sosio', 'makro', 'bisnis', 'moneter', 'makroekonomi',
                            'perekonomiannya', 'kesejahteraan', 'pertumbuhan', 'inflasi', 'industrialisasi', 'produktivitas', 'infrastruktur', 'pasar',
                            'produk', 'pembangunan', 'usaha', 'saham', 'ukm', 'ekspor', 'dieskpor', 'diimpor', 'mengekspor', 'mengimpor', 'pertumbuhan', 
                            'kecelakaan', 'tertabrak', 'tabrakan', 'menabrak', 'ditabrak', 'tenggelam', 'pesawat', 'simtoma', 'penyakit', 'kesehatan', 'covid',
                            'korban', 'pasien', 'terjangkit', 'tuberkulosis', 'dbd', 'hiv', 'diabetes', 'hipertensi', 'ginjal', 'jantung', 'melitus', 'infeksi',
                            'terinfeksi', 'bakteri', 'virus', 'vaksin', 'polio', 'imunisasi', 'meningitis', 'aids', 'diare', 'pneumonia', 'radang', 'pandemi',
                            'corona', 'malaria', 'muntah', 'kejang', 'batuk', 'hipertensi', 'obesitas', 'gizi', 'sars', 'darah', 'pasien', 'influenza', 'flu',
                            'kanker', 'anemia', 'hepatitis', 'liver', 'iritasi', 'pengobatan', 'obat', 'alergi', 'gatal', 'ruam', 'kelainan', 'bunuh', 'pembunuhan',
                            'membunuh', 'dibunuh', 'pencurian', 'curi', 'mencuri', 'dicuri', 'pemerkosaan', 'memperkosa', 'diperkosa', 'perkosa', 'rampok',
                            'perampokan', 'merampok', 'dirampok', 'begal', 'pembegalan', 'membegal', 'dibegal', 'pembacokan', 'bacok', 'membacok', 'dibacok',
                            'penusukan', 'tusuk', 'ditusuk', 'menusuk', 'pukul', 'pemukulan', 'memukul', 'dipukul', 'luka', 'melukai', 'dilukai', 'sepakbola',
                            'bulutangkis', 'basket', 'raket', 'voli', 'futsal', 'tenis', 'turnamen', 'motogp', 'pertandingan', 'pon')
                        if word1 not in dont_remove:
                            self.descberita[idx].remove(word1)
                        if word2 not in dont_remove:
                            self.descberita[idx].remove(word2)

            lda_desc_what = []
            for i in range(len(self.descberita)):
                val = []
                for word in self.words:
                    if word in self.descberita[i]:
                        val.append(word)
                lda_desc_what.append(val)
            
            lda_title_what = []
            for i in range(len(self.titleberita)):
                val = []
                for word in self.words:
                    if word in self.titleberita[i]:
                        val.append(word)
                lda_title_what.append(val)

            for idx, word_list in enumerate(lda_title_what):
                val = []
                for word in word_list:
                    if word in lda_desc_what[idx]:
                        continue
                    val.append(word)
                lda_desc_what[idx].extend(val)
                lda_desc_what[idx] = set(lda_desc_what[idx])
            
            for i in range(0, len(self.descberita)):
                self.save_to_mysql(self.idberita[i], lda_desc_what[i])

            return 'success'
        except:
            return 'error'
        
    def save_to_mysql(self, idberita, whatberita):
        try:
            conn = mysql.connector.connect(user = 'root', password='', database = 'Petakabar')
            cur = conn.cursor()
            add_news = ("UPDATE berita "
                        "SET qe_what = %s "
                    "WHERE ID = %s"
                    )
            hasilstr = ""
            for x in range(len(whatberita)):
                if len(whatberita[x].split("_")) == 2:
                    hasilstr = hasilstr + whatberita[x].split("_")[0] + " " + whatberita[x].split("_")[1]
                else:
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