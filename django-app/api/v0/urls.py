from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import StatusViewSet

router = DefaultRouter()
router.register(r'', StatusViewSet, basename='status')

urlpatterns = [
    path('', include(router.urls)),

    path('schema/yaml/',
         SpectacularAPIView.as_view(
             custom_settings={'TITLE': 'Dotrix API v0',
                              'DESCRIPTION': 'Тестовый API для Dotrix', 'VERSION': '0.0'},
             patterns=[path('api/v0/', include('api.v0.urls'))],
         ), name='schema-v0'),
    path('schema/swagger/',
         SpectacularSwaggerView.as_view(url_name='schema-v0'), name='swagger'),
    path('schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema-v0'), name='redoc'),
]
