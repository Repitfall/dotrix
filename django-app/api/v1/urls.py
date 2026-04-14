from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import StatusViewSet

router = DefaultRouter()
router.register(r'', StatusViewSet, basename='status')

urlpatterns = [
    path('', include(router.urls)),

    path('schema/',
         SpectacularAPIView.as_view(
             custom_settings={'TITLE': 'Dotrix API',
                              'DESCRIPTION': 'Документация по API Dotrix', 'VERSION': '1.0'},
             patterns=[path('api/v1/', include('api.v1.urls'))],
         ), name='schema-v1'),
    path('swagger/',
         SpectacularSwaggerView.as_view(url_name='schema-v1'), name='swagger'),
    path('redoc/',
         SpectacularRedocView.as_view(url_name='schema-v1'), name='redoc'),
]
