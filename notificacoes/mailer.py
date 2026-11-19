from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import format_datetime
import hashlib
import html
import smtplib
import ssl
from zoneinfo import ZoneInfo


def build_message(event, settings):
    date = datetime.fromtimestamp(event.due_at, ZoneInfo(settings.timezone)).strftime("%d/%m/%Y às %H:%M")
    msg = EmailMessage()
    msg["From"] = settings.mail_from
    msg["To"] = event.student_email
    msg["Subject"] = "Lembrete: " + event.assignment_name
    msg["Date"] = format_datetime(datetime.now(timezone.utc))
    digest = hashlib.sha256(event.event_id.encode()).hexdigest()
    msg["Message-ID"] = f"<reengaja-{digest}@example.test>"
    msg["X-Reengajamento-ID"] = event.event_id
    msg.set_content(f"Olá, {event.student_name}!\n\nA tarefa \"{event.assignment_name}\" ainda está pendente.\n"
                    f"Prazo: {date} ({settings.timezone}).\nAcesse: {event.assignment_url}\n\n"
                    "Este lembrete convida você a retomar sua participação.\n"
                    "Se já enviou a tarefa após esta verificação, desconsidere esta mensagem.\n\nEquipe de apoio acadêmico\n")
    msg.add_alternative(f"<html lang='pt-BR'><body><p>Olá, {html.escape(event.student_name)}!</p>"
                        f"<p>A tarefa <strong>{html.escape(event.assignment_name)}</strong> ainda está pendente.</p>"
                        f"<p>Prazo: <strong>{date}</strong> ({settings.timezone}).</p>"
                        f"<p><a href='{html.escape(event.assignment_url, quote=True)}'>Acessar a tarefa no Moodle</a></p>"
                        "<p>Este lembrete convida você a retomar sua participação.</p>"
                        "<p>Se já enviou a tarefa após esta verificação, desconsidere esta mensagem.</p>"
                        "<p>Equipe de apoio acadêmico</p></body></html>", subtype="html")
    return msg


class SmtpMailer:
    def __init__(self, settings):
        self.settings = settings

    def send(self, event):
        settings = self.settings
        factory = smtplib.SMTP_SSL if settings.smtp_security == "ssl" else smtplib.SMTP
        options = {"timeout": settings.smtp_timeout}
        if settings.smtp_security == "ssl":
            options["context"] = ssl.create_default_context()
        with factory(settings.smtp_host, settings.smtp_port, **options) as server:
            server.ehlo()
            if settings.smtp_security == "starttls":
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            refused = server.send_message(build_message(event, settings))
            if refused:
                raise smtplib.SMTPRecipientsRefused(refused)


def permanent_failure(exc):
    if isinstance(exc, smtplib.SMTPRecipientsRefused):
        return bool(exc.recipients) and all(500 <= code < 600 for code, _ in exc.recipients.values())
    return isinstance(exc, smtplib.SMTPResponseException) and 500 <= exc.smtp_code < 600
