import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from loguru import logger
from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
import pandas as pd
import redis
import time
import random
from jinja2 import Template
from supabase import create_client as _create_supabase_client

# Configure logging
logger.add("/app/logs/agents.log", rotation="1 day", retention="7 days", level="INFO")

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)
        
        # Initialize real Supabase client (no mocks)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise RuntimeError(f"[{name}] Missing Supabase configuration. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY/ANON_KEY")
        self.supabase = _create_supabase_client(supabase_url, supabase_key)
        logger.info(f"[{name}] Initialized real Supabase client")
        
    @abstractmethod
    async def process(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process job data and return result"""
        pass
    
    def update_job_status(self, job_id: str, status: str, result: Optional[Dict] = None, error: Optional[str] = None):
        """Update job status in Redis"""
        updates = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if result:
            updates["result"] = json.dumps(result)
            
        if error:
            updates["error"] = error
            
        self.redis_client.hset(f"agentik:status:{job_id}", mapping=updates)
        logger.info(f"[{self.name}] Updated job {job_id} status to {status}")
    
    def send_to_next_agent(self, next_agent: str, job_data: Dict[str, Any]):
        """Send job to next agent in workflow"""
        queue_name = f"agentik:agent:{next_agent}"
        self.redis_client.lpush(queue_name, json.dumps(job_data))
        logger.info(f"[{self.name}] Sent job {job_data.get('job_id')} to {next_agent}")

class RFQIntakeAgent(BaseAgent):
    """Agent responsible for processing incoming RFQs"""
    
    def __init__(self):
        super().__init__("rfq_intake")
    
    async def process(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate RFQ data"""
        try:
            job_id = job_data.get("job_id")
            if not job_id:
                logger.error(f"[{self.name}] Missing job_id in job_data")
                return {"success": False, "error": "Missing job_id"}
            
            rfq = job_data.get("payload", {}).get("rfq", {})
            
            logger.info(f"[{self.name}] Processing RFQ {rfq.get('id')}")
            
            # Validate RFQ data
            validation_result = self._validate_rfq(rfq)
            
            if not validation_result["valid"]:
                self.update_job_status(str(job_id), "failed", error=validation_result["errors"])
                return {"success": False, "error": validation_result["errors"]}
            
            # Enrich RFQ data
            enriched_rfq = self._enrich_rfq(rfq)
            
            # Update job data with enriched RFQ
            job_data["payload"]["rfq"] = enriched_rfq
            job_data["payload"]["intake_completed_at"] = datetime.utcnow().isoformat()
            
            # Update job status
            self.update_job_status(str(job_id), "in_progress", {
                "stage": "rfq_intake_completed",
                "rfq_validated": True,
                "next_agent": "supplier_discovery"
            })
            
            # Send to supplier discovery agent
            self.send_to_next_agent("supplier_discovery", job_data)
            
            return {"success": True, "rfq": enriched_rfq}
            
        except Exception as e:
            logger.error(f"[{self.name}] Error processing job: {e}")
            job_id = job_data.get("job_id")
            if job_id:
                self.update_job_status(str(job_id), "failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def _validate_rfq(self, rfq: Dict[str, Any]) -> Dict[str, Any]:
        """Validate RFQ data"""
        errors = []
        
        required_fields = ["title", "description", "category", "quantity", "deadline"]
        for field in required_fields:
            if not rfq.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate deadline
        try:
            deadline = datetime.fromisoformat(rfq.get("deadline", ""))
            if deadline <= datetime.utcnow():
                errors.append("Deadline must be in the future")
        except ValueError:
            errors.append("Invalid deadline format")
        
        # Validate quantity
        try:
            quantity = int(rfq.get("quantity", 0))
            if quantity <= 0:
                errors.append("Quantity must be greater than 0")
        except (ValueError, TypeError):
            errors.append("Invalid quantity format")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def _enrich_rfq(self, rfq: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich RFQ with additional metadata"""
        enriched = rfq.copy()
        
        # Add urgency level based on deadline
        try:
            deadline = datetime.fromisoformat(rfq["deadline"])
            days_until_deadline = (deadline - datetime.utcnow()).days
            
            if days_until_deadline <= 3:
                enriched["urgency"] = "high"
            elif days_until_deadline <= 7:
                enriched["urgency"] = "medium"
            else:
                enriched["urgency"] = "low"
                
            enriched["days_until_deadline"] = days_until_deadline
        except:
            enriched["urgency"] = "medium"
        
        # Add category keywords for supplier matching
        category_keywords = {
            "electronics": ["electronic", "technology", "hardware", "components"],
            "machinery": ["machine", "equipment", "tools", "industrial"],
            "chemicals": ["chemical", "raw materials", "substances"],
            "textiles": ["fabric", "cloth", "textile", "yarn"],
            "food": ["food", "beverage", "consumables", "perishable"]
        }
        
        enriched["keywords"] = category_keywords.get(rfq.get("category", "").lower(), [])
        
        return enriched

class SupplierDiscoveryAgent(BaseAgent):
    """Agent responsible for discovering and matching suppliers"""
    
    def __init__(self):
        super().__init__("supplier_discovery")
    
    async def process(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Discover suppliers for the RFQ"""
        try:
            job_id = job_data.get("job_id")
            rfq = job_data.get("payload", {}).get("rfq", {})
            
            logger.info(f"[{self.name}] Discovering suppliers for RFQ {rfq.get('id')}")
            
            # Find existing suppliers
            existing_suppliers = await self._find_existing_suppliers(rfq)
            
            # Simulate external supplier discovery
            discovered_suppliers = await self._discover_new_suppliers(rfq)
            
            # Combine and rank suppliers
            all_suppliers = existing_suppliers + discovered_suppliers
            ranked_suppliers = self._rank_suppliers(rfq, all_suppliers)
            
            # Store discovered suppliers
            await self._store_suppliers(discovered_suppliers)
            
            # Update job data
            job_data["payload"]["suppliers"] = ranked_suppliers[:10]  # Top 10 suppliers
            job_data["payload"]["discovery_completed_at"] = datetime.utcnow().isoformat()
            
            # Update job status
            self.update_job_status(job_id, "in_progress", {
                "stage": "supplier_discovery_completed",
                "suppliers_found": len(ranked_suppliers),
                "next_agent": "email_send"
            })
            
            # Send to email agent
            self.send_to_next_agent("email_send", job_data)
            
            return {"success": True, "suppliers": ranked_suppliers}
            
        except Exception as e:
            logger.error(f"[{self.name}] Error discovering suppliers: {e}")
            self.update_job_status(job_data.get("job_id"), "failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _find_existing_suppliers(self, rfq: Dict[str, Any]):
        """Find existing suppliers in database"""
        try:
            category = rfq.get("category", "")
            keywords = rfq.get("keywords", [])
            
            # Query suppliers by category
            response = self.supabase.table("suppliers").select("*").contains("categories", [category]).eq("verified", True).execute()
            
            suppliers = response.data if response.data else []
            
            # Add relevance score
            for supplier in suppliers:
                supplier["relevance_score"] = self._calculate_relevance(rfq, supplier)
                supplier["source"] = "existing"
            
            return suppliers
            
        except Exception as e:
            logger.error(f"Error finding existing suppliers: {e}")
            return []
    
    async def _discover_new_suppliers(self, rfq: Dict[str, Any]):
        """Simulate discovering new suppliers from external sources"""
        # In a real implementation, this would query external APIs, web scraping, etc.
        # For demo purposes, we'll generate some mock suppliers
        
        category = rfq.get("category", "general")
        mock_suppliers = [
            {
                "name": f"Premium {category.title()} Solutions",
                "email": f"sales@premium{category}solutions.com",
                "company": f"Premium {category.title()} Solutions Ltd.",
                "categories": [category],
                "description": f"Leading supplier of high-quality {category} products",
                "verified": False,
                "source": "discovered",
                "relevance_score": random.uniform(0.7, 0.9)
            },
            {
                "name": f"Global {category.title()} Trading",
                "email": f"inquiry@global{category}trading.com",
                "company": f"Global {category.title()} Trading Co.",
                "categories": [category],
                "description": f"International {category} supplier with competitive prices",
                "verified": False,
                "source": "discovered",
                "relevance_score": random.uniform(0.6, 0.8)
            },
            {
                "name": f"Elite {category.title()} Manufacturing",
                "email": f"contact@elite{category}mfg.com",
                "company": f"Elite {category.title()} Manufacturing Inc.",
                "categories": [category],
                "description": f"Specialized manufacturer of {category} components",
                "verified": False,
                "source": "discovered",
                "relevance_score": random.uniform(0.8, 0.95)
            }
        ]
        
        return mock_suppliers
    
    def _calculate_relevance(self, rfq: Dict[str, Any], supplier: Dict[str, Any]) -> float:
        """Calculate relevance score between RFQ and supplier"""
        score = 0.0
        
        # Category match
        rfq_category = rfq.get("category", "").lower()
        supplier_categories = [cat.lower() for cat in supplier.get("categories", [])]
        
        if rfq_category in supplier_categories:
            score += 0.5
        
        # Keyword matching
        rfq_keywords = rfq.get("keywords", [])
        supplier_desc = supplier.get("description", "").lower()
        
        keyword_matches = sum(1 for keyword in rfq_keywords if keyword in supplier_desc)
        score += (keyword_matches / max(len(rfq_keywords), 1)) * 0.3
        
        # Verification bonus
        if supplier.get("verified"):
            score += 0.2
        
        return min(score, 1.0)
    
    def _rank_suppliers(self, rfq: Dict[str, Any], suppliers) -> list:
        """Rank suppliers by relevance and other factors"""
        return sorted(suppliers, key=lambda s: s.get("relevance_score", 0), reverse=True)
    
    async def _store_suppliers(self, suppliers):
        """Store newly discovered suppliers in database"""
        for supplier in suppliers:
            if supplier.get("source") == "discovered":
                try:
                    supplier_data = {
                        "name": supplier["name"],
                        "email": supplier["email"],
                        "company": supplier["company"],
                        "categories": supplier["categories"],
                        "description": supplier["description"],
                        "verified": False,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    
                    self.supabase.table("suppliers").insert(supplier_data).execute()
                    logger.info(f"Stored new supplier: {supplier['name']}")
                    
                except Exception as e:
                    logger.error(f"Failed to store supplier {supplier['name']}: {e}")

class EmailSendAgent(BaseAgent):
    """Agent responsible for sending emails to suppliers"""
    
    def __init__(self):
        super().__init__("email_send")
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
    
    async def process(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send RFQ emails to suppliers"""
        try:
            job_id = job_data.get("job_id")
            rfq = job_data.get("payload", {}).get("rfq", {})
            suppliers = job_data.get("payload", {}).get("suppliers", [])
            
            logger.info(f"[{self.name}] Sending emails for RFQ {rfq.get('id')} to {len(suppliers)} suppliers")
            
            sent_emails = []
            failed_emails = []
            
            for supplier in suppliers:
                try:
                    email_result = await self._send_rfq_email(rfq, supplier)
                    
                    if email_result["success"]:
                        sent_emails.append({
                            "supplier_id": supplier.get("id"),
                            "email": supplier["email"],
                            "sent_at": datetime.utcnow().isoformat()
                        })
                        
                        # Log email in database
                        await self._log_email(rfq, supplier, "invitation", "sent")
                    else:
                        failed_emails.append({
                            "supplier_id": supplier.get("id"),
                            "email": supplier["email"],
                            "error": email_result["error"]
                        })
                        
                        await self._log_email(rfq, supplier, "invitation", "failed", email_result["error"])
                        
                except Exception as e:
                    logger.error(f"Failed to send email to {supplier.get('email')}: {e}")
                    failed_emails.append({
                        "supplier_id": supplier.get("id"),
                        "email": supplier.get("email"),
                        "error": str(e)
                    })
            
            # Update job data
            job_data["payload"]["email_results"] = {
                "sent": sent_emails,
                "failed": failed_emails,
                "sent_count": len(sent_emails),
                "failed_count": len(failed_emails)
            }
            job_data["payload"]["emails_sent_at"] = datetime.utcnow().isoformat()
            
            # Update job status
            self.update_job_status(job_id, "in_progress", {
                "stage": "emails_sent",
                "emails_sent": len(sent_emails),
                "emails_failed": len(failed_emails),
                "next_agent": "inbox_parser"
            })
            
            # Send to inbox parser (with delay to simulate response time)
            job_data["payload"]["expected_responses_after"] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
            self.send_to_next_agent("inbox_parser", job_data)
            
            return {
                "success": True,
                "emails_sent": len(sent_emails),
                "emails_failed": len(failed_emails)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error sending emails: {e}")
            self.update_job_status(job_data.get("job_id"), "failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _send_rfq_email(self, rfq: Dict[str, Any], supplier: Dict[str, Any]) -> Dict[str, Any]:
        """Send RFQ invitation email to supplier"""
        try:
            # Generate email content
            subject = f"RFQ Invitation: {rfq['title']}"
            body = self._generate_email_body(rfq, supplier)
            
            # For demo purposes, we'll simulate email sending
            # In production, you would actually send via SMTP
            if self.email_username and self.email_password:
                # Actual email sending code would go here
                pass
            
            # Simulate success with high probability
            if random.random() > 0.1:  # 90% success rate
                logger.info(f"Email sent to {supplier['email']} for RFQ {rfq['id']}")
                return {"success": True}
            else:
                return {"success": False, "error": "SMTP delivery failed"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_email_body(self, rfq: Dict[str, Any], supplier: Dict[str, Any]) -> str:
        """Generate email body using template"""
        template = Template("""
Dear {{ supplier.name }},

We would like to invite {{ supplier.company }} to participate in our Request for Quotation (RFQ).

**RFQ Details:**
- Title: {{ rfq.title }}
- Category: {{ rfq.category }}
- Quantity: {{ rfq.quantity }} {{ rfq.unit }}
- Deadline: {{ rfq.deadline }}
- Delivery Location: {{ rfq.delivery_location }}

**Description:**
{{ rfq.description }}

{% if rfq.requirements %}
**Requirements:**
{{ rfq.requirements }}
{% endif %}

{% if rfq.budget_min and rfq.budget_max %}
**Budget Range:** ${{ rfq.budget_min }} - ${{ rfq.budget_max }}
{% endif %}

To submit your quotation, please reply to this email with:
1. Unit price
2. Total price
3. Delivery time
4. Terms and conditions
5. Any additional notes

Please submit your quotation before {{ rfq.deadline }}.

Thank you for your interest.

Best regards,
Agentik B2B Platform
        """)
        
        return template.render(rfq=rfq, supplier=supplier)
    
    async def _log_email(self, rfq: Dict[str, Any], supplier: Dict[str, Any], email_type: str, status: str, error: Optional[str] = None):
        """Log email sending activity"""
        try:
            email_data = {
                "rfq_id": rfq["id"],
                "supplier_id": supplier.get("id"),
                "email_type": email_type,
                "recipient": supplier["email"],
                "subject": f"RFQ Invitation: {rfq['title']}",
                "body": self._generate_email_body(rfq, supplier),
                "sent_at": datetime.utcnow().isoformat(),
                "delivery_status": status,
                "error_message": error
            }
            
            self.supabase.table("email_logs").insert(email_data).execute()
            
        except Exception as e:
            logger.error(f"Failed to log email: {e}")

class InboxParserAgent(BaseAgent):
    """Agent responsible for parsing incoming email responses"""
    
    def __init__(self):
        super().__init__("inbox_parser")
    
    async def process(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse inbox for supplier responses"""
        try:
            job_id = job_data.get("job_id")
            rfq = job_data.get("payload", {}).get("rfq", {})
            suppliers = job_data.get("payload", {}).get("suppliers", [])
            
            logger.info(f"[{self.name}] Parsing responses for RFQ {rfq.get('id')}")
            
            # Simulate email parsing (in real implementation, would connect to IMAP)
            responses = await self._simulate_email_responses(rfq, suppliers)
            
            # Parse and extract offers from responses
            parsed_offers = []
            for response in responses:
                try:
                    offer = self._extract_offer_from_response(rfq, response)
                    if offer:
                        parsed_offers.append(offer)
                except Exception as e:
                    logger.error(f"Failed to parse response from {response.get('supplier_email')}: {e}")
            
            # Update job data
            job_data["payload"]["email_responses"] = responses
            job_data["payload"]["parsed_offers"] = parsed_offers
            job_data["payload"]["parsing_completed_at"] = datetime.utcnow().isoformat()
            
            # Update job status
            self.update_job_status(job_id, "in_progress", {
                "stage": "responses_parsed",
                "responses_received": len(responses),
                "offers_extracted": len(parsed_offers),
                "next_agent": "supplier_verifier"
            })
            
            # Send to supplier verifier
            self.send_to_next_agent("supplier_verifier", job_data)
            
            return {
                "success": True,
                "responses_count": len(responses),
                "offers_count": len(parsed_offers)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error parsing inbox: {e}")
            self.update_job_status(job_data.get("job_id"), "failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _simulate_email_responses(self, rfq: Dict[str, Any], suppliers) -> list:
        """Simulate email responses from suppliers"""
        responses = []
        
        # Simulate response rate (60-80% of suppliers respond)
        response_rate = random.uniform(0.6, 0.8)
        responding_suppliers = random.sample(suppliers, int(len(suppliers) * response_rate))
        
        for supplier in responding_suppliers:
            # Simulate different types of responses
            response_type = random.choices(
                ["quote", "request_info", "decline"],
                weights=[0.7, 0.2, 0.1]
            )[0]
            
            response = {
                "supplier_id": supplier.get("id"),
                "supplier_email": supplier["email"],
                "supplier_name": supplier["name"],
                "response_type": response_type,
                "received_at": datetime.utcnow().isoformat()
            }
            
            if response_type == "quote":
                # Generate mock quotation data
                base_price = random.uniform(10, 1000)
                quantity = rfq.get("quantity", 1)
                
                response["content"] = f"""
Dear Customer,

Thank you for your RFQ. We are pleased to provide the following quotation:

Product: {rfq.get('title', 'Product')}
Quantity: {quantity} {rfq.get('unit', 'pcs')}
Unit Price: ${base_price:.2f}
Total Price: ${base_price * quantity:.2f}
Delivery Time: {random.randint(5, 30)} days
Payment Terms: 30 days net

Please let us know if you need any clarification.

Best regards,
{supplier['name']}
{supplier['company']}
                """
                
                response["extracted_data"] = {
                    "unit_price": base_price,
                    "total_price": base_price * quantity,
                    "delivery_time": random.randint(5, 30),
                    "terms": "30 days net"
                }
                
            elif response_type == "request_info":
                response["content"] = f"""
Dear Customer,

Thank you for your RFQ. We need additional information to provide an accurate quote:

- Detailed specifications
- Preferred delivery schedule
- Volume discounts applicability

Best regards,
{supplier['name']}
                """
                
            else:  # decline
                response["content"] = f"""
Dear Customer,

Thank you for considering us. Unfortunately, we cannot provide a quotation for this requirement at this time.

Best regards,
{supplier['name']}
                """
            
            responses.append(response)
        
        return responses
    
    def _extract_offer_from_response(self, rfq: Dict[str, Any], response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract structured offer data from email response"""
        if response["response_type"] != "quote":
            return None
        
        extracted = response.get("extracted_data", {})
        
        if not all(key in extracted for key in ["unit_price", "total_price", "delivery_time"]):
            return None
        
        offer = {
            "rfq_id": rfq["id"],
            "supplier_id": response["supplier_id"],
            "unit_price": extracted["unit_price"],
            "total_price": extracted["total_price"],
            "delivery_time": extracted["delivery_time"],
            "terms": extracted.get("terms", ""),
            "notes": f"Response received from {response['supplier_name']}",
            "status": "submitted",
            "submitted_at": response["received_at"],
            "raw_response": response["content"]
        }
        
        return offer

class SupplierVerifierAgent(BaseAgent):
    """Agent responsible for verifying suppliers and their offers"""
    
    def __init__(self):
        super().__init__("supplier_verifier")
    
    async def process(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify suppliers and validate their offers"""
        try:
            job_id = job_data.get("job_id")
            offers = job_data.get("payload", {}).get("parsed_offers", [])
            
            logger.info(f"[{self.name}] Verifying {len(offers)} offers")
            
            verified_offers = []
            
            for offer in offers:
                verification_result = await self._verify_offer(offer)
                
                offer["verification"] = verification_result
                offer["verified"] = verification_result["passed"]
                
                if verification_result["passed"]:
                    verified_offers.append(offer)
                    
                    # Store offer in database
                    await self._store_offer(offer)
            
            # Update job data
            job_data["payload"]["verified_offers"] = verified_offers
            job_data["payload"]["verification_completed_at"] = datetime.utcnow().isoformat()
            
            # Update job status
            self.update_job_status(job_id, "in_progress", {
                "stage": "offers_verified",
                "total_offers": len(offers),
                "verified_offers": len(verified_offers),
                "next_agent": "aggregation_report"
            })
            
            # Send to aggregation agent
            self.send_to_next_agent("aggregation_report", job_data)
            
            return {
                "success": True,
                "total_offers": len(offers),
                "verified_offers": len(verified_offers)
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error verifying offers: {e}")
            self.update_job_status(job_data.get("job_id"), "failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _verify_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Verify individual offer"""
        verification = {
            "passed": True,
            "issues": [],
            "score": 1.0,
            "checks": {}
        }
        
        # Price validation
        unit_price = offer.get("unit_price", 0)
        total_price = offer.get("total_price", 0)
        
        if unit_price <= 0:
            verification["issues"].append("Invalid unit price")
            verification["passed"] = False
        
        if total_price <= 0:
            verification["issues"].append("Invalid total price")
            verification["passed"] = False
        
        verification["checks"]["price_valid"] = unit_price > 0 and total_price > 0
        
        # Delivery time validation
        delivery_time = offer.get("delivery_time", 0)
        if delivery_time <= 0 or delivery_time > 365:  # Max 1 year
            verification["issues"].append("Invalid delivery time")
            verification["score"] -= 0.2
        
        verification["checks"]["delivery_time_reasonable"] = 0 < delivery_time <= 365
        
        # Supplier verification
        supplier_verification = await self._verify_supplier(offer.get("supplier_id"))
        verification["checks"]["supplier_verified"] = supplier_verification["verified"]
        
        if not supplier_verification["verified"]:
            verification["score"] -= 0.3
            verification["issues"].extend(supplier_verification["issues"])
        
        # Final score adjustment
        if verification["issues"]:
            verification["score"] = max(0.0, verification["score"])
        
        return verification
    
    async def _verify_supplier(self, supplier_id: str) -> Dict[str, Any]:
        """Verify supplier credentials"""
        try:
            # Get supplier from database
            response = self.supabase.table("suppliers").select("*").eq("id", supplier_id).maybe_single().execute()
            
            if not response.data:
                return {"verified": False, "issues": ["Supplier not found"]}
            
            supplier = response.data
            
            # Perform verification checks
            issues = []
            
            # Check required fields
            required_fields = ["name", "email", "company"]
            for field in required_fields:
                if not supplier.get(field):
                    issues.append(f"Missing {field}")
            
            # Check email format
            email = supplier.get("email", "")
            if "@" not in email or "." not in email:
                issues.append("Invalid email format")
            
            # In a real implementation, you might:
            # - Check company registration
            # - Verify business licenses
            # - Check credit ratings
            # - Validate contact information
            
            return {
                "verified": len(issues) == 0,
                "issues": issues,
                "supplier": supplier
            }
            
        except Exception as e:
            logger.error(f"Error verifying supplier {supplier_id}: {e}")
            return {"verified": False, "issues": [f"Verification error: {str(e)}"]}
    
    async def _store_offer(self, offer: Dict[str, Any]):
        """Store verified offer in database"""
        try:
            offer_data = {
                "rfq_id": offer["rfq_id"],
                "supplier_id": offer["supplier_id"],
                "unit_price": offer["unit_price"],
                "total_price": offer["total_price"],
                "delivery_time": offer["delivery_time"],
                "terms": offer.get("terms", ""),
                "notes": offer.get("notes", ""),
                "status": offer["status"],
                "submitted_at": offer["submitted_at"],
                "verification_score": offer["verification"]["score"],
                "verified": offer["verified"]
            }
            
            self.supabase.table("offers").insert(offer_data).execute()
            logger.info(f"Stored offer from supplier {offer['supplier_id']}")
            
        except Exception as e:
            logger.error(f"Failed to store offer: {e}")

class AggregationReportAgent(BaseAgent):
    """Agent responsible for aggregating results and generating reports"""
    
    def __init__(self):
        super().__init__("aggregation_report")
    
    async def process(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final aggregation report"""
        try:
            job_id = job_data.get("job_id")
            rfq = job_data.get("payload", {}).get("rfq", {})
            verified_offers = job_data.get("payload", {}).get("verified_offers", [])
            
            logger.info(f"[{self.name}] Generating report for RFQ {rfq.get('id')} with {len(verified_offers)} offers")
            
            # Generate analysis
            analysis = await self._analyze_offers(rfq, verified_offers)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(rfq, verified_offers, analysis)
            
            # Create comparison table
            comparison_table = self._create_comparison_table(verified_offers)
            
            # Generate summary report
            report = {
                "rfq": rfq,
                "total_offers": len(verified_offers),
                "analysis": analysis,
                "recommendations": recommendations,
                "comparison_table": comparison_table,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Update RFQ status to completed
            await self._update_rfq_status(rfq["id"], "completed")
            
            # Update job data
            job_data["payload"]["final_report"] = report
            job_data["payload"]["completed_at"] = datetime.utcnow().isoformat()
            
            # Mark job as completed
            self.update_job_status(job_id, "completed", {
                "stage": "completed",
                "final_report_generated": True,
                "total_offers": len(verified_offers)
            })
            
            return {"success": True, "report": report}
            
        except Exception as e:
            logger.error(f"[{self.name}] Error generating report: {e}")
            self.update_job_status(job_data.get("job_id"), "failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _analyze_offers(self, rfq: Dict[str, Any], offers) -> Dict[str, Any]:
        """Analyze offers and generate insights"""
        if not offers:
            return {"message": "No offers received"}
        
        prices = [offer["total_price"] for offer in offers]
        delivery_times = [offer["delivery_time"] for offer in offers]
        scores = [offer["verification"]["score"] for offer in offers]
        
        analysis = {
            "price_analysis": {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "price_spread": max(prices) - min(prices)
            },
            "delivery_analysis": {
                "min_delivery_time": min(delivery_times),
                "max_delivery_time": max(delivery_times),
                "avg_delivery_time": sum(delivery_times) / len(delivery_times)
            },
            "quality_analysis": {
                "avg_verification_score": sum(scores) / len(scores),
                "high_quality_offers": len([s for s in scores if s >= 0.8]),
                "low_quality_offers": len([s for s in scores if s < 0.6])
            }
        }
        
        # Budget analysis
        budget_min = rfq.get("budget_min")
        budget_max = rfq.get("budget_max")
        
        if budget_min and budget_max:
            within_budget = [p for p in prices if budget_min <= p <= budget_max]
            analysis["budget_analysis"] = {
                "within_budget_count": len(within_budget),
                "below_budget_count": len([p for p in prices if p < budget_min]),
                "above_budget_count": len([p for p in prices if p > budget_max])
            }
        
        return analysis
    
    def _generate_recommendations(self, rfq: Dict[str, Any], offers, analysis: Dict[str, Any]) -> list:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if not offers:
            recommendations.append("Consider expanding supplier search criteria")
            recommendations.append("Review RFQ requirements for clarity")
            return recommendations
        
        # Price-based recommendations
        price_analysis = analysis.get("price_analysis", {})
        if price_analysis.get("price_spread", 0) > price_analysis.get("avg_price", 0) * 0.5:
            recommendations.append("Wide price range detected - consider negotiating with mid-range suppliers")
        
        # Quality-based recommendations
        quality_analysis = analysis.get("quality_analysis", {})
        if quality_analysis.get("high_quality_offers", 0) > 0:
            recommendations.append(f"{quality_analysis['high_quality_offers']} high-quality offers available - prioritize these suppliers")
        
        # Delivery-based recommendations
        delivery_analysis = analysis.get("delivery_analysis", {})
        if delivery_analysis.get("min_delivery_time", 0) < 7:
            recommendations.append("Fast delivery options available - consider for urgent requirements")
        
        # Budget-based recommendations
        budget_analysis = analysis.get("budget_analysis", {})
        if budget_analysis.get("within_budget_count", 0) > 0:
            recommendations.append(f"{budget_analysis['within_budget_count']} offers within budget range")
        elif budget_analysis.get("below_budget_count", 0) > 0:
            recommendations.append("Consider suppliers offering below-budget prices")
        
        # Find best value offer
        if offers:
            # Score offers based on price, delivery time, and quality
            scored_offers = []
            for offer in offers:
                price_score = 1 - (offer["total_price"] / price_analysis.get("max_price", 1))
                delivery_score = 1 - (offer["delivery_time"] / delivery_analysis.get("max_delivery_time", 1))
                quality_score = offer["verification"]["score"]
                
                total_score = (price_score * 0.4) + (delivery_score * 0.3) + (quality_score * 0.3)
                scored_offers.append((offer, total_score))
            
            best_offer = max(scored_offers, key=lambda x: x[1])[0]
            recommendations.append(f"Best value offer: Supplier {best_offer.get('supplier_id', 'Unknown')} with score {scored_offers[0][1]:.2f}")
        
        return recommendations
    
    def _create_comparison_table(self, offers) -> list:
        """Create structured comparison table"""
        comparison = []
        
        for offer in offers:
            comparison.append({
                "supplier_id": offer.get("supplier_id"),
                "unit_price": offer.get("unit_price"),
                "total_price": offer.get("total_price"),
                "delivery_time": offer.get("delivery_time"),
                "terms": offer.get("terms", ""),
                "verification_score": offer["verification"]["score"],
                "verified": offer.get("verified", False)
            })
        
        # Sort by total price
        return sorted(comparison, key=lambda x: x["total_price"])
    
    async def _update_rfq_status(self, rfq_id: str, status: str):
        """Update RFQ status in database"""
        try:
            self.supabase.table("rfqs").update({
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", rfq_id).execute()
            
            logger.info(f"Updated RFQ {rfq_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update RFQ status: {e}")
