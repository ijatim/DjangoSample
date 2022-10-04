from rest_framework import generics, permissions, exceptions, status
from rest_framework.response import Response

from .models import Post, Vote, VoteSnapshot
from .serializers import PostSerializer, VoteSerializer, VoteSnapshotSerializer


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user)


class VoteCreate(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return Vote.objects.filter(voter=user, post=post).first()

    def perform_create(self, serializer):
        prev_vote = self.get_queryset()
        post = Post.objects.get(pk=self.kwargs['pk'])
        if prev_vote is not None:
            prev_vote_score = prev_vote.score
            serializer.save(voter=self.request.user, post=post, type='UPDATE', prev_score=prev_vote_score)
            return

        serializer.save(voter=self.request.user, post=post, type='NEW', prev_score=0)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise exceptions.ValidationError('You have never voted for this post.')


# This will not be a real production service and this will be done in regular intervals using scheduling processes
class SnapShotCreate(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = VoteSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        for post in self.get_queryset():
            last_snapshot = VoteSnapshot.objects.filter(post=post.pk).first()

            prev_snapshot_total_score = 0
            prev_snapshot_vote_count = 0
            prev_snapshot_creation_time = '1970-01-01 00:00:00.000000'
            if last_snapshot is not None:
                prev_snapshot_vote_count= last_snapshot.vote_count
                prev_snapshot_total_score = prev_snapshot_vote_count * last_snapshot.score
                prev_snapshot_creation_time = last_snapshot.created

            votes = Vote.objects.filter(post=post, created__gt=prev_snapshot_creation_time)

            votes_count = 0
            after_last_snapshot_score = 0
            latest_vote_datetime = None
            for vote in votes:
                if latest_vote_datetime is None:
                    latest_vote_datetime = vote.created
                if vote.type == 'NEW':
                    votes_count += 1
                    after_last_snapshot_score += vote.score
                elif vote.type == 'UPDATE':
                    after_last_snapshot_score += (vote.score - vote.prev_score)

            if votes_count == 0 and prev_snapshot_vote_count == 0:
                return

            calculated_score = (prev_snapshot_total_score + after_last_snapshot_score) / (votes_count + prev_snapshot_vote_count)

            serializer.save(post=post, vote_count=votes_count + prev_snapshot_vote_count, score=calculated_score,
                            created=latest_vote_datetime)
