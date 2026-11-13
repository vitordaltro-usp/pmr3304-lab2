from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.models import User

from .models import Category, Comment, Post


class PostCrudTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(
            title='Post de teste',
            content='<p>Conteúdo <strong>em HTML</strong></p>',
            pub_date=timezone.make_aware(datetime(2026, 11, 4, 10, 0)),
        )
        self.cat = Category.objects.create(name='Tecnologia')
        self.post.categories.add(self.cat)

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
            'title': 'Novo', 'content': '<p>Olá</p>', 'categories': [self.cat.pk],
        })
        novo = Post.objects.get(title='Novo')
        self.assertRedirects(resp, reverse('blog:post_detail', args=[novo.pk]))

    def test_criar_post_sem_titulo_mostra_erro(self):
        resp = self.client.post(reverse('blog:post_create'), {
            'title': '', 'content': '<p>Olá</p>',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'errorlist')
        self.assertEqual(Post.objects.count(), 1)

    def test_editar_post(self):
        url = reverse('blog:post_update', args=[self.post.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.post(url, {'title': 'Editado', 'content': '<p>x</p>', 'categories': [self.cat.pk]})
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


class CommentTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title='Post', content='<p>x</p>')
        self.user = User.objects.create_user('leitor_teste', password='senha-de-teste-123')
        self.url = reverse('blog:comment_create', args=[self.post.pk])

    def test_detalhe_tem_link_para_comentar(self):
        resp = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        self.assertContains(resp, self.url)

    def test_comentar_exige_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp['Location'])

    def test_comentar_post_inexistente_retorna_404(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('blog:comment_create', args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_criar_comentario_logado(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        resp = self.client.post(self.url, {'text': 'Ótima notícia!'})
        self.assertRedirects(resp, reverse('blog:post_detail', args=[self.post.pk]))
        comment = Comment.objects.get()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_comentarios_mais_recentes_primeiro(self):
        Comment.objects.create(
            post=self.post, author=self.user, text='antigo',
            created_at=timezone.make_aware(datetime(2026, 11, 1, 9, 0)),
        )
        Comment.objects.create(
            post=self.post, author=self.user, text='recente',
            created_at=timezone.make_aware(datetime(2026, 11, 2, 9, 0)),
        )
        resp = self.client.get(reverse('blog:post_detail', args=[self.post.pk]))
        html = resp.content.decode()
        self.assertLess(html.index('recente'), html.index('antigo'))
        self.assertContains(resp, '02/11/2026 09:00')


class CategoryTests(TestCase):
    def setUp(self):
        self.tec = Category.objects.create(name='Tecnologia', description='Notícias de tecnologia')
        self.cie = Category.objects.create(name='Ciência')
        self.p1 = Post.objects.create(title='Post em duas', content='<p>a</p>')
        self.p1.categories.add(self.tec, self.cie)
        self.p2 = Post.objects.create(title='Só ciência', content='<p>b</p>')
        self.p2.categories.add(self.cie)

    def test_header_tem_link_para_categorias(self):
        resp = self.client.get(reverse('blog:post_list'))
        self.assertContains(resp, reverse('blog:category_list'))

    def test_listagem_de_categorias(self):
        resp = self.client.get(reverse('blog:category_list'))
        self.assertContains(resp, 'Tecnologia')
        self.assertContains(resp, reverse('blog:category_detail', args=[self.cie.pk]))

    def test_categoria_lista_seus_posts_reutilizando_template(self):
        resp = self.client.get(reverse('blog:category_detail', args=[self.tec.pk]))
        self.assertTemplateUsed(resp, 'blog/post_list.html')
        self.assertContains(resp, 'Categoria: Tecnologia')
        self.assertContains(resp, 'Notícias de tecnologia')
        self.assertContains(resp, 'Post em duas')
        self.assertNotContains(resp, 'Só ciência')

    def test_categoria_inexistente_retorna_404(self):
        resp = self.client.get(reverse('blog:category_detail', args=[9999]))
        self.assertEqual(resp.status_code, 404)

    def test_detalhe_do_post_mostra_categorias_com_link(self):
        resp = self.client.get(reverse('blog:post_detail', args=[self.p1.pk]))
        self.assertContains(resp, reverse('blog:category_detail', args=[self.tec.pk]))
        self.assertContains(resp, reverse('blog:category_detail', args=[self.cie.pk]))

    def test_post_sem_categoria_e_recusado_no_formulario(self):
        resp = self.client.post(reverse('blog:post_create'), {'title': 'X', 'content': '<p>x</p>'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Post.objects.filter(title='X').exists())
