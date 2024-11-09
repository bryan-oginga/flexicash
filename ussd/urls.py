from django.urls import path
from . import views

app_name = 'ussd'

urlpatterns = [
    path('', views.ussd_view, name='ussd'),
]
