from core.base_agent import BaseAgent
from typing import Dict, Any, Optional, List
from loguru import logger
from core.database import get_db_pool
import json
import asyncio
from datetime import datetime, timedelta

class SupplierVerifierAgent(BaseAgent):
    """Agent responsible for verifying supplier information and validating offers"""
    
    def __init__(self):
        super().__init__(
            name="supplier_verifier_agent",
            description="Verifies supplier credibility, validates offers, and scores suppliers"
        )
        
    async def process_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process supplier verification task"""
        try:
            logger.info(f"Processing supplier verification task: {task_data}")
            
            task_type = task_data.get('action', 'verify_offer')
            
            if task_type == 'verify_offer':
                return await self._verify_offer(task_data)
            elif task_type == 'verify_supplier':
                return await self._verify_supplier_profile(task_data)
            elif task_type == 'validate_bulk_offers':
                return await self._validate_bulk_offers(task_data)
            else:
                return {"error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Error in supplier verification: {e}")
            return {"error": str(e)}
            
    async def _verify_offer(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a single offer and supplier"""
        rfq_id = task_data.get('rfq_id')
        supplier_id = task_data.get('supplier_id')
        offer_id = task_data.get('offer_id')
        
        if not all([rfq_id, supplier_id, offer_id]):
            return {"error": "Missing required fields for offer verification"}
        
        # Get offer and supplier details
        offer_details = await self._get_offer_details(offer_id)
        supplier_details = await self._get_supplier_details(supplier_id)
        rfq_details = await self._get_rfq_details(rfq_id)
        
        if not all([offer_details, supplier_details, rfq_details]):
            return {"error": "Could not retrieve required details"}
        
        # Perform comprehensive verification
        verification_result = await self._perform_comprehensive_verification(
            offer_details, supplier_details, rfq_details
        )
        
        # Update offer with verification results
        await self._update_offer_verification(offer_id, verification_result)
        
        # If offer passes verification, trigger aggregation
        if verification_result['verified'] and verification_result['credibility_score'] >= 60:
            await self._trigger_aggregation_update(rfq_id)
        
        return {
            "success": True,
            "offer_id": offer_id,
            "supplier_id": supplier_id,
            "verification_result": verification_result
        }
        
    async def _verify_supplier_profile(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify supplier profile independently"""
        supplier_id = task_data.get('supplier_id')
        
        if not supplier_id:
            return {"error": "Supplier ID not provided"}
        
        supplier_details = await self._get_supplier_details(supplier_id)
        if not supplier_details:
            return {"error": "Supplier not found"}
        
        # Perform supplier verification
        verification_result = await self._verify_supplier_credibility(supplier_details)
        
        # Update supplier profile with verification
        await self._update_supplier_verification(supplier_id, verification_result)
        
        return {
            "success": True,
            "supplier_id": supplier_id,
            "verification_result": verification_result
        }
        
    async def _validate_bulk_offers(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate multiple offers for an RFQ"""
        rfq_id = task_data.get('rfq_id')
        
        if not rfq_id:
            return {"error": "RFQ ID not provided"}
        
        # Get all pending offers for this RFQ
        pending_offers = await self._get_pending_offers(rfq_id)
        
        verified_count = 0
        failed_count = 0
        
        for offer in pending_offers:
            try:
                verification_task = {
                    'action': 'verify_offer',
                    'rfq_id': rfq_id,
                    'supplier_id': offer['supplier_id'],
                    'offer_id': offer['id']
                }
                
                result = await self._verify_offer(verification_task)
                
                if result.get('success'):
                    verified_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error verifying offer {offer['id']}: {e}")
                failed_count += 1
        
        return {
            "success": True,
            "rfq_id": rfq_id,
            "offers_verified": verified_count,
            "offers_failed": failed_count,
            "total_offers": len(pending_offers)
        }
        
    async def _perform_comprehensive_verification(self, offer_details: Dict[str, Any], 
                                                supplier_details: Dict[str, Any], 
                                                rfq_details: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive verification of offer and supplier"""
        
        # Initialize verification result
        verification_result = {
            "verified": False,
            "credibility_score": 0,
            "verification_details": {},
            "flags": [],
            "recommendations": []
        }
        
        # 1. Supplier credibility check
        supplier_score = await self._verify_supplier_credibility(supplier_details)
        verification_result["credibility_score"] = supplier_score["credibility_score"]
        verification_result["verification_details"]["supplier"] = supplier_score
        
        # 2. Offer validity check
        offer_validity = await self._verify_offer_validity(offer_details, rfq_details)
        verification_result["verification_details"]["offer"] = offer_validity
        
        # 3. Price reasonableness check
        price_analysis = await self._analyze_offer_pricing(offer_details, rfq_details)
        verification_result["verification_details"]["pricing"] = price_analysis
        
        # 4. Delivery feasibility check
        delivery_check = await self._verify_delivery_feasibility(offer_details, supplier_details)
        verification_result["verification_details"]["delivery"] = delivery_check
        
        # 5. Historical performance check
        performance_check = await self._check_supplier_performance(supplier_details)
        verification_result["verification_details"]["performance"] = performance_check
        
        # Calculate overall verification score
        overall_score = self._calculate_overall_score(
            supplier_score, offer_validity, price_analysis, 
            delivery_check, performance_check
        )
        
        verification_result["credibility_score"] = overall_score
        verification_result["verified"] = overall_score >= 60  # 60% threshold
        
        # Generate flags and recommendations
        verification_result["flags"] = self._generate_verification_flags(
            supplier_score, offer_validity, price_analysis, delivery_check
        )
        
        verification_result["recommendations"] = self._generate_recommendations(
            verification_result["flags"], overall_score
        )
        
        return verification_result
        
    async def _verify_supplier_credibility(self, supplier_details: Dict[str, Any]) -> Dict[str, Any]:
        """Verify supplier credibility based on profile data"""
        score = 0
        details = {}
        
        # Check verification status (30 points)
        if supplier_details.get('verified'):
            score += 30
            details['verification_status'] = 'verified'
        else:
            details['verification_status'] = 'unverified'
            details['flags'] = details.get('flags', []) + ['unverified_supplier']
        
        # Check rating (25 points)
        rating = float(supplier_details.get('rating', 0))
        if rating >= 4.5:
            score += 25
        elif rating >= 4.0:
            score += 20
        elif rating >= 3.5:
            score += 15
        elif rating >= 3.0:
            score += 10
        
        details['rating'] = rating
        details['rating_score'] = min(25, int((rating / 5.0) * 25))
        
        # Check completion history (20 points)
        completed_orders = supplier_details.get('total_completed_orders', 0)
        if completed_orders >= 50:
            score += 20
        elif completed_orders >= 20:
            score += 15
        elif completed_orders >= 10:
            score += 10
        elif completed_orders >= 5:
            score += 5
        
        details['completed_orders'] = completed_orders
        details['experience_level'] = 'expert' if completed_orders >= 50 else \
                                    'experienced' if completed_orders >= 20 else \
                                    'moderate' if completed_orders >= 10 else \
                                    'beginner' if completed_orders >= 5 else 'new'
        
        # Check response time (15 points)
        avg_response_time = supplier_details.get('average_response_time', 48)
        if avg_response_time <= 6:
            score += 15
        elif avg_response_time <= 12:
            score += 12
        elif avg_response_time <= 24:
            score += 8
        elif avg_response_time <= 48:
            score += 5
        
        details['response_time'] = avg_response_time
        details['response_category'] = 'excellent' if avg_response_time <= 6 else \
                                     'good' if avg_response_time <= 12 else \
                                     'average' if avg_response_time <= 24 else \
                                     'slow' if avg_response_time <= 48 else 'very_slow'
        
        # Check profile completeness (10 points)
        completeness_score = self._calculate_profile_completeness(supplier_details)
        score += int(completeness_score * 10)
        details['profile_completeness'] = completeness_score * 100
        
        return {
            "credibility_score": min(100, score),
            "details": details
        }
        
    async def _verify_offer_validity(self, offer_details: Dict[str, Any], rfq_details: Dict[str, Any]) -> Dict[str, Any]:
        """Verify offer validity and completeness"""
        validity_check = {
            "valid": True,
            "completeness_score": 0,
            "missing_fields": [],
            "issues": []
        }
        
        # Check required fields
        required_fields = ['price', 'delivery_time']
        total_fields = len(required_fields) + 3  # + currency, payment_terms, notes
        
        completed_fields = 0
        
        for field in required_fields:
            if offer_details.get(field):
                completed_fields += 1
            else:
                validity_check["missing_fields"].append(field)
                validity_check["issues"].append(f"Missing {field}")
        
        # Check optional but important fields
        if offer_details.get('currency'):
            completed_fields += 1
        if offer_details.get('payment_terms'):
            completed_fields += 1
        if offer_details.get('notes'):
            completed_fields += 1
        
        validity_check["completeness_score"] = (completed_fields / total_fields) * 100
        
        # Check price validity
        price = offer_details.get('price')
        if price:
            if price <= 0:
                validity_check["valid"] = False
                validity_check["issues"].append("Invalid price (non-positive)")
            
            # Check against budget if specified
            budget_max = rfq_details.get('budget_max')
            if budget_max and price > budget_max * 1.5:  # Allow 50% over budget
                validity_check["issues"].append("Price significantly over budget")
        
        # Check delivery time
        delivery_time = offer_details.get('delivery_time')
        if delivery_time:
            if delivery_time <= 0:
                validity_check["valid"] = False
                validity_check["issues"].append("Invalid delivery time")
            
            deadline = rfq_details.get('deadline_date')
            if deadline:
                # Check if delivery time is feasible given RFQ deadline
                deadline_date = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
                required_delivery = datetime.now() + timedelta(days=delivery_time)
                
                if required_delivery > deadline_date:
                    validity_check["issues"].append("Delivery time exceeds RFQ deadline")
        
        # Check valid until date
        valid_until = offer_details.get('valid_until')
        if valid_until:
            try:
                valid_date = datetime.fromisoformat(valid_until) if isinstance(valid_until, str) else valid_until
                if valid_date <= datetime.now():
                    validity_check["valid"] = False
                    validity_check["issues"].append("Offer has expired")
            except:
                validity_check["issues"].append("Invalid valid_until date format")
        
        return validity_check
        
    async def _analyze_offer_pricing(self, offer_details: Dict[str, Any], rfq_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze offer pricing for reasonableness"""
        pricing_analysis = {
            "reasonable": True,
            "price_category": "market_rate",
            "comparison": {},
            "flags": []
        }
        
        price = offer_details.get('price')
        if not price:
            return {"reasonable": False, "flags": ["no_price"]}
        
        # Get budget constraints
        budget_min = rfq_details.get('budget_min')
        budget_max = rfq_details.get('budget_max')
        
        # Compare against budget
        if budget_max:
            if price <= budget_max * 0.7:
                pricing_analysis["price_category"] = "competitive"
            elif price <= budget_max:
                pricing_analysis["price_category"] = "market_rate"
            elif price <= budget_max * 1.2:
                pricing_analysis["price_category"] = "premium"
                pricing_analysis["flags"].append("above_budget")
            else:
                pricing_analysis["price_category"] = "overpriced"
                pricing_analysis["reasonable"] = False
                pricing_analysis["flags"].append("significantly_overpriced")
        
        if budget_min and price < budget_min * 0.8:
            pricing_analysis["flags"].append("suspiciously_low")
            pricing_analysis["reasonable"] = False
        
        # Get market comparison (simulate with other offers for same RFQ)
        market_comparison = await self._get_market_price_comparison(rfq_details.get('id'), price)
        pricing_analysis["comparison"] = market_comparison
        
        return pricing_analysis
        
    async def _verify_delivery_feasibility(self, offer_details: Dict[str, Any], supplier_details: Dict[str, Any]) -> Dict[str, Any]:
        """Verify delivery feasibility"""
        delivery_check = {
            "feasible": True,
            "confidence": "high",
            "factors": {}
        }
        
        delivery_time = offer_details.get('delivery_time')
        if not delivery_time:
            return {"feasible": False, "confidence": "low", "factors": {"missing_delivery_time": True}}
        
        # Check against supplier's historical delivery performance
        avg_delivery = supplier_details.get('average_delivery_time', delivery_time)
        
        if delivery_time < avg_delivery * 0.7:
            delivery_check["confidence"] = "low"
            delivery_check["factors"]["optimistic_timeline"] = True
        elif delivery_time < avg_delivery * 0.9:
            delivery_check["confidence"] = "medium"
            delivery_check["factors"]["tight_timeline"] = True
        
        # Check supplier capacity
        active_orders = supplier_details.get('active_orders_count', 0)
        if active_orders > 10:
            delivery_check["confidence"] = "medium"
            delivery_check["factors"]["high_workload"] = True
        
        return delivery_check
        
    async def _check_supplier_performance(self, supplier_details: Dict[str, Any]) -> Dict[str, Any]:
        """Check supplier historical performance"""
        performance_check = {
            "score": 50,  # Default score
            "metrics": {},
            "trends": []
        }
        
        # Calculate performance metrics
        rating = float(supplier_details.get('rating', 3.0))
        completed_orders = supplier_details.get('total_completed_orders', 0)
        response_time = supplier_details.get('average_response_time', 48)
        
        # Performance score calculation
        score = 0
        
        # Rating contribution (40%)
        score += (rating / 5.0) * 40
        
        # Experience contribution (30%)
        if completed_orders >= 100:
            score += 30
        elif completed_orders >= 50:
            score += 25
        elif completed_orders >= 20:
            score += 20
        elif completed_orders >= 10:
            score += 15
        elif completed_orders >= 5:
            score += 10
        
        # Response time contribution (30%)
        if response_time <= 6:
            score += 30
        elif response_time <= 12:
            score += 25
        elif response_time <= 24:
            score += 20
        elif response_time <= 48:
            score += 15
        else:
            score += 5
        
        performance_check["score"] = min(100, score)
        performance_check["metrics"] = {
            "rating": rating,
            "completed_orders": completed_orders,
            "response_time": response_time,
            "reliability": "high" if score >= 80 else "medium" if score >= 60 else "low"
        }
        
        return performance_check
        
    def _calculate_profile_completeness(self, supplier_details: Dict[str, Any]) -> float:
        """Calculate supplier profile completeness percentage"""
        required_fields = [
            'company_name', 'email', 'phone', 'specializations', 
            'industry', 'website', 'description'
        ]
        
        completed = sum(1 for field in required_fields if supplier_details.get(field))
        return completed / len(required_fields)
        
    def _calculate_overall_score(self, supplier_score: Dict[str, Any], offer_validity: Dict[str, Any],
                                price_analysis: Dict[str, Any], delivery_check: Dict[str, Any],
                                performance_check: Dict[str, Any]) -> int:
        """Calculate overall verification score"""
        
        # Weighted scoring
        weights = {
            'supplier': 0.30,
            'offer_validity': 0.25,
            'pricing': 0.25,
            'delivery': 0.10,
            'performance': 0.10
        }
        
        # Individual scores
        supplier_score_val = supplier_score.get('credibility_score', 0)
        validity_score = offer_validity.get('completeness_score', 0) if offer_validity.get('valid') else 0
        pricing_score = 80 if price_analysis.get('reasonable') else 40
        delivery_score = 80 if delivery_check.get('feasible') and delivery_check.get('confidence') == 'high' else 60
        performance_score = performance_check.get('score', 50)
        
        # Calculate weighted average
        overall_score = (
            supplier_score_val * weights['supplier'] +
            validity_score * weights['offer_validity'] +
            pricing_score * weights['pricing'] +
            delivery_score * weights['delivery'] +
            performance_score * weights['performance']
        )
        
        return int(overall_score)
        
    def _generate_verification_flags(self, supplier_score: Dict[str, Any], offer_validity: Dict[str, Any],
                                   price_analysis: Dict[str, Any], delivery_check: Dict[str, Any]) -> List[str]:
        """Generate verification flags based on checks"""
        flags = []
        
        # Supplier flags
        if supplier_score.get('credibility_score', 0) < 60:
            flags.append('low_supplier_credibility')
        
        # Offer validity flags
        if not offer_validity.get('valid'):
            flags.append('invalid_offer')
        if offer_validity.get('completeness_score', 0) < 70:
            flags.append('incomplete_offer')
        
        # Pricing flags
        if not price_analysis.get('reasonable'):
            flags.append('unreasonable_pricing')
        if 'significantly_overpriced' in price_analysis.get('flags', []):
            flags.append('overpriced')
        if 'suspiciously_low' in price_analysis.get('flags', []):
            flags.append('suspiciously_low_price')
        
        # Delivery flags
        if not delivery_check.get('feasible'):
            flags.append('delivery_not_feasible')
        if delivery_check.get('confidence') == 'low':
            flags.append('delivery_uncertainty')
        
        return flags
        
    def _generate_recommendations(self, flags: List[str], overall_score: int) -> List[str]:
        """Generate recommendations based on verification results"""
        recommendations = []
        
        if overall_score >= 80:
            recommendations.append('Highly recommended supplier')
        elif overall_score >= 60:
            recommendations.append('Acceptable supplier with minor concerns')
        else:
            recommendations.append('Not recommended without further verification')
        
        if 'low_supplier_credibility' in flags:
            recommendations.append('Request additional supplier credentials')
        
        if 'incomplete_offer' in flags:
            recommendations.append('Request complete offer details')
        
        if 'overpriced' in flags:
            recommendations.append('Consider negotiating price')
        
        if 'suspiciously_low_price' in flags:
            recommendations.append('Verify quality and authenticity')
        
        if 'delivery_uncertainty' in flags:
            recommendations.append('Confirm delivery timeline and capacity')
        
        return recommendations
        
    async def _get_offer_details(self, offer_id: str) -> Optional[Dict[str, Any]]:
        """Get offer details from database"""
        db_pool = get_db_pool()
        if not db_pool:
            return None
            
        try:
            async with db_pool.acquire() as connection:
                row = await connection.fetchrow(
                    "SELECT * FROM offers WHERE id = $1", offer_id
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting offer details: {e}")
            return None
            
    async def _get_supplier_details(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Get supplier details from database"""
        db_pool = get_db_pool()
        if not db_pool:
            return None
            
        try:
            async with db_pool.acquire() as connection:
                row = await connection.fetchrow(
                    """
                    SELECT s.*, c.name as company_name, c.email, c.phone, 
                           c.website, c.industry
                    FROM suppliers s
                    JOIN companies c ON s.company_id = c.id
                    WHERE s.id = $1
                    """, supplier_id
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting supplier details: {e}")
            return None
            
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
            
    async def _get_pending_offers(self, rfq_id: str) -> List[Dict[str, Any]]:
        """Get pending offers for verification"""
        db_pool = get_db_pool()
        if not db_pool:
            return []
            
        try:
            async with db_pool.acquire() as connection:
                rows = await connection.fetch(
                    "SELECT * FROM offers WHERE rfq_id = $1 AND status = 'pending'", 
                    rfq_id
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting pending offers: {e}")
            return []
            
    async def _get_market_price_comparison(self, rfq_id: str, current_price: float) -> Dict[str, Any]:
        """Get market price comparison for similar offers"""
        db_pool = get_db_pool()
        if not db_pool:
            return {"comparison": "unavailable"}
            
        try:
            async with db_pool.acquire() as connection:
                # Get other offers for the same RFQ
                rows = await connection.fetch(
                    """
                    SELECT price FROM offers 
                    WHERE rfq_id = $1 AND price IS NOT NULL 
                    AND id != (SELECT id FROM offers WHERE rfq_id = $1 AND price = $2 LIMIT 1)
                    """, 
                    rfq_id, current_price
                )
                
                if not rows:
                    return {"comparison": "no_other_offers"}
                
                prices = [float(row['price']) for row in rows]
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                # Determine position
                if current_price <= min_price:
                    position = "lowest"
                elif current_price >= max_price:
                    position = "highest"
                elif current_price <= avg_price:
                    position = "below_average"
                else:
                    position = "above_average"
                
                return {
                    "comparison": "available",
                    "position": position,
                    "avg_price": avg_price,
                    "min_price": min_price,
                    "max_price": max_price,
                    "total_offers": len(prices) + 1
                }
                
        except Exception as e:
            logger.error(f"Error getting market price comparison: {e}")
            return {"comparison": "error"}
            
    async def _update_offer_verification(self, offer_id: str, verification_result: Dict[str, Any]):
        """Update offer with verification results"""
        db_pool = get_db_pool()
        if not db_pool:
            return
            
        try:
            async with db_pool.acquire() as connection:
                await connection.execute(
                    """
                    UPDATE offers 
                    SET 
                        verification_status = $2,
                        credibility_score = $3,
                        verification_details = $4,
                        verified_at = CASE WHEN $2 = 'verified' THEN NOW() ELSE NULL END,
                        updated_at = NOW()
                    WHERE id = $1
                    """,
                    offer_id,
                    'verified' if verification_result['verified'] else 'failed',
                    verification_result['credibility_score'],
                    json.dumps(verification_result)
                )
                
                logger.info(f"Updated offer {offer_id} verification status")
                
        except Exception as e:
            logger.error(f"Error updating offer verification: {e}")
            
    async def _update_supplier_verification(self, supplier_id: str, verification_result: Dict[str, Any]):
        """Update supplier with verification results"""
        db_pool = get_db_pool()
        if not db_pool:
            return
            
        try:
            async with db_pool.acquire() as connection:
                await connection.execute(
                    """
                    UPDATE suppliers 
                    SET 
                        credibility_score = $2,
                        last_verified_at = NOW(),
                        updated_at = NOW()
                    WHERE id = $1
                    """,
                    supplier_id,
                    verification_result['credibility_score']
                )
                
                logger.info(f"Updated supplier {supplier_id} verification")
                
        except Exception as e:
            logger.error(f"Error updating supplier verification: {e}")
            
    async def _trigger_aggregation_update(self, rfq_id: str):
        """Trigger aggregation agent to update reports"""
        try:
            await self.queue_task('aggregation_report_agent', {
                'action': 'update_rfq_report',
                'rfq_id': rfq_id
            })
            
            logger.info(f"Triggered aggregation update for RFQ {rfq_id}")
            
        except Exception as e:
            logger.error(f"Error triggering aggregation update: {e}")