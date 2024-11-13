from django.urls import path
from .views import MpesaExpressCallback


urlpatterns = [
   
  path('callback/',MpesaExpressCallback.as_view(),name='stk-callback'),

]