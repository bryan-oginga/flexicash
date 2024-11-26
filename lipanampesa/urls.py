# urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('stk-webhook/', views.intasend_stk_webhook, name='intasend-webhook'),
    path('b2c-webhook/', views.intasend_b2c_webhook, name='intasend-webhook'),


]
  