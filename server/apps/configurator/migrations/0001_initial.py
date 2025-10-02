# Generated manually on 2025-10-03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceAdjustmentRule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('adjusted_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('affected_option', models.ForeignKey(db_column='affected_option_id', on_delete=django.db.models.deletion.CASCADE, related_name='price_adjustments', to='products.partoption')),
                ('condition_option', models.ForeignKey(db_column='condition_option_id', on_delete=django.db.models.deletion.CASCADE, related_name='conditioned_adjustments', to='products.partoption')),
            ],
            options={
                'db_table': 'priceadjustmentrule',
            },
        ),
        migrations.CreateModel(
            name='IncompatibilityRule',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('message', models.TextField()),
                ('incompatible_with_option', models.ForeignKey(db_column='incompatible_with_option_id', on_delete=django.db.models.deletion.CASCADE, related_name='incompatible_with', to='products.partoption')),
                ('part_option', models.ForeignKey(db_column='part_option_id', on_delete=django.db.models.deletion.CASCADE, related_name='incompatibilities', to='products.partoption')),
            ],
            options={
                'db_table': 'incompatibilityrule',
            },
        ),
    ]
