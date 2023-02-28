import os
import pandas as pd
from BTrees.OOBTree import OOBTree
from parsivar import Normalizer
from parsivar import Tokenizer
import re
from parsivar import FindStems
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle as pkl
from helper import IdMap

my_normalizer = Normalizer()
my_tokenizer = Tokenizer()
my_stemmer = FindStems()

path = 'persian_stopwords.txt'
stop_words = []
f = open(path, "r", encoding='utf-8-sig')
for x in f:
    stop_words.append(x.rstrip("\n"))

class Index:
    
    def __init__(self, data_dir, output_dir):
        self.term_id_map = IdMap()
        self.doc_id_map = IdMap()
        self.data_dir = data_dir
        self.index = OOBTree()
        self.output_dir = output_dir
        
 
    def save(self):
        # writing index into disk
        with open(os.path.join(self.output_dir, 'index.dict'), 'wb') as f:
            pkl.dump(self.index, f)
            
    def load(self):
        # loading index from disk
        with open(os.path.join(self.output_dir, 'index.dict'), 'rb') as f:
            self.index = pkl.load(f)
            
        
    def parse(self):
        # creates dictionary and postings list
        postings = []

        for file in os.listdir(self.data_dir):
            doc_id = self.doc_id_map._get_doc_id(file)
            data_path = self.data_dir + '\\' + file
            file_content = open(data_path, "r", encoding='utf-8-sig').read()
            file_content = re.sub('[0-9]+', '', file_content)
            file_content = re.sub('[a-zA-Z]+', '', file_content)
            normalized_text = my_normalizer.normalize(file_content)
            tokens = my_tokenizer.tokenize_words(my_normalizer.normalize(normalized_text))
            for token in tokens:
                stemmed_token = my_stemmer.convert_to_stem(token)
                if stemmed_token not in stop_words :
                    term_id = self.term_id_map._get_id(stemmed_token)
                    term_tuple = (term_id, doc_id)
                    postings.append(term_tuple)
        
        words_dict = OOBTree()
        for pair in postings:
            if pair[0] not in words_dict:
                words_dict[pair[0]] = set()
                words_dict[pair[0]].add(pair[1])
            else:
                words_dict[pair[0]].add(pair[1])

        self.index = words_dict
        print("**********************************************")
        # self.save(words_dict)
    
    def retrieve(self, query):
        # retrieves documents related to query
        query_words = []    
        normalized_query = my_normalizer.normalize(query)
        tokens = my_tokenizer.tokenize_words(my_normalizer.normalize(normalized_query)) 
        for token in tokens:
            stemmed_token = my_stemmer.convert_to_stem(token)
            query_words.append(stemmed_token)

        documents_lists = []
        
        for word in query_words:
            if word not in self.term_id_map.str_to_id:
                continue
            word_id = self.term_id_map._get_id(word)
            
            related_docs = self.index[word_id]
            
            documents_lists.append(set(related_docs))
            
        print(documents_lists)
        union_set = documents_lists[0].union(*documents_lists)

        return union_set, query_words

    def ranker(self, query):
        related_docs, clean_query = self.retrieve(query)
        if len(related_docs)==0:
            return("Sorry there is no matching document")

        total_docs = []
        for doc_id in related_docs:
            file = self.doc_id_map._get_doc_str(doc_id)
            data_path = self.data_dir + '\\' + file
            file_content = open(data_path, "r", encoding='utf-8-sig').read()
            file_content = re.sub('[0-9]+', '', file_content)
            file_content = re.sub('[a-zA-Z]+', '', file_content)
            normalized_text = my_normalizer.normalize(file_content)
            tokens = my_tokenizer.tokenize_words(my_normalizer.normalize(normalized_text))
            stemmed_tokens = []
            for token in tokens:
                stemmed_tokens.append(my_stemmer.convert_to_stem(token))
            clean_text = "".join([word + " " for word in stemmed_tokens])
            document_info = [file, clean_text]
            total_docs.append(document_info)
                
        df=pd.DataFrame(total_docs, columns=['file_name', 'text'])        
        vectorizer = TfidfVectorizer(analyzer='word', stop_words = stop_words ,max_features = 500)
        X = vectorizer.fit_transform(df['text'])
        query_vec = vectorizer.transform(clean_query)
        results = cosine_similarity(X,query_vec)

        score_list = []
        for each in results:
            total_score = sum(each)
            score_list.append(total_score)
            
        df['score'] = score_list
        
        df = df.sort_values(by="score", ascending=False)
        
        return df