from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import (
    StatusView,
    LoginView,
    ProfileView,
    UserView,
    UserListView,

    AccessRegistryListView,
    AccessRegistryView,
    AccessRegistryRestoreView,

    AccessSectionListView,
    AccessSectionView,

    AccessNodeListView,

    AccessObjectListView,

    AccessTypeListView
)

urlpatterns = [
    path('status/', StatusView.as_view(), name='status'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('users/', UserListView.as_view(), name='users'),
    path('users/<int:id>', UserView.as_view(), name='user'),

    path('access_registries/',
         AccessRegistryListView.as_view(), name='registies'),
    path('access_registries/<int:id>',
         AccessRegistryView.as_view(), name='registry'),
    path('access_registries/<int:id>/restore',
         AccessRegistryRestoreView.as_view(), name='registry_restore'),

    path('access_sections/',
         AccessSectionListView.as_view(), name='sections'),
    path('access_sections/<int:id>',
         AccessSectionView.as_view(), name='section'),

    path('access_nodes/',
         AccessNodeListView.as_view(), name='nodes'),

    path('access_objects/',
         AccessObjectListView.as_view(), name='objects'),

    path('access_types/',
         AccessTypeListView.as_view(), name='types'),

    path('schema/',
         SpectacularAPIView.as_view(
             custom_settings={'TITLE': 'Dotrix API (LEGACY)',
                              'DESCRIPTION': 'Документация по тестовому API Dotrix, является эксприментальным и не подходит для работы', 'VERSION': '0.0'},
             patterns=[path('api/v0/', include('api.v0.urls'))],
         ), name='schema-v0'),
    path('swagger/',
         SpectacularSwaggerView.as_view(url_name='schema-v0'), name='swagger'),
    path('redoc/',
         SpectacularRedocView.as_view(url_name='schema-v0'), name='redoc'),
]
