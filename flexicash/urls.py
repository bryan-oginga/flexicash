
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ussd.urls',namespace='ussd')),  
    path('dashboard/', include('reports.urls',namespace='reports')),  
    path('payment/', include('lipanampesa.urls',namespace='payment')),  
]
