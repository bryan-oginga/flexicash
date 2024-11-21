# urls.py
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('', views.mpesa_payment, name='payment'),
    path('initiate/', views.stk_push_view, name='initiate_payment'),
    # path('tinypesa-webhook/', views.tinypesa_webhook, name='tinypesa-webhook'),
    # path('payhero_callback/', views.payhero_callback, name='payhero_callback'),


]
  