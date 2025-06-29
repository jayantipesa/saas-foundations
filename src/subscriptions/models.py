from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, pre_save

from django.conf import settings
from helpers.billing import create_product, create_price

User = settings.AUTH_USER_MODEL # 'auth.User'

# Create your models here.

SUBSCRIPTION_PERMISSIONS = [
    ('basic', 'Basic Plan'),
    ('pro', 'Pro Plan'),
    ('advanced', 'Advanced Plan'),
    ('basic_ai', 'Basic AI plan')
]

class Subscription(models.Model):
    """
    Subcription = Stripe product
    """
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={
            'content_type__app_label': 'subscriptions',
            'codename__in': [x[0] for x in  SUBSCRIPTION_PERMISSIONS]
        })
    stripe_id = models.CharField(max_length=120, blank=True, null=True)
    order = models.IntegerField(default=-1, help_text='Ordering on Pricing page')
    featured = models.BooleanField(default=True, help_text='Featured on Pricing page')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'
    class Meta:
        ordering = ['order', 'featured', '-updated_at']
        permissions = SUBSCRIPTION_PERMISSIONS

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = create_product(
                name=self.name,
                metadata={
                'subscription_plan_id': self.id
                }
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)


class SubscriptionPrice(models.Model):
    """
    Subscription Price = Stripe Price
    """
    class IntervalChoices(models.TextChoices):
        MONTHLY = 'month', 'Monthly'
        YEARLY = 'year', 'Yearly'

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    interval = models.CharField(max_length=120, default=IntervalChoices.MONTHLY,
                                choices=IntervalChoices.choices
                            )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    order = models.IntegerField(default=-1, help_text='Ordering on Pricing page')
    featured = models.BooleanField(default=True, help_text='Featured on Pricing page')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subscription__order', 'order', 'featured', '-updated_at']

    @property
    def stripe_currency(self):
        return 'usd'

    @property
    def stripe_price(self):
        """
        Remove decimal places
        """
        return int(self.price * 100)

    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id

    def save(self, *args, **kwargs):
        if (self.stripe_id is None and self.product_stripe_id is not None):
            stripe_id = create_price(
                currency=self.stripe_currency,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product=self.product_stripe_id,
                metadata={
                    'subscription_plan_price_id': self.id
                }
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            """
            set all other prices for this particular subscription and particular
            interval to featured=False
            """
            qs = SubscriptionPrice.objects.filter(
                subscription=self.subscription,
                interval=self.interval,
                featured=True
            ).exclude(id=self.id)
            qs.update(featured=False)
            


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription,
                                     on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} - {self.subscription.name}'


def user_subscription_post_save(sender, instance, *args, **kwargs):
    user = instance.user
    subscription_groups_set = set()
    user_subscription = instance.subscription
    if user_subscription is not None:
        subscription_groups_qs = Subscription.objects.values_list('groups__id', flat=True)
        subscription_groups_set = set(subscription_groups_qs)

    # remove the current subscription plan from user's groups:
    new_user_groups = user.groups.exclude(id__in=subscription_groups_set)
    user.groups.set(new_user_groups)

    # add new subscription groups
    user.groups.add(*user_subscription.groups.all())

post_save.connect(user_subscription_post_save, sender=UserSubscription)