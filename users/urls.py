from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import AuthViewSet, RolePermissionViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles-permissions', RolePermissionViewSet, basename='role-permission')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('me/', AuthViewSet.as_view({'get': 'me'}), name='me'),
    path('change-password/', AuthViewSet.as_view({'post': 'change_password'}), name='change_password'),
]
