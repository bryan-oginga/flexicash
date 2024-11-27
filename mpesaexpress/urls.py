# urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    
    path('intasend-webhook/', views.intasend_stk_webhook, name='intasend-webhook'),
    path('payhero_express/', views.initiate_payhero_stk_push, name='initiate_payhero_stk_push'),
    path('payhero_callback/', views.payhero_callback, name='payhero_callback'),
    path('mpesa_express/', views.initiate_mpesa_stk_push, name='initiate_mpesa_stk_push'),

]
  