import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from huey.contrib.djhuey import task
from store.models import Claim, Sell

logger = logging.getLogger(__name__)


@task()
def send_sell_receipt_to_user_email(sell: Sell):
    user = sell.user

    context = {
        "user": user.username,
        "date": sell.paid_at.strftime("%d de %B de %Y"),
    }

    receipt_pdf = sell.receipt

    message = render_to_string("store/receipt_email_template.txt", context)
    email_msg = EmailMessage(
        "Boleta de pago - Edukar",
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )

    email_msg.attach("Boleta de pago.pdf", receipt_pdf.read())
    email_msg.send(fail_silently=False)

    logger.info(
        f"Se ha enviado el correo al usuario {user.username}, con ID de compra '{sell.id}'"
    )


@task()
def send_user_claim(claim: Claim):
    name = claim.name

    context = {
        "name": name,
        "date": claim.date.strftime("%d de %B de %Y"),
    }

    claim_pdf = claim.claim_file

    message = render_to_string("store/lrecomendaciones.txt", context)
    email_msg = EmailMessage(
        "Edukar: Detalle de reclamo",
        message,
        settings.DEFAULT_FROM_EMAIL,
        [claim.email],
    )

    email_msg.attach("Hoja de reclamacion.pdf", claim_pdf.read())
    email_msg.send(fail_silently=False)

    logger.info(
        f"Se ha enviado el correo al usuario {claim.name}, con ID de reclamo '{claim.id}'"
    )
