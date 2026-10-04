from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("problems", "0014_submission_reviewed_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="problem",
            name="category",
            field=models.CharField(
                choices=[
                    ("meca", "Mécanique"),
                    ("opt", "Optique"),
                    ("ond", "Ondes"),
                    ("thermo", "Thermodynamique"),
                    ("elec", "Électromagnétisme"),
                    ("autre", "Autre"),
                ],
                default="autre",
                max_length=10,
            ),
        ),
    ]