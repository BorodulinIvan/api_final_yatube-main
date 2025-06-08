from rest_framework import viewsets, filters, permissions
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment, Follow
from api.serializers import (PostSerializer, GroupSerializer,
                             FollowSerializer, CommentSerializer)
from api.permissions import IsAuthorOrReadOnly, IsNotSelfFollow

User = get_user_model()


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def paginate_queryset(self, queryset):
        if (self.request.query_params.get('limit') or
           self.request.query_params.get('offset')):
            return super().paginate_queryset(queryset)
        return None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostViewSet(BaseModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = None


class CommentViewSet(BaseModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = None

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(author=self.request.user, post_id=post_id)


class FollowViewSet(BaseModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotSelfFollow]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=following__username']
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Follow.objects.none()
        queryset = Follow.objects.filter(user=self.request.user)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = (queryset.filter
                        (following__username__iexact=search_query))
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
