# Generated by Django 3.0.4 on 2020-05-03 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innovation', '0003_auto_20200502_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='build_graphics',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='start_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='stop_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='created',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]