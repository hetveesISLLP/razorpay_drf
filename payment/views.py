import json
import os
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
    payment_link = client.payment_link.create(request.data)
    # The data should be passed in this format
    # ({
    #     "amount": 50000,
    #     "currency": "INR",
    #     "description": "For XYZ purpose",
    #     "customer": {
    #         "name": "Hetvee SHah",
    #         "email": "shahhetu.hs@gmail.com",
    #         "contact": "+918866911353"
    #     },
    #     "notify": {
    #         "sms": True,
    #         "email": True,
    #     },
    #     "reference_id": uuid.uuid4().hex[:6].upper(),
    #     "callback_url": "http://127.0.0.1:8000/callback-url.com/",
    #     "callback_method": "get"
    # })
    return Response(payment_link)


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
        except:
            return Response({"message": "Payment link details not found"}, status=status.HTTP_404_NOT_FOUND)

    # required for webhook
    def post(self, request):
        captured_data = json.loads(request.body)
        print()
        try:
            client.utility.verify_webhook_signature(str(request.body, 'utf-8'),
                                                    request.headers['X-Razorpay-Signature'],
                                                    os.environ.get('RAZORPAY_SECRET_KEY'))
            # if payment is captured
            if captured_data['event'] == 'payment.captured':
                print("Success")
                return Response({"message": "Payment Succeced"}, status=status.HTTP_200_OK)
            # if payment is not captured or payment is failed.
            print("Failed")
            return Response({"message": "Payment Failed"}, status=status.HTTP_400_BAD_REQUEST)
        # if webhook signature verification failed.
        except Exception as e:
            print(e, 'JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ')
            return Response({"message": "Webhook signature verification failed."}, status=status.HTTP_400_BAD_REQUEST)
