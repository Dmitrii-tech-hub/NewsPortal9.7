from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post


@shared_task
def send_new_post_email(post_id):
    post = Post.objects.get(pk=post_id)

    for category in post.categories.all():
        subscribers = category.subscribers.all()
        for subscriber in subscribers:
            # Prepare email content
            html_content = render_to_string(
                'new_post_email.html',
                {
                    'user': subscriber,
                    'post': post,
                    'preview': post.content[:50],  # First 50 characters
                }
            )

            # Email setup
            msg = EmailMultiAlternatives(
                subject=f'Новая статья в категории {category.name}: {post.title}',
                body=post.content[:50],
                from_email='dmitrij.croitoru@yandex.com',  # Replace with your email
                to=[subscriber.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
