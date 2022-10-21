from http import HTTPStatus
import tempfile
from django.conf import settings


from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..models import Post

TEST_SLUG = 'test_slug'
TEST_SLUG_2 = 'test_slug_2'
TEST_USER = 'test_name'
TEST_USER_2 = 'test_name_2'
INDEX = reverse('posts:index')
FOLLOW = reverse('posts:follow_index')
SUBSCRIBED_USER = reverse('posts:profile_follow', args=[TEST_USER])
SUBSCRIBED_USER_2 = reverse('posts:profile_follow', args=[TEST_USER_2])
UNSUBSCRIBED_USER = reverse('posts:profile_unfollow', args=[TEST_USER])
POST_CREATE = reverse('posts:post_create')
GROUP_LIST = reverse('posts:group_list', args=[TEST_SLUG])
GROUP_LIST_2 = reverse('posts:group_list', args=[TEST_SLUG_2])
PROFILE = reverse('posts:profile', args=[TEST_USER])
LOGIN = reverse('users:login')
LOGOUT = reverse('users:logout')
SINGUP = reverse('users:signup')
NEXT = '?next='
REDIRECT_POST_CREATE = f'{LOGIN}{NEXT}{POST_CREATE}'
REDIRECT_LOGIN_FOLLOW = f'{LOGIN}{NEXT}{SUBSCRIBED_USER}'
REDIRECT_LOGIN_UNFOLLOW = f'{LOGIN}{NEXT}{UNSUBSCRIBED_USER}'
REDIRECT_LOGIN_FOLLOW_INDEX = f'{LOGIN}{NEXT}{FOLLOW}'
UNEXISTING_PAGE = '/unexisting_page/'
OK = HTTPStatus.OK
REDIRECT = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND
IMAGE = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
TEST_PICTURE = SimpleUploadedFile(
    name='test_pic.png',
    content=IMAGE,
    content_type='image/png',
)
TEST_PICTURE_2 = SimpleUploadedFile(
    name='test_pic_2.png',
    content=IMAGE,
    content_type='image/png',
)
IMAGE_FOLDER = Post._meta.get_field("image").upload_to
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

