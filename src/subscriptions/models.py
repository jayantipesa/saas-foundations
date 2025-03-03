from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, pre_save

from django.conf import settings

User = settings.AUTH_USER_MODEL # 'auth.User'

# Create your models here.

SUBSCRIPTION_PERMISSIONS = [
    ('basic', 'Basic Plan'),
    ('pro', 'Pro Plan'),
    ('advanced', 'Advanced Plan'),
    ('basic_ai', 'Basic AI plan')
]

class Subscription(models.Model):
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(
        Permission,
        limit_choices_to={
            'content_type__app_label': 'subscriptions',
            'codename__in': [x[0] for x in  SUBSCRIPTION_PERMISSIONS]
        })

    def __str__(self):
        return f'{self.name}'
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS


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