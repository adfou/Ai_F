from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from .app import feel_ing
from .reporter import words_classifier,create_report
from .models import Account,Report
from .serializers import RegistrationSerializer ,ReportSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
import time
from django.utils import timezone
from datetime import date
import json
from .modules.utils import remove_stopwords
from .modules.translator import translate_to_arabic, translate_to_english
import Levenshtein
from .modules.scraper import scrape_data

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
    content = json.loads(request.body)
    print(content)
    text = content["text"]
    english , prediction = feel_ing(text)
    print(prediction)
    number_word= len(text.split())
    print('---------------body------------')
    cordination = content['coordinate']
    email = acount.user
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

    print(main_report)
    print('----------------------')
    all_report = Report.objects.exclude(id=report_id)
    similarity = []
    noms = []
    dates = []
    for report in all_report :
      prev_date =report.date
      prev_desc =report.text_report
      prev_feel = report.text_felling_field
      a = remove_stopwords(translate_to_english(cur_desc))
      b = remove_stopwords(translate_to_english(prev_desc))
      noms.append('report '+str(report.id))
      dates.append(prev_date)
      similarity.append(100 - Levenshtein.distance(a, b))
      print('***********************************************************')
      print(cur_feel)
      print(prev_feel)
    print(noms)
    print(dates) 
    print(similarity) 
    data['dates'] = dates
    data['noms'] = noms
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
    print(new_all)
    news = news['Title'].values.tolist()
   
    similarity = []
    vip_news = []
    for new in news:
        a = remove_stopwords(translate_to_english(cur_desc))
        b = remove_stopwords(translate_to_english(new))
        sim = 100 - Levenshtein.distance(a, b)
        similarity.append(sim)
        if sim > 90:
            vip_news.append(new)
        else:
            print(f"There's No to {new}")
    data['similare_news']= vip_news
    data['similarity']= similarity
    data['new'] = new_all
    return Response(data)