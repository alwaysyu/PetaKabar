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

day = ("senin", 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu')
month = ('januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember')
kata_excl = ('usd', 'rp', 'timur', 'pusat', 'barat', 'utara', 'selatan', 'tengah', 'tenggara', 'kecamatan', 'kelurahan', 'desa', 'kabupaten', 'kota', 'dusun', 'rt', 'kampung','provinsi', 'jawa', 'nusa', 'kalimantan', 'sulawesi', 'papua' ,'aceh', 'jakarta', 'lombok', 'sumba', 'barito', 'surakarta', 'jalan')
jan = ('januari', 'jan', 'january')
feb = ('februari', 'feb', 'pebruari', 'peb', 'february')
mar = ('maret', 'mar', 'march')
apr = ('april', 'apr')
mei = ('mei', 'may')
jun = ('juni', 'jun', 'june')
jul = ('juli', 'jul', 'july')
agu = ('agustus', 'august', 'agu', 'aug')
sep = ('september', 'sept', 'sep')
okt = ('oktober', 'okt', 'oct', 'october')
nov = ('november', 'nov', 'nopember', 'nop')
des = ('desember', 'des', 'dec', 'december')

pattern_date = [('PROPN', 'PUNCT', 'NUM', 'PUNCT', 'NUM', 'PUNCT', 'NUM', 'PUNCT'), #Kamis (1/12/2022)
                ('PROPN', 'PUNCT', 'NUM', 'PROPN', 'NUM', 'PUNCT'), # Jakarta, Minggu, 4 Desember 2022,
                ('PROPN', 'PUNCT', 'NUM', 'PUNCT', 'NUM', 'PUNCT'), # Dirangkum Minggu (25/12),
                ('PROPN', 'NOUN', 'PUNCT', 'NUM', 'PROPN', 'NUM', 'PUNCT'), # Jumat malam, 2 Desember 2022.
                ('PROPN', 'PROPN', 'PUNCT', 'NUM', 'PROPN', 'NUM', 'PUNCT'), # Selasa pagi, 6 Desember 2022.
                ('NUM', 'PROPN', 'NUM'), # 7 Desember 2022
                ('NUM', 'PROPN', 'PUNCT'), # 22 Desember, 
                ('NUM', 'PUNCT', 'NUM', 'PUNCT', 'NUM') # 2022/12/14 OR 14/12/2022
                ]
idx_date = [(0, 2, 4, 6),
            (0, 2, 3, 4),
            (0, 2, 4),
            (0, 3, 4, 5),
            (0, 3, 4, 5),
            (-1, 0, 1, 2),
            (-1, 0, 1, -1),
            (-1, 0, 2, 4)
            ]

class WhoWhereWhen:
    def __init__(self) -> None:
        self.prov = joblib.load('D:/PetaKabar/datasets/provinsi.pkl')
        self.kab = joblib.load('D:/PetaKabar/datasets/kabupaten.pkl')
        self.kec = joblib.load('D:/PetaKabar/datasets/kecamatan.pkl')
        self.daerah = joblib.load('D:/PetaKabar/datasets/listProvKabKec.pkl')
        self.tag_pos = SequenceTagger.load("D:/Petakabar/models/best-model.pt")
        # self.negara = joblib.load('D:/PetaKabar/datasets/list_negara.pkl') # ekonomi

        self.batch_size = 32

        self.newsscrapped = []
        try:
            cnx = mysql.connector.connect(user = 'root', password='', database = 'Petakabar')
            cursor = cnx.cursor()
            # cursor.execute("SELECT ID, berita_date, berita_desc FROM berita where berita_topik_id = 1 LIMIT 10")
            cursor.execute("SELECT ID, berita_date, berita_desc FROM berita where berita_topik_id = 1 AND class_classification is null")
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
        self.dateberita = []
        self.descberita = []
        for i in range(len(self.newsscrapped)):
            self.idberita.append(self.newsscrapped[i][0])
            self.dateberita.append(self.newsscrapped[i][1])
            self.descberita.append(self.newsscrapped[i][2])

    def __preprocessing(self, berita):
        s = str(berita)
        s = s.replace('\n', ' ')
        s = s.replace('\r', ' ')
        s = s.replace('  ', ' ')
        return s

    def clean_num(self, text):
        return re.sub('\D', '', text)

    def represents_int(self, s):
        try: 
            int(s)
        except ValueError:
            return False
        else:
            return True

    def handle_bulan(self, text):
        if self.represents_int(text):
            if int(text) < 13 and int(text) > 0:
                return int(text)
        else:
            text = text.lower()
            if text in jan:
                return 1
            if text in feb:
                return 2
            if text in mar:
                return 3
            if text in apr:
                return 4
            if text in mei:
                return 5
            if text in jun:
                return 6
            if text in jul:
                return 7
            if text in agu:
                return 8
            if text in sep:
                return 9
            if text in okt:
                return 10
            if text in nov:
                return 11
            if text in des:
                return 12
        return -1

    def handle_tahun(self, text):
        # print(text)
        # print(type(text))
        text = self.clean_num(text)
        if self.represents_int(text):
            if int(text) < 2050 and int(text) > 2000:
                return int(text)
        return -1

    def handle_tanggal(self, text):
        # print(text)
        # print(type(text))
        if len(text.split("-")) == 2:
            text = text.split("-")[0]
        text = self.clean_num(text)
        if self.represents_int(text):
            if int(text) < 32 and int(text) > 0:
                return int(text)
        print(text, type(text))
        return 0

    def write_date(self, tgl, bulan, tahun):
        # print("1")
        if tgl/10 < 1:
            tgl = "0" + str(tgl)     
        if bulan/10 < 1:
            bulan = "0" + str(bulan)
        return str(tgl)+"/"+str(bulan)+"/"+str(tahun)  

    def find_date(self, sentence=None):
        hari = []
        tgl = []
        bulan = []
        tahun = []
        len_sentence = len(sentence)
        for j in range(len_sentence):

            for i in range(len(pattern_date)):
                len_pattern = len(pattern_date[i])
                if len_sentence - j < len_pattern: # untuk jaga-jaga out of index
                    break
                flag = True # kalau true ada yg masuk dari 1 pattern
                
                for k in range(len_pattern):
                    if sentence.tokens[j+k].tag != pattern_date[i][k]:
                        flag = False
                        break
                
                if flag:
                    if idx_date[i][0] == -1:
                        if self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text) != -1:
                            if idx_date[i][-1] == -1 and self.handle_tanggal(sentence.tokens[j + idx_date[i][1]].text) > 0 and self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text) > 0:
                                hari.append('-')
                                tgl.append(self.handle_tanggal(sentence.tokens[j + idx_date[i][1]].text))
                                bulan.append(self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text))
                                tahun.append(-999)
                            elif self.handle_tanggal(sentence.tokens[j + idx_date[i][1]].text) > 0 and self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text) > 0 and self.handle_tahun(sentence.tokens[j + idx_date[i][3]].text) > 0:
                                hari.append('-')
                                tgl.append(self.handle_tanggal(sentence.tokens[j + idx_date[i][1]].text))
                                bulan.append(self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text))
                                tahun.append(self.handle_tahun(sentence.tokens[j + idx_date[i][3]].text))
                            elif self.handle_tanggal(sentence.tokens[j + idx_date[i][3]].text) > 0 and self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text) > 0 and self.handle_tahun(sentence.tokens[j + idx_date[i][1]].text) > 0:
                                hari.append('-')
                                tahun.append(self.handle_tahun(sentence.tokens[j + idx_date[i][1]].text))
                                bulan.append(self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text))
                                tgl.append(self.handle_tanggal(sentence.tokens[j + idx_date[i][3]].text))
                        else:
                            continue
                    elif str(sentence.tokens[j + idx_date[i][0]].text).lower() not in day:
                        continue
                    elif len(idx_date[i]) == 4 and self.handle_tanggal(sentence.tokens[j + idx_date[i][1]].text) > 0 and self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text) > 0 and self.handle_tahun(sentence.tokens[j + idx_date[i][3]].text) > 0:
                        hari.append(str(sentence.tokens[j + idx_date[i][0]].text))
                        tgl.append(self.handle_tanggal(sentence.tokens[j + idx_date[i][1]].text))
                        bulan.append(self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text))
                        tahun.append(self.handle_tahun(sentence.tokens[j + idx_date[i][3]].text))
                    elif len(idx_date[i]) == 3 and self.handle_tanggal(sentence.tokens[j + idx_date[i][1]].text) > 0 and self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text) > 0:
                        hari.append(str(sentence.tokens[j + idx_date[i][0]].text))
                        tgl.append(self.handle_tanggal(sentence.tokens[j + idx_date[i][1]].text))
                        bulan.append(self.handle_bulan(sentence.tokens[j + idx_date[i][2]].text))
                        tahun.append(-999)
            
        return hari, tgl, bulan, tahun

    def toOriginal(self, teks):
            teks = teks.lower()
            hasil=''
            if(teks=='sulsel'):
                hasil='sulawesi selatan'
            elif(teks=='sultra'):
                hasil='sulawesi tenggara'
            elif(teks=='sulut'):
                hasil='sulawesi utara'
            elif(teks=='sulteng'):
                hasil='sulawesi tengah'
            elif(teks=='sulbar'):
                hasil='sulawesi barat'
            elif(teks=='kaltim'):
                hasil='kalimantan timur'
            elif(teks=='kaltara'):
                hasil='kalimantan utara'
            elif(teks=='kalteng'):
                hasil='kalimantan tengah'
            elif(teks=='kalsel'):
                hasil='kalimantan selatan'
            elif(teks=='kalbar'):
                hasil='kalimantan barat'
            elif(teks=='jatim'):
                hasil='jawa timur'
            elif(teks=='jateng'):
                hasil='jawa tengah'
            elif(teks=='solo' or teks=='surakarta' ):
                hasil='surakarta (solo)'
            elif(teks=='jabar'):
                hasil='jawa barat'
            elif(teks=='diy' or teks =='yogyakarta'):
                hasil='di yogyakarta'
            elif(teks=='jakbar'):
                hasil='jakarta barat'
            elif(teks=='jaktim'):
                hasil='jakarta timur'
            elif(teks=='jaksel'):
                hasil='jakarta selatan'
            elif(teks=='jakpus'):
                hasil='jakarta pusat'
            elif(teks=='jakut'):
                hasil='jakarta utara'
            elif(teks=='nad'):
                hasil='nanggroe aceh darussalam'
            elif(teks=='sumsel'):
                hasil='sumatera selatan'
            elif(teks=='sumut'):
                hasil='sumatera utara'
            elif(teks=='sumbar'):
                hasil='sumatera barat'
            elif(teks=='jakarta'):
                hasil='dki jakarta'
            else:
                hasil=teks
            return hasil

    def clean_koma(self, list, idx_list):
        val = []
        idx_val = []
        for j in range(len(list)):
            splitted = list[j].split(",")
            if len(splitted) == 1:
                val.append(self.toOriginal(list[j]))
                idx_val.append(idx_list[j])
            else:
                for i in range(len(splitted)):
                    val.append(self.toOriginal(splitted[i]))
                    idx_val.append(idx_list[j])
        return val, idx_val

    def ngrams_maker(self, words, idx_list):
        val = []
        left = []
        right = []
        i = 0
        temp = ""
        while i < len(words):
            if i+1 < len(words) and idx_list[i+1] - 1 == idx_list[i]:
                if temp:
                    temp1 = " ".join([temp, words[i+1]])
                    temp = temp1
                else:
                    temp = " ".join([words[i], words[i+1]])
                    left.append(idx_list[i])
            elif temp:
                val.append(temp)
                temp = ""
                right.append(idx_list[i])
            else:
                val.append(words[i])
                left.append(idx_list[i])
                right.append(idx_list[i])
            i += 1
        return val, left, right

    def punct_check(self, s):
        for ch in s:
            if ch in string.punctuation:
                return False
        return True

    def dedup_list(self, l):
        q = set(l)
        return list(q)

    def find_left_tag_text(self, tagged, idx):
        i = idx - 1
        while i >= 0:
            if tagged.tokens[i].tag == 'PROPN' or tagged.tokens[i].tag == 'CCONJ' or tagged.tokens[i].tag == 'NUM':
                i -= 1 
            else:
                return [tagged.tokens[i].tag, tagged.tokens[i].text, i]
        return ['', '', -1]

    def find_right_tag_text(self, tagged, idx):
        i = idx + 1
        while i < len(tagged):
            if tagged.tokens[i].tag == 'PROPN' or tagged.tokens[i].tag == 'CCONJ' or tagged.tokens[i].tag == 'NUM':
                i += 1 
            else:
                return [tagged.tokens[i].tag, tagged.tokens[i].text, i]
        return ['', '', -1]
    
    def getWhoWhereWhen(self, tagged, beritadate, beritaid):
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
        # ----------------------------------- WHEN
        # print("1", beritadate, beritaid)
        dates = []
        sentences = []

        # find date
        for i in range(len(tagged)):
            result = '-'
            beritadate[i] = beritadate[i].replace(" WIB","")
            # date_format = datetime.strptime(beritadate[i], "%A, %d %b %Y %H:%M")
            sentences.append(tagged[i])
            sentence = tagged[i]
            hari, tgl, bulan, tahun = self.find_date(sentence)
            if hari:
                idx = -1
                max = 0
                tahun_now = datetime.strptime(beritadate[i], "%A, %d %b %Y %H:%M").year
                for j in range(len(tahun)):
                    if tahun[j] == -999:
                        tahun[j] = tahun_now
                    if max < tahun[j]:
                        max = tahun[j]
                for j in range(len(tahun)):
                    if tahun[j] != -1 and max == tahun[j]:
                        tahun = tahun[j]
                        idx = j
                        break
                if idx == -1 or tahun == -999:
                    tahun = datetime.strptime(beritadate[i], "%A, %d %b %Y %H:%M").year
                    tgl = tgl[0]
                    bulan = bulan[0]
                else:
                    tgl = tgl[idx]
                    bulan = bulan[idx]
                result = self.write_date(tgl, bulan, tahun)
                # print(result)
            # else:
            #     print('-----')
            # print("1" + beritadate[i])
            # print("1")
            if result == '-':
                tahun = datetime.strptime(beritadate[i], "%A, %d %b %Y %H:%M").year
                bulan = datetime.strptime(beritadate[i], "%A, %d %b %Y %H:%M").month
                tgl = datetime.strptime(beritadate[i], "%A, %d %b %Y %H:%M").day
                # print("1")
                result = self.write_date(tgl, bulan, tahun)
            dates.append(result)

        # df_dates.to_csv(PATH + 'date_tagged_result_v2_' + n + '.csv')
        # print("1")
        # ----------------------------------- WHERE
        locations = []
        countries = [] # untuk ekonomi

        for i in range(len(tagged)):
            # print(tagged[i])
            propn_list = [] # untuk semua 'propn'
            idx_list = []
            adp_idx = [] # untuk 'di' + propn
            
            # save each propn words to list
            for j in range(0, len(tagged[i])):
                if tagged[i].tokens[j].tag == 'PROPN':
                    idx_list.append(j)
                    propn_list.append(tagged[i].tokens[j].text)
                if tagged[i].tokens[j].text == 'di' or tagged[i].tokens[j].text == 'ke':
                    adp_idx.append(j)
            # print(adp_idx)
            # create bigrams and trigrams
            bigrams = []
            bigrams_idx = []
            trigrams = []
            trigrams_idx = []

            # check bigrams
            for j in range(1,len(idx_list)):
                if idx_list[j] - 1 == idx_list[j-1]:
                    bigrams.append([propn_list[j-1], propn_list[j]])
                    bigrams_idx.append([idx_list[j-1], idx_list[j]])

            for j in range(1, len(bigrams_idx)):
                if bigrams_idx[j][0] == bigrams_idx[j-1][1]:
                    trigrams.append([bigrams[j-1][0], bigrams[j-1][1], bigrams[j][1]])
                    trigrams_idx.append([bigrams_idx[j-1][0], bigrams_idx[j-1][1], bigrams_idx[j][1]])

            def check_list(text, list):
                val = text.lower()
                for x in list:
                    if val == x:
                        return True
                return False
            
            propn_list, idx_list = self.clean_koma(propn_list, idx_list)
            res = []

            # check kec
            for j in range(len(trigrams)):
                joined = " ".join(trigrams[j])
                if check_list(self.toOriginal(joined), self.kec) or check_list(self.toOriginal(joined), self.kab) or check_list(self.toOriginal(joined), self.prov):
                    res.append([trigrams_idx[j][0], self.toOriginal(joined)])
            for j in range(len(bigrams)):
                joined = " ".join(bigrams[j])
                if check_list(self.toOriginal(joined), self.kec) or check_list(self.toOriginal(joined), self.kab) or check_list(self.toOriginal(joined), self.prov):
                    res.append([bigrams_idx[j][0], self.toOriginal(joined)])
            for j in range(len(propn_list)):
                if check_list(propn_list[j], self.kec) or check_list(propn_list[j], self.kab) or check_list(propn_list[j], self.prov):
                    res.append([idx_list[j], propn_list[j]])
            
            # remove child grams if there's bigram or trigram
            temp = []
            flag_idx = []
            remove_idx = []
            for j in range(len(res)):
                if res[j][0] not in flag_idx:
                    flag_idx.append(res[j][0])
                else:
                    remove_idx.append(j)
            for j in range(len(res)):
                if j in remove_idx:
                    continue
                temp.append(res[j])
            res = temp

            # print(res)
            res_lower = []
            for j in range(len(res)):
                res_lower.append(res[j][1].lower())

            kec_idx = []
            kab_idx = []
            prov_idx = []
            # catch frasa Kecamatan, Kabupaten, Provinsi
            for j in range(len(propn_list)-2):
                if propn_list[j] == 'kecamatan':
                    kec_idx.append(idx_list[j])
                elif propn_list[j] == 'kabupaten' or propn_list[j] == 'kota':
                    kab_idx.append(idx_list[j])
                elif propn_list[j] == 'provinsi':
                    prov_idx.append(idx_list[j])
            # eval/validate found lists
            trueKec = []
            trueKab = []
            trueProv = []
            
            for loc in res:
                if loc[0] - 1 in kec_idx:
                    trueKec.append(loc[1])
                elif loc[0] - 1 in kab_idx:
                    trueKab.append(loc[1])
                elif loc[0] - 1 in prov_idx:
                    trueProv.append(loc[1])
            # print([(trueKec), (trueKab), (trueProv)])
            trueLocation = []
            for x in self.daerah:
                for loc in trueKec:
                    if loc.lower() == x[2]:
                        if x[1] in res_lower:
                            trueLocation.append([x[2], x[1], x[0]])
                for loc in trueKab:
                    if loc.lower() == x[1]:
                        if x[0] in res_lower:
                            trueLocation.append([x[1], x[0]])
                        else:
                            trueLocation.append([x[1], x[0]])
            for x in trueProv:
                trueLocation.append([x.lower()])

            if len(trueLocation) == 0: # jika tidak ada istilah 'Kecamatan', 'Kabupaten' , 'Kota', 'Provinsi'
                for x in self.daerah: # cek apakah terdapat kabupaten atau provinsi, kecamatan akan masuk juga jika ada kab/prov
                    for loc in res_lower:
                        if loc == x[2]: # loc in kecamatan
                            if x[0] in res_lower: # kecamatan provinsi masuk
                                trueLocation.append([x[2], x[1], x[0]])
                            if x[2] == x[1]: # jika kecamatan == kabupaten (ex: sampang sampang)
                                continue
                            if x[1] in res_lower: # kecamatan kabupaten masuk
                                trueLocation.append([x[2], x[1], x[0]])
                        elif loc == x[1]: # loc in kabupaten
                            if x[0] == x[1]: # jika provinsi == kabupaten (ex: jambi jambi)
                                continue
                            if x[0] in res_lower: # kabupaten provinsi masuk
                                trueLocation.append([x[1], x[0]])
                        #     else:
                        #         trueLocation.append([x[1], x[0]])
                        # elif loc == x[0]:
                        #     trueLocation.append([x[0]])
                if len(trueLocation) == 0:
                    # print(adp_idx)
                    for j in range(len(adp_idx)): # jika terdapat kata 'di' preposisi, maka cek kata setelahnya yg mengandung daerah
                        for k in res:
                            if adp_idx[j] < k[0] and k[0] - adp_idx[j] < 14: #jika jarak lebih dari 13, maka sudah tidak berkaitan
                                for x in self.daerah:
                                    if k[1] == x[0]: #jika provinsi
                                        trueLocation.append([x[0]])
                                    elif k[1] == x[1]: #jika kabupaten
                                        trueLocation.append([x[1], x[0]])
                                    # elif k[1] == x[2]: #jika kecamatan
                                    #     trueLocation.append([x[2], x[1], x[0]])
                    # trueLocation.sort(key = len)
                else:
                    trueLocation.sort(key = len, reverse=True)
            else:
                trueLocation.sort(key = len, reverse=True)

            # for ekonomi
            # trueNegara = []
            # for j in range(len(propn_list)):
            #     if propn_list[j].lower() in self.negara:
            #         trueNegara.append(propn_list[j].lower())
            temp_prov = '-'
            # if trueNegara and n == 'ekonomi':
            #     if trueNegara[0] == 'indonesia':
            #         temp_prov = 'dki jakarta'
            #     countries.append(trueNegara[0])
            # else:
            #     countries.append('-')

            if trueLocation:
                # print(i, trueLocation[0], '||', berita['ner_kec'], berita['ner_kab'], berita['ner_prov'])
                if len(trueLocation[0]) == 3:
                    locations.append([trueLocation[0][0], trueLocation[0][1], trueLocation[0][2]])
                elif len(trueLocation[0]) == 2:
                    locations.append(['-',trueLocation[0][0], trueLocation[0][1]])
                elif len(trueLocation[0]) == 1:
                    locations.append(['-', '-', trueLocation[0][0]])
            else:
                # print(i, '-'*10, berita['ner_kec'], berita['ner_kab'], berita['ner_prov'])
                locations.append(['-', '-', temp_prov])
        # print("1")       

        locations1 = []
        locations2 = []
        locations3 = []
        for i in range(len(locations)):
            locations1.append(locations[i][0])
            locations2.append(locations[i][1])
            locations3.append(locations[i][2])

        # ----------------------------------- WHO

        entities = []

        for i in range(len(tagged)):
            # print(tagged[i])
            propn_list = []
            idx_list = []
            
            # save each propn words to list
            for j in range(1, len(tagged[i])):
                teks = tagged[i].tokens[j].text.lower()
                if tagged[i].tokens[j].tag == 'PROPN' and tagged[i].tokens[j].text[0].isupper() and self.punct_check(teks) and \
                    teks not in day and teks not in month and teks not in kata_excl and teks not in self.kec and teks not in self.kab and self.toOriginal(teks) not in self.prov:
                    idx_list.append(j)
                    propn_list.append(tagged[i].tokens[j].text)
            # print(propn_list)
            right_idx = []
            left_idx = []
            all_propn = []

            all_propn, left_idx, right_idx = self.ngrams_maker(propn_list, idx_list)
            # print(all_propn, left_idx, right_idx)
            
            filtered_propn = []
            for j in range(len(all_propn)):
                lower_propn = all_propn[j].lower()
                if lower_propn in self.kec and lower_propn in self.kab and lower_propn in self.prov:
                    continue
                # AUX = adalah, telah
                # PART = tidak
                # ADP = di, ke, dalam
                # DET = ini, itu, tersebut
                # SCONJ = saat

                # check left
                if left_idx[j] - 2 >= 0:
                    left_tag = tagged[i].tokens[left_idx[j] - 1].tag
                    left_text = tagged[i].tokens[left_idx[j] - 1].text
                    left_left_tag = tagged[i].tokens[left_idx[j] - 2].tag
                    if left_tag == 'PROPN':
                        temp = self.find_left_tag_text(tagged[i], left_idx[j] - 1)
                        if temp:
                            left_tag = temp[0]
                            left_text = temp[1]
                            temp = self.find_left_tag_text(tagged[i], temp[2] - 1)
                            left_left_tag = temp[0]
                            left_left_text = temp[1]
                    if left_tag == 'VERB' or (left_left_tag == 'VERB' and left_tag == 'AUX'):
                        if (right_idx[j] + 1 < len(tagged[i]) and (tagged[i].tokens[right_idx[j] + 1].tag == 'ADP' or tagged[i].tokens[right_idx[j] + 1].tag == 'NUM')):
                            continue
                        filtered_propn.append(all_propn[j])
                        continue
                # check right
                if right_idx[j] + 2 < len(tagged[i]):
                    right_tag = tagged[i].tokens[right_idx[j] + 1].tag
                    right_right_tag = tagged[i].tokens[right_idx[j] + 2].tag
                    right_text = tagged[i].tokens[right_idx[j] + 1].text
                    right_right_text = tagged[i].tokens[right_idx[j] + 2].text
                    if right_tag == 'PROPN':
                        temp = self.find_right_tag_text(tagged[i], right_idx[j] + 1)
                        if temp:
                            right_tag = temp[0]
                            right_text = temp[1]
                            temp = self.find_right_tag_text(tagged[i], temp[2] + 1)
                            right_right_tag = temp[0]
                            right_right_text = temp[1]
                    if right_tag == 'VERB' or \
                        (right_tag == 'PUNCT' and right_text == '.') or \
                        ((right_tag == 'AUX' or right_tag == 'PART' or right_tag == 'SCONJ') and right_right_tag == 'VERB'):
                        if (left_idx[j] - 1 >= 0 and tagged[i].tokens[left_idx[j] - 1].tag == 'NUM') or \
                            tagged[i].tokens[right_idx[j] + 1].text == 'ada':
                            continue
                        filtered_propn.append(all_propn[j])
                        continue
                    # check both
                    if left_idx[j] - 2 >= 0:
                        left_tag = tagged[i].tokens[left_idx[j] - 1].tag
                        left_text = tagged[i].tokens[left_idx[j] - 1].text
                        left_left_tag = tagged[i].tokens[left_idx[j] - 2].tag
                        right_tag = tagged[i].tokens[right_idx[j] + 1].tag
                        right_text = tagged[i].tokens[right_idx[j] + 1].text
                        right_right_tag = tagged[i].tokens[right_idx[j] + 2].tag
                        if right_tag == 'PROPN':
                            temp = self.find_right_tag_text(tagged[i], right_idx[j] + 1)
                            if temp:
                                right_tag = temp[0]
                                right_text = temp[1]
                                temp = self.find_right_tag_text(tagged[i], temp[2] + 1)
                                right_right_tag = temp[0]
                                right_right_text = temp[1]
                        if left_tag == 'PROPN':
                            temp = self.find_left_tag_text(tagged[i], left_idx[j] - 1)
                            if temp:
                                left_tag = temp[0]
                                left_text = temp[1]
                                temp = self.find_left_tag_text(tagged[i], temp[2] - 1)
                                left_left_tag = temp[0]
                                left_left_text = temp[1]
                        #add sconj to right tag
                        if left_tag == 'NOUN' and ((left_text == 'kata' and right_tag == 'PUNCT') or right_tag == 'DET' or (right_tag == 'ADP' and right_text == 'dalam' or right_text == 'di' or right_text == 'kepada') or right_text == ',') or \
                            (left_tag == 'PUNCT' and left_text == ',' and ((right_tag == 'PUNCT' and right_text == ',') or right_tag == 'ADP')) or \
                            (left_tag == 'PUNCT' and left_text == '.' and right_tag == 'PUNCT' and right_text == ','):
                            filtered_propn.append(all_propn[j])
                
            filtered_propn = self.dedup_list(filtered_propn)
            # print(filtered_propn)
            entities.append(", ".join(filtered_propn))
        # print("1")
        for i in range(len(tagged)):
            self.save_to_mysql(beritaid[i], dates[i], entities[i], locations3[i], locations2[i], locations1[i])
        return True
    
    def sentence_mini_batch(self, berita):
        # tagged = []
        small_batch = []
        batch_size = self.batch_size
        batch_iter = 1
        for i in range((batch_iter-1)*batch_size, len(berita)):
            if len(small_batch) == batch_size:
                self.tag_pos.predict(small_batch)
                self.getWhoWhereWhen(small_batch, self.dateberita[i-batch_size:i], self.idberita[i-batch_size:i])
                # for j in range(len(small_batch)):
                #     tagged.append(small_batch[j])
                # joblib.dump(tagged, 'D:/PetaKabar/whowherewhen/all_tagged_'+ iter_through[x-1] + '_' + str(batch_iter) + '.pkl')
                small_batch = []
                # tagged = []
                print(batch_iter)
                time.sleep(10)
                batch_iter += 1
            text = berita[i]
            preprocessed_text = self.__preprocessing(text)
            sentence = Sentence(preprocessed_text)
            small_batch.append(sentence)

        if len(small_batch) != 0:
            self.tag_pos.predict(small_batch)
            self.getWhoWhereWhen(small_batch, self.dateberita[(batch_iter-1)*batch_size:((batch_iter-1)*batch_size)+len(small_batch)], self.idberita[(batch_iter-1)*batch_size:((batch_iter-1)*batch_size)+len(small_batch)])
            # for j in range(len(small_batch)):
                # tagged.append(small_batch[j])
            # joblib.dump(tagged, 'D:/PetaKabar/whowherewhen/all_tagged_'+ iter_through[x-1] + '_' + str(batch_iter) + '.pkl')
            small_batch = []
            # tagged = []
            batch_iter += 1
        return batch_iter

    def get3W(self):
        try:
            self.sentence_mini_batch(self.descberita)
            return 'success'
        except:
            return 'error'
    
    def save_to_mysql(self, idberita, when, who, provinsi, kabupaten, kecamatan):
        try:
            conn = mysql.connector.connect(user = 'root', password='', database = 'Petakabar')
            cur = conn.cursor()
            add_news = ("UPDATE berita "
                "SET ner_when = %s, ner_who = %s, ner_prov = %s, ner_kab = %s, ner_kec = %s "
            "WHERE ID = %s"
            )
            # whostr = ""
            # for y in range(len(who)):
            #     whostr = whostr + who[y]
            #     if y < len(who)-1:
            #         whostr = whostr + ", "
            data_news = (when, who, provinsi, kabupaten, kecamatan, idberita)
            print(data_news)
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