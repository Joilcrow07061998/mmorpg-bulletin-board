from django.core.cache import cache
from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.models import User
from linecache import cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from allauth.account.adapter import DefaultAccountAdapter


from .filters import ResponseFilter
from .models import Post, Response
from .forms import PostForm, ResponseForm
import random


class PostList(ListView):
    model = Post
    template_name = 'board/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return (
                Post.objects.filter(headline__icontains=query)
                | Post.objects.filter(body__icontains=query)
            )
        return Post.objects.all().order_by('-created_at')


class PostDetail(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'board/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ResponseForm()
        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'board/post_form.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('board:post_list')
    template_name = 'board/post_confirm_delete.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

# создание отклика
class ResponseCreate(LoginRequiredMixin, CreateView):
    model = Response
    form_class = ResponseForm
    template_name = 'board/response_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        if post.author == request.user:
            return HttpResponseForbidden(
                'Нельзя оставить отклик на собственное объявление.'
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        response = form.save()

        post_author_email = response.post.author.email
        if post_author_email:
            send_mail(
                subject='Новый отклик на ваш пост',
                message=(
                    f'Пользователь {self.request.user.email} оставил отклик '
                    f'на ваш пост "{response.post.headline}".\n\n'
                    f'Текст отклика:\n{response.body}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[post_author_email],
                fail_silently=False,
            )

        return redirect('board:post_detail', pk=self.kwargs['pk'])

# список откликов
class ResponseList(LoginRequiredMixin, FilterView):
    model = Response
    template_name = 'board/user_responses.html'
    context_object_name = 'responses'
    filterset_class = ResponseFilter

    def get_queryset(self):
        return Response.objects.filter(
            post__author=self.request.user
        ).order_by('-created_at')

# удаление отклика
@login_required
@require_POST
def delete_response(request, pk):
    response = get_object_or_404(
        Response,
        pk=pk,
        post__author=request.user
    )
    response.delete()
    return redirect('board:user_responses')

#принятие отклика с отправкой на почту
@login_required
@require_POST
def accept_response(request, pk):
    response = get_object_or_404(
        Response,
        pk=pk,
        post__author=request.user
    )

    if not response.is_accepted:
        response.is_accepted = True
        response.save(update_fields=['is_accepted'])

        subscriber_email = response.author.email
        if subscriber_email:
            send_mail(
                subject='Ваш отклик принят',
                message=(
                    f'Ваш отклик на пост "{response.post.headline}" '
                    f'был принят автором.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber_email],
                fail_silently=False,
            )

    return redirect('board:user_responses')


def handle_user_signed_up(request, user, **kwargs):
    # Делаем пользователя неактивным (блокируем до ввода кода)
    user.is_active = False
    user.save()

    # Генерируем случайный 6-значный код
    code = str(random.randint(100000, 999999))

    # Сохраняем код в кэш, где КЛЮЧ - это email, а ЗНАЧЕНИЕ - код.
    # timeout=300 означает, что код сгорит сам через 5 минут (300 секунд)
    cache.set(user.email, code, timeout=300)

    # Запоминаем email в сессии текущего браузера, чтобы знать, чей код проверять
    request.session['verification_email'] = user.email

    # Отправляем письмо с кодом в консоль (или на реальную почту)
    send_mail(
        subject='Код подтверждения регистрации',
        message=f'Привет! Твой одноразовый код подтверждения для MMORPG Board: {code}\nКод действует 5 минут.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


# 2. VIEW: Страница, куда пользователя перекинет для ввода кода
class VerifyCodeView(View):
    def get(self, request):
        # Если в сессии нет email (зашли напрямую), кидаем на регистрацию
        if 'verification_email' not in request.session:
            return redirect('account_signup')
        return render(request, 'account/verify_code.html')

    def post(self, request):
        email = request.session.get('verification_email')
        input_code = request.POST.get('code')

        # Достаем правильный код из кэша по email
        saved_code = cache.get(email)

        # Проверяем, совпали ли коды и не истекло ли время
        if saved_code and input_code == saved_code:
            # Находим заблокированного юзера, активируем его и логиним
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()

            # Автоматически авторизуем его в системе, чтобы не заставлять вводить пароль еще раз
            login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')

            # Чистим сессию от временных данных
            del request.session['verification_email']
            cache.delete(email)

            return redirect('board:post_list')  # Успех! Перекидываем на главную ленту

        # Если код неверный или сгорел
        return render(request, 'account/verify_code.html', {'error': 'Неверный код или истекло время его действия!'})


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # Если пользователь только что зарегистрировался и еще не активен
        if request.user.is_authenticated and not request.user.is_active:
            return '/account/verify/'
        # Во всех остальных случаях (обычный вход) — на главную
        return '/'
