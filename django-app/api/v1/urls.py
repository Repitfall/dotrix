from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.viewsets.status import StatusView
from api.v1.viewsets.auth import LoginView, LogoutView, RefreshTokenView, ChangePasswordView
from api.v1.viewsets.users import UserViewSet
from api.v1.viewsets.access_registry import AccessRegistryViewSet
from api.v1.viewsets.access_group import AccessGroupViewSet
from api.v1.viewsets.access_section import AccessSectionViewSet

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

urlpatterns = [
    path('status/', StatusView.as_view(), name='status'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),

    path('', include(router.urls))
]
