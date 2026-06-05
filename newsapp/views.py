from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import News, Comment
from .forms import CommentForm

def index(request):
    latest_news = News.objects.all()[:3]
    return render(request, 'index.html', {'latest_news': latest_news})

def contacts(request):
    return render(request, 'contacts.html')

def news_list(request):
    news = News.objects.all()
    search = request.GET.get('search')
    if search:
        news = news.filter(title__icontains=search)
    sort = request.GET.get('sort')
    if sort == 'asc':
        news = news.order_by('pub_date')
    else:
        news = news.order_by('-pub_date')
    return render(request, 'news_list.html', {'news': news, 'search': search})

def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.news = item
            c.user = request.user
            c.save()
            return redirect('news_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'news_detail.html', {'news': item, 'form': form, 'comments': item.comments.all()})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('index')
