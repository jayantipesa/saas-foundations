import stripe
from decouple import config

DJANGO_DEBUG = config('DJANGO_DEBUG', cast=bool, default=False)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', cast=str, default='')

if 'sk_test' in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError('Invalid stripe key for prod')

stripe.api_key = STRIPE_SECRET_KEY


def create_customer(user, raw=False):
    response = stripe.Customer.create(
    name=user.username,
    email=user.email,
    )
    if raw:
        return response
    return response.id