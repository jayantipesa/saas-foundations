# Generated by Django 5.0.10 on 2025-06-29 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0016_usersubscription_stripe_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='user_cancelled',
            field=models.BooleanField(default=False),
        ),
    ]
