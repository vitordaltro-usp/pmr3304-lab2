"""Views do blog — versão 3: classes genéricas do Django.

ListView, DetailView, CreateView, UpdateView e DeleteView já implementam
o fluxo de CRUD; aqui só configuramos modelo, formulário, ordenação e
para onde redirecionar após salvar ou remover.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


class PostListView(ListView):
    model = Post
    ordering = ['-pub_date']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('categories')
    # template padrão: blog/post_list.html; contexto: post_list


class PostDetailView(DetailView):
    # DetailView já responde com 404 se o post não existir.
    model = Post
    # template padrão: blog/post_detail.html; contexto: post


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    # template padrão: blog/post_form.html

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    # template padrão: blog/post_form.html; contexto: post e form

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(DeleteView):
    # GET mostra blog/post_confirm_delete.html; POST remove o post.
    model = Post
    success_url = reverse_lazy('blog:post_list')


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Página de criação de comentário de um post (exige login).

    O autor é o usuário logado e o post vem da URL; o formulário só pede o texto.
    """

    model = Comment
    form_class = CommentForm
    # template padrão: blog/comment_form.html

    def dispatch(self, request, *args, **kwargs):
        # 404 se o post não existir.
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.post_obj
        return context

    def form_valid(self, form):
        form.instance.post = self.post_obj
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class CategoryListView(ListView):
    model = Category
    # template padrão: blog/category_list.html; contexto: category_list

    def get_queryset(self):
        return Category.objects.annotate(num_posts=Count('posts')).order_by('name')


class CategoryDetailView(DetailView):
    """Página de uma categoria com todos os seus posts.

    DetailView responde com 404 se a categoria não existir. O template da
    listagem de posts (parte 1) é reutilizado, recebendo também a categoria.
    """

    model = Category
    template_name = 'blog/post_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_list'] = (
            self.object.posts.order_by('-pub_date').prefetch_related('categories')
        )
        return context
