from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Category
from .models import Profile
from .forms import ProfileUpdateForm
from .forms import PostForm
from django.http import JsonResponse
from .models import Comment
from django.db.models import Q
from .forms import RegisterForm

# Главная страница
from django.shortcuts import render
from .models import Post, Category


def home(request):
    # Получаем все категории
    categories = Category.objects.all()

    # Фильтрация по категории
    category_id = request.GET.get("category")
    if category_id:
        posts = Post.objects.filter(category_id=category_id).order_by("-created_at")
    else:
        posts = Post.objects.all().order_by("-created_at")

    # Проверяем, подписан ли пользователь на авторов постов
    following = {}
    if request.user.is_authenticated:
        following = {post.author.username: request.user in post.author.profile.followers.all() for post in posts}

    return render(request, "blog/home.html", {"posts": posts, "following": following, "categories": categories})

# Страница входа
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'blog/login.html')


# Страница регистрации
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
        else:
            return render(request, "blog/register.html", {"form": form})  # Покажет ошибки
    else:
        form = RegisterForm()

    return render(request, "blog/register.html", {"form": form})


def messages_view(request):
    return render(request, 'blog/messages.html')


@login_required
def create_post_view(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    categories = Category.objects.all()  # ✅ Загружаем категории из базы

    return render(request, "blog/create_post.html", {"form": form, "categories": categories})  # ✅ Передаём категории


@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile  # Получаем профиль
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')  # Загружаем посты
    is_following = request.user in profile_user.profile.followers.all() if request.user.is_authenticated else False

    # Обработка формы изменения профиля
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=username)
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'blog/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'form': form,
        'is_following': is_following,
        'posts': posts
    })


@login_required
def follow_unfollow(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = target_user.profile  # Получаем профиль пользователя
    user = request.user  # Текущий пользователь

    if user in profile.followers.all():
        profile.followers.remove(user)
        following = False
    else:
        profile.followers.add(user)
        following = True

    return JsonResponse({"following": following, "followers_count": profile.total_followers()})

@login_required
@csrf_exempt
def create_post_view(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Метод не поддерживается"}, status=400)

    title = request.POST.get("title", "").strip()
    content = request.POST.get("content", "").strip()
    image = request.FILES.get("image")
    category_id = request.POST.get("category")

    if not title or not content:
        return JsonResponse({"success": False, "error": "Не заполнены обязательные поля"}, status=400)

    category = None
    if category_id:
        category = Category.objects.filter(id=category_id).first()

    post = Post.objects.create(
        author=request.user,
        title=title,
        content=content,
        image=image,
        category=category  # ✅ Добавляем категорию
    )

    return JsonResponse({
        "success": True,
        "title": post.title,
        "content": post.content,
        "image": post.image.url if post.image else None,
        "author": post.author.username,
        "category": post.category.name if post.category else "Без категории"
    })

@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content")

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )

        return JsonResponse({
            "success": True,
            "author": request.user.username,
            "avatar": request.user.profile.avatar.url,
            "content": comment.content,
            "comment_id": comment.id
        })
    return JsonResponse({"success": False, "error": "Неверный метод запроса"}, status=400)


def get_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent=None).order_by('-created_at')

    comment_list = []
    for comment in comments:
        comment_list.append({
            "comment_id": comment.id,
            "author": comment.author.username,
            "avatar": comment.author.profile.avatar.url,
            "content": comment.content,
            "created_at": comment.created_at.strftime('%d-%m-%Y %H:%M')
        })

    return JsonResponse({"success": True, "comments": comment_list})

#читать далее
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, "blog/post.html", {"post": post})

@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)  # Если уже лайкнул – убираем лайк
        liked = False
    else:
        post.likes.add(user)  # Добавляем лайк
        post.dislikes.remove(user)  # Убираем дизлайк, если был
        liked = True

    return JsonResponse({"likes": post.total_likes(), "dislikes": post.total_dislikes(), "liked": liked})

@login_required
def dislike_post(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user

    if user in post.dislikes.all():
        post.dislikes.remove(user)  # Если уже дизлайкнул – убираем дизлайк
        disliked = False
    else:
        post.dislikes.add(user)  # Добавляем дизлайк
        post.likes.remove(user)  # Убираем лайк, если был
        disliked = True

    return JsonResponse({"likes": post.total_likes(), "dislikes": post.total_dislikes(), "disliked": disliked})

def search_view(request):
    query = request.GET.get("q", "").strip()
    users = []
    posts = []

    if query:
        users = User.objects.filter(username__icontains=query)
        posts = Post.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))

    return render(request, "blog/search_results.html", {"query": query, "users": users, "posts": posts})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        post.delete()
        return redirect('home')

    return render(request, 'blog/delete_post.html', {'post': post})