from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0002_update_field_validations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Price in major currency units (e.g. dollars/euros).",
                max_digits=10,
                validators=[MinValueValidator(Decimal("0.01"))],
            ),
        ),
    ]
