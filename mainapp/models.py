from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify

from .utils import transliteration


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Категория')
    slug = models.SlugField(max_length=50, unique=True, db_index=True, verbose_name="Slug")
    subscribers = models.ManyToManyField(User, verbose_name='Подписки', related_name='followers', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_absolute_url(self):
        return reverse('category', kwargs={'category_slug': self.slug})

    def get_users_list(self):
        queryset_users = self.subscribers.values()
        return [i['username'] for i in queryset_users]


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_post', verbose_name='Автор')
    title = models.CharField(max_length=255, verbose_name='Название')
    text = models.TextField(verbose_name='Текст')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория',
                                 related_name="category_post")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d", blank=True)
    video_file = models.FileField(upload_to='post_video', blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="Slug")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        string = transliteration(self.title)
        self.slug = slugify(string)
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comment', verbose_name='Пост')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment', verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="Slug")
    time_created = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    status = models.BooleanField(default=False, verbose_name='Активно')

    def __str__(self):
        return f"Post: {self.post} - user: {self.user}"

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def get_absolute_url(self):
        return reverse('comment', kwargs={'comment_slug': self.slug})

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.text[:25])
        return super().save(*args, **kwargs)







