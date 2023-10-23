from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from wagtail_tenants.models import SmtpAuthenticator
from django.utils.html import strip_tags
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail import get_connection

WAGTAIL_TEANTS_USE_SINGLE_SMTP = getattr(settings, "WAGTAIL_TEANTS_USE_SMTP", False)
WAGTAIL_TEANTS_SMTP_CLIENT = getattr(settings, "WAGTAIL_TEANTS_SMTP_CLIENT", None)
WAGTAIL_TENANTS_EMAIL_FAIL_SILENT = getattr(
    settings, "WAGTAIL_TENANTS_EMAIL_FAIL_SILENT", False
)


class TenantEmailservice:
    def __init__(
        self,
        site,
        tenant=None,
        **kwargs,
    ):
        if not tenant:
            tenant = kwargs.pop("tenant", None)
        self.site = site
        self.tenant = tenant
        if WAGTAIL_TEANTS_USE_SINGLE_SMTP:
            self.client_credentials = WAGTAIL_TEANTS_SMTP_CLIENT
        else:
            try:
                self.client_credentials = SmtpAuthenticator.objects.get(
                    tenant=self.tenant, site=self.site
                )

            except SmtpAuthenticator.DoesNotExist:
                self.client_credentials = None

        if self.client_credentials:
            self.client = EmailBackend(
                host=self.client_credentials.smtp_host or None,
                port=self.client_credentials.smtp_port or None,
                username=self.client_credentials.smtp_user or None,
                password=self.client_credentials.smtp_password or None,
                use_tls=self.client_credentials.use_tls or False,
                fail_silently=WAGTAIL_TENANTS_EMAIL_FAIL_SILENT,
                use_ssl=self.client_credentials.use_ssl or False,
                timeout=self.client_credentials.timeout or None,
                ssl_keyfile=self.client_credentials.ssl_keyfile or None,
                ssl_certfile=self.client_credentials.ssl_certfile or None,
            )

    def send(
        self,
        subject,
        message="",
        html_template=None,
        context=None,
        to=[],
        from_email=None,
        cc=None,
        bcc=None,
    ):
        if not from_email:
            from_email = self.client_credentials.email

        text_content = strip_tags(message)

        if html_template:
            html_content = render_to_string(html_template, context)
            text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to,
            cc=cc,
            bcc=bcc,
        )

        if html_template:
            msg.attach_alternative(html_content, "text/html")

        self.client.send_messages([msg])
