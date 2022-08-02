# from django.test import TestCase

# # Create your tests here.
# # kind of views.py
# # main.py where order api is integrated
# #
# # app.html form where user fills details, when submitted, order api will be fired and order id will be generated
# #
# # pay.html has checkout code, user clicks pay button in this page to open razorpay checkout popup to complete paymet
# {
#   "id": "plink_ExjpAUN3gVHrPJ",
#   # Unique identifier of the Payment Link
#   "payments": [],
#   # Payment details such as amount, payment ID, Payment Link ID and more. This array gets populated only after the customer makes a payment. Until then, the value is null.
#   "reference_id": "TS1989",
#   # Reference number tagged to Payment Link. Must be a unique number for each Payment Link. 
#   "short_url": "https://rzp.io/i/nxrHnLJ",
#   "user_id": ""
#   # A unique identifier for the user role through which the Payment Link was created
# }