#!/usr/local/bin/python3
import yagmail
from datetime import datetime

from config import user, password


if user and password:
    user = user
    password = password
else:
    user = 'your username'
    password = 'your password'
to_send = {'e-mail to send': 'person\'s name'}

yag = yagmail.SMTP(user, password)


def send_email_yag(corpo_email, assunto):
    yag = yagmail.SMTP(user, password)
    to = to_send

    corpo_email_renderizado = f"Enviando report: <br> {corpo_email}"

    human_date = datetime.now().strftime("%d_%m_%Y_%H:%M:%S")
    assunto_email = f"{human_date} | {assunto}"

    for email, nome in to.items():
        try:
            yag.send(email, assunto_email, corpo_email_renderizado)
            print(
                f"Email enviado com sucesso para: {nome}: {email} Subject: {human_date}"
            )
        except Exception as e:
            print(f"problema ao enviar e-mail: {e}")


def trigger_send_mail():
    clt = datetime.now().strftime("%d_%m_%Y_%H:%M:%S")
    if clt[-5:-3] == "01":
        result = True
    else:
        result = False
    return result


if __name__ == "__main__":
    trigger_send_mail()
