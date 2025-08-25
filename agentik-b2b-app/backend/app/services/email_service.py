from supabase import Client
from loguru import logger
from typing import Dict, Any, Optional, List
from app.core.redis_client import RedisService
from app.models.email import EmailCreate, EmailType, EmailStatus
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import jinja2
import os

class EmailService:
    """Service for email operations"""
    
    # Email templates
    TEMPLATES = {
        EmailType.RFQ_INVITATION: {
            "subject": "RFQ Davetiniz - {{rfq_title}}",
            "template": "rfq_invitation.html"
        },
        EmailType.OFFER_SUBMISSION: {
            "subject": "Yeni Teklif Alındı - {{rfq_title}}",
            "template": "offer_submission.html"
        },
        EmailType.RFQ_AWARD: {
            "subject": "Tebrikler! RFQ Kazandınız - {{rfq_title}}",
            "template": "rfq_award.html"
        }
    }
    
    @staticmethod
    async def send_email(
        email_data: EmailCreate,
        db: Client,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send email and log the operation"""
        try:
            # Create email log entry
            log_data = email_data.model_dump()
            log_data["status"] = EmailStatus.PENDING
            
            log_result = db.table("email_logs").insert(log_data).execute()
            
            if not log_result.data:
                logger.error("Failed to create email log")
                return False
            
            email_log_id = log_result.data[0]["id"]
            
            # Queue email for sending
            await RedisService.enqueue_task("email_queue", {
                "email_log_id": email_log_id,
                "email_data": log_data,
                "template_data": template_data or {}
            })
            
            logger.info(f"Email queued for sending: {email_log_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    @staticmethod
    async def process_email_queue(
        email_task: Dict[str, Any],
        db: Client
    ) -> bool:
        """Process email from queue (called by agent)"""
        try:
            email_log_id = email_task["email_log_id"]
            email_data = email_task["email_data"]
            template_data = email_task.get("template_data", {})
            
            # Render email content if template is specified
            if email_data.get("email_type") in EmailService.TEMPLATES:
                template_info = EmailService.TEMPLATES[email_data["email_type"]]
                
                # Render subject
                subject_template = jinja2.Template(template_info["subject"])
                subject = subject_template.render(**template_data)
                
                # Render body (placeholder - would load from template files)
                body = email_data["body"]
                if template_data:
                    body_template = jinja2.Template(body)
                    body = body_template.render(**template_data)
                
                email_data["subject"] = subject
                email_data["body"] = body
            
            # Send via SMTP
            success = await EmailService._send_via_smtp(email_data)
            
            # Update email log
            status = EmailStatus.SENT if success else EmailStatus.FAILED
            db.table("email_logs").update({
                "status": status,
                "sent_at": "now()"
            }).eq("id", email_log_id).execute()
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing email queue: {e}")
            return False
    
    @staticmethod
    async def _send_via_smtp(email_data: Dict[str, Any]) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email_data["subject"]
            msg["From"] = email_data["sender_email"]
            msg["To"] = email_data["recipient_email"]
            
            # Add HTML body
            html_part = MIMEText(email_data["body"], "html")
            msg.attach(html_part)
            
            # Send email
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT,
                start_tls=settings.SMTP_USE_TLS,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD
            )
            
            logger.info(f"Email sent successfully to {email_data['recipient_email']}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP send error: {e}")
            return False
    
    @staticmethod
    async def send_rfq_invitation(
        rfq_data: Dict[str, Any],
        supplier_email: str,
        db: Client
    ) -> bool:
        """Send RFQ invitation to supplier"""
        try:
            email_data = EmailCreate(
                sender_email=settings.SMTP_USERNAME,
                recipient_email=supplier_email,
                subject=f"RFQ Davetiniz - {rfq_data['title']}",
                body=f"""
                <h2>Yeni RFQ Daveti</h2>
                <p>Merhaba,</p>
                <p>Aşağıdaki RFQ için teklif vermenizi bekliyoruz:</p>
                <h3>{rfq_data['title']}</h3>
                <p>{rfq_data['description']}</p>
                <p>Kategori: {rfq_data.get('category', 'Belirtilmemiş')}</p>
                <p>Son tarih: {rfq_data.get('deadline_date', 'Belirtilmemiş')}</p>
                <p>Teklif vermek için platformumuzu ziyaret edin.</p>
                """,
                email_type=EmailType.RFQ_INVITATION,
                rfq_id=rfq_data["id"]
            )
            
            return await EmailService.send_email(
                email_data,
                db,
                template_data={
                    "rfq_title": rfq_data["title"],
                    "rfq_description": rfq_data["description"],
                    "rfq_category": rfq_data.get("category", "Belirtilmemiş"),
                    "deadline_date": rfq_data.get("deadline_date", "Belirtilmemiş")
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending RFQ invitation: {e}")
            return False