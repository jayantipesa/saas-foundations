import stripe
from decouple import config

from .date_utils import timestamp_as_datetime

DJANGO_DEBUG = config('DJANGO_DEBUG', cast=bool, default=False)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', cast=str, default='')

if 'sk_test' in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError('Invalid stripe key for prod')

stripe.api_key = STRIPE_SECRET_KEY

def serialize_subscription_data(data):
    current_period_start = timestamp_as_datetime(data.current_period_start)
    current_period_end = timestamp_as_datetime(data.current_period_end)
    return {
        'plan_id': data.plan.id,
        'current_period_start': current_period_start,
        'current_period_end': current_period_end,
        'status': data.status
    }

def create_customer(user, raw=False):
    metadata = {
        'user_id': user.id
    }
    response = stripe.Customer.create(
        name=user.username,
        email=user.email,
        metadata=metadata
    )
    if raw:
        return response
    return response.id


def create_product(name='', metadata={}, raw=False):
    response = stripe.Product.create(
        name=name,
        metadata=metadata
    )
    if raw:
        return response
    stripe_id = response.id
    return stripe_id


def create_price(
        currency='usd',
        unit_amount=9999,
        interval='month',
        product=None,
        metadata={},
        raw=False
    ):
    if product is None:
        return None
    response = stripe.Price.create(
        currency=currency,
        unit_amount=unit_amount,
        recurring={'interval': interval},
        product=product,
        metadata=metadata
    )
    if raw:
        return response
    return response.id

def start_checkout_session(customer_id,
                           success_url='',
                           cancel_url='',
                           price_stripe_id='',
                           raw=True
                        ):
    """
        Appending this, so stripe can replace it with session id on success
        In the success view, we use the session id to retreive payment related information
    """
    if not success_url.endswith('?session_id={CHECKOUT_SESSION_ID}'):
        success_url = f'{success_url}' + '?session_id={CHECKOUT_SESSION_ID}'
    response = stripe.checkout.Session.create(
        customer=customer_id,
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{'price': price_stripe_id, 'quantity': 1}],
        mode='subscription'
    )
    if not raw:
        return response.url
    return response

def get_checkout_session(session_id, raw=True):
    response = stripe.checkout.Session.retrieve(session_id)
    if not raw:
        return response.url
    return response

def get_subscription_detail(subscription_id, raw=True):
    response = stripe.Subscription.retrieve(subscription_id)
    if not raw:
        return response.url
    return response

def get_checkout_customer_plan(session_id):
    """
        Returns the customer id, chosen plan's price id and the new subscription id
    """
    checkout_session = get_checkout_session(session_id)
    subscription_stripe_id = checkout_session.subscription
    subscription_response = get_subscription_detail(subscription_stripe_id)
    subscription_data = serialize_subscription_data(subscription_response)

    return {
        'customer_id': checkout_session.customer,
        'stripe_id': subscription_stripe_id,
        **subscription_data
    }

def cancel_subscription(stripe_id, reason='', feedback='other', raw=True):
    response = stripe.Subscription.cancel(
        stripe_id,
        cancellation_details={
            'comment': reason,
            'feedback': feedback
        }
    )
    if not raw:
        return response.url
    return response