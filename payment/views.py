from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.core import exceptions

from utilities.utils import create_payment_link_razorpay, verify_payment_link_signature_razorpay, \
    payment_captured, payment_failed

load_dotenv()


@api_view(['POST'])
def create_payment_link(request):
    # creating a payment link
    try:
        payment_link = create_payment_link_razorpay(request)
        return Response(payment_link, status=status.HTTP_200_OK)
    except ValueError as value_error:
        return Response({"ValueError_message": str(value_error)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except exceptions.BadRequest:
        return Response({"message": "Payment link creation failed."}, status=status.HTTP_400_BAD_REQUEST)


class PaymentHandler(APIView):
    def get(self, request):
        try:
            verify_payment_link = verify_payment_link_signature_razorpay(request)
            return Response({"payment_link_verified": verify_payment_link, "message": "Payment is successful."},
                            status=status.HTTP_200_OK)
        except exceptions.BadRequest:
            return Response({"message": "Payment link not verified"}, status=status.HTTP_404_NOT_FOUND)

    # required for webhook
    # this will work if you use ngrok and post generated url in razorpay dashboard setting webhook url
    def post(self, request):
        captured = payment_captured(request)
        if captured:
            return Response({"payment": "Captured"}, status=status.HTTP_200_OK)
        failed = payment_failed(request)
        if failed:
            return Response({"payment": "Failed"}, status=status.HTTP_200_OK)












# Data to be passed as :
# {
#     "amount": 500,
#     "description": "djkshcvdkcjd",
#     "customer":{
#         "name": "Hetu",
#         "email": "sjd@dhcde.com",
#         "contact": "+91123456789"
#     },
#     "notes": {
#         "address": "asdjhwjidws"
#     }
# }
