import shutil
import tempfile

from django import forms
from django.conf import settings
from django.test import Client, TestCase, override_settings

from ..models import Comment, Group, Post, User
from .constant import *

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USER)
        cls.user_2 = User.objects.create_user(username=TEST_USER_2)
        cls.group = Group.objects.create(
            slug=TEST_SLUG,
            title="Тестовая группа",
            description="Тестовое описание",
        )
        cls.group_2 = Group.objects.create(
            slug=TEST_SLUG_2,
            title="Тестовая группа 2 ",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text="Тестовый пост",
        )
        cls.POST_DETAIL = reverse("posts:post_detail", args=[cls.post.id])
        cls.POST_EDIT = reverse("posts:post_edit", args=[cls.post.id])
        cls.POST_COMMENT = reverse("posts:add_comment", args=[cls.post.id])
        cls.REDIRECT_POST_COMMENT = f"{LOGIN}{NEXT}{cls.POST_COMMENT}"
        cls.REDIRECT_POST_EDIT = f"{LOGIN}{NEXT}{cls.POST_EDIT}"
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2 = Client()
        cls.authorized_client_2.force_login(cls.user_2)

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        Post.objects.all().delete()

        form_data = {
            "text": "Второй тестовый пост",
            "group": self.group.id,
            "image": TEST_PICTURE,
        }
        response = self.authorized_client.post(
            POST_CREATE, data=form_data, follow=True
        )
        self.assertRedirects(response, PROFILE)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.group_id, form_data["group"])
        self.assertEqual(post.author, self.user)
        self.assertEqual(
            post.image.name, f'{IMAGE_FOLDER}{form_data["image"].name}'
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            "text": "Второй тестовый пост",
            "group": self.group_2.id,
            "image": TEST_PICTURE_2,
        }
        response = self.authorized_client.post(
            self.POST_EDIT, data=form_data, follow=True
        )
        urls = (self.POST_EDIT, POST_CREATE)
        form_fields = {
            "text": forms.CharField,
            "group": forms.fields.ChoiceField,
        }
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(Post.objects.count(), post_count)
        post = response.context["post"]
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.group_id, form_data["group"])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(
            post.image.name, f'{IMAGE_FOLDER}{form_data["image"].name}'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    form_field = response.context["form"].fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_create_comment(self):
        """Валидная форма создает запись в Comment."""
        Comment.objects.count()
        form_data = {"text": "Новый комментарий"}
        response = self.authorized_client.post(
            self.POST_COMMENT, data=form_data, follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get()
        self.assertEqual(comment.text, form_data["text"])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

    def test_guest_can_not_create_post_or_comment(self):
        """Неавторизованный пользователь не может создать
        пост или комментарий."""
        Post.objects.all().delete()
        Comment.objects.all().delete()
        cases = (
            (
                Post,
                POST_CREATE,
                REDIRECT_POST_CREATE,
                {
                    "text": "Еще один тестовый пост",
                    "group": self.group_2.id,
                    "image": TEST_PICTURE,
                },
            ),
            (
                Comment,
                self.POST_COMMENT,
                self.REDIRECT_POST_COMMENT,
                {"text": "Еще один тестовый комментарий"},
            ),
        )
        for (
            obj,
            url,
            redirect_url,
            form_data,
        ) in cases:
            with self.subTest(url=url):
                response = self.client.post(url, data=form_data, follow=True)
                self.assertRedirects(response, redirect_url)
                self.assertEqual(len(obj.objects.all()), 0)

    def test_guest_or_non_author_cannot_edit(self):
        """Неавторизованный пользователь и не-автор поста не может
        отредактировать пост."""
        cases = (
            (self.client, "Пост изменен анонимом", self.REDIRECT_POST_EDIT),
            (
                self.authorized_client_2,
                "Пост изменен не-автором",
                self.POST_DETAIL,
            ),
        )
        for client, text, redirect_url in cases:
            with self.subTest(client=client):
                form_data = {
                    "text": text,
                    "group": self.group_2,
                    "image": TEST_PICTURE,
                }
                response = client.post(
                    self.POST_EDIT,
                    data=form_data,
                )
                post = Post.objects.get(id=self.post.id)
                self.assertRedirects(response, redirect_url)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.image, self.post.image)
