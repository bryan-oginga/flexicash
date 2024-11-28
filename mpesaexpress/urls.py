# urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    
    path('intasend_stk_webhook/', views.intasend_stk_webhook, name='intasend-webhook'),
    path('mpesa_express/', views.initiate_mpesa_stk_push, name='initiate_mpesa_stk_push'),

]
  