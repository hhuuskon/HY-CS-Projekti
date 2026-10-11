from django.contrib.auth.hashers import make_password
from django.db import migrations

from wallet.keys import encrypt, new_address, new_private_key


def create_test_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Wallet = apps.get_model('wallet', 'Wallet')
    for name in ['kissa', 'koira']:
        user = User.objects.create(username=name, password=make_password(name + '123'))
        Wallet.objects.create(owner=user, address=new_address(), balance=100,
                              private_key=encrypt(new_private_key()))


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_test_users),
    ]
