from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def paginator_func(post_list, request):
    # Paginator
    paginator = Paginator(post_list, PAGINATOR_PAGE_COUNT)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


@cache_page(20)
def index(request):
    # Главная страница
    post_list = Post.objects.select_related("author").all()
    page_obj = paginator_func(post_list, request)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    # Страница с группами
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related("author").all()
    page_obj = paginator_func(post_list, request)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    # Профиль пользователя
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author).exists()
    post_list = author.posts.all()
    page_obj = paginator_func(post_list, request)
    context = {
        "author": author,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    # Показывает пост
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        "post": post,
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    # Создание нового поста
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        temp_form = form.save(commit=False)
        temp_form.author = request.user
        temp_form.save()
        return redirect("posts:profile", temp_form.author)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    # Редактирование поста
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)
    return render(
        request,
        "posts/create_post.html",
        {"form": form, "is_edit": True, "post": post},
    )


@login_required
def add_comment(request, post_id):
    # Добавить комментарий
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    title = "Публикации избранных авторов"
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_func(post_list, request)
    context = {
        "title": title,
        "page_obj": page_obj,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    follow_author = get_object_or_404(User, username=username)
    if follow_author != request.user and (
        not request.user.follower.filter(author=follow_author).exists()
    ):
        Follow.objects.create(user=request.user, author=follow_author)
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    follow_author = get_object_or_404(User, username=username)
    data_follow = request.user.follower.filter(author=follow_author)
    if data_follow.exists():
        data_follow.delete()
    return redirect("posts:profile", username)
