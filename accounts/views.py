
from django.http.response import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import messages
from django.shortcuts import redirect, render

# from rest_framework import serializers
# from rest_framework.generics import GenericAPIView
from .serializers import UserSerializer
from django.contrib.auth.models import User, auth
from rest_framework.views import APIView
import jwt , datetime
import requests
from django.conf import settings
from django.core.mail import send_mail , EmailMessage 
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from .models import login_history
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode 
from django.utils.encoding import force_bytes, force_text
from .tokens import generate_token
User = get_user_model()

class registerView(APIView):
    # serializer_class = UserSerializer

    # @api_view(['GET'])
    def get(self,request):
        # return render(request,"index.html")
        sgs=User.objects.all()
        serializer=UserSerializer(sgs,many=True)
        return Response(serializer.data)
    
    # @api_view(['POST'])
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class LoginView(APIView):
    # def get(self,request):
    #     pass
    
    # serializer_class = UserSerializer

    def post(self,request):
        email = request.data['email']
        password = request.data['password']
        
        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found!")

        if user.email_verify==True:
            if user.sign_in_attempt_cnt <5:

                if not user.check_password(password):
                    user.sign_in_attempt_cnt +=1
                    user.save()
                    raise AuthenticationFailed("Incorrect Password!")
                else:
                    user.sign_in_attempt_cnt =0
                    user.save()

                login_success = login_history(user=user,login_dt=datetime.datetime.now())   
                login_success.save()

                payload = {
                    'id':user.id,
                    'exp':datetime.datetime.now() +datetime.timedelta(minutes=60),
                    'iat':datetime.datetime.now()
                }
                
                token = jwt.encode(payload,'secret',algorithm='HS256')
                
                resp = Response()

                resp.set_cookie(key='jwt',value=token,httponly=True)
                resp.data = {
                    'jwt':token
                }
                return resp
            else:
                return HttpResponse("Your account is locked")
        else:
            return HttpResponse("Your Email is not verified!!!")
# {
#     "email":"test@gmail.com",
#     "password":"test@123"
# }        

class LogoutView(APIView):
    def post(self,request):
        response =Response()
        response.delete_cookie('jwt')
        response.data ={
            "message" : "Logged out successfully"
        }
        return response

# Create your views here.
def home(request):
    if request.method== "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username Taken")
                return redirect("home")
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect("home")
            else:
                user = User.objects.create_user(
                    username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                user.save()
                data={
                     "username": username,
                     "first_name": first_name,
                     "last_name": last_name,
                     "email": email,
                     "password": password1
                     }

                header = {'Content-Type': 'application/json'}
                read = requests.post('http://127.0.0.1:8000/ap/',json=data,headers=header)
                
                #Email verification
                
                current_site = get_current_site(request)
                subj = "Email verification"
                
                msg = render_to_string('email.html',{
                    'name': user.first_name,
                    'domain' :current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':generate_token.make_token(user),
                })
                from_email = settings.EMAIL_HOST_USER
                to_list = [user.email]
                email = EmailMessage(subj, msg, from_email, to_list)
                email.fail_silently = False
                email.send()
                messages.success(request,"Please verify your mail!")

                
                return render(request,"login.html")
        else:
            messages.warning(request, "Password not matching.")
            return redirect("home")
    else:
        return render(request, 'index.html')


    return render(request,"index.html")

# @api_view()
@api_view(['GET', 'POST', ])
def login(request):
    login_status=0
    if request.method== "POST":
        email = request.POST['email']
        password = request.POST['password']

        data={
                "email": email,
                "password": password
            }

        header = {'Content-Type': 'application/json'}
        read = requests.post('http://127.0.0.1:8000/ap/login',json=data,headers=header)
        
        # return HttpResponse(read)
        return render(request,'test.html',{'resp':read}) 
    elif request.method == "GET":
        return render(request,"login.html")
       

def logout(request):
   
    header = {'Content-Type': 'application/json'}
    read = requests.post('http://127.0.0.1:8000/ap/logout',headers=header)
    return HttpResponse(read)
    
def activate(request, uidb64, token):
    try:
        uid= force_text(urlsafe_base64_decode(uidb64))
        user =  User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None

    if user is not None and generate_token.check_token(user,token):
        user.email_verify = True
        user.save()
        messages.success(request,"Email verified!")
        return redirect("http://127.0.0.1:8000/login")
    else:
        return HttpResponse("Activation Failed!!! <br>Please Try Again.")