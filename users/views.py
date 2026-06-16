from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from core.exceptions import ConflictException
from core.permissions import IsSuperAdmin
from users.models import RolePermission
from users.serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RolePermissionSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)
from users.services import UserService

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(tags=['Authentication'])
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @extend_schema(request=CustomTokenObtainPairSerializer, responses={200: CustomTokenObtainPairSerializer})
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        return CustomTokenObtainPairView.as_view()(request._request)

    @extend_schema(responses={200: UserReadSerializer})
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserReadSerializer(request.user).data)

    @extend_schema(request=ChangePasswordSerializer, responses={204: None})
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        UserService.change_password(request.user, serializer.validated_data['new_password'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ('create',):
            return UserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        return UserReadSerializer

    def get_queryset(self):
        qs = User.objects.all()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ('true', '1'))
        return qs.order_by('-date_joined')

    def create(self, request, *args, **kwargs):
        if User.objects.filter(email=request.data.get('email')).exists():
            raise ConflictException('Email is already registered.')
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if 'email' in request.data:
            raise PermissionDenied('Email cannot be updated.')
        return super().update(request, *args, **kwargs)

    @extend_schema(responses={204: None})
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        UserService.deactivate(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={200: UserReadSerializer(many=True)})
    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=['Roles & Permissions'])
class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsSuperAdmin]
    filterset_fields = ['role', 'module']
