from django_filters import FilterSet, DateFilter
from django import forms
from .models import Post

class PostFilter(FilterSet):
    created_at = DateFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Дата позже',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],
            'author__user__username': ['icontains'],
            'created_at': ['gte'],
        }
