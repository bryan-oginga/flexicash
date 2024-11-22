# urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('intasend-webhook/', views.intasend_webhook, name='intasend-webhook'),


]
  