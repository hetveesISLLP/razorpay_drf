import uuid
import os
from dotenv import load_dotenv
from django.conf import settings
import razorpay
import re
import json

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
load_dotenv()


def create_payment_link_razorpay(request):
    amount = request.data.get('amount', None)
    if not amount:
        raise ValueError("Amount is required")
    if amount != int(amount):
        raise ValueError("Amount can be int only")

    supported_currency = ['AED', 'ALL', 'AMD', 'ARS', 'AUD', 'AWG', 'BBD', 'BDT', 'BMD', 'BND', 'BOB', 'BSD', 'BWP',
                          'BZD', 'CAD', 'CHF', 'CNY', 'COP', 'CRC', 'CUP', 'CZK', 'DKK', 'DOP', 'DZD', 'EGP', 'ETB',
                          'EUR', 'FJD', 'GBP', 'GHS', 'GIP', 'GMD', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF',
                          'IDR', 'ILS', 'INR', 'JMD', 'KES', 'KGS', 'KHR', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD',
                          'LSL', 'MAD', 'MDL', 'MKD', 'MMK', 'MNT', 'MOP', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'NAD',
                          'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'PEN', 'PGK', 'PHP', 'PKR', 'QAR', 'RUB', 'SAR', 'SCR',
                          'SEK', 'SGD', 'SLL', 'SOS', 'SSP', 'SVC', 'SZL', 'THB', 'TTD', 'TZS', 'USD', 'UYU', 'UZS',
                          'YER', 'ZAR']
    currency = request.data.get('currency', None)
    currency = currency.upper()
    if not currency:
        raise ValueError("Currency is required")
    if currency.upper() not in supported_currency:
        raise ValueError("Currency must be from ", supported_currency)

    description = request.data.get('description', None)
    if not description:
        raise ValueError("Description is required")

    customer = request.data.get('customer', None)

    if not customer:
        raise ValueError("Customer details are required")

    email_format = r'\b[A-Za-z0-9._]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{1,}\b'
    if not customer['email']:
        raise ValueError("Customer's email is required")
    elif customer['email'] != str(customer['email']):
        raise ValueError("Customer's email must be a string")
    elif not re.fullmatch(email_format, customer['email']):
        raise ValueError("Customer's email must be in name@domain.com")

    if not customer['contact']:
        raise ValueError("Customer's contact is required")
    elif customer['contact'] != str(customer['contact']):
        raise ValueError("Customer's contact must be a string")
    elif not (8 <= len(customer['contact']) <= 14):
        raise ValueError("Customer's contact must be 8 to 14 characters long")

    notify = request.data.get('notify', None)
    if not notify:
        raise ValueError("Notification detail is required. Either Email or SMS or both are required")

    reference_id = uuid.uuid4().hex[:6].upper()

    callback_url = request.build_absolute_uri() + "callback-url/"

    callback_method = "get"

    return client.payment_link.create({
        "amount": amount,
        "currency": currency,
        "description": description,
        "customer": customer,
        "notify": notify,
        "reference_id": reference_id,
        "callback_url": callback_url,
        "callback_method": callback_method
    })


def verify_payment_link_signature_razorpay(request):
    payment_link_id = request.GET.get('razorpay_payment_link_id', None)
    if not payment_link_id:
        raise ValueError("payment_link_id not found")

    payment_link_reference_id = request.GET.get('razorpay_payment_link_reference_id')
    if not payment_link_reference_id:
        raise ValueError("payment_link_reference_id not found")

    payment_link_status = request.GET.get('razorpay_payment_link_status')
    if not payment_link_status:
        raise ValueError("payment_link_status not found")

    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    if not razorpay_payment_id:
        raise ValueError("razorpay_payment_id not found")

    razorpay_signature = request.GET.get('razorpay_signature')
    if not razorpay_signature:
        raise ValueError("razorpay_signature not found")

    params = {
        'payment_link_id': payment_link_id,
        'payment_link_reference_id': payment_link_reference_id,
        'payment_link_status': payment_link_status,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }
    return client.utility.verify_payment_link_signature(params)


def payment_captured(request):
    captured_data = json.loads(request.body)
    client.utility.verify_webhook_signature(str(request.body, 'utf-8'),
                                            request.headers['X-Razorpay-Signature'],
                                            os.environ.get('RAZORPAY_SECRET_KEY'))
    # if payment is captured
    if captured_data['event'] == 'payment.captured':
        return True


def payment_failed(request):
    captured_data = json.loads(request.body)
    client.utility.verify_webhook_signature(str(request.body, 'utf-8'),
                                            request.headers['X-Razorpay-Signature'],
                                            os.environ.get('RAZORPAY_SECRET_KEY'))
    # if payment is captured
    if captured_data['event'] == 'payment.failed':
        return True

# {
#     "amount": 1000,
#     "currency": "INR",
#     "description": "description",
#     "customer": {
#         "name": "djde",
#         "email": "shahhetu.hs@gmail.com",
#         "contact": "+918866911353"
#     },
#     "notify": {
#         "email": "true",
#         "sms": "true"
#     }
#
# }
