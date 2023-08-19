from typing import Dict, List
from xmlrpc.client import boolean
from nltk.tag import CRFTagger
import pandas as pd
from nltk import word_tokenize
import re
import random
from typing import List
import mysql.connector
from mysql.connector import errorcode

class Severity:
    def __init__(self) -> None:
        self.ct =CRFTagger()
        # self.ct.set_model_file('model/TagIndo/all_indo_man_tag_corpus_model.crf.tagger')
        self.ct.set_model_file('D:/Repository/PetaKabar/ekonomi/model/TagIndo/all_indo_man_tag_corpus_model.crf.tagger')
        # self.scrapped_news = pd.read_csv('result/4w/4w_news.csv')

        #ambil data dari db
        self.newsscrapped = []
        try:
            cnx = mysql.connector.connect(user='admin', password='admin', database = 'Petakabar')
            cursor = cnx.cursor()
            cursor.execute("SELECT ID, berita_desc FROM berita where berita_topik_id = 2 AND class_classification is null")
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

    def __preprocessingKeparahan(self, berita: str):
        s = berita
        s = s.replace('\n', ' ')
        s = s.replace('\r', ' ')
        s = re.sub("\(.*?\)", "", s)
        # s = s.lower()
        tokens = word_tokenize(s)
        return tokens

    def structureCheck(self,indeks: int,arr: List[str]) -> int:
        if(arr[0][indeks][1]=='VB' or arr[0][indeks][1]=='IN' or arr[0][indeks][1]=='NN' or arr[0][indeks][1]=='NNP' or arr[0][indeks][1]=='SC' or arr[0][indeks][1]=='JJ' or arr[0][indeks][1]=='PR'  or arr[0][indeks][1]=='NND'  or arr[0][indeks][1]=='RB'  or arr[0][indeks][1]=='SYM'  or arr[0][indeks][1]=='RP' or arr[0][indeks][1]=='PRP' or arr[0][indeks][1]=='DT' or arr[0][indeks][1]=='FW' or arr[0][indeks][1]=='MD' or arr[0][indeks][1]=='NEG' or arr[0][indeks][1]=='UH' or arr[0][indeks][1]=='VH'):
            return 1
        else:
            return 0
    def cdStructureCheck(self,indeks: int,arr: List[str]) -> int:
        if(arr[0][indeks][1]=='CD' or arr[0][indeks][1]=='OD' or arr[0][indeks][0]=='Sang' or arr[0][indeks][0]=='sang' or arr[0][indeks][0]=='Seorang'  or arr[0][indeks][0]=='seorang'  or arr[0][indeks][0]=='seseorang' or arr[0][indeks][0]=='Seseorang' or arr[0][indeks][0]=='Empat' or arr[0][indeks][0]=='Lima' or arr[0][indeks][0]=='Enam' or arr[0][indeks][0]=='Tujuh' or arr[0][indeks][0]=='Delapan' or arr[0][indeks][0]=='Sembilan' or arr[0][indeks][0]=='Sepuluh'  or arr[0][indeks][0]=='Pasangan'  or arr[0][indeks][0]=='pasangan'  or arr[0][indeks][0]=='belasan'  or arr[0][indeks][0]=='Belasan'):
            return 1
        else:
            return 0
    
    def struktur1(self,arr: List[str],indeks: int):
        
        if(indeks-2>=0 
            and self.cdStructureCheck(indeks-1,arr) 
            and self.cdStructureCheck(indeks-2,arr)):
            return (arr[0][indeks-2][0] + ' ' + arr[0][indeks-1][0])
        elif(indeks+2<=len(arr[0])-1 
            and self.cdStructureCheck(indeks+1,arr) 
            and self.cdStructureCheck(indeks+2,arr)):
            return (arr[0][indeks+1][0] + ' ' + arr[0][indeks+2][0])
        elif(indeks-1>=0 
            and self.cdStructureCheck(indeks-1,arr)):
            return arr[0][indeks-1][0]
        elif(indeks+1<=len(arr[0])-1 
            and self.cdStructureCheck(indeks+1,arr)):
            return arr[0][indeks+1][0]
        elif(indeks-3>=0 
            and self.structureCheck(indeks-1,arr) 
            and self.cdStructureCheck(indeks-2,arr) and self.cdStructureCheck(indeks-3,arr)):
            return (arr[0][indeks-3][0] + ' ' + arr[0][indeks-2][0])
        elif(indeks+3<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) 
            and self.cdStructureCheck(indeks+2,arr) and self.cdStructureCheck(indeks+3,arr)):
            return (arr[0][indeks+2][0] + ' ' + arr[0][indeks+3][0])
        elif(indeks-2>=0 
            and self.structureCheck(indeks-1,arr) 
            and self.cdStructureCheck(indeks-2,arr)):
            return arr[0][indeks-2][0]
        elif(indeks+2<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) 
            and self.cdStructureCheck(indeks+2,arr)):
            return arr[0][indeks+2][0]
        elif(indeks-4>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) 
            and self.cdStructureCheck(indeks-3,arr) and self.cdStructureCheck(indeks-4,arr)):
            return (arr[0][indeks-4][0] + ' ' + arr[0][indeks-3][0])
        elif(indeks+4<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) 
            and self.cdStructureCheck(indeks+3,arr) and self.cdStructureCheck(indeks+4,arr)):
            return (arr[0][indeks+3][0] + ' ' + arr[0][indeks+4][0])
        elif(indeks-3>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) 
            and self.cdStructureCheck(indeks-3,arr)):
            return arr[0][indeks-3][0]
        elif(indeks+3<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) 
            and self.cdStructureCheck(indeks+3,arr)):
            return arr[0][indeks+3][0]
        elif(indeks-5>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) 
            and self.cdStructureCheck(indeks-4,arr) and self.cdStructureCheck(indeks-5,arr)):
            return (arr[0][indeks-5][0] + ' ' + arr[0][indeks-4][0])
        elif(indeks+5<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) 
            and self.cdStructureCheck(indeks+4,arr) and self.cdStructureCheck(indeks+5,arr)):
            return (arr[0][indeks+4][0] + ' ' + arr[0][indeks+5][0])
        elif(indeks-4>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) 
            and self.cdStructureCheck(indeks-4,arr)):
            return arr[0][indeks-4][0]
        elif(indeks+4<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) 
            and self.cdStructureCheck(indeks+4,arr)):
            return arr[0][indeks+4][0]
        elif(indeks-6>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.cdStructureCheck(indeks-5,arr) and self.cdStructureCheck(indeks-6,arr)):
            return (arr[0][indeks-6][0] + ' ' + arr[0][indeks-5][0])
        elif(indeks+6<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.cdStructureCheck(indeks+5,arr) and self.cdStructureCheck(indeks+6,arr)):
            return (arr[0][indeks+5][0] + ' ' + arr[0][indeks+6][0])
        elif(indeks-5>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.cdStructureCheck(indeks-5,arr)):
            return arr[0][indeks-5][0]
        elif(indeks+5<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.cdStructureCheck(indeks+5,arr)):
            return arr[0][indeks+5][0]
        elif(indeks-7>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) 
            and self.cdStructureCheck(indeks-6,arr) and self.cdStructureCheck(indeks-7,arr)):
            return (arr[0][indeks-7][0] + ' ' + arr[0][indeks-6][0])
        elif(indeks+7<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) 
            and self.cdStructureCheck(indeks+6,arr) and self.cdStructureCheck(indeks+7,arr)):
            return (arr[0][indeks+6][0] + ' ' + arr[0][indeks+7][0])
        elif(indeks-6>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) 
            and self.cdStructureCheck(indeks-6,arr)):
            return arr[0][indeks-6][0]
        elif(indeks+6<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) 
            and self.cdStructureCheck(indeks+6,arr)):
            return arr[0][indeks+6][0]
        elif(indeks-8>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) 
            and self.cdStructureCheck(indeks-7,arr) and self.cdStructureCheck(indeks-8,arr)):
            return (arr[0][indeks-8][0] + ' ' + arr[0][indeks-7][0])
        elif(indeks+8<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) 
            and self.cdStructureCheck(indeks+7,arr) and self.cdStructureCheck(indeks+8,arr)):
            return (arr[0][indeks+7][0] + ' ' + arr[0][indeks+8][0])
        elif(indeks-7>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) 
            and self.cdStructureCheck(indeks-7,arr)):
            return arr[0][indeks-7][0]
        elif(indeks+7<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) 
            and self.cdStructureCheck(indeks+7,arr)):
            return arr[0][indeks+7][0]
        elif(indeks-9>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) 
            and self.cdStructureCheck(indeks-8,arr) and self.cdStructureCheck(indeks-9,arr)):
            return (arr[0][indeks-9][0] + ' ' + arr[0][indeks-8][0])
        elif(indeks+9<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) 
            and self.cdStructureCheck(indeks+8,arr) and self.cdStructureCheck(indeks+9,arr)):
            return (arr[0][indeks+8][0] + ' ' + arr[0][indeks+9][0])
        elif(indeks-8>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) 
            and self.cdStructureCheck(indeks-8,arr)):
            return arr[0][indeks-8][0]
        elif(indeks+8<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) 
            and self.cdStructureCheck(indeks+8,arr)):
            return arr[0][indeks+8][0]
        elif(indeks-10>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.cdStructureCheck(indeks-9,arr) and self.cdStructureCheck(indeks-10,arr)):
            return (arr[0][indeks-10][0] + ' ' + arr[0][indeks-9][0])
        elif(indeks+10<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.cdStructureCheck(indeks+9,arr) and self.cdStructureCheck(indeks+10,arr)):
            return (arr[0][indeks+9][0] + ' ' + arr[0][indeks+10][0])
        elif(indeks-9>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.cdStructureCheck(indeks-9,arr)):
            return arr[0][indeks-9][0]
        elif(indeks+9<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.cdStructureCheck(indeks+9,arr)):
            return arr[0][indeks+9][0]
        elif(indeks-11>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) 
            and self.cdStructureCheck(indeks-10,arr) and self.cdStructureCheck(indeks-11,arr)):
            return (arr[0][indeks-11][0] + ' ' + arr[0][indeks-10][0])
        elif(indeks+11<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) 
            and self.cdStructureCheck(indeks+10,arr) and self.cdStructureCheck(indeks+11,arr)):
            return (arr[0][indeks+10][0] + ' ' + arr[0][indeks+11][0])
        elif(indeks-10>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) 
            and self.cdStructureCheck(indeks-10,arr)):
            return arr[0][indeks-10][0]
        elif(indeks+10<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) 
            and self.cdStructureCheck(indeks+10,arr)):
            return arr[0][indeks+10][0]
        elif(indeks-12>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) 
            and self.cdStructureCheck(indeks-11,arr) and self.cdStructureCheck(indeks-12,arr)):
            return (arr[0][indeks-12][0] + ' ' + arr[0][indeks-11][0])
        elif(indeks+12<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) 
            and self.cdStructureCheck(indeks+11,arr) and self.cdStructureCheck(indeks+12,arr)):
            return (arr[0][indeks+11][0] + ' ' + arr[0][indeks+12][0])
        elif(indeks-11>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) 
            and self.cdStructureCheck(indeks-11,arr)):
            return arr[0][indeks-11][0]
        elif(indeks+11<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) 
            and self.cdStructureCheck(indeks+11,arr)):
            return arr[0][indeks+11][0]
        elif(indeks-13>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) and self.structureCheck(indeks-11,arr) 
            and self.cdStructureCheck(indeks-12,arr) and self.cdStructureCheck(indeks-13,arr)):
            return (arr[0][indeks-13][0] + ' ' + arr[0][indeks-12][0])
        elif(indeks+13<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) and self.structureCheck(indeks+11,arr) 
            and self.cdStructureCheck(indeks+12,arr) and self.cdStructureCheck(indeks+13,arr)):
            return (arr[0][indeks+12][0] + ' ' + arr[0][indeks+13][0])
        elif(indeks-12>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) and self.structureCheck(indeks-11,arr) 
            and self.cdStructureCheck(indeks-12,arr)):
            return arr[0][indeks-12][0]
        elif(indeks+12<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) and self.structureCheck(indeks+11,arr) 
            and self.cdStructureCheck(indeks+12,arr)):
            return arr[0][indeks+12][0]
        elif(indeks-14>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) and self.structureCheck(indeks-11,arr) and self.structureCheck(indeks-12,arr) 
            and self.cdStructureCheck(indeks-13,arr) and self.cdStructureCheck(indeks-14,arr)):
            return (arr[0][indeks-14][0] + ' ' + arr[0][indeks-13][0])
        elif(indeks+14<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) and self.structureCheck(indeks+11,arr) and self.structureCheck(indeks+12,arr) 
            and self.cdStructureCheck(indeks+13,arr) and self.cdStructureCheck(indeks+14,arr)):
            return (arr[0][indeks+13][0] + ' ' + arr[0][indeks+14][0])
        elif(indeks-13>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) and self.structureCheck(indeks-11,arr) and self.structureCheck(indeks-12,arr) 
            and self.cdStructureCheck(indeks-13,arr)):
            return arr[0][indeks-13][0]
        elif(indeks+13<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) and self.structureCheck(indeks+11,arr) and self.structureCheck(indeks+12,arr) 
            and self.cdStructureCheck(indeks+13,arr)):
            return arr[0][indeks+13][0]
        elif(indeks-15>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) and self.structureCheck(indeks-11,arr) and self.structureCheck(indeks-12,arr) 
            and self.structureCheck(indeks-13,arr) 
            and self.cdStructureCheck(indeks-14,arr) and self.cdStructureCheck(indeks-15,arr)):
            return (arr[0][indeks-15][0] + ' ' + arr[0][indeks-14][0])
        elif(indeks+15<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) and self.structureCheck(indeks+11,arr) and self.structureCheck(indeks+12,arr) 
            and self.structureCheck(indeks+13,arr) 
            and self.cdStructureCheck(indeks+14,arr) and self.cdStructureCheck(indeks+15,arr)):
            return (arr[0][indeks+14][0] + ' ' + arr[0][indeks+15][0])
        elif(indeks-14>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) and self.structureCheck(indeks-11,arr) and self.structureCheck(indeks-12,arr) 
            and self.structureCheck(indeks-13,arr) 
            and self.cdStructureCheck(indeks-14,arr)):
            return arr[0][indeks-14][0]
        elif(indeks+14<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) and self.structureCheck(indeks+11,arr) and self.structureCheck(indeks+12,arr) 
            and self.structureCheck(indeks+13,arr) 
            and self.cdStructureCheck(indeks+14,arr)):
            return arr[0][indeks+14][0]
        elif(indeks-15>=0 
            and self.structureCheck(indeks-1,arr) and self.structureCheck(indeks-2,arr) and self.structureCheck(indeks-3,arr) and self.structureCheck(indeks-4,arr) 
            and self.structureCheck(indeks-5,arr) and self.structureCheck(indeks-6,arr) and self.structureCheck(indeks-7,arr) and self.structureCheck(indeks-8,arr) 
            and self.structureCheck(indeks-9,arr) and self.structureCheck(indeks-10,arr) and self.structureCheck(indeks-11,arr) and self.structureCheck(indeks-12,arr) 
            and self.structureCheck(indeks-13,arr) and self.structureCheck(indeks-14,arr) 
            and self.cdStructureCheck(indeks-15,arr)):
            return arr[0][indeks-15][0]
        elif(indeks+15<=len(arr[0])-1 
            and self.structureCheck(indeks+1,arr) and self.structureCheck(indeks+2,arr) and self.structureCheck(indeks+3,arr) and self.structureCheck(indeks+4,arr) 
            and self.structureCheck(indeks+5,arr) and self.structureCheck(indeks+6,arr) and self.structureCheck(indeks+7,arr) and self.structureCheck(indeks+8,arr) 
            and self.structureCheck(indeks+9,arr) and self.structureCheck(indeks+10,arr) and self.structureCheck(indeks+11,arr) and self.structureCheck(indeks+12,arr) 
            and self.structureCheck(indeks+13,arr) and self.structureCheck(indeks+14,arr) 
            and self.cdStructureCheck(indeks+15,arr)):
            return arr[0][indeks+15][0]
        else:
            return 1

        
    def isfloat(self,num):
        try:
            float(num)
            return True
        except ValueError:
            return False
    
    def convertTeks(self,string: str):
        string = string.lower()
        string = string.split()
        string = [x.replace(',','.') for x in string]
        
        arr = []

        if(len(string)==2 and self.isfloat(string[0])==True  and string[1]=='juta'):
            hasil="{:.0f}".format(float(string[0])*1000000)
            arr.append(hasil)
        elif(len(string)==2 and self.isfloat(string[0])==True  and string[1]=='ribu'):
            hasil="{:.0f}".format(float(string[0])*1000)
            arr.append(hasil)
        elif(len(string)==2 and self.isfloat(string[0])==True  and string[1]=='miliar'):
            hasil="{:.0f}".format(float(string[0])*1000000000)
            arr.append(hasil)
        elif(len(string)==2 and self.isfloat(string[0])==True  and string[1]=='triliun'):
            hasil="{:.0f}".format(float(string[0])*1000000000000)
            arr.append(hasil)
        else:
            for teks in string:
                if(teks[-1:]=='%' and (teks[:-1].isdigit() or self.isfloat(teks[:-1])==True)):
                    arr.append(str(teks))
                elif(len(teks)==5 and teks[2]=='.' and self.isfloat(teks)==True):
                    arr.append(str(1))
                elif(len(teks)>=5 and teks[-4]=='.' and self.isfloat(teks)==True):
                    teks=teks.replace('.','')
                    arr.append(teks)
                elif(teks=="2010" or teks=="2011" or teks=="2012" or teks=="2013" or teks=="2014" or teks=="2015" or teks=="2016" or teks=="2017" or teks=="2018" or teks=="2019" or teks=="2020" or teks=="2021" or teks=="2022"):
                    arr.append(str(1))
                elif(self.isfloat(teks)==True):
                    arr.append(teks)
                elif(teks=="satu" or teks=="seorang" or teks=="seseorang" or teks=="sesosok" or teks=="sang" or teks=="sedikit" or teks=="suatu" or teks=='pertama' or teks=='sebagian' or teks=='paruh'):
                    arr.append(str(1))
                elif(teks=="dua" or teks=="kedua" or teks=="keduanya" or teks=="pasangan" or teks=='ke-2'):
                    arr.append(str(2))
                elif(teks=="tiga" or teks=="ketiga" or teks=='ke-3'):
                    arr.append(str(3))
                elif(teks=="empat" or teks=="keempat" or teks=='ke-4'):
                    arr.append(str(4))
                elif(teks=="lima" or teks=="kelima" or teks=='ke-5'):
                    arr.append(str(5))
                elif(teks=="enam"  or teks=="keenam" or teks=='ke-6'):
                    arr.append(str(6))
                elif(teks=="tujuh"  or teks=="ketujuh" or teks=='ke-7'):
                    arr.append(str(7))
                elif(teks=="delapan"  or teks=="kedelapan" or teks=='ke-8'):
                    arr.append(str(8))
                elif(teks=="sembilan"  or teks=="kesembilan" or teks=='ke-9'):
                    arr.append(str(9))
                elif(teks=="sepuluh"  or teks=="kesepuluh" or teks=="puluhan" or teks=='ke-10'):
                    arr.append(str(10))
                elif(teks=="salah" or teks=="sebanyak" or teks=="akibatnya"):
                    arr.append('')
                elif(teks=="persen"):
                    arr.append('%')
                elif(teks=="belasan"):
                    arr.append(str(11))

                #Banyak yang di bawah ini tergantung topik masing2
                elif(teks=="semua"):
                    arr.append(str(random.randint(1,5)))
                elif(teks=="sejumlah"):
                    arr.append(str(random.randint(6,10)))
                elif(teks=="seluruh"):
                    arr.append(str(random.randint(6,15)))
                elif(teks=="beberapa"):
                    arr.append(str(random.randint(1,5)))
                elif(teks=="banyak"):
                    arr.append(str(random.randint(1,5)))
                elif(teks=="puluh"):
                    arr.append(str(0))
                elif(teks=="ratus"):
                    arr.append(str(00))
                elif(teks=="ratusan"):
                    arr.append(str(100))
                elif(teks=="ribuan"):
                    arr.append(str(1000))
                elif(teks=="ribu"):
                    arr.append(str(000))
                elif(teks=="jutaan"):
                    arr.append(str(1000000))
                elif(teks=="juta"):
                    arr.append(str(000000))
                elif(teks=="miliar"):
                    arr.append(str(000000000))
                elif(teks=="miliaran"):
                    arr.append(str(1000000000))
                elif(teks=="triliun"):
                    arr.append(str(000000000000))
                elif(teks=="triliunan"):
                    arr.append(str(1000000000000))
                else:
                    arr.append(str(1))

        hasil="".join(arr)

        if(hasil[-1:]=='%' and (hasil[:-1].isdigit() or self.isfloat(hasil[:-1])==True)):
            hasil=float(hasil[:-1])/100
            arr.append(str(hasil))

        return(hasil)


    def indeksKe(self,arr: List[str],indikator: List[str]):
        for x in range(0, len(arr[0])):
            for y in indikator:
                y=y.split()
                if(len(y)==1 and arr[0][x][0]==y[0]):
                    return x
                elif(len(y)==2 and len(arr[0])>x and arr[0][x][0]==y[0] and arr[0][x+1][0]==y[1]):
                    return x
        return -1
     

    def getKeparahan(self,berita, cariCD: boolean, indikator: List[str]):
    
        arr =[]
        keparahan_teks =self.__preprocessingKeparahan(berita)
        arr.append(keparahan_teks)
        tag_keparahan = self.ct.tag_sents(arr)

        hasil_indeks= self.indeksKe(tag_keparahan,indikator)

        value=''
        if(cariCD==True):
            if(hasil_indeks==-1):
                value = 0
            else:
                value = self.struktur1(tag_keparahan,hasil_indeks)
                if(isinstance(value, str)):
                    value=self.convertTeks(value)
        else:
            if(hasil_indeks==-1):
                value = 0
            else:
                value = 1

        return(value)
    
    def getKeparahanVelue(self):
        try:
            document_result = []
            self.descberita = []
            self.idberita = []

            if(len(self.newsscrapped)>0):
                self.idberita, self.descberita = zip(*self.newsscrapped)
            
            
            # for i in range(0, self.scrapped_news.shape[0]):
            #     title = self.scrapped_news.iloc[i, 0]
            #     berita = self.scrapped_news.iloc[i, 1]
            #     time = self.scrapped_news.iloc[i, 2]
            #     what = self.scrapped_news.iloc[i, 3]
            #     tanggal_asli = self.scrapped_news.iloc[i, 4]
            #     orang = self.scrapped_news.iloc[i, 5]
            #     negara = self.scrapped_news.iloc[i, 6]
            #     provinsi = self.scrapped_news.iloc[i, 7]
            #     kabupaten = self.scrapped_news.iloc[i, 8]
            #     kecamatan = self.scrapped_news.iloc[i, 9]
            for i in range(0, len(self.newsscrapped)):
                berita = self.descberita[i]
                idberita = self.idberita[i]

                """
                Bagian ini adalah indikator yang perlu disesuaikan untuk masing - masing topik
                """
              
                moneyUSD= self.getKeparahan(berita, True, ['USD$','usd$','US$','Dolar AS','dolar AS','dolar as','$'])
                moneyIDR= self.getKeparahan(berita, True, ['Rupiah','rupiah','RP','Rp','IDR','idr'])
                persen= self.getKeparahan(berita, True, ['%','Persen','persen'])
                inflasi= self.getKeparahan(berita, False, ['INFLASI','Inflasi','inflasi'])

                if(moneyUSD == ''):
                    moneyUSD = 0
                elif(moneyIDR == ''):
                    moneyIDR = 0
                elif(persen == ''):
                    persen = 0
                elif(inflasi == ''):
                    inflasi = 0

                self.save_to_mysql(idberita, moneyUSD, moneyIDR, persen, inflasi)


                # document_result.append([title, berita, time, what, tanggal_asli, orang,negara, provinsi, kabupaten, kecamatan, moneyUSD, moneyIDR, persen, inflasi])

            # writer = pd.DataFrame(document_result, columns=[
            #                     'title', 'description', 'time', 'what', 'when', 'who','negara', 'provinsi', 'kabupaten / kota', 'kecamatan', "moneyUSD", 'moneyIDR', 'persen', 'inflasi'], index=None)
            # writer.to_csv('result/tagging/severity_count.csv', index=False, sep=',')
            return "success"
        except:
            return "error"

    def save_to_mysql(self, idberita, moneyUSD, moneyIDR, persen, inflasi):
        try:
            conn = mysql.connector.connect(user='admin', password='admin', database = 'Petakabar')
            cur = conn.cursor()
            add_news = ("UPDATE berita "
                        "SET sev_moneyUSD = %s, sev_moneyIDR = %s, sev_persen = %s, sev_inflasi = %s "
                    "WHERE ID = %s"
                    )
            data_news = (moneyUSD, moneyIDR, persen, inflasi, idberita)

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