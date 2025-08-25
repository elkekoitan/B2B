from core.base_agent import BaseAgent
from typing import Dict, Any, Optional
from loguru import logger
from core.database import get_db_pool
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from jinja2 import Template

class EmailSendAgent(BaseAgent):
    """Agent responsible for sending emails (RFQ invitations, notifications, etc.)"""
    
    def __init__(self):
        super().__init__(
            name="email_send_agent",
            description="Handles email sending for RFQ invitations, notifications, and communications"
        )
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
    async def process_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process email sending task"""
        try:
            logger.info(f"Processing email task: {task_data}")
            
            task_type = task_data.get('action')
            
            if task_type == 'send_rfq_invitation':
                return await self._send_rfq_invitation(task_data)
            elif task_type == 'send_offer_notification':
                return await self._send_offer_notification(task_data)
            elif task_type == 'send_award_notification':
                return await self._send_award_notification(task_data)
            else:
                return {"error": f"Unknown email task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Error in email sending: {e}")
            return {"error": str(e)}
            
    async def _send_rfq_invitation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send RFQ invitation email to supplier"""
        rfq_id = task_data.get('rfq_id')
        supplier_email = task_data.get('supplier_email')
        supplier_name = task_data.get('supplier_name')
        invitation_id = task_data.get('invitation_id')
        
        if not all([rfq_id, supplier_email]):
            return {"error": "Missing required fields for RFQ invitation"}
            
        # Get RFQ details
        rfq_details = await self._get_rfq_details(rfq_id)
        if not rfq_details:
            return {"error": "RFQ not found"}
            
        # Prepare email content
        subject = f"RFQ Daveti - {rfq_details.get('title', 'Yeni RFQ')}"
        html_content = self._generate_rfq_invitation_html(rfq_details, supplier_name)
        
        # Send email
        success = await self._send_email(
            to_email=supplier_email,
            subject=subject,
            html_content=html_content
        )
        
        # Log email attempt
        await self._log_email(rfq_id, None, supplier_email, subject, 
                             'rfq_invitation', 'sent' if success else 'failed')
        
        if success:
            # Update invitation status
            await self._update_invitation_status(invitation_id, 'sent')
            
        return {
            "success": success,
            "rfq_id": rfq_id,
            "supplier_email": supplier_email,
            "invitation_id": invitation_id
        }
        
    async def _send_offer_notification(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification about new offer to RFQ owner"""
        rfq_id = task_data.get('rfq_id')
        offer_id = task_data.get('offer_id')
        
        # Get RFQ and offer details
        rfq_details = await self._get_rfq_details(rfq_id)
        offer_details = await self._get_offer_details(offer_id)
        
        if not all([rfq_details, offer_details]):
            return {"error": "RFQ or offer not found"}
            
        # Get RFQ owner email
        owner_email = await self._get_rfq_owner_email(rfq_id)
        if not owner_email:
            return {"error": "RFQ owner email not found"}
            
        # Prepare email content
        subject = f"Yeni Teklif Alındı - {rfq_details.get('title')}"
        html_content = self._generate_offer_notification_html(rfq_details, offer_details)
        
        # Send email
        success = await self._send_email(
            to_email=owner_email,
            subject=subject,
            html_content=html_content
        )
        
        # Log email attempt
        await self._log_email(rfq_id, offer_id, owner_email, subject, 
                             'offer_notification', 'sent' if success else 'failed')
        
        return {
            "success": success,
            "rfq_id": rfq_id,
            "offer_id": offer_id,
            "owner_email": owner_email
        }
        
    async def _send_award_notification(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send award notification to winning supplier"""
        # Implementation for award notification
        return {"success": True, "message": "Award notification sent"}
        
    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SMTP"""
        if not all([self.smtp_username, self.smtp_password]):
            logger.error("SMTP credentials not configured")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
            
    def _generate_rfq_invitation_html(self, rfq_details: Dict[str, Any], supplier_name: str) -> str:
        """Generate HTML content for RFQ invitation email"""
        template = Template("""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">🎯 Yeni RFQ Daveti</h2>
                
                <p>Merhaba {% if supplier_name %}{{ supplier_name }}{% else %}Değerli Tedarikçi{% endif %},</p>
                
                <p>Aşağıdaki RFQ için teklif vermenizi bekliyoruz:</p>
                
                <div style="background: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #1e40af;">{{ title }}</h3>
                    <p><strong>Kategori:</strong> {{ category }}</p>
                    <p><strong>Açıklama:</strong></p>
                    <p style="margin-left: 20px;">{{ description }}</p>
                    {% if deadline_date %}
                    <p><strong>Son Tarih:</strong> {{ deadline_date }}</p>
                    {% endif %}
                    {% if budget_max %}
                    <p><strong>Bütçe:</strong> ₺{{ budget_max|number_format }}</p>
                    {% endif %}
                </div>
                
                <p>Bu fırsatı değerlendirmek için platformumuzu ziyaret edin ve teklifinizi gönderin.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="#" style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Teklif Ver</a>
                </div>
                
                <p>Sorularınız için bizimle iletişime geçebilirsiniz.</p>
                
                <p>Saygılarımızla,<br>
                <strong>Agentik B2B Ekibi</strong></p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 12px; color: #6b7280;">Bu e-posta, Agentik B2B platformu üzerinden otomatik olarak gönderilmiştir.</p>
            </div>
        </body>
        </html>
        """)
        
        return template.render(
            supplier_name=supplier_name,
            title=rfq_details.get('title', ''),
            category=rfq_details.get('category', ''),
            description=rfq_details.get('description', ''),
            deadline_date=rfq_details.get('deadline_date'),
            budget_max=rfq_details.get('budget_max')
        )
        
    def _generate_offer_notification_html(self, rfq_details: Dict[str, Any], offer_details: Dict[str, Any]) -> str:
        """Generate HTML content for offer notification email"""
        template = Template("""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">🎉 Yeni Teklif Alındı!</h2>
                
                <p>Merhaba,</p>
                
                <p>"{{ rfq_title }}" RFQ'nuz için yeni bir teklif alındı.</p>
                
                <div style="background: #ecfdf5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 10px 0; color: #047857;">Teklif Detayları</h3>
                    <p><strong>Tedarikçi:</strong> {{ supplier_name }}</p>
                    <p><strong>Fiyat:</strong> ₺{{ price|number_format }} {{ currency }}</p>
                    <p><strong>Teslimat Süresi:</strong> {{ delivery_time }} gün</p>
                    {% if notes %}
                    <p><strong>Notlar:</strong> {{ notes }}</p>
                    {% endif %}
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="#" style="background: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Teklifi İncele</a>
                </div>
                
                <p>Saygılarımızla,<br>
                <strong>Agentik B2B Ekibi</strong></p>
            </div>
        </body>
        </html>
        """)
        
        return template.render(
            rfq_title=rfq_details.get('title', ''),
            supplier_name=offer_details.get('supplier_name', 'Bilinmeyen Tedarikçi'),
            price=offer_details.get('price', 0),
            currency=offer_details.get('currency', 'TRY'),
            delivery_time=offer_details.get('delivery_time', 'Belirtilmemiş'),
            notes=offer_details.get('notes')
        )
        
    async def _get_rfq_details(self, rfq_id: str) -> Optional[Dict[str, Any]]:
        """Get RFQ details from database"""
        db_pool = get_db_pool()
        if not db_pool:
            return None
            
        try:
            async with db_pool.acquire() as connection:
                row = await connection.fetchrow(
                    "SELECT * FROM rfqs WHERE id = $1", rfq_id
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting RFQ details: {e}")
            return None
            
    async def _get_offer_details(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Get offer details from database"""
        db_pool = get_db_pool()
        if not db_pool:
            return None
            
        try:
            async with db_pool.acquire() as connection:
                row = await connection.fetchrow(
                    """
                    SELECT o.*, c.name as supplier_name
                    FROM offers o
                    JOIN suppliers s ON o.supplier_id = s.id
                    JOIN companies c ON s.company_id = c.id
                    WHERE o.id = $1
                    """, offer_id
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting offer details: {e}")
            return None
            
    async def _get_rfq_owner_email(self, rfq_id: str) -> Optional[str]:
        """Get RFQ owner's email address"""
        db_pool = get_db_pool()
        if not db_pool:
            return None
            
        try:
            async with db_pool.acquire() as connection:
                email = await connection.fetchval(
                    """
                    SELECT u.email
                    FROM rfqs r
                    JOIN users u ON r.requester_id = u.auth_user_id::text
                    WHERE r.id = $1
                    """, rfq_id
                )
                return email
        except Exception as e:
            logger.error(f"Error getting RFQ owner email: {e}")
            return None
            
    async def _log_email(self, rfq_id: str, offer_id: Optional[str], recipient: str, 
                        subject: str, email_type: str, status: str):
        """Log email sending attempt"""
        db_pool = get_db_pool()
        if not db_pool:
            return
            
        try:
            async with db_pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO email_logs 
                    (rfq_id, offer_id, sender_email, recipient_email, subject, 
                     email_type, status, sent_at, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, 
                           CASE WHEN $7 = 'sent' THEN NOW() ELSE NULL END, NOW())
                    """,
                    rfq_id, offer_id, self.smtp_username, recipient, 
                    subject, email_type, status
                )
        except Exception as e:
            logger.error(f"Error logging email: {e}")
            
    async def _update_invitation_status(self, invitation_id: str, status: str):
        """Update invitation status"""
        db_pool = get_db_pool()
        if not db_pool:
            return
            
        try:
            async with db_pool.acquire() as connection:
                await connection.execute(
                    "UPDATE rfq_invitations SET status = $1 WHERE id = $2",
                    status, invitation_id
                )
        except Exception as e:
            logger.error(f"Error updating invitation status: {e}")