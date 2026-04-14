from django.urls import path, include

urlpatterns = [
    path('v0/', include('api.v0.urls')),
    path('v1/', include('api.v1.urls')),

    path('latest/', include('api.v1.urls'))
]
