# Generated by Django 4.0.4 on 2022-05-28 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0003_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
