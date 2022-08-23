from django.urls import path
from .views import create_payment_link, PaymentHandler, GetPaymentLinks, GetDetailPaymentLink, home

urlpatterns = [

    # for creating payment link
    path('create_payment_link/', create_payment_link, name='create_payment'),
    # for verifying signature and handle payment
    path('create_payment_link/callback-url/', PaymentHandler.as_view(), name='verify_pl'),
    # fetch all payment links
    path('all_payment_links/', GetPaymentLinks.as_view(), name='all_payment_links'),
    # fetch particular payment link
    path('payment_links/<paymentLinkId>/', GetDetailPaymentLink.as_view(), name='particular_payment_links'),
    path('', home, name='home'),
    # path('callback-url/', call, name='call'),
]
