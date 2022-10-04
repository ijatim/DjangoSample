from rest_framework import serializers

from .models import Post, Vote, VoteSnapshot


class VoteSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteSnapshot
        fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    poster = serializers.ReadOnlyField(source='poster.username')
    vote_counts = serializers.SerializerMethodField()
    vote_score = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'text', 'poster', 'created', 'vote_counts', 'vote_score']

    def get_vote_counts(self, post):
        last_vote_snapshot = VoteSnapshot.objects.filter(post=post).first()
        if last_vote_snapshot is None:
            snap_shot_creation_time = '1970-01-01 00:00:00.000000'
            snap_shot_vote_count = 0
        else:
            snap_shot_creation_time = last_vote_snapshot.created
            snap_shot_vote_count = last_vote_snapshot.vote_count

        votes_count = Vote.objects.filter(post=post, created__gt=snap_shot_creation_time, type='NEW').count()

        return snap_shot_vote_count + votes_count

    def get_vote_score(self, post):
        last_vote_snapshot = VoteSnapshot.objects.filter(post=post).first()
        if last_vote_snapshot is None:
            snap_shot_creation_time = '1970-01-01 00:00:00.000000'
            snap_shot_score = 0
            snap_shot_vote_count = 0
        else:
            snap_shot_creation_time = last_vote_snapshot.created
            snap_shot_score = last_vote_snapshot.score
            snap_shot_vote_count = last_vote_snapshot.vote_count

        after_last_snap_shot_score = 0
        votes = Vote.objects.filter(post=post, created__gt=snap_shot_creation_time)

        votes_count = 0
        for vote in votes:
            if vote.type == 'NEW':
                votes_count += 1
                after_last_snap_shot_score += vote.score
            elif vote.type == 'UPDATE':
                after_last_snap_shot_score += (vote.score - vote.prev_score)

        if votes_count == 0 and snap_shot_vote_count == 0:
            return 0

        return round(
            (((snap_shot_score * snap_shot_vote_count) + after_last_snap_shot_score) / (
                           snap_shot_vote_count + votes_count))
        )


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'score']
