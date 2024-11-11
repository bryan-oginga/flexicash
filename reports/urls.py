from django.urls import path, include
from .views import *

app_name = 'reports'

urlpatterns = [
    path('',FlexicashDashboard, name='dashboard'),
   
    ]