import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from .constant import *

from ..models import User, Group, Post, Follow



@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USER)
        cls.user_2 = User.objects.create_user(username=TEST_USER_2)
        Follow.objects.create(
            user=cls.user_2,
            author=cls.user
        )
        cls.group = Group.objects.create(
            slug=TEST_SLUG,
            title='Тестовая группа',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            slug=TEST_SLUG_2,
            title='Вторая тестовая группа',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост',
            image=TEST_PICTURE
        )
        cls.POST_DETAIL = reverse('posts:post_detail', args=[cls.post.id])
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.authorized_user_2 = Client()
        cls.authorized_user_2.force_login(cls.user_2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_show_correct_context(self):
        """Шаблоны index, group_list, profile, post_detail, follow_index
        сформированы с правильным контекстом."""
        cache.clear()
        cases = (
            (INDEX, self.authorized_user, 'page_obj'),
            (FOLLOW, self.authorized_user_2, 'page_obj'),
            (GROUP_LIST, self.authorized_user, 'page_obj'),
            (PROFILE, self.authorized_user, 'page_obj'),
            (self.POST_DETAIL, self.authorized_user, 'post'),
        )
        for url, test_client, obj in cases:
            with self.subTest(url=url):
                response = test_client.get(url)
                if obj == 'page_obj':
                    self.assertEqual(len(response.context[obj]), 1)
                    post = response.context[obj][0]
                elif obj == 'post':
                    post = response.context[obj]
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image, self.post.image)

    def test_follow_post_page(self):
        """Пост не появялется в group_list и follow_index, для которых
        не предназначен."""
        urls = (GROUP_LIST_2, FOLLOW)
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertNotIn(self.post, response.context['page_obj'])

    def test_author_profile_display(self):
        """Автор появляется в контексте профиля."""
        response = self.authorized_user.get(PROFILE)
        author = response.context['author']
        self.assertEqual(author, self.user)

    def test_group_group_list_display(self):
        """Группа появляется в контексте групп-ленты
        без искажения атрибутов."""
        response = self.authorized_user.get(GROUP_LIST)
        group = response.context['group']
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.id, self.group.id)

    def test_pages_contain_num_posts(self):
        """Ленты с постами содержат правильное число постов
        на страницах."""
        cache.clear()
        Post.objects.all().delete()
        self.posts = Post.objects.bulk_create(
            Post(
                author=self.user,
                group=self.group,
                text=f'Тестовый пост {i}',
            )
            for i in range(settings.PAGE_COUNT + 1)
        )
        pages = [
            [INDEX, settings.PAGE_COUNT],
            [GROUP_LIST, settings.PAGE_COUNT],
            [PROFILE, settings.PAGE_COUNT],
            [FOLLOW, settings.PAGE_COUNT],
            [f'{INDEX}?page=2', 1],
            [f'{GROUP_LIST}?page=2', 1],
            [f'{PROFILE}?page=2', 1],
            [f'{FOLLOW}?page=2', 1],
        ]
        for page, num_posts in pages:
            with self.subTest(page=page):
                response = self.authorized_user_2.get(page)
                self.assertEqual(len(response.context['page_obj']), num_posts)

    def test_cache_index_page(self):
        """При удалении поста он останется в response.content /index/,
        пока не отчистить кэш принудительно."""
        response_1 = self.authorized_user.get(INDEX)
        Post.objects.all().delete
        response_2 = self.authorized_user.get(INDEX)
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.authorized_user.get(INDEX)
        self.assertNotEqual(response_1.content, response_3.content)

    def test_follow_page(self):
        """Авторизированный автор может подписаться на другого автора."""
        follow_count = Follow.objects.count()
        self.authorized_user.get(SUBSCRIBED_USER_2)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            ).exists()
        )

    def test_unfollow_page(self):
        """Авторизированный автор может отписаться от избранного автора."""
        follow_count = Follow.objects.count()
        self.authorized_user_2.get(UNSUBSCRIBED_USER)
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_2,
                author=self.user
            ).exists()
        )