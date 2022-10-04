from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField()
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']


class Vote(models.Model):
    SCORE_CHOICES = [
        (i, i) for i in range(6)
    ]

    TYPE_CHOICES = [
        ('NEW', 'NEW'),
        ('UPDATE', 'UPDATE')
    ]

    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    prev_score = models.IntegerField(choices=SCORE_CHOICES, default=0)
    score = models.IntegerField(choices=SCORE_CHOICES)
    type = models.CharField(choices=TYPE_CHOICES, max_length=6)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        constraints = [
            models.UniqueConstraint(fields=['voter', 'post'], name='unique_user_vote',
                                    condition=models.Q(type='NEW'))
        ]


class VoteSnapshot(models.Model):
    created = models.DateTimeField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    vote_count = models.IntegerField()
    score = models.DecimalField(decimal_places=2, max_digits=3)

    class Meta:
        ordering = ['-created']
