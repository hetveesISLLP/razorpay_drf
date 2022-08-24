import uuid
import os
import razorpay
import re
import json
from django.core import exceptions


EMAIL_FORMAT = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{1,}\b"

CONTACT_PATTERN = "^\\+?[1-9][0-9]{7,14}$"

SUPPORTED_CURRENCY = ['AED', 'ALL', 'AMD', 'ARS', 'AUD', 'AWG', 'BBD', 'BDT', 'BMD', 'BND', 'BOB', 'BSD', 'BWP',
                      'BZD', 'CAD', 'CHF', 'CNY', 'COP', 'CRC', 'CUP', 'CZK', 'DKK', 'DOP', 'DZD', 'EGP', 'ETB',
                      'EUR', 'FJD', 'GBP', 'GHS', 'GIP', 'GMD', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF',
                      'IDR', 'ILS', 'INR', 'JMD', 'KES', 'KGS', 'KHR', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD',
                      'LSL', 'MAD', 'MDL', 'MKD', 'MMK', 'MNT', 'MOP', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'NAD',
                      'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'PEN', 'PGK', 'PHP', 'PKR', 'QAR', 'RUB', 'SAR', 'SCR',
                      'SEK', 'SGD', 'SLL', 'SOS', 'SSP', 'SVC', 'SZL', 'THB', 'TTD', 'TZS', 'USD', 'UYU', 'UZS',
                      'YER', 'ZAR']

client = razorpay.Client(auth=(os.environ.get('RAZORPAY_KEY_ID'), os.environ.get('RAZORPAY_SECRET_KEY')))


def create_payment_link_razorpay(request: object) -> object:
    amount = request.data.get('amount')
    if not amount:
        raise exceptions.FieldDoesNotExist("Amount is required")
    if type(amount) != int:
        raise TypeError("Currency is required in integer format only.")
    # todo
    if amount > 50000000:
        raise exceptions.BadRequest("Currency cant exceed 5,00,000.00 or 50000000.")

    description = request.data.get('description')
    if description and type(description) != str:
        raise TypeError("Description is required in string only.")

    currency = request.data.get('currency')
    if not currency:
        raise exceptions.FieldDoesNotExist("Currency is required.")
    if type(currency) != str:
        raise TypeError("Currency must be string")
    currency = currency.upper()
    if currency.upper() not in SUPPORTED_CURRENCY:
        raise exceptions.ImproperlyConfigured("Currency must be from ", SUPPORTED_CURRENCY)

    customer = request.data.get('customer')
    if not customer:
        raise exceptions.FieldDoesNotExist("Customer details are required")
    email = customer.get('email')
    if email and (type(email) != str or not re.fullmatch(EMAIL_FORMAT, email)):
        raise exceptions.ImproperlyConfigured("Customer's email must be in name@domain.com")
    contact = customer.get('contact')
    if contact and (type(contact) != str or not re.fullmatch(CONTACT_PATTERN, contact)):
        raise exceptions.ImproperlyConfigured(
            "Customer's contact must be a string of valid format as +91123456789 having length 8 to 14")

    notify = request.data.get('notify')
    if not notify:
        raise exceptions.FieldDoesNotExist("Notification detail is required. Either Email or SMS or both are required")
    notify_sms = notify.get('sms')
    notify_email = notify.get('email')
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
        if type(first_min_partial_amount) != int and not 100 <= first_min_partial_amount <= amount:
            raise ValueError("First minimum partial amount should be greater than 100 INR and less than payable amount")

    reminder_enable = request.data.get('reminder_enable')
    if reminder_enable and type(reminder_enable) != bool:
        raise TypeError("Reminder must be boolean")

    reference_id = str(uuid.uuid4())

    callback_url = f"{request.build_absolute_uri()}callback-url/"

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

    if captured_data['event'] in ['payment.captured', 'payment.failed']:
        return captured_data['event'], True
    else:
        return False

def fetch_all_payment_links():
    return client.payment_link.all()


def fetch_particular_payment_link(payment_link_id):
    return client.payment_link.fetch(payment_link_id)

