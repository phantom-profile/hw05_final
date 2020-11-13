from .models import Post, Comment
from django import forms


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'group': 'Сообщество',
                  'text': 'Текст поста',
                  'image': 'Картинка', }
        help_texts = {'group': 'Выберите сообщество из списка',
                      'text': 'Пост не может быть пустым и '
                              'состоять только из пробелов',
                      'image': 'Загрузите сюда картинку', }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Текст комментария', }
        help_texts = {'text': 'Комментарий не может быть пустым и '
                              'состоять только из пробелов', }
        widgets = {'text': forms.Textarea({'rows': 4})}
