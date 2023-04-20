from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from .app import feel_ing
from .reporter import words_classifier,create_report
from .models import Account
from .serializers import RegistrationSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
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
	


 
#def report (request):
  

  #else:
    #data["detail"]="Bad Request"
    #return Response(data,status= status.HTTP_400_BAD_REQUEST)

  #{"id":"1","no" :"2","feelings" :"انا حزين"}
  #{"keyword":" بشرة","section_number" :2 ,"token" :"71d169a1" ,"language":"ar","country" :"eg" }