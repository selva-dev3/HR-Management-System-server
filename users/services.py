import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from core.exceptions import HRMSException

User = get_user_model()
logger = logging.getLogger('hrms')


class UserService:
    @staticmethod
    def change_password(user, new_password):
        user.set_password(new_password)
        user.reset_lockout()
        user.save(update_fields=['password', 'failed_login_attempts', 'locked_until'])
        logger.info(f'Password changed for user {user.id}')

    @staticmethod
    def deactivate(user):
        user.is_active = False
        user.save(update_fields=['is_active'])
        logger.info(f'User {user.id} deactivated')

    @staticmethod
    def record_failed_login(email):
        try:
            user = User.objects.get(email=email)
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.HRMS['MAX_FAILED_LOGIN_ATTEMPTS']:
                user.locked_until = timezone.now() + timezone.timedelta(minutes=settings.HRMS['LOGIN_LOCKOUT_MINUTES'])
                logger.warning(f'User {email} locked out until {user.locked_until}')
            user.save(update_fields=['failed_login_attempts', 'locked_until'])
        except User.DoesNotExist:
            pass

    @staticmethod
    def send_password_reset_email(user, reset_url):
        subject = 'Password Reset Request'
        message = f'Click the link to reset your password: {reset_url}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        logger.info(f'Password reset email sent to {user.email}')
