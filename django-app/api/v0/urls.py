from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import StatusView, LoginView, ProfileView

urlpatterns = [
    path('status/', StatusView.as_view(), name='status'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('schema/',
         SpectacularAPIView.as_view(
             custom_settings={'TITLE': 'Dotrix API',
                              'DESCRIPTION': 'Документация по тестовому API Dotrix', 'VERSION': '0.0'},
             patterns=[path('api/v0/', include('api.v0.urls'))],
         ), name='schema-v0'),
    path('swagger/',
         SpectacularSwaggerView.as_view(url_name='schema-v0'), name='swagger'),
    path('redoc/',
         SpectacularRedocView.as_view(url_name='schema-v0'), name='redoc'),
]
