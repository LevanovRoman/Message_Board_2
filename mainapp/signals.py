from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from .models import Post, Comment
from .utils import mailing_task


@receiver(post_save, sender=Post)
def notify_create_post(sender, instance, created, **kwargs):
    if created:
        all_cat = instance.category.subscribers.all()
        subs_list = [cat.email for cat in all_cat if cat.email]
        template_name = 'mainapp/message_create_post.html'
        mailing_task(instance.title, list(subs_list),
                     instance.text, instance.slug, template_name)


@receiver(post_save, sender=Comment)
def notify_create_post(sender, instance, created, **kwargs):
    if created:
        author_mail = instance.post.user.email
        template_name = 'mainapp/message_get_comment.html'
        mailing_task(instance.text, [author_mail,],
                     instance.text, instance.post.slug, template_name)

