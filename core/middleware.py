import logging
import time

from django.utils.deprecation import MiddlewareMixin

from core.services import AuditLogService

logger = logging.getLogger('hrms')


class AuditLogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._audit_start_time = time.time()

    def process_response(self, request, response):
        if not hasattr(request, '_audit_start_time'):
            return response

        user = request.user if request.user.is_authenticated else None
        duration_ms = int((time.time() - request._audit_start_time) * 1000)

        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            AuditLogService.log_action(
                user=user,
                action=f"{request.method} {request.path}",
                module=request.resolver_match.app_names[0] if hasattr(request, 'resolver_match') and request.resolver_match else 'unknown',
                record_id=None,
                ip_address=self._get_client_ip(request),
                status_code=response.status_code,
            )

        logger.info(
            f"{request.method} {request.path} {response.status_code} {duration_ms}ms - {getattr(user, 'email', 'anonymous')}"
        )
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
