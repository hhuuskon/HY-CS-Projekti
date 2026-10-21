from django.contrib.auth.hashers import make_password
from django.db import migrations

from wallet.keys import encrypt, new_address, new_private_key


def create_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Wallet = apps.get_model('wallet', 'Wallet')
    user = User.objects.create(username='admin', password=make_password('admin123'),
                               is_staff=True, is_superuser=True)
    Wallet.objects.create(owner=user, address=new_address(), balance=0,
                          private_key=encrypt(new_private_key()))


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_test_users'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]
