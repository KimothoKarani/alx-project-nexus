from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_order_confirmation_email(order_id, recipient_email, order_details):
    subject = f"Your Order #{order_id} Confirmation"
    message = (
        f"Thank you for your order!\n\n"
        f"Order ID: {order_id}\n"
        f"Status: {order_details['status']}\n"
        f"Total: ${order_details['total_amount']}\n\n"
        f"Items:\n"
        + "\n".join(
            f"- {item['product_name']} (x{item['quantity']}) - ${item['price']}"
            for item in order_details["items"]
        )
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        fail_silently=False,
    )

    return f"Order confirmation for {order_id} sent to {recipient_email}"
