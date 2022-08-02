import os
import uuid

from rest_framework.response import Response
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import HttpResponse
import razorpay

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

# creating a payment link
@api_view(['GET'])
def create_payment_link(request):
    payment_link = client.payment_link.create({
        "amount": 50000,
        "currency": "INR",
        "description": "For XYZ purpose",
        "customer": {
            "name": "Hetvee SHah",
            "email": "shahhetu.hs@gmail.com",
            "contact": "+918866911353"
        },
        "notify": {
            "sms": True,
            "email": True,
        },
        "reference_id": uuid.uuid4().hex[:6].upper(),
        "callback_url": "http://127.0.0.1:8000/callback-url.com/",
        "callback_method": "get"
    })
    return HttpResponse('You are going to receive a mail and sms. Click on that link to start payment')


@api_view(['GET'])
def verify_payment_link_signature(request):

    verify_pay_link = client.utility.verify_payment_link_signature({
        'payment_link_id': request.GET.get('razorpay_payment_link_id'),
        'payment_link_reference_id': request.GET.get('razorpay_payment_link_reference_id'),
        'payment_link_status': request.GET.get('razorpay_payment_link_status'),
        'razorpay_payment_id': request.GET.get('razorpay_payment_id'),
        'razorpay_signature': request.GET.get('razorpay_signature')
    })
    if request.GET.get('razorpay_payment_link_status') == 'paid':
        return HttpResponse('done')
    return HttpResponse('payment failed')
