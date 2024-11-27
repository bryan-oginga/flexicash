# urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('intasend-webhook/', views.intasend_stk_webhook, name='intasend-webhook'),
    path('express/', views.initiate_payhero_stk_push, name='initiate_mpesa_stk_push'),
    path('api/callback/', views.payhero_callback, name='payhero_callback'),


]
  