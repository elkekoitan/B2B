from core.base_agent import BaseAgent
from typing import Dict, Any, Optional
from loguru import logger
from core.database import get_db_pool
import json

class RFQIntakeAgent(BaseAgent):
    """Agent responsible for processing and validating new RFQ submissions"""
    
    def __init__(self):
        super().__init__(
            name="rfq_intake_agent",
            description="Processes and validates new RFQ submissions, enriches data and triggers supplier discovery"
        )
        
    async def process_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process RFQ intake task"""
        try:
            logger.info(f"Processing RFQ intake task: {task_data}")
            
            task_type = task_data.get('action', 'process_rfq')
            
            if task_type == 'process_rfq':
                return await self._process_new_rfq(task_data)
            elif task_type == 'validate_rfq':
                return await self._validate_rfq(task_data)
            else:
                return {"error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Error in RFQ intake processing: {e}")
            return {"error": str(e)}
            
    async def _process_new_rfq(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a new RFQ submission"""
        rfq_data = task_data.get('rfq_data', {})
        rfq_id = rfq_data.get('id')
        
        if not rfq_id:
            return {"error": "RFQ ID not provided"}
            
        # 1. Validate RFQ data
        validation_result = await self._validate_rfq_data(rfq_data)
        if not validation_result['valid']:
            return {"error": f"RFQ validation failed: {validation_result['errors']}"}
            
        # 2. Enrich RFQ data with additional context
        enriched_data = await self._enrich_rfq_data(rfq_data)
        
        # 3. Update RFQ in database
        await self._update_rfq_status(rfq_id, 'processed', enriched_data)
        
        # 4. Trigger supplier discovery if RFQ is published
        if rfq_data.get('status') == 'published':
            await self._trigger_supplier_discovery(rfq_id, enriched_data)
            
        return {
            "success": True,
            "rfq_id": rfq_id,
            "enriched_data": enriched_data
        }
        
    async def _validate_rfq_data(self, rfq_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate RFQ data completeness and quality"""
        errors = []
        
        # Required fields validation
        required_fields = ['title', 'description', 'category']
        for field in required_fields:
            if not rfq_data.get(field):
                errors.append(f"Missing required field: {field}")
                
        # Title length validation
        title = rfq_data.get('title', '')
        if len(title) < 5:
            errors.append("Title too short (minimum 5 characters)")
            
        # Description validation
        description = rfq_data.get('description', '')
        if len(description) < 20:
            errors.append("Description too short (minimum 20 characters)")
            
        # Budget validation
        budget_min = rfq_data.get('budget_min')
        budget_max = rfq_data.get('budget_max')
        if budget_min and budget_max and budget_min >= budget_max:
            errors.append("Maximum budget must be greater than minimum budget")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
        
    async def _enrich_rfq_data(self, rfq_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich RFQ data with additional context and metadata"""
        enriched = rfq_data.copy()
        
        # Add category-specific keywords
        category = rfq_data.get('category', '').lower()
        keywords = self._generate_keywords_for_category(category)
        enriched['search_keywords'] = keywords
        
        # Add urgency score based on deadline and priority
        urgency_score = self._calculate_urgency_score(rfq_data)
        enriched['urgency_score'] = urgency_score
        
        # Add estimated supplier count based on category
        estimated_suppliers = self._estimate_supplier_count(category)
        enriched['estimated_suppliers'] = estimated_suppliers
        
        return enriched
        
    def _generate_keywords_for_category(self, category: str) -> list:
        """Generate search keywords based on category"""
        keyword_map = {
            'elektronik': ['elektronik', 'komponent', 'devre', 'chip', 'semi'],
            'endüstri': ['endüstriyel', 'makine', 'ekipman', 'otomasyon'],
            'otomotiv': ['otomotiv', 'araba', 'parça', 'yedek'],
            'tekstil': ['tekstil', 'kumaş', 'dokuma', 'iplik'],
            'gıda': ['gıda', 'beslenme', 'organik', 'helal'],
            'inşaat': ['inşaat', 'yapı', 'malzeme', 'beton']
        }
        return keyword_map.get(category, [category])
        
    def _calculate_urgency_score(self, rfq_data: Dict[str, Any]) -> int:
        """Calculate urgency score (1-100)"""
        score = 50  # Base score
        
        # Priority adjustment
        priority = rfq_data.get('priority', 'medium')
        priority_scores = {'low': -20, 'medium': 0, 'high': 20, 'urgent': 40}
        score += priority_scores.get(priority, 0)
        
        # Deadline adjustment (if exists)
        deadline = rfq_data.get('deadline_date')
        if deadline:
            # Add logic to adjust based on how soon the deadline is
            pass
            
        return max(1, min(100, score))
        
    def _estimate_supplier_count(self, category: str) -> int:
        """Estimate number of potential suppliers for category"""
        category_estimates = {
            'elektronik': 150,
            'endüstri': 200,
            'otomotiv': 120,
            'tekstil': 80,
            'gıda': 90,
            'inşaat': 180
        }
        return category_estimates.get(category, 50)
        
    async def _update_rfq_status(self, rfq_id: str, status: str, enriched_data: Dict[str, Any]):
        """Update RFQ status in database"""
        db_pool = get_db_pool()
        if not db_pool:
            logger.error("Database pool not available")
            return
            
        try:
            async with db_pool.acquire() as connection:
                # Update RFQ with enriched data
                await connection.execute(
                    """
                    UPDATE rfqs 
                    SET 
                        requirements = COALESCE(requirements, '{}'::jsonb) || $2::jsonb,
                        updated_at = NOW()
                    WHERE id = $1
                    """,
                    rfq_id,
                    json.dumps({
                        'search_keywords': enriched_data.get('search_keywords', []),
                        'urgency_score': enriched_data.get('urgency_score', 50),
                        'estimated_suppliers': enriched_data.get('estimated_suppliers', 50),
                        'processed_by_intake_agent': True
                    })
                )
                logger.info(f"Updated RFQ {rfq_id} with enriched data")
                
        except Exception as e:
            logger.error(f"Error updating RFQ status: {e}")
            
    async def _trigger_supplier_discovery(self, rfq_id: str, rfq_data: Dict[str, Any]):
        """Trigger supplier discovery agent"""
        from core.redis_client import get_redis
        
        redis_client = get_redis()
        if not redis_client:
            logger.error("Redis client not available")
            return
            
        try:
            task_data = {
                'action': 'discover_suppliers',
                'rfq_id': rfq_id,
                'rfq_data': rfq_data,
                'search_keywords': rfq_data.get('search_keywords', []),
                'category': rfq_data.get('category'),
                'urgency_score': rfq_data.get('urgency_score', 50)
            }
            
            await redis_client.lpush(
                'agent_supplier_discovery_agent_queue',
                json.dumps(task_data)
            )
            
            logger.info(f"Triggered supplier discovery for RFQ {rfq_id}")
            
        except Exception as e:
            logger.error(f"Error triggering supplier discovery: {e}")