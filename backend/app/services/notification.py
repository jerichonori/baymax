from typing import Optional, List
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class NotificationService:
    def __init__(self):
        self.ses_client = boto3.client(
            "ses",
            region_name=settings.AWS_SES_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        
        self.sns_client = boto3.client(
            "sns",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> bool:
        try:
            response = self.ses_client.send_email(
                Source=settings.AWS_SES_FROM_EMAIL,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {
                        "Text": {"Data": body_text},
                        "Html": {"Data": body_html} if body_html else {},
                    },
                },
            )
            
            logger.info(
                "Email sent successfully",
                to=to_email,
                message_id=response["MessageId"],
            )
            return True
            
        except ClientError as e:
            logger.error(
                "Failed to send email",
                to=to_email,
                error=str(e),
            )
            return False
    
    async def send_sms(
        self,
        phone: str,
        message: str,
    ) -> bool:
        try:
            if not phone.startswith("+"):
                phone = f"+91{phone}"
            
            response = self.sns_client.publish(
                PhoneNumber=phone,
                Message=message,
            )
            
            logger.info(
                "SMS sent successfully",
                to=phone,
                message_id=response["MessageId"],
            )
            return True
            
        except ClientError as e:
            logger.error(
                "Failed to send SMS",
                to=phone,
                error=str(e),
            )
            return False
    
    async def send_appointment_reminder(
        self,
        patient_email: Optional[str],
        patient_phone: str,
        appointment_time: str,
        provider_name: str,
        appointment_type: str,
        zoom_link: Optional[str] = None,
    ) -> bool:
        message = (
            f"Reminder: You have an appointment with Dr. {provider_name} "
            f"on {appointment_time}. "
        )
        
        if appointment_type == "virtual" and zoom_link:
            message += f"Join via: {zoom_link}"
        else:
            message += "Please arrive 10 minutes early."
        
        sms_sent = await self.send_sms(patient_phone, message)
        
        email_sent = False
        if patient_email:
            email_body = (
                f"Dear Patient,\n\n"
                f"This is a reminder for your upcoming appointment:\n\n"
                f"Provider: Dr. {provider_name}\n"
                f"Date & Time: {appointment_time}\n"
                f"Type: {appointment_type.capitalize()}\n"
            )
            
            if appointment_type == "virtual" and zoom_link:
                email_body += f"Zoom Link: {zoom_link}\n"
            
            email_body += (
                f"\nPlease complete your intake form if you haven't already.\n\n"
                f"Best regards,\nBaymax Health Team"
            )
            
            email_sent = await self.send_email(
                to_email=patient_email,
                subject="Appointment Reminder - Baymax Health",
                body_text=email_body,
            )
        
        return sms_sent or email_sent