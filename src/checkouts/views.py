from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from helpers.billing import (
    start_checkout_session,
    get_checkout_customer_plan,
    cancel_subscription
)
from subscriptions.models import (
    SubscriptionPrice,
    Subscription,
    UserSubscription
)

User = get_user_model()
BASE_URL = settings.BASE_URL
# Create your views here.

def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id
    return redirect('stripe-checkout-start')


@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get('checkout_subscription_price_id')
    try:
        sub_price = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except SubscriptionPrice.DoesNotExist:
        sub_price = None
    if checkout_subscription_price_id is None or sub_price is None:
        return redirect('pricing')
    customer_stripe_id = request.user.customer.stripe_id
    success_url_path = reverse('stripe-checkout-end')
    pricing_url_path = reverse('pricing')

    success_url = f'{BASE_URL}{success_url_path}'
    cancel_url = f'{BASE_URL}{pricing_url_path}'
    url = start_checkout_session(
        customer_id=customer_stripe_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_stripe_id=sub_price.stripe_id,
        raw=False
    )
    return redirect(url)


def checkout_finalize_view(request):
    session_id = request.GET.get('session_id')
    customer_id, plan_id, sub_stripe_id = get_checkout_customer_plan(session_id)
    try:
        # reverse relationship from Subscription to SubscriptionPrice
        user_obj = User.objects.get(customer__stripe_id=customer_id)
        subscription_obj = Subscription.objects.get(subscriptionprice__stripe_id=plan_id)
    except User.DoesNotExist:
        return HttpResponseBadRequest('Invalid user provided.')
    except Subscription.DoesNotExist:
        return HttpResponseBadRequest('Provided subscription plan is invalid.')

    user_subscription = UserSubscription.objects.filter(user=user_obj).first()
    if user_subscription:
        if user_subscription.subscription == subscription_obj:
            return HttpResponse('User is already subscribed to the provided plan.')
        else:
            # cancel the existing subscription
            old_stripe_id = user_subscription.stripe_id
            if old_stripe_id:
                cancel_subscription(old_stripe_id, reason='Auto ended, new membership.')

            user_subscription.subscription = subscription_obj
            user_subscription.stripe_id = sub_stripe_id
            user_subscription.save()
            return HttpResponse('User\'s plan upgraded.')

    UserSubscription.objects.create(user=user_obj, subscription=subscription_obj)
    return render(request, 'checkout/success.html', context={'subscription': subscription_obj})