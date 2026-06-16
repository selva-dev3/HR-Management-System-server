from core.models import AuditLog


class AuditLogService:
    @staticmethod
    def log_action(user, action, module, record_id, ip_address, status_code=None):
        AuditLog.objects.create(
            user=user,
            action=action,
            module=module,
            record_id=record_id,
            ip_address=ip_address,
            status_code=status_code,
        )
