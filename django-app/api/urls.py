from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('v0/', include('api.v0.urls')),

    path('v1/', include('api.v1.urls')),
    path('v1/schema/', SpectacularAPIView.as_view(
        api_version='v1',
        custom_settings={'TITLE': "Dotrix API", 'VERSION': '1.0'},
        patterns=[path('api/v1/', include('api.v1.urls'))]
    ), name='schema-v1'),
    path('v1/swagger/', SpectacularSwaggerView.as_view(url_name='schema-v1'),
         name='swagger-v1'),
    path('v1/redoc/', SpectacularRedocView.as_view(url_name='schema-v1'),
         name='redoc-v1'),

    path('latest/', include('api.v1.urls')),
]
