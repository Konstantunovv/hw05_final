from http import HTTPStatus
from django.core.cache import cache

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="authorized")
        cls.user_not = User.objects.create_user(username="not_authorized")
        cls.group = Group.objects.create(
            title="Test Group",
            slug="test_slug",
            description="test description of the group",
        )
        cls.post = Post.objects.create(text="test post", author=cls.user)
        cls.page_templates = {
            "/": HTTPStatus.OK,
            f"/group/{cls.group.slug}/": HTTPStatus.OK,
            f"/profile/{cls.user}/": HTTPStatus.OK,
            f"/posts/{cls.post.id}/": HTTPStatus.OK,
            f"/posts/{cls.post.pk}/edit/": HTTPStatus.FOUND,
            "/create/": HTTPStatus.FOUND,
            "/unexisting_page/": HTTPStatus.NOT_FOUND,
            "/auth/reset/done/": HTTPStatus.OK,
            "/auth/reset/<uidb64>/<token>/": HTTPStatus.OK,
            "/auth/password_reset/done/": HTTPStatus.OK,
            "/auth/password_reset/": HTTPStatus.OK,
            "/auth/password_change/done/": HTTPStatus.FOUND,
            "/auth/password_change/": HTTPStatus.FOUND,
            "/auth/logout/": HTTPStatus.OK,
            "/auth/login/": HTTPStatus.OK,
            "/auth/signup/": HTTPStatus.OK,
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_no_posts = Client()
        self.authorized_client_no_posts.force_login(self.user_not)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/":"posts/index.html",
            f"/group/{self.group.slug}/": "posts/group_list.html",
            f"/profile/{self.user}/": "posts/profile.html",
            f"/posts/{self.post.id}/": "posts/post_detail.html",
            f"/posts/{self.post.pk}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }
        cache.clear()
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_access_guest(self):
        """URL-адрес доступен или нет не авторизированному пользователю."""
        for address, code_status in self.page_templates.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, code_status)

    def test_urls_uses_correct_access_auth(self):
        """URL-адрес доступен авторизированному пользователю."""
        self.page_templates = {
            "/auth/password_change/": HTTPStatus.OK,
        }
        for address, code_status in self.page_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code_status)

    def test_urls_uses_correct_access_auth_edit(self):
        """URL-адрес редактирования не доступен пользователю."""
        self.page_templates = {
            "/auth/password_change/": HTTPStatus.OK,
        }
        for address, code_status in self.page_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client_no_posts.get(address)
                self.assertEqual(response.status_code, code_status)

    def test_404(self):
        """Проверяем возвращает ли сервер код 404, если страница не найдена"""
        response = self.client.get("/404/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
