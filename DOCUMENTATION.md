### Create Payment Link
<hr>

```Python
import razorpay
client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))

client.payment_link.create({
  "amount": 500,
  "currency": "INR",
  "description": "For XYZ purpose",
  "reference_id": "TS1989",
  "customer": {
    "name": "Gaurav Kumar",
    "email": "gaurav.kumar@example.com",
    "contact": "+919999999999"
  },
  "notify": {
    "sms": True,
    "email": True
  },
  "callback_url": "https://example-callback-url.com/",
  "callback_method": "get"
})
```

> **_Note_** : Payment Link will be valid for six months from the date of creation. Please note that the expire by date cannot exceed more than six months from the date of creation.

The query parameters will be added to url as

    https://example-callback-url.com/?razorpay_payment_id=pay_Fc8mUeDrEKf08Y&razorpay_payment_link_id=plink_Fc8lXILABzQL7M&razorpay_payment_link_reference_id=TSsd1989&razorpay_payment_link_status=partially_paid&razorpay_signature=b0ea302006d9c3da504510c9be482a647d5196b265f5a82aeb272888dcbee70e
<br>

### Verify Payment Link signature
<hr>

- payment_link_id
- payment_link_reference_id
- payment_link_status
- razorpay_payment_id 
- razorpay_signature
> **_Note_** : All these values can be found as payload from request

```python
import razorpay
client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))

client.utility.verify_payment_link_signature({
   'payment_link_id': payment_link_id,
   'payment_link_reference_id': payment_link_reference_id,
   'payment_link_status':payment_link_status,
   'razorpay_payment_id': razorpay_payment_id,
   'razorpay_signature': razorpay_signature
   })
```
### Fetch Payment Links
<hr>

Fetch All
```python
import razorpay
client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))
client.payment_link.all()
```

Fetch Specific Payment Links by ID
```python
import razorpay
client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))
client.payment_link.fetch(paymentLinkId)
```

### Validate Webhooks
```python
import razorpay
client.utility.verify_webhook_signature(webhook_body, webhook_signature, webhook_secret)
```
Parameters

* webhook_body : can be obtained from payload. The body must be passed in raw request format encoded with utf-8 as string

* webhook signature : Can be obtained from request.headers['X-Razorpay-Signature']

* webhook_secret : Enter you webhook secret that you entered while creating webhook on dashboard


