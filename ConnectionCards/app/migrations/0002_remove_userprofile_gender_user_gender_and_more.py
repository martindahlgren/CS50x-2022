# Generated by Django 4.1.7 on 2023-11-12 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='gender',
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(choices=[('M', 'Man'), ('W', 'Woman'), ('O', 'Non-Binary')], default='O', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.CharField(max_length=300),
        ),
    ]
