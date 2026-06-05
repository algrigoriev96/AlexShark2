import os

# Содержимое Python-файлов
files = {
    'newsapp/models.py': '''from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='news/', blank=True, null=True)

class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
''',

    'newsapp/admin.py': '''from django.contrib import admin
from .models import News, Comment

admin.site.register(News)
admin.site.register(Comment)
''',

    'newsapp/forms.py': '''from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {'text': forms.Textarea(attrs={'rows': 2})}
''',

    'newsapp/views.py': '''from django.shortcuts import render, get_object_or_404, redirect
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
''',

    'newsapp/urls.py': '''from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contacts/', views.contacts, name='contacts'),
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]
''',

    'myproject/urls.py': '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('newsapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
''',
}

# Создаём папку templates и HTML-файлы
templates_dir = 'newsapp/templates'
os.makedirs(templates_dir, exist_ok=True)

templates = {
    'base.html': '''<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Моя компания{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="/">МояКомпания</a>
        <div>
            <a href="/" class="btn btn-outline-light">Главная</a>
            <a href="/news/" class="btn btn-outline-light">Новости</a>
            <a href="/contacts/" class="btn btn-outline-light">Контакты</a>
            {% if user.is_authenticated %}
                <span class="text-white">{{ user.username }}</span>
                <a href="/logout/" class="btn btn-danger">Выход</a>
            {% else %}
                <a href="/login/" class="btn btn-success">Вход</a>
                <a href="/register/" class="btn btn-primary">Регистрация</a>
            {% endif %}
            {% if user.is_staff or user.is_superuser %}
                <a href="/admin/" class="btn btn-warning">Админка</a>
            {% endif %}
        </div>
    </div>
</nav>
<div class="container mt-4">
    {% block content %}{% endblock %}
</div>
</body>
</html>''',

    'index.html': '''{% extends 'base.html' %}
{% block content %}
<h1>Добро пожаловать!</h1>
<p>Это сайт нашей компании. Здесь будут последние новости.</p>
<h3>Последние новости</h3>
{% for item in latest_news %}
    <div class="card mb-2">
        <div class="card-body">
            <h5>{{ item.title }}</h5>
            <p>{{ item.content|truncatewords:20 }}</p>
            <a href="/news/{{ item.id }}/">Читать</a>
            <small class="text-muted">Автор: {{ item.author.username }}, {{ item.pub_date }}</small>
        </div>
    </div>
{% empty %}
    <p>Новостей пока нет.</p>
{% endfor %}
{% endblock %}''',

    'contacts.html': '''{% extends 'base.html' %}
{% block content %}
<h1>Контакты</h1>
<p>Телефон: 8-800-123-45-67</p>
<p>Email: info@mycompany.ru</p>
<p>Адрес: г. Москва, ул. Ленина, д.1</p>
{% endblock %}''',

    'news_list.html': '''{% extends 'base.html' %}
{% block content %}
<h1>Все новости</h1>
<form method="get" class="mb-3">
    <input name="search" value="{{ search }}" placeholder="Поиск по названию">
    <button type="submit">Искать</button>
    <a href="?sort=asc">Сначала старые</a>
    <a href="?sort=desc">Сначала новые</a>
</form>
{% for item in news %}
    <div class="card mb-2">
        <div class="card-body">
            <h5>{{ item.title }}</h5>
            <p>{{ item.pub_date|date:"d.m.Y H:i" }}</p>
            <a href="/news/{{ item.id }}/">Подробнее</a>
        </div>
    </div>
{% empty %}
    <p>Новостей не найдено.</p>
{% endfor %}
{% endblock %}''',

    'news_detail.html': '''{% extends 'base.html' %}
{% block content %}
<h1>{{ news.title }}</h1>
<p>{{ news.pub_date|date:"d.m.Y H:i" }} | Автор: {{ news.author.username }}</p>
{% if news.image %}
    <img src="{{ news.image.url }}" width="300" class="img-fluid">
{% endif %}
<p>{{ news.content|linebreaks }}</p>

<h3>Комментарии</h3>
{% for c in comments %}
    <div class="border p-2 mb-2">
        <strong>{{ c.user.username }}</strong> ({{ c.created_date|date:"d.m.Y H:i" }}):<br>
        {{ c.text }}
    </div>
{% empty %}
    <p>Нет комментариев.</p>
{% endfor %}

{% if user.is_authenticated %}
    <h4>Добавить комментарий</h4>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Отправить</button>
    </form>
{% else %}
    <p><a href="/login/">Войдите</a>, чтобы комментировать.</p>
{% endif %}
{% endblock}''',

    'register.html': '''{% extends 'base.html' %}
{% block content %}
<h2>Регистрация</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Зарегистрироваться</button>
</form>
{% endblock}''',

    'login.html': '''{% extends 'base.html' %}
{% block content %}
<h2>Вход</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Войти</button>
</form>
{% endblock}''',
}

# Записываем Python файлы
for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Записываем HTML шаблоны
for name, content in templates.items():
    with open(os.path.join(templates_dir, name), 'w', encoding='utf-8') as f:
        f.write(content)

print("Все файлы успешно созданы!")