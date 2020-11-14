from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page,
               'paginator': paginator,
               }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts_group.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page,
               'paginator': paginator,
               'group': group,
               }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new.html', {'form': form})

    form = PostForm(request.POST, files=request.FILES or None)

    if form.is_valid():
        author = Post(author=request.user)
        new_form = PostForm(request.POST, instance=author,
                            files=request.FILES or None)
        new_form.save()
        return redirect('index')

    return render(request, 'new.html', {'form': form})


def profile(request, username):
    viewer = request.user
    page_user = get_object_or_404(User, username=username)
    posts = page_user.posts.all()
    first_post = page_user.posts.first()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if viewer.is_authenticated:
        following = viewer.follower.filter(author=page_user)
    else:
        following = False
    context = {'page_user': page_user,
               'page': page,
               'post': first_post,
               'paginator': paginator,
               'viewer': viewer,
               'following': following,
               }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    viewer = request.user
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {
        'page_user': post.author,
        'post': post,
        'viewer': viewer,
        'comments': comments,
        'form': form
    }
    return render(request, 'post.html', context)


@login_required
def add_comment(request, username, post_id):
    viewer = request.user
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.method != 'POST':
        return redirect('post_view', username=username, post_id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid:
        comment = Comment(author=viewer, post=post)
        form = CommentForm(request.POST, instance=comment)
        form.save()
        return redirect('post_view', username=username, post_id=post_id)

    return redirect('post_view', username=username, post_id=post_id)


@login_required
def post_edit(request, username, post_id):
    instance = get_object_or_404(Post, author__username=username, pk=post_id)
    if instance.author != request.user:
        return redirect('post_view', username=username, post_id=instance.pk)

    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=instance)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post_view', username=username, post_id=post_id)

    return render(request, 'edit_post.html', {'form': form, 'post': instance})


@login_required
def follow_index(request):
    viewer = request.user
    followings = User.objects.filter(following__user=viewer)
    post_list = Post.objects.filter(author__in=followings)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {'page': page,
               'paginator': paginator,
               }
    return render(request, 'follow_index.html', context)


@login_required
def profile_follow(request, username):
    viewer = request.user
    author = get_object_or_404(User, username=username)

    if viewer == author or viewer.follower.filter(author=author).exists():
        return redirect('profile', username=username)

    Follow.objects.create(user=viewer, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    viewer = request.user
    author = get_object_or_404(User, username=username)

    if viewer == author or not viewer.follower.filter(author=author).exists():
        return redirect('profile', username=username)

    on_delete = Follow.objects.get(user=viewer, author=author)
    on_delete.delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
