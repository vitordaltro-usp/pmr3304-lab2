"""Views do blog — versão 3: classes genéricas do Django.

ListView, DetailView, CreateView, UpdateView e DeleteView já implementam
o fluxo de CRUD; aqui só configuramos modelo, formulário, ordenação e
para onde redirecionar após salvar ou remover.
"""

from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import PostForm
from .models import Post


class PostListView(ListView):
    model = Post
    ordering = ['-pub_date']
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
