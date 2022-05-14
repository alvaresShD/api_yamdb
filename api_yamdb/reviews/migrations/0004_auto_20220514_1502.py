# Generated by Django 2.2.16 on 2022-05-14 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20220512_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='title',
            name='rating',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'admin'), ('moderator', 'moderator'), ('user', 'user')], default='user', max_length=16),
        ),
    ]