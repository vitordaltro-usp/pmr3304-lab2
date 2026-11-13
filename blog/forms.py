from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        help_texts = {
            'content': 'Use tags HTML, como &lt;p&gt;, &lt;h3&gt; e &lt;ul&gt;.',
        }
