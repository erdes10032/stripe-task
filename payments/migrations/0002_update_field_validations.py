from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="discount",
            name="percent_off",
            field=models.FloatField(
                validators=[
                    django.core.validators.MinValueValidator(0.01),
                    django.core.validators.MaxValueValidator(100.0),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="currency",
            field=models.CharField(
                choices=[("usd", "USD"), ("eur", "EUR")],
                default="usd",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="item",
            name="price",
            field=models.PositiveIntegerField(
                help_text="Price in the smallest currency unit (e.g. cents)"
            ),
        ),
        migrations.AlterField(
            model_name="tax",
            name="percentage",
            field=models.FloatField(
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(100.0),
                ]
            ),
        ),
    ]
