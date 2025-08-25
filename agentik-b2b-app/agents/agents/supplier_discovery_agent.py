from core.base_agent import BaseAgent
from typing import Dict, Any, Optional, List
from loguru import logger
from core.database import get_db_pool
import json
import asyncio

class SupplierDiscoveryAgent(BaseAgent):
    """Agent responsible for discovering and matching suppliers to RFQs"""
    
    def __init__(self):
        super().__init__(
            name="supplier_discovery_agent",
            description="Discovers relevant suppliers for RFQs and sends invitations"
        )
        
    async def process_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process supplier discovery task"""
        try:
            logger.info(f"Processing supplier discovery task: {task_data}")
            
            task_type = task_data.get('action', 'discover_suppliers')
            
            if task_type == 'discover_suppliers':
                return await self._discover_suppliers(task_data)
            else:
                return {"error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Error in supplier discovery: {e}")
            return {"error": str(e)}
            
    async def _discover_suppliers(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Discover relevant suppliers for an RFQ"""
        rfq_id = task_data.get('rfq_id')
        rfq_data = task_data.get('rfq_data', {})
        search_keywords = task_data.get('search_keywords', [])
        category = task_data.get('category')
        
        if not rfq_id:
            return {"error": "RFQ ID not provided"}
            
        # 1. Find matching suppliers
        matching_suppliers = await self._find_matching_suppliers(
            category, search_keywords, rfq_data
        )
        
        # 2. Score and rank suppliers
        ranked_suppliers = await self._rank_suppliers(matching_suppliers, rfq_data)
        
        # 3. Select top suppliers to invite
        selected_suppliers = self._select_suppliers_to_invite(ranked_suppliers)
        
        # 4. Create invitations and trigger email agent
        invitations_sent = await self._create_invitations(rfq_id, selected_suppliers)
        
        return {
            "success": True,
            "rfq_id": rfq_id,
            "suppliers_found": len(matching_suppliers),
            "suppliers_selected": len(selected_suppliers),
            "invitations_sent": invitations_sent
        }
        
    async def _find_matching_suppliers(self, category: str, keywords: List[str], rfq_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find suppliers matching the RFQ criteria"""
        db_pool = get_db_pool()
        if not db_pool:
            logger.error("Database pool not available")
            return []
            
        try:
            async with db_pool.acquire() as connection:
                # Find suppliers by category and specializations
                query = """
                    SELECT s.*, c.name as company_name, c.email as company_email,
                           c.phone, c.website, c.industry
                    FROM suppliers s
                    JOIN companies c ON s.company_id = c.id
                    WHERE s.verified = true
                    AND (
                        $1 = ANY(s.specializations)
                        OR c.industry ILIKE '%' || $1 || '%'
                        OR EXISTS (
                            SELECT 1 FROM unnest(s.specializations) as spec
                            WHERE spec ILIKE ANY($2::text[])
                        )
                    )
                    ORDER BY s.rating DESC, s.total_completed_orders DESC
                    LIMIT 50
                """
                
                # Prepare keyword patterns for ILIKE
                keyword_patterns = [f"%{keyword}%" for keyword in keywords]
                
                rows = await connection.fetch(query, category, keyword_patterns)
                
                suppliers = []
                for row in rows:
                    supplier_data = dict(row)
                    suppliers.append(supplier_data)
                    
                logger.info(f"Found {len(suppliers)} matching suppliers")
                return suppliers
                
        except Exception as e:
            logger.error(f"Error finding matching suppliers: {e}")
            return []
            
    async def _rank_suppliers(self, suppliers: List[Dict[str, Any]], rfq_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank suppliers based on relevance and quality metrics"""
        for supplier in suppliers:
            score = 0
            
            # Rating score (0-50 points)
            rating = float(supplier.get('rating', 0))
            score += (rating / 5.0) * 50
            
            # Completion rate (0-30 points)
            completed_orders = supplier.get('total_completed_orders', 0)
            if completed_orders > 0:
                # Higher completion count = higher score
                score += min(30, completed_orders * 2)
            
            # Response time (0-20 points)
            avg_response_time = supplier.get('average_response_time', 48)  # hours
            if avg_response_time <= 6:
                score += 20
            elif avg_response_time <= 24:
                score += 10
            elif avg_response_time <= 48:
                score += 5
                
            # Verification status (bonus)
            if supplier.get('verified'):
                score += 10
                
            supplier['match_score'] = score
            
        # Sort by score (highest first)
        return sorted(suppliers, key=lambda x: x.get('match_score', 0), reverse=True)
        
    def _select_suppliers_to_invite(self, ranked_suppliers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Select top suppliers to invite based on scoring and diversity"""
        # Select top 10 suppliers, ensuring diversity
        selected = []
        selected_companies = set()
        
        for supplier in ranked_suppliers:
            company_id = supplier.get('company_id')
            
            # Avoid duplicate companies
            if company_id in selected_companies:
                continue
                
            # Only invite high-quality suppliers (score > 30)
            if supplier.get('match_score', 0) > 30:
                selected.append(supplier)
                selected_companies.add(company_id)
                
                # Limit to top 10
                if len(selected) >= 10:
                    break
                    
        logger.info(f"Selected {len(selected)} suppliers to invite")
        return selected
        
    async def _create_invitations(self, rfq_id: str, suppliers: List[Dict[str, Any]]) -> int:
        """Create invitation records and trigger email sending"""
        db_pool = get_db_pool()
        if not db_pool:
            logger.error("Database pool not available")
            return 0
            
        invitations_created = 0
        
        try:
            async with db_pool.acquire() as connection:
                for supplier in suppliers:
                    # Create invitation record
                    invitation_id = await connection.fetchval(
                        """
                        INSERT INTO rfq_invitations 
                        (rfq_id, supplier_id, invited_by, status, invited_at)
                        VALUES ($1, $2, (
                            SELECT requester_id FROM rfqs WHERE id = $1
                        ), 'pending', NOW())
                        RETURNING id
                        """,
                        rfq_id, supplier['id']
                    )
                    
                    if invitation_id:
                        # Trigger email sending
                        await self._trigger_email_invitation(rfq_id, supplier, invitation_id)
                        invitations_created += 1
                        
            logger.info(f"Created {invitations_created} invitations for RFQ {rfq_id}")
            return invitations_created
            
        except Exception as e:
            logger.error(f"Error creating invitations: {e}")
            return 0
            
    async def _trigger_email_invitation(self, rfq_id: str, supplier: Dict[str, Any], invitation_id: str):
        """Trigger email invitation to supplier"""
        from core.redis_client import get_redis
        
        redis_client = get_redis()
        if not redis_client:
            logger.error("Redis client not available")
            return
            
        try:
            task_data = {
                'action': 'send_rfq_invitation',
                'rfq_id': rfq_id,
                'supplier_id': supplier['id'],
                'supplier_email': supplier.get('company_email'),
                'supplier_name': supplier.get('company_name'),
                'invitation_id': invitation_id
            }
            
            await redis_client.lpush(
                'agent_email_send_agent_queue',
                json.dumps(task_data)
            )
            
            logger.info(f"Triggered email invitation to {supplier.get('company_name')}")
            
        except Exception as e:
            logger.error(f"Error triggering email invitation: {e}")