from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', include('ussd.urls',namespace='ussd')),  
    path('dashboard/', include('reports.urls',namespace='reports')),  
    path('payment/', include('mpesaexpress.urls',namespace='payment')),
    path('api/', include('mpesaexpress.api.urls')),
  
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)