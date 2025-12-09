from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Category, Comment
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from .forms import PostForm, CommentForm, UserForm
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.db.models import Count, Prefetch

User = get_user_model()


class UserIsAuthorMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise Http404
        return obj


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).prefetch_related(
        'comments'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    paginate_by = 10


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        base_qs = Post.objects.prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related(
                    'author').order_by('created_at')
            )
        )
        return base_qs

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        # Оригинальная логика - оставляем как было
        if self.request.user.is_authenticated and obj.author == self.request.user:
            return obj

        if (
            not obj.is_published
            or not obj.category.is_published
            or obj.pub_date > timezone.now()
        ):
            raise Http404

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'blog/category.html'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'
    context_object_name = 'category'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_published:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(
            category=self.object,
            is_published=True,
            pub_date__lte=timezone.now(),
        ).select_related(
            'author'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj

        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class EditPostView(UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])

        if not request.user.is_authenticated or post.author != request.user:
            return redirect('blog:post_detail', post_id=post.pk)

        self.object = post
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(UserIsAuthorMixin, LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object or None)
        return context


class UserProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.object
        current_user = self.request.user

        if current_user == user_profile:
            posts = user_profile.posts.all()
        else:
            posts = user_profile.posts.filter(
                is_published=True,
                pub_date__lte=timezone.now()
            )

        posts = posts.annotate(comment_count=Count(
            'comments', distinct=False)).order_by('-pub_date')

        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)

        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

    def get_object(self):
        return self.request.user


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        return super().form_valid(form)


class EditCommentView(UserIsAuthorMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class DeleteCommentView(UserIsAuthorMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})