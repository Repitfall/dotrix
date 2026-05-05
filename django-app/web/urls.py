from django.urls import path
from .views import (
    DashboardView,
    LoginView,
    ProfileView,

    RegistryListView,
    RegistryDetailView,
    RegistryEditView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('registries/', RegistryListView.as_view(), name='registry-list'),
    path('registries/<int:pk>/', RegistryDetailView.as_view(),
         name='registry-detail'),
    path('registries/<int:pk>/edit/',
         RegistryEditView.as_view(), name='registry-edit'),
]
