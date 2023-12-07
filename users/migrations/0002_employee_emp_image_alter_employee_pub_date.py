# Generated by Django 4.2.7 on 2023-11-02 02:50

import datetime
from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='emp_image',
            field=models.ImageField(default='profile_pic/image.jpg', upload_to=users.models.image_path),
        ),
        migrations.AlterField(
            model_name='employee',
            name='pub_date',
            field=models.DateField(default=datetime.datetime(2023, 11, 2, 2, 50, 27, 935702, tzinfo=datetime.timezone.utc)),
        ),
    ]