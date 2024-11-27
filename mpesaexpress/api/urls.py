from django.urls import path
from .views import MpesaExpressCallback

urlpatterns = [
    path('mpesa_callback/', MpesaExpressCallback.as_view(), name='mpesa_callback'),
]
