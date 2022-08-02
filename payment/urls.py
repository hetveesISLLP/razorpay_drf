from django.urls import path
from . views import create_payment_link, verify_payment_link_signature

urlpatterns = [
    path('', create_payment_link, name='create_payment'),
    path('callback-url.com/', verify_payment_link_signature, name='verify_pl'),
]