import logging
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException, NotAuthenticated, PermissionDenied as DRFPermissionDenied
from rest_framework.response import Response
from rest_framework.views import set_rollback

logger = logging.getLogger('hrms')


class HRMSException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'HRMS_ERROR'
    default_detail = 'An error occurred.'


class ConflictException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'CONFLICT'
    default_detail = 'Resource conflict.'


def custom_exception_handler(exc, context):
    request = context.get('request', None)
    user_id = getattr(getattr(request, 'user', None), 'id', None)

    if isinstance(exc, Http404):
        exc = APIException(detail='Not found.', code='NOT_FOUND')
        exc.status_code = status.HTTP_404_NOT_FOUND

    if isinstance(exc, PermissionDenied):
        exc = DRFPermissionDenied()

    if isinstance(exc, ValidationError):
        exc = APIException(detail=str(exc), code='VALIDATION_ERROR')
        exc.status_code = status.HTTP_400_BAD_REQUEST

    if isinstance(exc, APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = str(int(exc.wait))

        set_rollback()
        detail = exc.detail
        if isinstance(detail, list):
            detail = detail[0] if detail else 'An error occurred.'
        if isinstance(detail, dict):
            detail = next(iter(detail.values()))
            if isinstance(detail, list):
                detail = detail[0] if detail else 'An error occurred.'

        response = Response({
            'error': exc.get_codes(),
            'message': str(detail),
            'status': exc.status_code,
        }, status=exc.status_code, headers=headers)

        return response

    logger.error(f"Unhandled exception | user={user_id} | path={getattr(request, 'path', 'unknown')}", exc_info=True)

    return Response({
        'error': 'INTERNAL_ERROR',
        'message': 'An unexpected error occurred. Please try again later.',
        'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
