from django import forms

from .models import Comment, Post,Group


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        help_text = {
            "group": "Группа",
            "text": "Текст",
            "image": "Изображение",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('title', 'slug', 'description',)
        prepopulated_fields = {"slug": ("title",)}
        help_text = {'title':'Название группы',
                    'description':'Описание группы',}