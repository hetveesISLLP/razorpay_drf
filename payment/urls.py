from django.urls import path
from .views import create_payment_link, PaymentHandler

urlpatterns = [
    # for creating payment link
    path('',create_payment_link, name='create_payment'),
    # for verifying signature and handle payment
    path('callback-url/', PaymentHandler.as_view(), name='verify_pl')

]
