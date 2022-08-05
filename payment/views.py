import json
import os
import uuid
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.decorators import api_view
import razorpay
from django.core import exceptions

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
load_dotenv()


@api_view(['POST'])
def create_payment_link(request):
    # creating a payment link using request.data values
    try:
        payment_link = client.payment_link.create(
            # The data should be passed in this format
            {
                # total amount of the product required
                "amount": request.data.get('amount'),
                # takes INR by default not req (comes in mail in payment link)
                "currency": "INR",
                # description of the product not req (comes in mail in payment link)
                "description": request.data.get('description'),
                # details of the customer (name not req, email req if u want to notify via email, same for phone)
                "customer": request.data.get('customer'),
                # notify the payment link via sms and email
                "notify": {
                    "sms": True,
                    "email": True,
                },
                "notes": {
                    "address": request.data.get('address')
                },
                "reference_id": uuid.uuid4().hex[:6].upper(),
                # handler of payment
                "callback_url": request.build_absolute_uri() + "callback-url",
                "callback_method": "get"
            })
        return Response(payment_link, status=status.HTTP_200_OK)
    except exceptions.BadRequest:
        return Response({"message": "Payment link creation failed."}, status=status.HTTP_400_BAD_REQUEST)


'''Handler of callback url'''


class PaymentHandler(APIView):
    def get(self, request):
        try:
            params = {
                # get payment_link_id from request
                'payment_link_id': request.GET.get('razorpay_payment_link_id'),
                # get payment_link_reference_id from request
                'payment_link_reference_id': request.GET.get('razorpay_payment_link_reference_id'),
                # get payment_link_status from request
                'payment_link_status': request.GET.get('razorpay_payment_link_status'),
                # get razorpay_payment_id from request
                'razorpay_payment_id': request.GET.get('razorpay_payment_id'),
                # get razorpay_signature from request
                'razorpay_signature': request.GET.get('razorpay_signature')
            }
            # verify payment link signature
            verify_pay_link = client.utility.verify_payment_link_signature(params)
            # if verified payment_link_signature
            if verify_pay_link:
                return Response({"message": "Payment is successful."}, status=status.HTTP_200_OK)
            # if payment_link_signature is not verified
            return Response({"message": "Payment link verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.BadRequest:
            return Response({"message": "Payment link details not found"}, status=status.HTTP_404_NOT_FOUND)

    # required for webhook
    # this will work if you use ngrok and post generated url in razorpay dashboard setting webhook url
    def post(self, request):
        captured_data = json.loads(request.body)
        try:
            client.utility.verify_webhook_signature(str(request.body, 'utf-8'),
                                                    request.headers['X-Razorpay-Signature'],
                                                    settings.RAZORPAY_SECRET_KEY)
            # if payment is captured
            if captured_data['event'] == 'payment.captured':
                print("Successfully captured payment")
                return Response({"message": "Payment Succeeded"}, status=status.HTTP_200_OK)
            # if payment is not captured or payment is failed.
            elif captured_data['event'] == 'payment.failed':
                print("Failed to capture payment")
                return Response({"message": "Payment Failed"}, status=status.HTTP_205_RESET_CONTENT)
        # if webhook signature verification failed.
        except razorpay.errors.SignatureVerificationError as ve:
            print(ve, "Verification fail")
            return Response({"message": "Webhook signature verification failed."}, status=status.HTTP_205_RESET_CONTENT)
        except exceptions as e:
            print(e, 'Exception occurred')
            return Response({"message": "Webhook signature verification failed."}, status=status.HTTP_205_RESET_CONTENT)
