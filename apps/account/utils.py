# from django.core.mail import send_mail
from decouple import config
from django.core.mail import EmailMultiAlternatives, send_mail


def send_notification(title: str, email:str):
    message = f""
    from_email = "rayhancafe@gmail.com"
    send_mail(
        title,
        message,
        from_email,
        [email],
        fail_silently=False,
    )

    # send_mail(
    #     title,
    #     message,
    #     from_email,
    #     [email],
    #     fail_silently=False,
    # )
