from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('auth/', include('users.urls')),
        path('employees/', include('employees.urls')),
        path('recruitment/', include('recruitment.urls')),
        path('attendance/', include('attendance.urls')),
        path('leave/', include('leave.urls')),
        path('payroll/', include('payroll.urls')),
        path('performance/', include('performance.urls')),
        path('training/', include('training.urls')),
        path('assets/', include('assets.urls')),
        path('reports/', include('reports.urls')),
        path('schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
