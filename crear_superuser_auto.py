import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth.models import User

USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME')
EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL')
PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=USERNAME).exists():
    print(f"Creando superusuario: {USERNAME}")
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print("¡Superusuario creado con éxito!")
else:
    print("El superusuario ya existe. No se hace nada.")