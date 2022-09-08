# Razorpay 
### Prerequisite
<hr>

[Python](https://www.python.org/downloads/), [Django](https://docs.djangoproject.com/en/4.0/topics/install/), [DRF](https://www.django-rest-framework.org/)

<br>### Installation
<hr>

> pip install razorpay

<br>
<br>

### Implementation
<hr>


    import razorpay
    client = razorpay.Client(auth=("<YOUR_API_KEY>", "<YOUR_API_SECRET>"))

YOUR_API_KEY and YOUR_API_SECRET will be generated once you create an account in [Razorpay](https://razorpay.com/). On your Dashboard > Settings > API Keys > Generate Key.
> **_NOTE:_**  Kindly store YOUR_API_SECRET somewhere as it will be used many times.

<br>
<br>

### Payment Links
<hr>


Payment Links are URLs that you can send to your customers through SMS and/or email to collect payments from them. Customers can click on the URL, which opens the payment request page, and complete the payment using any of the available payment methods.

There are two types of Payment Links:

1. Standard Payment Links: You can make payments using netbanking, cards, wallets, UPI and bank transfer payment methods using Standard Payment Links.

2. UPI Payment Links: You can select the UPI app of your choice to make payments using UPI Payment Links.


> **_Note_** : We are continuing with Standard Payment Links in this project

<br>
<br>

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
Verify the razorpay_signature parameter to validate that it is authentic and sent from Razorpay servers.

The razorpay_signature should be validated by your server. In order to verify the signature, you need to create a signature using

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
<br><br>
### Fetch Payment Links
<hr>

Fetch All
```python
client.payment_link.all()
```
<br>

Fetch Specific Payment Links by ID
```python
client.payment_link.fetch(paymentLinkId)
```
<BR>
<BR>

## Webhooks
<hr>
Webhooks are used to get notified about events related to the Razorpay payment flow such as orders, payments, settlements, disputes and workflow steps related to other Razorpay Products.

Webhooks (Web Callback, HTTP Push API or Reverse API) are one way that a web application can send information to another application in real-time when a specific event happens.

e.g order.paid, payment.failed, payment.captured, etc.

Razorpay Webhooks can be used to configure and receive notifications when a specific event occurs. When one of these events is triggered, we send an HTTP POST payload in JSON to the webhook's configured URL.

> **_Note_** : In webhook URLs, only port numbers 80 and 443 are currently allowed.

Inside [Razorpay Dashboard](https://razorpay.com/) navigate to Settings > Webhooks > Add New Webhook.

1. Enter the URL where you want to receive the webhook payload when an event is triggered. We recommended using an HTTPS URL.
2. Enter a Secret for the webhook endpoint. The secret is used to validate that the webhook is from Razorpay. Do not expose the secret publicly(Secret is recommended, not compulsory. It doesn't need to be RAZORPAY_SECRET_KEY). 
3. In the Alert Email field, enter the email address to which the notifications should be sent in case of webhook failure. You will receive webhook deactivation notifications to this email address.
4. Select the required events from the list of Active Events.

<br>

> **_Note_** :
> - All webhook responses must return a status code in the range 2XX within a window of 5 seconds.If response codes other than this is received or the request times out, it is considered a failure. 
> - On failure, a webhook is re-tried at progressive intervals of time, defined in the exponential back-off policy, for 24 hours. If the failures continue for 24 hours, the webhook is disabled. 
> - Webhooks can only be delivered to public URLs
### Test Webhooks

1. On Localhost

- You cannot use localhost directly to receive webhook events as webhook delivery requires a public URL. 
- You can handle this by creating a tunnel to your localhost using tools such as ngrok or localtunnel. 

> **_Note_** : Here we are using [ngrok](https://ngrok.com/)
> > sudo snap install ngrok
- For generating an authtoken, create account in [ngrok](https://ngrok.com/), navigate to Dashboard > Getting Started > Your Authtoken and Copy the authtoken
> ngrok config [add-authtoken-value]
- For generating an url :
> ngrok http 8000
- This will give an url which has https, Use the URL endpoint generated in the webhook URL while setting up your webhooks in Razorpay Dashboard.
2. Deployed
- Set the url for Webhook url in Razorpay Dashboard (no need of tunneling)

<br>
<br>

### Validate Webhooks
- When your webhook secret is set, Razorpay uses it to create a hash signature with each payload. This hash signature is passed with each request under the X-Razorpay-Signature header that you need to validate at your end.

> client.utility.verify_webhook_signature(webhook_body, webhook_signature, webhook_secret)

<br>

#### Parameters 

> webhook_body can be obtained from payload 
- The body must be passed in raw request format encoded with utf-8 as string

> webhook signature
- Can be obtained from request.headers['X-Razorpay-Signature']

> webhook_secret
- Enter you webhook secret that you entered while creating webhook on dashboard


Webhook Example
- Let’s say you’ve registered to receive the payment.captured event and a customer clicks the “Pay” button in your app or website. A webhook between Razorpay and your app tells your app whether the customer’s payment is successful or not. After your webhook endpoint receives the payment.captured event, your webhook function can then run backend actions as per your logic. Using an API for this workflow is like calling the API every millisecond to ask, was the payment successful?

> **_NOTE_** : For event handler, the webhook has POST request which will be executed first and not the get request.

## Limits / Transaction :
<hr>


> Max amt : 5,00,000
>
> net banking : 5,00,000
>
> cards : 5,00,000
>  
> wallet : 99,999
> 
> pay later : 5,00,000
>  
> UPI : 1,00,000
>
> QR : valid for 11:55


> **_NOTE_** : The settlements are made in INR. The payment is converted using the exchange rate at the time of payment creation.

> **_NOTE_** : GST is not mandatory if your business does not have an annual turnover of over ₹20 lakhs. However, if you do not provide your GST details, you would not be able to claim TDS at the time of filing your tax returns.

> **_NOTE_** : 18% GST is charged on the fee deducted for all payment methods except domestic card transactions of amount <= ₹ 2,000

