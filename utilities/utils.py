import uuid
import os
import razorpay
import re
import json
from django.core import exceptions

currency_pattern = "([A-Z]){3}"

email_format = r"\b[A-Za-z0-9._]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{1,}\b"

contact_pattern = "^\\+?[1-9][0-9]{7,14}$"

supported_currency = ['AED', 'ALL', 'AMD', 'ARS', 'AUD', 'AWG', 'BBD', 'BDT', 'BMD', 'BND', 'BOB', 'BSD', 'BWP',
                      'BZD', 'CAD', 'CHF', 'CNY', 'COP', 'CRC', 'CUP', 'CZK', 'DKK', 'DOP', 'DZD', 'EGP', 'ETB',
                      'EUR', 'FJD', 'GBP', 'GHS', 'GIP', 'GMD', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF',
                      'IDR', 'ILS', 'INR', 'JMD', 'KES', 'KGS', 'KHR', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD',
                      'LSL', 'MAD', 'MDL', 'MKD', 'MMK', 'MNT', 'MOP', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'NAD',
                      'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'PEN', 'PGK', 'PHP', 'PKR', 'QAR', 'RUB', 'SAR', 'SCR',
                      'SEK', 'SGD', 'SLL', 'SOS', 'SSP', 'SVC', 'SZL', 'THB', 'TTD', 'TZS', 'USD', 'UYU', 'UZS',
                      'YER', 'ZAR']

client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_SECRET_KEY')))


# max transaction amount per dy, upi, scanner


def create_payment_link_razorpay(request):
    amount = request.data.get('amount')
    if not amount:
        raise exceptions.FieldDoesNotExist("Amount is required")
    if type(amount) != int:
        raise TypeError("Currency is required in integer format only.")
    if amount > 50000000:
        raise exceptions.BadRequest("Currency cant exceed 5,00,000.00 or 50000000 .")

    description = request.data.get('description')
    if description:
        if type(description) != str:
            raise TypeError("Description is required in string only.")

    currency = request.data.get('currency')

    if not currency:
        raise exceptions.FieldDoesNotExist("Currency is required in integer format only.")
    if type(currency) != str:
        raise TypeError("Currency must be String")
    currency = currency.upper()
    if not re.match(currency_pattern, currency):
        raise ValueError("Currency is in invalid format.")
    if currency not in supported_currency:
        raise exceptions.ImproperlyConfigured("Currency must be from ", supported_currency)

    customer = request.data.get('customer')

    if not customer:
        raise exceptions.FieldDoesNotExist("Customer details are required")

    email = customer.get('email')

    if email:
        if type(email) != str:
            raise TypeError("Customer's email must be string")
        if not re.fullmatch(email_format, email):
            raise exceptions.ImproperlyConfigured("Customer's email must be in name@domain.com")

    contact = customer.get('contact')

    if contact:
        if type(contact) != str:
            raise TypeError("Customer's contact must be string")
        if not re.fullmatch(contact_pattern, contact):
            raise exceptions.ImproperlyConfigured(
                "Customer's contact must be valid format as +91123456789 having length 8 to 14")

    notify = request.data.get('notify')
    if not notify:
        raise exceptions.FieldDoesNotExist("Notification detail is required. Either Email or SMS or both are required")

    notify_sms = notify.get('sms')
    notify_email = notify.get('email')

    # check is notify_email and notify_sms are present or not
    if not (notify_email or notify_sms):
        raise exceptions.FieldDoesNotExist("Either notify via email or notify via sms or both are required.")

    if notify_email and not email:
        raise exceptions.FieldError("Notify via email works only if customer email is provided")

    if notify_sms and not contact:
        raise exceptions.FieldError("Notify via sms works only if customer contact is provided")

    accept_partial = request.data.get('accept_partial')

    first_min_partial_amount = request.data.get('first_min_partial_amount')
    if accept_partial:
        if type(accept_partial) != bool:
            raise TypeError("Accept partial must be a Boolean Value")
        if not first_min_partial_amount:
            raise exceptions.FieldError(
                "First Minimum Partial Amount is required if you want to accept partial payment")
        if type(first_min_partial_amount) != int:
            raise TypeError("First Minimum Partial Amount must be integer")
        if first_min_partial_amount < 100:
            raise ValueError("First minimum partial amount should be greater than 100 INR.")
        if first_min_partial_amount > amount:
            raise ValueError("First minimum partial amount should be less than payable amount.")

    reminder_enable = request.data.get('reminder_enable')
    if reminder_enable:
        if type(reminder_enable) != bool:
            raise TypeError("Reminder must be boolean")

    reference_id = str(uuid.uuid4())

    callback_url = request.build_absolute_uri() + "callback-url/"

    callback_method = "get"

    return client.payment_link.create({
        "amount": amount,
        "accept_partial": accept_partial,
        "first_min_partial_amount": first_min_partial_amount,
        "currency": currency,
        "description": description,
        "customer": customer,
        "notify": notify,
        "reminder_enable": reminder_enable,
        "reference_id": reference_id,
        "callback_url": callback_url,
        "callback_method": callback_method,
    })


def verify_payment_link_signature_razorpay(request):
    params = {
        'payment_link_id': request.GET.get('razorpay_payment_link_id'),
        'payment_link_reference_id': request.GET.get('razorpay_payment_link_reference_id'),
        'payment_link_status': request.GET.get('razorpay_payment_link_status'),
        'razorpay_payment_id': request.GET.get('razorpay_payment_id'),
        'razorpay_signature': request.GET.get('razorpay_signature')
    }
    return client.utility.verify_payment_link_signature(params)


def check_webhook(request):
    captured_data = json.loads(request.body)
    client.utility.verify_webhook_signature(str(request.body, 'utf-8'),
                                            request.headers['X-Razorpay-Signature'],
                                            os.environ.get('RAZORPAY_SECRET_KEY'))
    print(captured_data['event'], "jdkkkkkkkkkkkkk")
    if captured_data['event'] == 'payment.captured' or captured_data['event'] == 'payment.failed':
        return True
    return False

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

def fetch_all_payment_links():
    return client.payment_link.all()


def fetch_particular_payment_link(paymentLinkId):
    return client.payment_link.fetch(paymentLinkId)
