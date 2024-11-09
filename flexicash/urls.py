
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ussd.urls',namespace='ussd')),  # Include the API URLs in our main URL configuration
]
