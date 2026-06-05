from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile_previous_scores'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='accepted_terms',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='allow_leaderboard_display',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='age_confirmation',
            field=models.BooleanField(default=False),
        ),
    ]