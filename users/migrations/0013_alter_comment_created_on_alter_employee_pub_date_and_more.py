# Generated by Django 4.2.7 on 2023-11-20 14:05

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_remove_employee_previous_salary_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 20, 14, 5, 55, 50309, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='employee',
            name='pub_date',
            field=models.DateField(default=datetime.datetime(2023, 11, 20, 14, 5, 55, 50309, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('attended', models.BooleanField(default=False)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.employee')),
            ],
        ),
    ]
