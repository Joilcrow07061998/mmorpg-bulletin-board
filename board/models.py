from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field

# описание категории
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Categories' # что бы не было "Categorys" в админке

    def __str__(self):
        return self.name

# описание поста
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='posts')
    headline = models.CharField(max_length=255)
    body = CKEditor5Field('Text', config_name='default') # редактор картинок
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.headline

# описание отклика
class Response(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    body = models.TextField()
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response by {self.author.username} on {self.post.headline}" # что бы в админке было понятно, что за отклик
