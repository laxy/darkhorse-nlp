" To classify/categorize text/language based on supplied input data. Requires two input files: parse_config.json and input.dat"
from nltk.corpus import stopwords
from nltk import word_tokenize, WordNetLemmatizer, NaiveBayesClassifier, classify, MaxentClassifier
import os, glob, re, csv, random, pickle, json
import memcache
mc = memcache.Client(['127.0.0.1:11211'])

# List of common words in english
commonwords = stopwords.words('english')

# Initialize Lemmatizer
wordlemmatizer = WordNetLemmatizer()

# Extract features from data
def extract_features(sent):
    features = {}
    wordtokens = [wordlemmatizer.lemmatize(word.lower()) for word in word_tokenize(sent)]
    for word in wordtokens:
        if word not in commonwords:
            features[word] =  True
    return features

# Build featureset from dataset
def build_featureset(config, parameter):
    delimiter = config['delimiter']
    comment_line = config['comment_line']
    pos_data = config['parse_line'].index('case_query')
    pos_parameter = config['parse_line'].index(parameter)
    dataset = []    
    
    with open(config['file'], 'r') as f:
        for line in f:
            if any(comment in line for comment in comment_line) or line=='\n':
                continue
            split = map(unicode.strip, line.split(delimiter[0]))
            dataset.append((split[pos_data], split[pos_parameter]))
        featureset = [(extract_features(a), b) for (a, b) in dataset]
    return featureset
    
# Builds the classifier and saves a copy on the same directory
def build_classifier(parameter, user_input):
    with open('parse_config.json', 'r') as f:
        featureset = build_featureset(json.load(f), parameter)
    classifier = NaiveBayesClassifier.train(featureset)
    print 'Classifier Accuracy: ', classify.accuracy(classifier, featureset)
            
    # Save Classifier
    with open((parameter+'.classifier'), 'wb') as f:
        pickle.dump(classifier, f)
    mc.set((parameter+'.classifier'), classifier, 0)
    
    if (user_input):
        print 'labels:', classifier.labels()
        while(True):
            featset = extract_features(raw_input("Enter text to classify: "))
            print classifier.classify(featset)
           
# Wrapper function to classify input with the provided classifer
def dh_classify_text(classifier, data):
    return classifier.classify(extract_features(data))

if __name__ == '__main__':
    build_classifier('section', 0)
    build_classifier('priority', 0)
    
    