from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post


class PostCrudTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(
            title='Post de teste',
            content='<p>Conteúdo <strong>em HTML</strong></p>',
            pub_date=timezone.make_aware(datetime(2026, 11, 4, 10, 0)),
        )

    def test_listagem_mostra_titulo_com_link(self):
        resp = self.client.get(reverse('blog:post_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'base.html')
        self.assertContains(resp, 'Post de teste')
        self.assertContains(resp, reverse('blog:post_detail', args=[self.post.pk]))

    def test_detalhe_renderiza_html_e_data(self):
        resp = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '<strong>em HTML</strong>', html=False)
        self.assertContains(resp, '4 de Novembro de 2026, 10:00')

    def test_detalhe_inexistente_retorna_404(self):
        resp = self.client.get(reverse('blog:post_detail', args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_criar_post(self):
        resp = self.client.post(reverse('blog:post_create'), {
            'title': 'Novo', 'content': '<p>Olá</p>',
        })
        novo = Post.objects.get(title='Novo')
        self.assertRedirects(resp, reverse('blog:post_detail', args=[novo.pk]))

    def test_editar_post(self):
        url = reverse('blog:post_update', args=[self.post.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.post(url, {'title': 'Editado', 'content': '<p>x</p>'})
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Editado')

    def test_remover_pede_confirmacao_e_remove_por_post(self):
        url = reverse('blog:post_delete', args=[self.post.pk])
        resp = self.client.get(url)
        self.assertContains(resp, 'Tem certeza')
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('blog:post_list'))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
