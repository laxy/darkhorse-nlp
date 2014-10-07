from pymongo import MongoClient
import datetime, json

def load_db(case):

    with open('parse_config.json', 'r') as f:
        config = json.load(f)
        delimiter = config['delimiter']
        comment_line = config['comment_line']
        parse_line = config['parse_line']
        
    with open(config['file'], 'r') as f:
        for line in f:
            if any(comment in line for comment in comment_line) or line=='\n':
                continue
            split = map(unicode.strip, line.split(delimiter[0]))
            case.insert(dict(zip(parse_line, split)))
                #    Format: case_id | section | date+time | case_synopsis | case_query | priority \n

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    db = client.test_nlp_db
    db.test_collection.drop()
    case = db.test_collection
    
    load_db(case)
    for case in case.find({"section": "Human Resources"}):
        print case
