from django_filters import FilterSet

from .models import Post, Response

class ResponseFilter(FilterSet):
    class Meta:
        model = Response
        fields = ['post']

    def __init__(self, *args, **kwargs):
        request = kwargs.get('request')
        super().__init__(*args, **kwargs)
        if request and request.user.is_authenticated:
            self.filters['post'].queryset = Post.objects.filter(author=request.user)
