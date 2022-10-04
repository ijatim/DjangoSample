# Generated by Django 4.1.2 on 2022-10-04 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_vote_score'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='vote',
            constraint=models.UniqueConstraint(fields=('voter', 'post'), name='unique_user_vote'),
        ),
    ]