from django.contrib import admin

# Register your models here.
from .models import Subscription, UserSubscription, SubscriptionPrice

class UserSubscriptionInline(admin.TabularInline):
    model = UserSubscription
    extra = 0

class SubscriptionPrice(admin.TabularInline):
    model = SubscriptionPrice
    readonly_fields = ['stripe_id']
    extra = 0
    can_delete = False

class SubscriptionAdmin(admin.ModelAdmin):
    inlines = [SubscriptionPrice, UserSubscriptionInline]
    list_display = ['name', 'active']
    readonly_fields = ['stripe_id']

admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(UserSubscription)