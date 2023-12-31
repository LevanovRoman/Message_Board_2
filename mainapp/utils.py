import pyotp
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.conf import settings


dic = {'ь': '', 'ъ': '', 'а': 'a', 'б': 'b', 'в': 'v',
       'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
       'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l',
       'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
       'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
       'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ы': 'yi',
       'э': 'e', 'ю': 'yu', 'я': 'ya'}


def transliteration(x):
    t = ''
    for i in x:
        t += dic.get(i.lower(), i.lower()).upper() if i.isupper() else dic.get(i, i)
    return t


def send_otp(request, email):
    totp = pyotp.TOTP(pyotp.random_base32(), interval=180)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=3)
    request.session['otp_valid_date'] = str(valid_date)

    send_mail(
        subject='Code for registration',
        message=f'Code for registration is  {otp}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email,]
    )


def mailing_task(title, mail_set, text, slug, template_name):
    print("MAILING")
    print(settings.EMAIL_HOST_USER)
    subject = f'Новое на сайте'
    html_content = render_to_string(
        template_name,
        {
            'title': title,
            'text': text,
            'link': f'{settings.ALLOWED_HOSTS[1]}/post/{slug}/',
        }
    )
    msg = EmailMultiAlternatives(
        subject=subject,
        body=title,
        from_email=settings.EMAIL_HOST_USER,
        to=mail_set,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print("SEND")
