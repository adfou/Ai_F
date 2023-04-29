# Generated by Django 4.1.5 on 2023-04-29 20:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Api_Serp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('time', models.TimeField()),
                ('date', models.DateField()),
                ('text_felling_field', models.TextField()),
                ('text_report', models.TextField()),
                ('number', models.IntegerField()),
                ('coordinates', models.TextField()),
                ('user_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
