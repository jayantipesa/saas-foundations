import stripe
from decouple import config

DJANGO_DEBUG = config('DJANGO_DEBUG', cast=bool, default=False)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', cast=str, default='')

if 'sk_test' in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError('Invalid stripe key for prod')

stripe.api_key = STRIPE_SECRET_KEY


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