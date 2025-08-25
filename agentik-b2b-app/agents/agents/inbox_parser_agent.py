from core.base_agent import BaseAgent
from typing import Dict, Any, Optional, List
from loguru import logger
from core.database import get_db_pool
import json
import re
from datetime import datetime, timedelta
import random

class InboxParserAgent(BaseAgent):
    """Agent responsible for parsing incoming emails and extracting offers"""
    
    def __init__(self):
        super().__init__(
            name="inbox_parser_agent",
            description="Parses incoming emails to extract supplier offers and responses"
        )
        
    async def process_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process inbox parsing task"""
        try:
            logger.info(f"Processing inbox parsing task: {task_data}")
            
            task_type = task_data.get('action', 'parse_emails')
            
            if task_type == 'parse_emails':
                return await self._parse_pending_emails(task_data)
            elif task_type == 'simulate_responses':
                return await self._simulate_email_responses(task_data)
            elif task_type == 'process_single_email':
                return await self._process_single_email(task_data)
            else:
                return {"error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Error in inbox parsing: {e}")
            return {"error": str(e)}
            
    async def _parse_pending_emails(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse all pending emails (simulated for now)"""
        # Since we don't have real IMAP, we'll simulate email responses
        return await self._simulate_email_responses(task_data)
        
    async def _simulate_email_responses(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate email responses from suppliers"""
        rfq_id = task_data.get('rfq_id')
        
        if not rfq_id:
            return {"error": "RFQ ID not provided"}
        
        # Get sent invitations for this RFQ
        invitations = await self._get_sent_invitations(rfq_id)
        
        if not invitations:
            logger.info(f"No sent invitations found for RFQ {rfq_id}")
            return {"success": True, "parsed_offers": 0}
        
        parsed_offers = 0
        
        # Simulate responses from some suppliers (70% response rate)
        for invitation in invitations:
            if random.random() < 0.7:  # 70% chance of response
                simulated_email = self._generate_simulated_email_response(invitation)
                
                if simulated_email:
                    offer_data = await self._extract_offer_from_email(simulated_email)
                    
                    if offer_data:
                        # Create offer in database
                        offer_created = await self._create_offer_from_email(
                            rfq_id, invitation['supplier_id'], offer_data
                        )
                        
                        if offer_created:
                            parsed_offers += 1
                            
                            # Trigger supplier verification
                            await self._trigger_supplier_verification(
                                rfq_id, invitation['supplier_id'], offer_created
                            )
        
        return {
            "success": True,
            "rfq_id": rfq_id,
            "invitations_checked": len(invitations),
            "parsed_offers": parsed_offers
        }
        
    async def _process_single_email(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email content"""
        email_content = task_data.get('email_content')
        sender_email = task_data.get('sender_email')
        subject = task_data.get('subject')
        
        if not email_content:
            return {"error": "Email content not provided"}
        
        # Extract offer information from email
        offer_data = await self._extract_offer_from_email({
            'content': email_content,
            'sender': sender_email,
            'subject': subject
        })
        
        return {
            "success": True,
            "offer_data": offer_data,
            "sender_email": sender_email
        }
        
    def _generate_simulated_email_response(self, invitation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a simulated email response from supplier"""
        supplier_name = invitation.get('company_name', 'Tedarikçi')
        
        # Generate realistic offer values
        base_price = random.uniform(1000, 50000)  # Base price range
        delivery_days = random.choice([3, 5, 7, 10, 14, 21, 30])
        currency = random.choice(['TRY', 'USD', 'EUR'])
        
        # Different response types
        response_types = [
            'detailed_offer',
            'simple_offer', 
            'request_clarification',
            'decline'
        ]
        
        response_type = random.choices(
            response_types, 
            weights=[60, 25, 10, 5]  # 60% detailed, 25% simple, 10% clarification, 5% decline
        )[0]
        
        if response_type == 'decline':
            content = f"""
            Sayın Yetkili,
            
            RFQ talebiniz için teşekkür ederiz. Maalesef mevcut durumda bu projeye teklif veremiyoruz.
            
            Gelecekteki projelerinizde değerlendirmek üzere iletişimde kalmayı dileriz.
            
            Saygılarımızla,
            {supplier_name}
            """
            return {
                'content': content,
                'sender': invitation.get('company_email'),
                'subject': f"Re: RFQ Daveti - {invitation.get('rfq_title', 'RFQ')}",
                'type': 'decline'
            }
        
        elif response_type == 'request_clarification':
            content = f"""
            Merhaba,
            
            RFQ'nuz için teşekkürler. Teklif hazırlayabilmek için aşağıdaki detayları öğrenmek istiyoruz:
            
            - Teknik spesifikasyonlar hakkında daha detaylı bilgi
            - Miktar bilgisi
            - Teslimat adresi
            - Ödeme koşulları
            
            Bu bilgileri aldıktan sonra size en uygun teklifi sunabiliriz.
            
            İyi çalışmalar,
            {supplier_name}
            """
            return {
                'content': content,
                'sender': invitation.get('company_email'),
                'subject': f"Re: RFQ Daveti - Ek Bilgi Talebi",
                'type': 'clarification'
            }
        
        else:  # detailed_offer or simple_offer
            if response_type == 'detailed_offer':
                content = f"""
                Sayın Yetkili,
                
                RFQ'nuz için teklifimiz aşağıdadır:
                
                TEKLIF DETAYLARI:
                ================
                Toplam Fiyat: {base_price:,.2f} {currency}
                Birim Fiyat: {base_price/random.randint(1,10):,.2f} {currency}
                Teslimat Süresi: {delivery_days} iş günü
                Geçerlilik Süresi: 30 gün
                Ödeme Koşulları: %30 peşin, %70 teslimatta
                
                TEKNIK ÖZELLİKLER:
                - Kalite sertifikası: ISO 9001
                - Garanti süresi: 24 ay
                - Teknik destek: 7/24
                
                EK NOTLAR:
                - Kargo ücreti dahil değildir
                - Kurulum hizmeti sunuyoruz (+%10)
                - Toplu siparişlerde indirim mevcuttur
                
                Sorularınız için her zaman erişilebiliriz.
                
                Saygılarımızla,
                {supplier_name}
                Satış Müdürü: Ahmet Yılmaz
                Tel: +90 212 555 0123
                Email: satis@{supplier_name.lower().replace(' ', '')}.com
                """
            else:  # simple_offer
                content = f"""
                Merhaba,
                
                RFQ'nuz için teklifimiz:
                
                Fiyat: {base_price:,.2f} {currency}
                Teslimat: {delivery_days} gün
                Geçerlilik: 15 gün
                
                Detayları görüşebiliriz.
                
                {supplier_name}
                """
                
            return {
                'content': content,
                'sender': invitation.get('company_email'),
                'subject': f"Re: RFQ Daveti - Teklifimiz",
                'type': 'offer',
                'extracted_data': {
                    'price': base_price,
                    'currency': currency,
                    'delivery_time': delivery_days,
                    'valid_until': (datetime.now() + timedelta(days=30)).isoformat(),
                    'payment_terms': '30% peşin, 70% teslimatta' if response_type == 'detailed_offer' else 'Görüşülür',
                    'warranty': '24 ay' if response_type == 'detailed_offer' else None,
                    'notes': 'Teknik destek dahil' if response_type == 'detailed_offer' else None
                }
            }
        
        return None
        
    async def _extract_offer_from_email(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured offer data from email content"""
        content = email_data.get('content', '').lower()
        
        # If already extracted in simulation
        if 'extracted_data' in email_data:
            return email_data['extracted_data']
        
        # Check if this is a decline
        decline_keywords = ['maalesef', 'teklif veremiyoruz', 'üzgünüz', 'mevcut durumda']
        if any(keyword in content for keyword in decline_keywords):
            return {
                'type': 'decline',
                'reason': 'Tedarikçi teklif veremiyor'
            }
        
        # Check if this is a clarification request
        clarification_keywords = ['bilgi', 'detay', 'öğrenmek', 'sormak']
        if any(keyword in content for keyword in clarification_keywords):
            return {
                'type': 'clarification',
                'questions': self._extract_questions_from_email(content)
            }
        
        # Extract price information
        price_patterns = [
            r'(?:fiyat|tutar|ücret).*?:?\s*([₺$€]?\s*[\d,\.]+)\s*([a-z]{3})?',
            r'([₺$€]?\s*[\d,\.]+)\s*([a-z]{3})?.*?(?:fiyat|tutar|ücret)',
            r'(\d+(?:[,\.]\d+)?)\s*(try|usd|eur|₺|\$|€)'
        ]
        
        extracted_data = {}
        
        for pattern in price_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    price_str = match.group(1).replace(',', '').replace('₺', '').replace('$', '').replace('€', '').strip()
                    price = float(price_str)
                    
                    currency = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'TRY'
                    currency = currency.upper().replace('₺', 'TRY').replace('$', 'USD').replace('€', 'EUR')
                    
                    extracted_data['price'] = price
                    extracted_data['currency'] = currency
                    break
                except (ValueError, AttributeError):
                    continue
                    
        # Extract delivery time
        delivery_patterns = [
            r'(?:teslimat|teslim).*?(\d+)\s*(?:gün|gun|days?)',
            r'(\d+)\s*(?:gün|gun|days?).*?(?:teslimat|teslim)',
            r'(?:süre|sure).*?(\d+)\s*(?:gün|gun|days?)'
        ]
        
        for pattern in delivery_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    extracted_data['delivery_time'] = int(match.group(1))
                    break
                except ValueError:
                    continue
        
        # Extract validity period
        validity_patterns = [
            r'(?:geçerli|gecerli).*?(\d+)\s*(?:gün|gun|days?)',
            r'(\d+)\s*(?:gün|gun|days?).*?(?:geçerli|gecerli)'
        ]
        
        for pattern in validity_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    days = int(match.group(1))
                    extracted_data['valid_until'] = (datetime.now() + timedelta(days=days)).isoformat()
                    break
                except ValueError:
                    continue
        
        # Extract payment terms
        if 'ödeme' in content or 'odeme' in content:
            payment_match = re.search(r'(?:ödeme|odeme).*?:(.*?)(?:\n|$)', content, re.IGNORECASE)
            if payment_match:
                extracted_data['payment_terms'] = payment_match.group(1).strip()
        
        # Extract warranty info
        if 'garanti' in content:
            warranty_match = re.search(r'garanti.*?(\d+)\s*(?:ay|yıl|yil|month|year)', content, re.IGNORECASE)
            if warranty_match:
                extracted_data['warranty'] = warranty_match.group(0).strip()
        
        # Extract notes
        notes_sections = []
        if 'not:' in content.lower():
            notes_match = re.search(r'not:(.+?)(?:\n\n|\n[A-Z]|$)', content, re.IGNORECASE | re.DOTALL)
            if notes_match:
                notes_sections.append(notes_match.group(1).strip())
        
        if notes_sections:
            extracted_data['notes'] = ' | '.join(notes_sections)
        
        # Default type
        extracted_data['type'] = 'offer'
        
        return extracted_data if extracted_data else None
        
    def _extract_questions_from_email(self, content: str) -> List[str]:
        """Extract questions from clarification emails"""
        questions = []
        
        # Look for question patterns
        question_patterns = [
            r'([^.!?]*\?[^.!?]*)',
            r'- ([^-\n]+)',
            r'• ([^•\n]+)',
            r'\d+\.\s*([^\d\n]+)'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                question = match.strip()
                if len(question) > 10 and question not in questions:
                    questions.append(question)
        
        return questions[:5]  # Limit to 5 questions
        
    async def _get_sent_invitations(self, rfq_id: str) -> List[Dict[str, Any]]:
        """Get sent invitations for an RFQ"""
        db_pool = get_db_pool()
        if not db_pool:
            return []
            
        try:
            async with db_pool.acquire() as connection:
                rows = await connection.fetch(
                    """
                    SELECT ri.*, s.id as supplier_id, c.name as company_name, 
                           c.email as company_email, r.title as rfq_title
                    FROM rfq_invitations ri
                    JOIN suppliers s ON ri.supplier_id = s.id
                    JOIN companies c ON s.company_id = c.id
                    JOIN rfqs r ON ri.rfq_id = r.id
                    WHERE ri.rfq_id = $1 
                    AND ri.status = 'sent'
                    AND ri.invited_at > NOW() - INTERVAL '7 days'
                    """,
                    rfq_id
                )
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting sent invitations: {e}")
            return []
            
    async def _create_offer_from_email(self, rfq_id: str, supplier_id: str, offer_data: Dict[str, Any]) -> Optional[str]:
        """Create offer record from parsed email data"""
        db_pool = get_db_pool()
        if not db_pool:
            return None
            
        # Handle different offer types
        if offer_data.get('type') == 'decline':
            # Update invitation status to declined
            try:
                async with db_pool.acquire() as connection:
                    await connection.execute(
                        """
                        UPDATE rfq_invitations 
                        SET status = 'declined', response_received_at = NOW(),
                            response_notes = $1
                        WHERE rfq_id = $2 AND supplier_id = $3
                        """,
                        offer_data.get('reason', 'Tedarikçi teklif vermedi'),
                        rfq_id, supplier_id
                    )
                logger.info(f"Updated invitation to declined for supplier {supplier_id}")
                return None
            except Exception as e:
                logger.error(f"Error updating declined invitation: {e}")
                return None
                
        elif offer_data.get('type') == 'clarification':
            # Update invitation status to needs_clarification
            try:
                async with db_pool.acquire() as connection:
                    await connection.execute(
                        """
                        UPDATE rfq_invitations 
                        SET status = 'needs_clarification', response_received_at = NOW(),
                            response_notes = $1
                        WHERE rfq_id = $2 AND supplier_id = $3
                        """,
                        json.dumps(offer_data.get('questions', [])),
                        rfq_id, supplier_id
                    )
                logger.info(f"Updated invitation to needs_clarification for supplier {supplier_id}")
                return None
            except Exception as e:
                logger.error(f"Error updating clarification request: {e}")
                return None
        
        # Create actual offer
        try:
            async with db_pool.acquire() as connection:
                offer_id = await connection.fetchval(
                    """
                    INSERT INTO offers 
                    (rfq_id, supplier_id, price, currency, delivery_time, 
                     valid_until, payment_terms, warranty, notes, 
                     status, submitted_at, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, 'pending', NOW(), NOW())
                    RETURNING id
                    """,
                    rfq_id, supplier_id, 
                    offer_data.get('price'),
                    offer_data.get('currency', 'TRY'),
                    offer_data.get('delivery_time'),
                    offer_data.get('valid_until'),
                    offer_data.get('payment_terms'),
                    offer_data.get('warranty'),
                    offer_data.get('notes')
                )
                
                # Update invitation status
                await connection.execute(
                    """
                    UPDATE rfq_invitations 
                    SET status = 'responded', response_received_at = NOW()
                    WHERE rfq_id = $1 AND supplier_id = $2
                    """,
                    rfq_id, supplier_id
                )
                
                logger.info(f"Created offer {offer_id} from email for supplier {supplier_id}")
                return offer_id
                
        except Exception as e:
            logger.error(f"Error creating offer from email: {e}")
            return None
            
    async def _trigger_supplier_verification(self, rfq_id: str, supplier_id: str, offer_id: str):
        """Trigger supplier verification for new offer"""
        try:
            await self.queue_task('supplier_verifier_agent', {
                'action': 'verify_offer',
                'rfq_id': rfq_id,
                'supplier_id': supplier_id,
                'offer_id': offer_id
            })
            
            logger.info(f"Triggered supplier verification for offer {offer_id}")
            
        except Exception as e:
            logger.error(f"Error triggering supplier verification: {e}")