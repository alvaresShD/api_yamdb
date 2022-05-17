# Generated by Django 2.2.16 on 2022-05-17 20:08

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews', '0007_auto_20220517_2003'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='review',
            name='unique_review',
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('author', 'title')},
        ),
    ]
