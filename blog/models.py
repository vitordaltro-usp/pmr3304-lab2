from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField('nome', max_length=100, unique=True)
    description = models.TextField('descrição', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField('título', max_length=200)
    # O conteúdo é HTML guardado como texto; no template ele é exibido com |safe.
    content = models.TextField('conteúdo (HTML)')
    pub_date = models.DateTimeField('data de postagem', default=timezone.now)
    # Um post pode estar em várias categorias (e deve estar em pelo menos uma).
    categories = models.ManyToManyField(
        Category,
        related_name='posts',
        verbose_name='categorias',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='post',
    )
    # O autor referencia o modelo de usuário do Django (settings.AUTH_USER_MODEL).
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='autor',
    )
    text = models.TextField('texto')
    created_at = models.DateTimeField('data de postagem', default=timezone.now)

    class Meta:
        # Mais recente primeiro.
        ordering = ['-created_at']
        verbose_name = 'comentário'
        verbose_name_plural = 'comentários'

    def __str__(self):
        return f'{self.author} em "{self.post}"'
