# urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('', views.mpesa_payment, name='payment'),
    path('initiate/', views.initiate_stk_push_view, name='initiate_payment'),
    path('intasend-webhook/', views.intasend_webhook, name='intasend-webhook'),


]
  