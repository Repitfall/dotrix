import json
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from api.v1.viewsets.status import StatusView
from api.v1.viewsets.auth import LoginView, LogoutView, RefreshTokenView, ChangePasswordView
from api.v1.viewsets.users import UserViewSet
from api.v1.viewsets.access_registry import AccessRegistryViewSet
from api.v1.viewsets.access_group import AccessGroupViewSet
from api.v1.viewsets.access_section import AccessSectionViewSet
from api.v1.viewsets.access_node import AccessNodeViewSet
from api.v1.viewsets.access_object import AccessObjectViewSet
from api.v1.viewsets.access_type_template import AccessTypeTemplateViewSet
from api.v1.viewsets.access_type import AccessTypeViewSet
from api.v1.viewsets.access_right import AccessRightViewSet
from api.v1.viewsets.audit import AuditViewSet


router = DefaultRouter()
router.register(
    'users',
    UserViewSet,
    basename='user'
)
router.register(
    'registries',
    AccessRegistryViewSet,
    basename='register'
)
router.register(
    'groups',
    AccessGroupViewSet,
    basename='group'
)
router.register(
    'sections',
    AccessSectionViewSet,
    basename='section'
)
router.register(
    'nodes',
    AccessNodeViewSet,
    basename='node'
)
router.register(
    'objects',
    AccessObjectViewSet,
    basename='object'
)
router.register(
    'types',
    AccessTypeViewSet,
    basename='type'
)
router.register(
    'rights',
    AccessRightViewSet,
    basename='right'
)
router.register(
    'template_types',
    AccessTypeTemplateViewSet,
    basename='template_type'
)
router.register(
    'logs',
    AuditViewSet,
    basename='log'
)

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(
        api_version='v1',
        custom_settings={'TITLE': "Dotrix API", 'VERSION': '1.0'},
        patterns=[path('api/v1/', include('api.v1.urls'))],
    ), name='schema-v1'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema-v1'),
         name='swagger-v1'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema-v1'), name='redoc-v1'),

    path('status/', StatusView.as_view(), name='status'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),

    path('', include(router.urls))
]
