from rest_framework import serializers

from .models import Post, Vote


class PostSerializer(serializers.ModelSerializer):
    poster = serializers.ReadOnlyField(source='poster.username')
    vote_counts = serializers.SerializerMethodField()
    vote_score = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'text', 'poster', 'created', 'vote_counts', 'vote_score']

    def get_vote_counts(self, post):
        return Vote.objects.filter(post=post).count()

    def get_vote_score(self, post):
        score = 0
        votes = Vote.objects.filter(post=post)
        for vote in votes:
            score += vote.score

        return round(score/votes.count())


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'score']
