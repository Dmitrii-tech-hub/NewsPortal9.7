from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post, Category
from .forms import PostForm, BaseRegisterForm
from django.contrib.auth.models import User, Group
from django.views.generic.edit import CreateView
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.views import View

# List view for news posts
class NewsListView(ListView):
    model = Post
    template_name = 'news_list.html'
    context_object_name = 'posts'
    queryset = Post.objects.filter(type='NW')  # Filter for news posts
    paginate_by = 10  # Number of posts per page

# Detail view for a single news post
class NewsDetailView(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'post'

# Create a news post
class NewsCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'news_create.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'NW'  # Set post type to News
        post.save()
        return super().form_valid(form)

# Update an existing news post
class NewsUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'news_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'NW'  # Ensure the type remains News
        post.save()
        return super().form_valid(form)

# Delete a news post
class NewsDeleteView(DeleteView):
    model = Post
    template_name = 'news_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(type='NW')  # Only delete News posts

# Create an article post
class ArticleCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'article_create.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AR'  # Set post type to Article
        post.save()
        return super().form_valid(form)

# Update an existing article post
class ArticleUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'article_edit.html'
    success_url = reverse_lazy('news_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type = 'AR'  # Ensure the type remains Article
        post.save()
        return super().form_valid(form)

# Delete an article post
class ArticleDeleteView(DeleteView):
    model = Post
    template_name = 'article_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('news_list')

    def get_queryset(self):
        return Post.objects.filter(type='AR')  # Only delete Article posts

# Search view for posts with filters (by title, author, and date)
class SearchView(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get('title')
        author_name = self.request.GET.get('author')
        after_date = self.request.GET.get('date_after')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author_name:
            queryset = queryset.filter(author__user__username__icontains=author_name)
        if after_date:
            queryset = queryset.filter(created_at__date__gt=after_date)

        return queryset

# Base registration view
class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    template_name = 'registration/register.html'  # Adjust this as per your template location
    success_url = reverse_lazy('news_list')

# Index view
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context

# View for upgrading users to 'authors' group
@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
    return redirect('/')

# View with specific permission requirements
class MyView(PermissionRequiredMixin, View):
    permission_required = ('simpleapp.add_post', 'simpleapp.change_post')

# Category detail view (for category subscriptions)
class CategoryDetailView(View):
    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        return render(request, 'category_detail.html', {'category': category})

    def post(self, request, *args, **kwargs):
        category_id = kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)

        if request.user.is_authenticated:
            # Add the user to category subscribers
            category.subscribers.add(request.user)

            # Prepare and send subscription email
            html_content = render_to_string(
                'subscription_email.html',  # Email template
                {
                    'user': request.user,
                    'category': category,
                }
            )

            msg = EmailMultiAlternatives(
                subject=f'Подписка на категорию {category.name}',
                body=f'Вы подписались на категорию {category.name}.',
                from_email=settings.DEFAULT_FROM_EMAIL,  # Set your default email
                to=[request.user.email],  # Send to the current user
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            # Show success message
            messages.success(request, f'Вы успешно подписались на категорию {category.name}')

        return redirect('category_detail', category_id=category_id)
