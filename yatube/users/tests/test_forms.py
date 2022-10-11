from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersFormTests(TestCase):
    def setUp(self):
        """Создаем клиент гостя."""
        self.guest_client = Client()

    def test_create_user(self):
        """Создание нового прользователя."""
        users_count = User.objects.count()
        form_data = {
            "first_name": "Andrey",
            "last_name": "Zharov",
            "username": "kotttobormottt",
            "email": "vin999_09@mail.ru",
            "password1": "qwerty12345_!",
            "password2": "qwerty12345_!",
        }
        response = self.guest_client.post(
            reverse("users:signup"), data=form_data, follow=True
        )
        user = User.objects.last()
        self.assertRedirects(response, reverse("posts:index"))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(user.username, form_data["username"])
        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])
