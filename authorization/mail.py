from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from config import settings

html_form_pattern = '''<html><body><form enctype="application/json", method="post", action="{host}/verify">
    <fieldset>
        <legend>Подтверждение почты</legend>
        <input type="hidden" value="{token}" name="token">
        <input type="submit" value="Подтвердить почту">
    </fieldset>
</form></body></html>'''


async def send_verify_request(email: str, token: str):
    message = MIMEMultipart('alternative')
    html = MIMEText(html_form_pattern.format(token=token, host=settings.base_url), 'html', 'utf-8')
    plain = MIMEText(F'Введите код подтверждения {token}', 'plain', 'utf-8')
    message['From'] = settings.email.sender
    message['To'] = email
    message['Subject'] = 'Подтверждениe почты'
    message.attach(html)
    message.attach(plain)
    await aiosmtplib.send(message,
                          hostname=settings.email.host,
                          port=settings.email.port,
                          username=settings.email.username,
                          password=settings.email.password,
                          use_tls=settings.email.use_tls,
                          start_tls=settings.email.starttls)