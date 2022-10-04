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

    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    score = models.IntegerField(choices=SCORE_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['voter', 'post'], name='unique_user_vote')
        ]
