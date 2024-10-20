from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Welcome to News Portal'
        message = f'Hi {instance.username}, thanks for signing up for our news portal!'
        send_mail(subject, message, 'dmitrij.croitoru@yandex.com', [instance.email])
