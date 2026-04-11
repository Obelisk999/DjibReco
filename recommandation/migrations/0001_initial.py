"""
recommandation/migrations/0001_initial.py
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('restaurants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='InteractionUtilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_action', models.CharField(
                    choices=[
                        ('vue',        'Vue restaurant'),
                        ('clic_menu',  'Clic sur item menu'),
                        ('partage',    'Partage'),
                    ],
                    max_length=20
                )),
                ('score',      models.FloatField(default=1.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('restaurant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='interactions_reco',
                    to='restaurants.restaurant'
                )),
                ('utilisateur', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='interactions_reco',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name':        'Interaction utilisateur',
                'verbose_name_plural': 'Interactions utilisateurs',
            },
        ),
        migrations.CreateModel(
            name='CacheRecommandation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurant_ids', models.JSONField(default=list)),
                ('calculee_le',    models.DateTimeField(auto_now=True)),
                ('utilisateur', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='cache_reco',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name':        'Cache recommandation',
                'verbose_name_plural': 'Caches recommandations',
            },
        ),
        migrations.AddIndex(
            model_name='interactionutilisateur',
            index=models.Index(fields=['utilisateur', 'restaurant'], name='reco_inter_user_rest_idx'),
        ),
        migrations.AddIndex(
            model_name='interactionutilisateur',
            index=models.Index(fields=['type_action'], name='reco_inter_type_idx'),
        ),
    ]
