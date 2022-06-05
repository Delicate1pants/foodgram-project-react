from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_tag'),
    ]

    operations = [
        HStoreExtension(),
    ]
