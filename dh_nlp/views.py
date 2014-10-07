from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import RequestContext, Context, Template

from cce.classifier import dh_classify_text
from cce.recommendation_engine import dh_recommendation_results
from django.core.cache import cache
import memcache, random, datetime
from pymongo import MongoClient

mc = memcache.Client(['127.0.0.1:11211'])

# Connect to db
client = MongoClient('localhost', 27017)
db = client.test_nlp_db
case_db = db.test_collection

def create_case(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('submit.html', c)
    
    
def post_case_data(request):
    case = {}
    c = {}
    c.update(csrf(request))
    case['case_data']= request.POST.get('case_data')
    case['synopsis'] = request.POST.get('synopsis')
    case['user'] = request.POST.get('username')
    case['datetime'] = datetime.datetime.now().strftime("%I:%M%p %B %d %Y")
    case['category'] = dh_classify_text(mc.get('section.classifier'), case['case_data'])
    case['priority'] = dh_classify_text(mc.get('priority.classifier'), case['case_data'])
    case['case_id'] = case['category'][0]+str(random.randint(1, 9999999))
    r = dh_recommendation_results(case['case_data'], case['category'], mc.get('recommendation.engine'))  
    case_db.insert({
            "case_id":    case['case_id'],
            "section":    case['category'],
            "datetime":   case['datetime'],
            "case_query": case['case_data'],
            "priority":   case['priority'] 
        })
    #    Format: case_id | section | date+time | case_synopsis | case_query | priority \n
    return render_to_response('response.html', {'case':case}, context_instance=RequestContext(request))

def pending_cases(request):
    cases = []
    c = {}
    c.update(csrf(request))
    
    for case in case_db.find():
        cases.append(case)
    return render_to_response('pending_cases.html', {'cases':cases}, context_instance=RequestContext(request))
