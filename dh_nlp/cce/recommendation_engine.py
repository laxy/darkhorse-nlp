"Recommendation Engine: To find similar context entries from an existing database for the provided input"
from nltk.corpus import stopwords
from nltk import word_tokenize, WordNetLemmatizer, NaiveBayesClassifier, classify, MaxentClassifier
from gensim import corpora, models, similarities
import os, glob, re, csv, random, pickle, json
from pymongo import MongoClient
import memcache

mc = memcache.Client(['127.0.0.1:11211'])


# List of common words in english
commonwords = stopwords.words('english')

client = MongoClient('localhost', 27017)
db = client.test_nlp_db
cases = db.test_collection

# Builds seperate classifiers for every category/section
def build_recommendation_engine(key):
    
    with open('parse_config.json', 'r') as f:
        config = json.load(f)
        delimiter = config['delimiter']
        comment_line = config['comment_line']
        parameters = config[key].keys()
        pos_parameter = config['parse_line'].index(key)
    
    classified_data_by_parameters = {}
    dh_re = {}
    
    for parameter in parameters:
        for case in cases.find({key: parameter}):
            if parameter not in classified_data_by_parameters:
                classified_data_by_parameters[parameter] = []
                
            classified_data_by_parameters[parameter].append(( case['case_id'], case['case_query']))
            id_list, data_list = zip(*classified_data_by_parameters[parameter])
        
        texts = [[word for word in case_data.lower().split() if word not in commonwords]
                 for case_data in data_list]
                               
        # remove words that appear only once
        #all_tokens = sum(texts, [])
        #tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        #texts = [[word for word in text if word not in tokens_once]
        #         for text in texts]       
    
        dictionary = corpora.Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=4)
        index = similarities.MatrixSimilarity(lsi[corpus])
        dh_re[parameter] = [id_list, dictionary, lsi, index]
    
    with open('recommendation.engine', 'wb') as f:
        pickle.dump(dh_re, f)
    mc.set('recommendation.engine', dh_re, 0)
    
    return dh_re

def dh_recommendation_results(data, classified_parameter, recommendation_engine):
    id_list, dictionary, lsi, index = recommendation_engine[classified_parameter]
    text = [word for word in data.lower().split() if word not in commonwords]
    vec_bow = dictionary.doc2bow(text)
    vec_lsi = lsi[vec_bow]
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    return [(cases.find_one({'case_id': id_list[i[0]]}), i[1]) for i in sims]

if __name__ == '__main__':
    dh_re = build_recommendation_engine('section')
    print 'HR'
    dh_recommendation_results("I would like to request an employment verification letter send to my home address. Employee Number 354532453", 'Human Resources', dh_re)
    print 'Testbed'
    dh_recommendation_results("adrian requesting lab access to building 5, lab 2. Requirements completed.", 'Testbed and Lab Support', dh_re)  
    
    
    

           