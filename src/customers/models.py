from django.db import models
from django.conf import settings
import stripe

from helpers.billing import create_customer

User = settings.AUTH_USER_MODEL

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}'
    
    def save(self, *args, **kwargs):
        if not self.stripe_id:
            if not self.user.email:
                raise ValueError('User must have an email id.')
            stripe_id = create_customer(self.user)
            self.stripe_id = stripe_id
        return super().save(*args, **kwargs)