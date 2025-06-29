from django.shortcuts import render
from django.urls import reverse
from .models import SubscriptionPrice

# Create your views here.

def subscription_price_view(request, interval='month'):
    INTERVAL_MAP = {
        'month': SubscriptionPrice.IntervalChoices.MONTHLY,
        'year': SubscriptionPrice.IntervalChoices.YEARLY
    }
    interval_choice = INTERVAL_MAP.get(interval, SubscriptionPrice.IntervalChoices.MONTHLY)
    monthly_redirect_url = reverse('pricing_detail', kwargs={'interval': SubscriptionPrice.IntervalChoices.MONTHLY})
    yearly_redirect_url = reverse('pricing_detail', kwargs={'interval': SubscriptionPrice.IntervalChoices.YEARLY})

    interval_queryset = SubscriptionPrice.objects.filter(featured=True, interval=interval_choice)

    context = {
        'object_list': interval_queryset,
        'monthly_url': monthly_redirect_url,
        'yearly_url': yearly_redirect_url,
        'active_tab': interval_choice
    }
    return render(request, 'subscriptions/pricing.html', context=context)
