from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="author")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_slug",
            description="Тестовое описание группы",
        )
        cls.post = Post.objects.create(
            text="Тест кеша", author=cls.user, group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_new_post_creates_new_post(self):
        """Главная страница кэширует отображаемую информацию"""
        response = self.guest_client.get(reverse("posts:index"))
        self.new_post = Post.objects.create(
            text="Тестовая заметка 2", author=self.user, group=self.group
        )
        response_2 = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(response.content, response_2.content)
        cache.clear()
        response_3 = self.guest_client.get(reverse("posts:index"))
        self.assertNotEqual(response.content, response_3.content)
