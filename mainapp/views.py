from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from django.views.generic.edit import FormMixin

from .utils import send_otp
from datetime import datetime
import pyotp

from .forms import RegisterUserForm, PostForm, CommentForm
from .models import *
from .filters import CommentFilter
from .utils import mailing_task


def main_view(request):
    posts = Post.objects.all()
    if 'username' in request.session:
        del request.session['username']
    context = {'posts': posts,
               'title': 'Главная'}
    return render(request, 'mainapp/board.html', context=context)


class ShowPost(FormMixin, DetailView):
    model = Post
    form_class = CommentForm
    template_name = 'mainapp/post-page.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Пост"
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('post', kwargs={'post_slug': self.get_object().slug})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.post = self.get_object()
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class CategoryPostList(ListView):
    model = Category
    template_name = 'mainapp/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = Category.objects.get(slug=self.kwargs['category_slug'])
        context['title'] = 'Категория:    ' + cat.name
        context['cat'] = cat.slug
        context['cat_name'] = cat.name
        context['cat_list'] = cat.get_users_list
        return context

    def get_queryset(self):
        return Post.objects.filter(category__slug=self.kwargs['category_slug'])


def subscr(request, slug):
    users = User.objects.all()
    if request.user in users:
        cat = Category.objects.get(slug=slug)
        cat.subscribers.add(request.user)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('register')


class CreatePost(CreateView):
    model = Post
    template_name = 'mainapp/post-create.html'
    success_url = reverse_lazy('main')
    fields = ('title', 'text', 'category', 'photo', 'video_file')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание поста'
        return context

    def form_valid(self, form):
        post = form.save(commit=False)
        us = self.request.user.username
        post.user = User.objects.get(username=us)
        post.save()
        return super().form_valid(form)


class UpdatePost(UpdateView):
    model = Post
    fields = ('title', 'text', 'category', 'photo', 'video_file')
    template_name = 'mainapp/post-update.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Изменение поста'
        return context


class DeletePost(DeleteView):
    model = Post
    template_name = 'mainapp/post-delete.html'
    success_url = reverse_lazy('main')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление поста'
        return context


class CommentsPage(ListView):
    model = Post
    template_name = 'mainapp/comments-page.html'
    context_object_name = 'comments'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

    def get_queryset(self):
        queryset = Comment.objects.filter(post__user=self.request.user)
        self.filterset = CommentFilter(self.request.GET, queryset)
        return self.filterset.qs


def login_view(request):
    error_message = None
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('main')
        else:
            error_message = "Invalid username or password"
    return render(request, 'mainapp/login.html', {error_message: error_message})


def otp_view(request):
    error_message = None
    if request.method == "POST":
        otp = request.POST["otp"]
        username = request.session['username']

        otp_secret_key = request.session['otp_secret_key']
        otp_valid_date = request.session['otp_valid_date']
        if otp_secret_key and otp_valid_date is not None:
            valid_until = datetime.fromisoformat(otp_valid_date)

            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=180)
                if totp.verify(otp):
                    user = get_object_or_404(User, username=username)
                    login(request, user)

                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']
                    return redirect('main')
                else:
                    error_message = 'invalid one time password'
            else:
                error_message = 'one time password has expired'
        else:
            error_message = 'ups... something went wrong'
    return render(request, 'mainapp/otp.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('main')


def register(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # создание объекта без сохранения в БД
            user.set_password(form.cleaned_data['password'])
            user.save()
            send_otp(request, request.POST['email'])
            username = request.POST['username']
            request.session['username'] = username
            return redirect('otp')
    else:
        form = RegisterUserForm()
    return render(request, 'mainapp/registration.html', {'form': form})


def comm_delete(request, slug):
    comment = Comment.objects.get(slug=slug)
    comment.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def comm_add(request, slug):
    comment = Comment.objects.get(slug=slug)
    comment.status = True
    comment.save()
    author_mail = comment.user.email
    template_name = 'mainapp/message_comment_accepted.html'
    mailing_task(comment.text, [author_mail, ],
                 comment.text, comment.post.slug, template_name)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

