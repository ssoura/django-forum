from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Post, Topic, Message, User
from .forms import PostForm, UserForm, MyUserCreationForm

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exit')

    context = {'page': page}
    return render(request, 'forum/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'forum/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    posts = Post.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    post_count = posts.count()
    post_messages = Message.objects.filter(
        Q(post__topic__name__icontains=q))[0:3]

    context = {'posts': posts, 'topics': topics,
               'post_count': post_count, 'post_messages': post_messages}
    return render(request, 'forum/home.html', context)


def post(request, pk):
    post = Post.objects.get(id=pk)
    post_messages = post.message_set.all()
    participants = post.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            post=post,
            body=request.POST.get('body')
        )
        post.participants.add(request.user)
        return redirect('post', pk=post.id)

    context = {'post': post, 'post_messages': post_messages,
               'participants': participants}
    return render(request, 'forum/post.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    posts = user.post_set.all()
    post_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'posts': posts,
               'post_messages': post_messages, 'topics': topics}
    return render(request, 'forum/profile.html', context)


@login_required(login_url='login')
def createPost(request):
    form = PostForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Post.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'forum/post_form.html', context)


@login_required(login_url='login')
def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)
    topics = Topic.objects.all()
    if request.user != post.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        post.name = request.POST.get('name')
        post.topic = topic
        post.description = request.POST.get('description')
        post.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'post': post}
    return render(request, 'forum/post_form.html', context)


@login_required(login_url='login')
def deletePost(request, pk):
    post = Post.objects.get(id=pk)

    if request.user != post.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'forum/delete.html', {'obj': post})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'forum/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'forum/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'forum/topics.html', {'topics': topics})


def activityPage(request):
    post_messages = Message.objects.all()
    return render(request, 'forum/activity.html', {'post_messages': post_messages})
