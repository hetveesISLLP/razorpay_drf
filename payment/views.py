from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.core import exceptions
from utilities.utils import create_payment_link_razorpay, verify_payment_link_signature_razorpay, \
    check_webhook, fetch_all_payment_links, fetch_particular_payment_link


@api_view(['POST'])
def create_payment_link(request):
    # creating a payment link
    try:
        payment_link = create_payment_link_razorpay(request)
        return Response(payment_link, status=status.HTTP_200_OK)
    except ValueError as value_error:
        return Response({"message": str(value_error)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except TypeError as type_error:
        return Response({"message": str(type_error)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except exceptions.FieldDoesNotExist as field_not_found:
        return Response({"message": str(field_not_found)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except exceptions.ImproperlyConfigured as improperly_configured_error:
        return Response({"message": str(improperly_configured_error)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except exceptions.FieldError as field_error:
        return Response({"message": str(field_error)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except exceptions.BadRequest as bad_request_error:
        return Response({"message": str(bad_request_error)}, status=status.HTTP_400_BAD_REQUEST)


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
        webhook, status_webhook = check_webhook(request)
        if status_webhook:
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetPaymentLinks(APIView):

    def get(self, request):
        links = fetch_all_payment_links()
        return Response(links, status=status.HTTP_200_OK)


class GetDetailPaymentLink(APIView):

    def get(self, request, payment_link_id):
        links = fetch_particular_payment_link(payment_link_id=payment_link_id)
        return Response(links, status=status.HTTP_200_OK)
