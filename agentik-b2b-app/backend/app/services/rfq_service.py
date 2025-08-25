from supabase import Client
from loguru import logger
from typing import Dict, Any, Optional, List
from uuid import UUID
from app.models.rfq import RFQ, RFQCreate, RFQUpdate, RFQStatus
from app.core.redis_client import RedisService

class RFQService:
    """Service for RFQ business logic"""
    
    @staticmethod
    async def create_rfq(
        rfq_data: RFQCreate,
        requester_id: str,
        company_id: str,
        db: Client
    ) -> Optional[Dict[str, Any]]:
        """Create a new RFQ with business logic"""
        try:
            # Prepare RFQ data
            rfq_dict = rfq_data.model_dump()
            rfq_dict["requester_id"] = requester_id
            rfq_dict["company_id"] = company_id
            rfq_dict["status"] = RFQStatus.DRAFT
            
            # Insert into database
            result = db.table("rfqs").insert(rfq_dict).execute()
            
            if result.data:
                rfq = result.data[0]
                logger.info(f"RFQ created: {rfq['id']}")
                
                # Cache RFQ data for quick access
                await RedisService.set_json(f"rfq:{rfq['id']}", rfq, expire=3600)
                
                return rfq
            else:
                logger.error("Failed to create RFQ")
                return None
                
        except Exception as e:
            logger.error(f"Error creating RFQ: {e}")
            return None
    
    @staticmethod
    async def publish_rfq(
        rfq_id: str,
        user_id: str,
        db: Client
    ) -> bool:
        """Publish an RFQ to make it visible to suppliers"""
        try:
            # Verify ownership
            rfq_result = db.table("rfqs").select("*").eq(
                "id", rfq_id
            ).eq("requester_id", user_id).maybe_single().execute()
            
            if not rfq_result.data:
                logger.error(f"RFQ not found or access denied: {rfq_id}")
                return False
            
            # Update status to published
            result = db.table("rfqs").update({
                "status": RFQStatus.PUBLISHED
            }).eq("id", rfq_id).execute()
            
            if result.data:
                logger.info(f"RFQ published: {rfq_id}")
                
                # Queue for agent processing (supplier discovery)
                await RedisService.enqueue_task("rfq_processing", {
                    "action": "supplier_discovery",
                    "rfq_id": rfq_id,
                    "rfq_data": rfq_result.data
                })
                
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error publishing RFQ: {e}")
            return False
    
    @staticmethod
    async def get_rfq_statistics(
        rfq_id: str,
        db: Client
    ) -> Dict[str, Any]:
        """Get statistics for an RFQ"""
        try:
            # Get offers for this RFQ
            offers_result = db.table("offers").select("price, status").eq(
                "rfq_id", rfq_id
            ).execute()
            
            offers = offers_result.data or []
            
            # Calculate statistics
            prices = [float(offer["price"]) for offer in offers if offer.get("price")]
            
            stats = {
                "total_offers": len(offers),
                "submitted_offers": len([o for o in offers if o["status"] == "submitted"]),
                "average_price": sum(prices) / len(prices) if prices else 0,
                "min_price": min(prices) if prices else 0,
                "max_price": max(prices) if prices else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting RFQ statistics: {e}")
            return {}
    
    @staticmethod
    async def search_rfqs(
        filters: Dict[str, Any],
        user_company_id: Optional[str] = None,
        db: Client = None
    ) -> List[Dict[str, Any]]:
        """Search RFQs with filters"""
        try:
            query = db.table("rfqs").select("*, companies(*)")
            
            # Apply filters
            if filters.get("status"):
                query = query.eq("status", filters["status"])
            
            if filters.get("category"):
                query = query.eq("category", filters["category"])
            
            if filters.get("search"):
                search_term = filters["search"]
                query = query.or_(f"title.ilike.%{search_term}%,description.ilike.%{search_term}%")
            
            # Access control
            if user_company_id:
                query = query.or_(f"company_id.eq.{user_company_id},status.eq.published")
            else:
                query = query.eq("status", "published")
            
            result = query.order("created_at", desc=True).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error searching RFQs: {e}")
            return []