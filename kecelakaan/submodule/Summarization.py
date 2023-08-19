from .DataCleansing import Preprocessing
from transformers import T5Tokenizer, T5ForConditionalGeneration
import mysql.connector
from mysql.connector import errorcode

class Summarization:
    def __init__(self):
        self.model_checkpoint = 'D:/Repository/PetaKabar/models/finetune_sum'
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_checkpoint)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_checkpoint)
        
        self.news_scrapped = []
        
        try:
            cnx = mysql.connector.connect(user = 'admin', password='admin', database = 'Petakabar')
            cursor = cnx.cursor()
            cursor.execute("SELECT ID, berita_desc FROM berita WHERE berita_topik_id = 3 AND berita_summary IS NULL LIMIT 10")
            myresult = cursor.fetchall()
            for row in myresult:
                self.news_scrapped.append(row)
                
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password HALOOO")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
                
        else:
            cursor.close()
            cnx.close()
    
    def _generate_summary(self, article):
        input_ids = self.tokenizer.encode(article, return_tensors='pt')
        summary_ids = self.model.generate(input_ids, 
                                          max_length=100,
                                          num_beams=2,
                                          repetition_penalty=2.5,
                                          length_penalty=1.0,
                                          early_stopping=True,
                                          no_repeat_ngram_size=2,
                                          use_cache=True)
        summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
        return summary_text
    
    def get_summary(self):
        try:
            self.berita_id = []
            self.berita_desc = []
            
            # check len of news_scrapped array
            if(len(self.news_scrapped)>0):
                self.berita_id, self.berita_desc = zip(*self.news_scrapped)
            
            for i in range(0, len(self.news_scrapped)):
                id_berita = self.berita_id[i]
                desc_berita = self.berita_desc[i]
                
                preprocessor = Preprocessing(desc_berita)
                cleaned_berita = preprocessor._process_text()
                summary_berita = self._generate_summary(cleaned_berita)
                
                # store to database
                self.save_to_mysql(id_berita, cleaned_berita, summary_berita)
                
            return "success"
        
        except:
            return "error"
    
    def save_to_mysql(self, id_berita, cleaned_berita, summary_berita):
        try:
            conn = mysql.connector.connect(user = 'admin', password='admin', database = 'Petakabar')
            cur = conn.cursor()
            add_news = "UPDATE berita SET berita_desc = %s, berita_summary = %s WHERE ID = %s"
            data_news = (cleaned_berita, summary_berita, id_berita)

            cur.execute(add_news, data_news)
            conn.commit()      
            cur.close()
            conn.close()
        
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password HEYYY")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
