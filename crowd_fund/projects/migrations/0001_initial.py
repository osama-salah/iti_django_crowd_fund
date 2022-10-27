# Generated by Django 4.1.2 on 2022-10-22 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64)),
                ('details', models.TextField(max_length=1024)),
                ('total_target', models.FloatField(validators=[utils.validators.greater_than_zero_validator])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(max_length=1024)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='projects.project')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='projects.projectcategory'),
        ),
        migrations.AddField(
            model_name='project',
            name='tags',
            field=models.ManyToManyField(related_name='projects', to='projects.projecttag'),
        ),
        migrations.AddField(
            model_name='project',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(validators=[utils.validators.greater_than_zero_validator])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donations', to='projects.project')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CommentReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply', models.TextField(max_length=1024)),
                ('comment_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='projects.projectcomment')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
