from django.db import models
from django.utils import timezone


class Post(models.Model):
    title = models.CharField('título', max_length=200)
    # O conteúdo é HTML guardado como texto; no template ele é exibido com |safe.
    content = models.TextField('conteúdo (HTML)')
    pub_date = models.DateTimeField('data de postagem', default=timezone.now)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.title
