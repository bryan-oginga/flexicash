from django.db.models import Avg,Sum,Count,Aggregate,Q,Max,Min
import pytz
from django.contrib import messages
import base64
from .models import MpesaTransaction
import json
from .mpesa_credentials import LipanaMpesaPassword
from django.http import HttpResponse,JsonResponse
import  requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth
from django.contrib.auth.decorators import  login_required
from django.contrib.admin.views.decorators import staff_member_required
import math
from django.core.cache import cache
from requests.auth import HTTPBasicAuth
from django.core.cache import cache
import requests

# Ensure these are defined in settings.py
SHORTCODE = settings.SHORTCODE
CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
CALL_BACK_URL = settings.CALL_BACK_URL
ACCESS_TOKEN_URL = settings.ACCESS_TOKEN_URL

def get_mpesa_access_token():
    access_token = cache.get('mpesa_access_token')

    if access_token:
        return access_token
    response = requests.get(ACCESS_TOKEN_URL, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        cache.set('mpesa_access_token', access_token, timeout=3600)
        return access_token
    else:
        print("Error response:", response.text)
    raise Exception("Failed to get Mpesa access token")

# @login_required
@csrf_exempt
def lipa_na_mpesa_express(request):
    phone = '254799043853'
    amount = 1
    access_token = get_mpesa_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    request_payload = {
        "BusinessShortCode": settings.SHORTCODE,
        "Password": LipanaMpesaPassword.decode_password,  # Ensure this is correctly defined
        "Timestamp": LipanaMpesaPassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": math.ceil(float(amount)),
        "PartyA": phone,
        "PartyB": settings.SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALL_BACK_URL,
        "AccountReference": 'Brian',
        "TransactionDesc": "Testing stk push"
    }
    
    try:
        response = requests.post(settings.API_URL, json=request_payload, headers=headers)
        response.raise_for_status()  # Raises an error if the response status is not 2xx
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return JsonResponse({"error": "Request failed"}, status=500)

    # Print and return the API response
    print(response.text)
    return JsonResponse(response.json())