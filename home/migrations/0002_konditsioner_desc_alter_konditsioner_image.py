# Generated by Django 5.2.4 on 2025-07-04 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='konditsioner',
            name='desc',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='konditsioner',
            name='image',
            field=models.ImageField(blank=True, default='default/cond.jpg', null=True, upload_to='kontitsionerlar/'),
        ),
    ]
