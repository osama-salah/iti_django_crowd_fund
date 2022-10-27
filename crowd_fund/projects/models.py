from django.db import models

from crowd_fund_app.models import CustomUser
from utils.validators import greater_than_zero_validator


class ProjectCategory(models.Model):
    name = models.CharField(max_length=16)

    def __str__(self):
        return self.name


class ProjectTag(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class CommentReply(models.Model):
    reply = models.TextField(max_length=1024)
    comment_id = models.ForeignKey(to='ProjectComment', related_name='replies', on_delete=models.CASCADE)
    user_id = models.ForeignKey(to=CustomUser, related_name='replies', on_delete=models.CASCADE)


class ProjectComment(models.Model):
    comment = models.TextField(max_length=1024)
    project_id = models.ForeignKey(to='Project', related_name='comments', on_delete=models.CASCADE)
    user_id = models.ForeignKey(to=CustomUser, related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return self.comment


class Project(models.Model):
    title = models.CharField(max_length=64, null=False)
    details = models.TextField(max_length=1024)
    category = models.ForeignKey(to=ProjectCategory, related_name='projects', on_delete=models.SET_NULL, null=True)
    user_id = models.ForeignKey(to=CustomUser, related_name='projects', on_delete=models.CASCADE)
    total_target = models.FloatField(null=False, validators=[greater_than_zero_validator])
    tags = models.ManyToManyField(to=ProjectTag, related_name='projects')
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProjectRate(models.Model):
    class Choices(models.IntegerChoices):
        Poor = 0
        Acceptable = 1
        Good = 2
        Viable = 3
        Promising = 4
        Wonderful = 5

    @classmethod
    def get_rate_title(cls, rate):
        return cls.Choices.choices[rate]

    @classmethod
    def get_rate_titles(cls):
        return cls.Choices.choices

    rate = models.IntegerField(choices=Choices.choices)
    project_id = models.ForeignKey(Project, models.CASCADE, related_name='rates')
    user_id = models.ForeignKey(CustomUser, models.CASCADE, related_name='rates')


class Donation(models.Model):
    user_id = models.ForeignKey(to=CustomUser, related_name='donations', on_delete=models.CASCADE)
    project_id = models.ForeignKey(to=Project, related_name='donations', on_delete=models.CASCADE)
    amount = models.FloatField(null=False, validators=[greater_than_zero_validator])
    date = models.DateTimeField(auto_now_add=True)