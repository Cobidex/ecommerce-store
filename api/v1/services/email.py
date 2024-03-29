import random
from os import getenv
from flask_mail import Mail, Message
from services.redis import redisClient

class EmailSender:

    def __init__(self):
        self.__mail = Mail()

    def initialize(self, app):
        self.__mail.init_app(app)
    
    def send_verification_code(self, buyer):
        confirmation_code = random.randint(10000, 99999)
        expiry_seconds = 30 * 60
        redisClient.setex(f"verify_{buyer.id}", expiry_seconds, confirmation_code)

        msg = Message(
                subject='Account verification',
                body=str(confirmation_code),
                recipients=[buyer.email])
        
        self.__mail.send(msg)


    def send_account_activation_notice(self, buyer):
        msg = Message(
                subject='Account is activated',
                body='Congratulations! Your account is activated',
                recipients=[buyer.email])
        self.__mail.send(msg)


    def notify_admin_for_approval(self, vendor_id):
        admin_email = getenv('ADMIN_EMAIL')
        msg = Message(
                subject='Request for approval',
                body=f"vendor {vendor_id} is requesting approval",
                recipients=[admin_email])
        
        self.__mail.send(msg)
    
    def send_receipt_to_buyer(self, **info):
        msg = Message(
            subject="Payment receipt",
            body=f"order {info.get('order_id')} paid for\n\nAmount:{info.get('amount')}",
            reciepients=[info.email]
        )

        self.__mail.send(msg)

    def notify_vendor(self, **info):
        """
            notify vendor of item purchased
        """
        msg = Message(
            subject="Order placed",
            body=f"order {info.get('id')} has been payed for",
            recipients=[info.get('vendor_email')]
        )

        self.__mail.send(msg)

    def send_delivery_token(self, buyer_email, item):
        delivery_code = str(random.randint(10000, 99999))

        msg = Message(
                subject='Delivery code',
                body=f"Your delivery code is {delivery_code}",
                recipients=[buyer_email])
        
        self.__mail.send(msg)
        item.delivery_code = delivery_code
        item.save()


email_sender = EmailSender()