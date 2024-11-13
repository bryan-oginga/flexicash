from django.urls import path
from .views import (lipa_na_mpesa_express)


app_name = 'payment'

urlpatterns = [
    path('express/',lipa_na_mpesa_express,name='express'),
    # path('token/',getAccessToken,name='access_token'),

  
]