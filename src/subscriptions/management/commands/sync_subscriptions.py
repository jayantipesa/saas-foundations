from typing import Any
from django.core.management.base import BaseCommand

from subscriptions.models import Subscription

class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any):
        queryset = Subscription.objects.filter(active=True)
        for obj in queryset:
            for group in obj.groups.all():
                sub_perms = obj.permissions.all()
                group.permissions.set(sub_perms)
    