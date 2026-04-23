import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Idempotent project bootstrap for first deploy."

    def handle(self, *args, **options):
        user_model = get_user_model()
        username = os.getenv("DJANGO_ADMIN_USERNAME", "admin")
        password = os.getenv("DJANGO_ADMIN_PASSWORD", "admin")
        email = os.getenv("DJANGO_ADMIN_EMAIL", "admin@example.com")

        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'"))
            return

        changed = False
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True
        if user.email != email:
            user.email = email
            changed = True

        # Password sync allows redeploy-driven recovery of admin access.
        if password and not user.check_password(password):
            user.set_password(password)
            changed = True

        if changed:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated superuser '{username}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already up to date"))
