from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from .app import feel_ing
from .reporter import words_classifier,create_report
from .models import Account,Report,Note
from .serializers import RegistrationSerializer ,ReportSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
import time
from django.utils import timezone
from datetime import date
import datetime as dt
import json
from .modules.utils import remove_stopwords,diffrence_time
from .modules.translator import translate_to_arabic, translate_to_english
import Levenshtein
from .modules.scraper import scrape_data
from django.core.serializers import serialize

api_token = 'ec3e2412d3d6e96e32039c78f735c2699a9072b0'
our_token = '71d169a1'
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, ))
def serp_api(request):
 

  data = {}
  if request.method == 'GET':
        final = {}
        sucess = ""
        key = ''
        try:
          key = request.query_params["key"]
        except:
            final['error'] = 'no key'
            return Response(final) 
        try:
            pass
        except:
            final['error'] = 'AI Algorithme'
            return Response(final) 
        
        english , arabic = feel_ing(key)
        # Get prediction
        
        final['feeling english'] = english 
        final['feeling arabic'] = arabic 
        return Response(final)
  #new report 
  if request.method == "POST":
        print('---------post----------')
        resp = {}
        # Get feelings
        #print(request.data)
        #data =JSONParser().parse(request).decode('utf-8')
        #print(data)
        '''id = data["id"]
        no = data["no"]
        feelings = data["feelings"]'''
        id = "1"
        no = "2"
        feelings = "joy"
        
        # Get prediction
       
        english , prediction = feel_ing(feelings)
        print('---------feel_ing----------')
        table_classes = words_classifier(feelings)
        print('---------words_classifier----------')
        create_report(no, id, "التقرير جديد", feelings, prediction, table_classes)
        print('---------create_report----------')
        sucess = "تم انشاء التقرير بنجاح"
        resp ['sucess']=sucess
        return Response(resp)

        
    # Render app
@api_view(['GET', 'POST'])  
def registration_view(request):
  
	if request.method == 'POST':
    
		data = {}
		email = request.data.get('email', '0').lower()
		if validate_email(email) != None:
			data['error_message'] = 'That email is already in use.'
			data['response'] = 'Error'
			return Response(data)
    
		username = request.data.get('username', '0')
		if validate_username(username) != None:
			data['error_message'] = 'That username is already in use.'
			data['response'] = 'Error'
			return Response(data)

		serializer = RegistrationSerializer(data=request.data)
		
		if serializer.is_valid():
			account = serializer.save()
			data['response'] = 'successfully registered new user.'
			data['email'] = account.email
			data['username'] = account.username
			data['pk'] = account.pk
			token = Token.objects.get(user=account).key
			data['token'] = token
		else:
			data = serializer.errors
		return Response(data)

def validate_email(email):
  account = None
  try:
    account = Account.objects.get(email=email)
  except Account.DoesNotExist:
    return None
  if account != None:
    return email

def validate_username(username):
	account = None
	try:
		account = Account.objects.get(username=username)
	except Account.DoesNotExist:
		return None
	if account != None:
		return 
	
@api_view(['POST']) 
@permission_classes((IsAuthenticated, ))
def create_report(request):
  
    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    acount = Token.objects.get(key=token)
    data = {}
    token = None
    email = acount.user
    #try:
      #content = json.loads(request.body)
    #except:
        #data ={}
        #data['response'] = 'Invalid JSON format.'
        #return Response(data)
    #text = content["text"]
    text = request.POST.get('text')
    print(text)
    print("*****************")
    english , prediction = feel_ing(text)
    number_word= len(text.split())
    cordination = request.POST.get('coordinate')
    print(cordination)
    #data['zabi']=token
    user = Account.objects.get(email=email)

    report = Report(
        time =  timezone.now(),
        date=date.today(), 
        coordinates=cordination,
        text_felling_field=prediction, 
        text_report =text,
        number=number_word,
        user_name=user,
    )
    print(report)
    id = report.save()
    print(report)
    data["id_report"] = id
    return Response(data)



@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def return_report_id(request):
   
    data = {}    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    report_id = request.query_params["report_id"]
    acount = Token.objects.get(key=token)
    email = acount.user
    all_instances = Report.objects.filter(user_name=email,id=report_id)
    list_instance = all_instances.values()
    if len(list_instance) >0 :
      data = {"report": all_instances.values()[0]}
    else:
        data = {"report": ""}
    return Response(data)

@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def return_report(request):
   
    data = {}    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    acount = Token.objects.get(key=token)
    email = acount.user
    all_instances = Report.objects.filter(user_name=email)
    data = {"reports": list(all_instances.values())}
    return Response(data)
@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def compare_report(request):
    report_id = request.query_params["report_id"]
    data = {}    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    data['report_id'] = report_id
    main_report = Report.objects.filter(id=report_id)
    main_report = main_report.values()
    main_report =  main_report[0]
    cur_date = main_report['date']
    cur_desc =main_report['text_report']
    cur_feel = main_report['text_felling_field']

    user_id_for_report = main_report["user_name_id"]
    all_report = Report.objects.exclude(id=report_id).filter(user_name_id=user_id_for_report)
    similarity = []
    noms = []
    dates = []
    for report in all_report :
      prev_date =report.date
      prev_desc =report.text_report
      prev_feel = report.text_felling_field
      a = remove_stopwords(translate_to_english(cur_desc))
      b = remove_stopwords(translate_to_english(prev_desc))
      noms.append(str(report.id))
      dates.append(prev_date)
      similarity.append(100 - Levenshtein.distance(a, b))
      print('***********************************************************')
      print(cur_feel)
      print(prev_feel)
    print(noms)
    print(dates) 
    print(similarity) 
    data['dates'] = dates
    data['id'] = noms
    data['similarity'] = similarity
    return Response(data)
@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def compare_news(request):
    report_id = request.query_params["report_id"]
    country = request.query_params["country"]
    period = request.query_params["period"]
    data = {}    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    data['report_id'] = report_id
    main_report = Report.objects.filter(id=report_id)
    main_report = main_report.values()
    main_report =  main_report[0]
    cur_date = main_report['date']
    cur_desc =main_report['text_report']
    cur_feel = main_report['text_felling_field']
    news,new_all = scrape_data(country, period)
    new_all = new_all
    main_report_date_time =str(main_report['date'])+" "+str(main_report['time']) 
    print("********************************")
    #diffrence_time
    print(str(main_report['date'])+" "+str(main_report['time']))
    print("********************************")
    news = news['Title'].values.tolist()
   
    similarity = []
    vip_news = []
    news_after_procces = []
    for i in range(len(news)):
        a = remove_stopwords(translate_to_english(cur_desc))
        b = remove_stopwords(translate_to_english(news[i]))
        sim = 100 - Levenshtein.distance(a, b)
        similarity.append(sim)
        #print(new_all[i]['datetime'])
        site = {}
        site['link'] = new_all[i]['link']
        site['title'] = translate_to_arabic(new_all[i]['title'])
        site['desc'] = translate_to_arabic(new_all[i]['desc'])
        site['media'] = new_all[i]['media']
        if new_all[i]['datetime'] != None:
            site['date'] = str(new_all[i]['datetime']).split("T")[0]
            
            time_news = new_all[i]['datetime']
            print(diffrence_time(str(time_news),main_report_date_time))
            site['time interval between the two'] = diffrence_time(str(time_news),main_report_date_time)
        else : 
            now = date.today()
            current_year = year = str(now.year)+'-'+str(now.month)+'-'+str(now.day)
            site['date'] =current_year
            site['time interval between the two'] = new_all[i]['date']
        site['similarity'] = sim
        news_after_procces.append(site)
        if sim > 70:
            vip_news.append(site)
    #data['similare_news']= vip_news
    #data['similarity']= similarity
    data['new'] = news_after_procces
    return Response(data)


@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def delet_report(request):
    report_id = request.query_params["report_id"]
    main_report = Report.objects.filter(id=report_id)
    
    data = {}   
    if len(main_report) == 0:
        data['error'] = 'there is no report with this id =' + report_id
        return Response(data ,status=404)
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    main_report.delete()
    data['succes'] = 'report with id =' + report_id + ' was deleted successfully'
    return Response(data)
@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def update_report(request):
    report_id = request.query_params["report_id"]
    text = request.query_params["text"]
    main_report = Report.objects.filter(id=report_id)
    data = {}   
    if len(main_report) == 0:
        data['error'] = 'there is no report with this id =' + report_id
        return Response(data ,status=404)
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    english , prediction = feel_ing(text)
    number = len(text.split())
    main_report.update(text_felling_field=prediction, 
        text_report =text,number=number)
    data['succes'] = 'report with id =' + report_id + ' was update successfully'
    return Response(data)

#----------------------------note----------------
@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, ))
def create_Note(request):
    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    acount = Token.objects.get(key=token)
    data = {}
    token = None
    #content = json.loads(request.body)
    #text = content["text"]
    text = request.POST.get('text')
    print(text)
    #print("************************************")
    english , prediction = feel_ing(text)
    number_word= len(text.split())
    #cordination = content['coordinate']
    cordination = request.POST.get('coordinate')
    email = acount.user
    #data['zabi']=token
    user = Account.objects.get(email=email)

    note = Note(
        time =  timezone.now(),
        date=date.today(), 
        coordinates=cordination,
        text_felling_field=prediction, 
        text_report =text,
        number=number_word,
        user_name=user,
    )
    id = note.save()
    print(note)
    data["id_note"] = id
    return Response(data)

@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def return_note(request):
    data = {}    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    acount = Token.objects.get(key=token)
    email = acount.user
    all_instances = Note.objects.filter(user_name=email)
    data = {"Notes": list(all_instances.values())}
    return Response(data)
@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def return_note_id(request):
    data = {}    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    
    note_id = request.query_params["note_id"]
    acount = Token.objects.get(key=token)
    email = acount.user
    all_instances = Note.objects.filter(user_name=email,id=note_id)
    list_instance = all_instances.values()
    if len(list_instance) >0 :
      data = {"note": all_instances.values()[0]}
    else:
        data = {"note": ""}
    return Response(data)
@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def compare_note(request):
    note_id = request.query_params["note_id"]
    data = {}    
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    data['note_id'] = note_id
    main_report = Note.objects.filter(id=note_id)
    main_report = main_report.values()
    main_report =  main_report[0]
    cur_date = main_report['date']
    cur_desc =main_report['text_report']
    cur_feel = main_report['text_felling_field']

    user_id_for_report = main_report["user_name_id"]
    all_report = Note.objects.exclude(id=note_id).filter(user_name_id=user_id_for_report)
    
    similarity = []
    noms = []
    dates = []
    for report in all_report :
      prev_date =report.date
      prev_desc =report.text_report
      prev_feel = report.text_felling_field
      a = remove_stopwords(translate_to_english(cur_desc))
      b = remove_stopwords(translate_to_english(prev_desc))
      noms.append(str(report.id))
      dates.append(prev_date)
      similarity.append(100 - Levenshtein.distance(a, b))
      
    data['dates'] = dates
    data['id'] = noms
    data['similarity'] = similarity
    return Response(data)

@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def delet_note(request):
    note_id = request.query_params["note_id"]
    main_report = Report.objects.filter(id=note_id)
    data = {}   
    if len(main_report) == 0:
        data['error'] = 'there is no note with this id =' + note_id
        return Response(data ,status=404)
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token
    main_report.delete()
    data['succes'] = 'note with id = ' + note_id + ' was deleted successfully'
    return Response(data)

@api_view(['GET']) 
@permission_classes((IsAuthenticated, ))
def update_note(request):
    report_id = request.query_params["note_id"]
    text = request.query_params["text"]
    main_report = Note.objects.filter(id=report_id)
    data = {}   
    if len(main_report) == 0:
        data['error'] = 'there is no note with this id = ' + report_id
        return Response(data ,status=404)
    # check if the Authorization header exists in the request
    if 'Authorization' in request.headers:
        # split the header value into the authentication scheme and token
        auth_header = request.headers['Authorization']
        auth_scheme, auth_token = auth_header.split(' ')
        if auth_scheme == 'token':
            token = auth_token

    english , prediction = feel_ing(text)
    number = len(text.split())
    main_report.update(text_felling_field=prediction, 
        text_report =text,number=number)
    data['succes'] = 'Note with id = ' + report_id + ' was update successfully'
    return Response(data)

@api_view(['GET', 'POST'])
def test_form_post(request):
    data = {}
    print(request.POST)
    name = request.POST.get('name')
    print("***********************")
    print(name)
    data["name"]=name   
    return Response(data)