# Generated by Django 5.0.4 on 2025-05-18 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logAnalysis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverlog',
            name='promo_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
