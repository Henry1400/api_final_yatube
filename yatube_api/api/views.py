from django.shortcuts import get_object_or_404
from rest_framework import viewsets, pagination, permissions, mixins, filters

from .permissions import IsAuthorOrReadOnly
from posts.models import Post, Group
from .serializers import PostSerializer, CommentSerializer, GroupSerializer, FollowSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    '''Список групп.'''
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class PostViewSet(viewsets.ModelViewSet):
    '''Список публикаций.'''
    queryset = Post.objects.select_related('author', 'group')
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    '''Комментарии к посту.'''
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs.get('post_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_post())

    def get_queryset(self):
        return self.get_post().comments.select_related('author')


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    '''Список подписок.'''
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username', 'user__username',)

    def get_queryset(self):
        return self.request.user.follower.select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
