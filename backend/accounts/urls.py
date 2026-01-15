from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('api-token-auth/', views.CustomAuthToken.as_view(), name='api_token_auth'),
    path('me/', views.user_profile, name='user_profile'),
    path('', include(router.urls)),
]
