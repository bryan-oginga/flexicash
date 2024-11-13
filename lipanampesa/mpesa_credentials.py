import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from django.conf import settings

CONSUMER_KEY = settings.CONSUMER_KEY
CONSUMER_SECRET = settings.CONSUMER_SECRET
ACCESS_TOKEN_URL = settings.ACCESS_TOKEN_URL
SHORTCODE = settings.SHORTCODE
MPESA_PASSKEY = settings.MPESA_PASSKEY





class LipanaMpesaPassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
    Business_short_code = SHORTCODE
    passkey = MPESA_PASSKEY
    data_to_encode = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')