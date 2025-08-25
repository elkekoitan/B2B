from core.base_agent import BaseAgent
from typing import Dict, Any, Optional, List
from loguru import logger
from core.database import get_db_pool
import json
from datetime import datetime, timedelta
import statistics
import pandas as pd
from io import BytesIO
import base64
from jinja2 import Template

class AggregationReportAgent(BaseAgent):
    """Agent responsible for aggregating data and generating reports"""
    
    def __init__(self):
        super().__init__(
            name="aggregation_report_agent",
            description="Aggregates system data and generates analytical reports and insights"
        )
        
    async def process_task(self, task_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process aggregation and reporting task"""
        try:
            logger.info(f"Processing aggregation task: {task_data}")
            
            task_type = task_data.get('action', 'generate_daily_report')
            
            if task_type == 'generate_daily_report':
                return await self._generate_daily_report(task_data)
            elif task_type == 'generate_rfq_analysis':
                return await self._generate_rfq_analysis(task_data)
            elif task_type == 'generate_supplier_report':
                return await self._generate_supplier_report(task_data)
            elif task_type == 'generate_performance_metrics':
                return await self._generate_performance_metrics(task_data)
            elif task_type == 'generate_market_insights':
                return await self._generate_market_insights(task_data)
            else:
                return {"error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Error in aggregation and reporting: {e}")
            return {"error": str(e)}
            
    async def _generate_daily_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily system performance report"""
        target_date = task_data.get('date', datetime.now().date())
        
        # Collect daily metrics
        metrics = await self._collect_daily_metrics(target_date)
        
        # Generate insights
        insights = await self._generate_daily_insights(metrics)
        
        # Create report
        report = {
            'date': str(target_date),
            'metrics': metrics,
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        }
        
        # Store report
        await self._store_report('daily_report', target_date, report)
        
        # Trigger notifications if needed
        await self._check_and_trigger_alerts(metrics)
        
        return {
            "success": True,
            "report_type": "daily_report",
            "date": str(target_date),
            "metrics_collected": len(metrics)
        }
        
    async def _generate_rfq_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RFQ performance analysis"""
        rfq_id = task_data.get('rfq_id')
        
        if not rfq_id:
            return {"error": "RFQ ID not provided"}
            
        # Get RFQ data
        rfq_data = await self._get_rfq_comprehensive_data(rfq_id)
        if not rfq_data:
            return {"error": "RFQ not found"}
            
        # Analyze offers
        offer_analysis = await self._analyze_rfq_offers(rfq_id)
        
        # Analyze supplier engagement
        engagement_analysis = await self._analyze_supplier_engagement(rfq_id)
        
        # Generate recommendations
        recommendations = await self._generate_rfq_recommendations(rfq_data, offer_analysis)
        
        report = {
            'rfq_id': rfq_id,
            'rfq_data': rfq_data,
            'offer_analysis': offer_analysis,
            'engagement_analysis': engagement_analysis,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
        
        # Store analysis
        await self._store_report('rfq_analysis', rfq_id, report)
        
        return {
            "success": True,
            "rfq_id": rfq_id,
            "total_offers": offer_analysis.get('total_offers', 0),
            "recommendations_count": len(recommendations)
        }
        
    async def _generate_supplier_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate supplier performance report"""
        supplier_id = task_data.get('supplier_id')
        period_days = task_data.get('period_days', 30)
        
        # Get supplier performance data
        performance_data = await self._get_supplier_performance(supplier_id, period_days)
        
        # Calculate metrics
        metrics = await self._calculate_supplier_metrics(performance_data)
        
        # Generate recommendations
        recommendations = await self._generate_supplier_recommendations(metrics)
        
        report = {
            'supplier_id': supplier_id,
            'period_days': period_days,
            'performance_data': performance_data,
            'metrics': metrics,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
        
        await self._store_report('supplier_report', supplier_id, report)
        
        return {
            "success": True,
            "supplier_id": supplier_id,
            "period_days": period_days,
            "performance_score": metrics.get('overall_score', 0)
        }
        
    async def _generate_performance_metrics(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate system performance metrics"""
        period_days = task_data.get('period_days', 7)
        
        # Collect system-wide metrics
        metrics = {
            'rfq_metrics': await self._get_rfq_metrics(period_days),
            'supplier_metrics': await self._get_supplier_metrics(period_days),
            'offer_metrics': await self._get_offer_metrics(period_days),
            'email_metrics': await self._get_email_metrics(period_days),
            'agent_metrics': await self._get_agent_metrics(period_days)
        }
        
        # Calculate KPIs
        kpis = await self._calculate_system_kpis(metrics)
        
        report = {
            'period_days': period_days,
            'metrics': metrics,
            'kpis': kpis,
            'generated_at': datetime.now().isoformat()
        }
        
        await self._store_report('performance_metrics', str(period_days), report)
        
        return {
            "success": True,
            "period_days": period_days,
            "kpis_calculated": len(kpis)
        }
        
    async def _collect_daily_metrics(self, date) -> Dict[str, Any]:
        """Collect daily system metrics"""
        db_pool = get_db_pool()
        if not db_pool:
            return {}
            
        try:
            async with db_pool.acquire() as connection:
                # RFQ metrics
                rfq_count = await connection.fetchval(
                    "SELECT COUNT(*) FROM rfqs WHERE DATE(created_at) = $1", date
                )
                
                published_rfqs = await connection.fetchval(
                    "SELECT COUNT(*) FROM rfqs WHERE DATE(created_at) = $1 AND status = 'published'", date
                )
                
                # Offer metrics
                offer_count = await connection.fetchval(
                    "SELECT COUNT(*) FROM offers WHERE DATE(created_at) = $1", date
                )
                
                # Email metrics
                emails_sent = await connection.fetchval(
                    "SELECT COUNT(*) FROM email_logs WHERE DATE(created_at) = $1 AND status = 'sent'", date
                )
                
                # Supplier metrics
                new_suppliers = await connection.fetchval(
                    "SELECT COUNT(*) FROM suppliers WHERE DATE(created_at) = $1", date
                )
                
                verified_suppliers = await connection.fetchval(
                    "SELECT COUNT(*) FROM suppliers WHERE DATE(verification_date) = $1", date
                )
                
                return {
                    'total_rfqs': rfq_count or 0,
                    'published_rfqs': published_rfqs or 0,
                    'total_offers': offer_count or 0,
                    'emails_sent': emails_sent or 0,
                    'new_suppliers': new_suppliers or 0,
                    'verified_suppliers': verified_suppliers or 0
                }
                
        except Exception as e:
            logger.error(f"Error collecting daily metrics: {e}")
            return {}
            
    async def _generate_daily_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate insights from daily metrics"""
        insights = []
        
        # RFQ insights
        total_rfqs = metrics.get('total_rfqs', 0)
        published_rfqs = metrics.get('published_rfqs', 0)
        
        if total_rfqs > 0:
            publish_rate = (published_rfqs / total_rfqs) * 100
            if publish_rate > 80:
                insights.append(f"Yüksek RFQ yayın oranı: %{publish_rate:.1f}")
            elif publish_rate < 50:
                insights.append(f"Düşük RFQ yayın oranı: %{publish_rate:.1f} - İnceleme gerekli")
                
        # Offer insights
        total_offers = metrics.get('total_offers', 0)
        if total_rfqs > 0 and total_offers > 0:
            offer_per_rfq = total_offers / total_rfqs
            if offer_per_rfq > 3:
                insights.append(f"Yüksek teklif alım oranı: RFQ başına {offer_per_rfq:.1f} teklif")
            elif offer_per_rfq < 1:
                insights.append("Düşük teklif alım oranı - Tedarikçi katılımını artırma stratejileri gerekli")
                
        # Supplier insights
        new_suppliers = metrics.get('new_suppliers', 0)
        verified_suppliers = metrics.get('verified_suppliers', 0)
        
        if new_suppliers > 5:
            insights.append(f"Yüksek tedarikçi kayıt sayısı: {new_suppliers} yeni kayıt")
            
        if verified_suppliers > 0:
            insights.append(f"{verified_suppliers} tedarikçi doğrulandı")
            
        return insights
        
    async def _analyze_rfq_offers(self, rfq_id: str) -> Dict[str, Any]:
        """Analyze offers for a specific RFQ"""
        db_pool = get_db_pool()
        if not db_pool:
            return {}
            
        try:
            async with db_pool.acquire() as connection:
                # Get all offers for the RFQ
                offers = await connection.fetch(
                    """
                    SELECT o.*, c.name as supplier_name, s.rating as supplier_rating
                    FROM offers o
                    JOIN suppliers s ON o.supplier_id = s.id
                    JOIN companies c ON s.company_id = c.id
                    WHERE o.rfq_id = $1
                    ORDER BY o.price ASC
                    """,
                    rfq_id
                )
                
                if not offers:
                    return {'total_offers': 0}
                    
                prices = [float(offer['price']) for offer in offers]
                ratings = [float(offer['supplier_rating']) for offer in offers if offer['supplier_rating']]
                
                analysis = {
                    'total_offers': len(offers),
                    'price_analysis': {
                        'min_price': min(prices),
                        'max_price': max(prices),
                        'avg_price': statistics.mean(prices),
                        'median_price': statistics.median(prices),
                        'price_range': max(prices) - min(prices)
                    }
                }
                
                if ratings:
                    analysis['supplier_quality'] = {
                        'avg_rating': statistics.mean(ratings),
                        'min_rating': min(ratings),
                        'max_rating': max(ratings)
                    }
                    
                # Best value analysis
                best_offers = []
                for offer in offers[:3]:  # Top 3 by price
                    score = self._calculate_offer_score(
                        float(offer['price']),
                        float(offer['supplier_rating'] or 0),
                        offer.get('delivery_time', 30)
                    )
                    best_offers.append({
                        'offer_id': offer['id'],
                        'supplier_name': offer['supplier_name'],
                        'price': float(offer['price']),
                        'rating': float(offer['supplier_rating'] or 0),
                        'score': score
                    })
                    
                analysis['best_offers'] = sorted(best_offers, key=lambda x: x['score'], reverse=True)
                
                return analysis
                
        except Exception as e:
            logger.error(f"Error analyzing RFQ offers: {e}")
            return {}
            
    def _calculate_offer_score(self, price: float, rating: float, delivery_time: int) -> float:
        """Calculate offer score based on price, supplier rating, and delivery time"""
        # Normalize factors (lower price is better, higher rating is better, shorter delivery is better)
        price_score = max(0, 100 - (price / 1000))  # Adjust based on your price ranges
        rating_score = (rating / 5.0) * 100
        delivery_score = max(0, 100 - delivery_time)
        
        # Weighted average
        total_score = (price_score * 0.4) + (rating_score * 0.4) + (delivery_score * 0.2)
        return round(total_score, 2)
        
    async def _generate_rfq_recommendations(self, rfq_data: Dict[str, Any], offer_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for RFQ management"""
        recommendations = []
        
        total_offers = offer_analysis.get('total_offers', 0)
        
        if total_offers == 0:
            recommendations.append("Hiç teklif alınmamış - RFQ kriterlerini genişletmeyi düşünün")
            recommendations.append("Daha fazla tedarikçiye davet göndermeyi deneyin")
        elif total_offers < 3:
            recommendations.append("Az sayıda teklif - Daha fazla tedarikçi araştırılabilir")
        elif total_offers > 10:
            recommendations.append("Yüksek ilgi - En iyi teklifleri değerlendirmeye odaklanın")
            
        # Price analysis recommendations
        price_analysis = offer_analysis.get('price_analysis', {})
        if price_analysis:
            price_range = price_analysis.get('price_range', 0)
            avg_price = price_analysis.get('avg_price', 0)
            
            if price_range > avg_price * 0.5:  # High price variance
                recommendations.append("Yüksek fiyat farklılığı - Detaylı karşılaştırma yapın")
                
        # Best offers recommendation
        best_offers = offer_analysis.get('best_offers', [])
        if best_offers:
            best_offer = best_offers[0]
            recommendations.append(f"En iyi teklif: {best_offer['supplier_name']} - Skor: {best_offer['score']}")
            
        return recommendations
        
    async def _store_report(self, report_type: str, identifier: str, report_data: Dict[str, Any]):
        """Store generated report in database"""
        db_pool = get_db_pool()
        if not db_pool:
            return
            
        try:
            async with db_pool.acquire() as connection:
                await connection.execute(
                    """
                    INSERT INTO system_reports 
                    (report_type, identifier, report_data, created_at)
                    VALUES ($1, $2, $3, NOW())
                    ON CONFLICT (report_type, identifier) 
                    DO UPDATE SET 
                        report_data = $3,
                        updated_at = NOW()
                    """,
                    report_type, identifier, json.dumps(report_data)
                )
        except Exception as e:
            logger.error(f"Error storing report: {e}")
            
    async def _check_and_trigger_alerts(self, metrics: Dict[str, Any]):
        """Check metrics and trigger alerts if thresholds are exceeded"""
        alerts = []
        
        # Check for low activity
        if metrics.get('total_rfqs', 0) == 0:
            alerts.append("Uyarı: Bugün hiç RFQ oluşturulmadı")
            
        # Check for email failures
        emails_sent = metrics.get('emails_sent', 0)
        if emails_sent == 0 and metrics.get('total_rfqs', 0) > 0:
            alerts.append("Uyarı: RFQ var ama e-posta gönderilmedi")
            
        # If there are alerts, trigger notifications
        if alerts:
            await self._trigger_system_alerts(alerts)
            
    async def _trigger_system_alerts(self, alerts: List[str]):
        """Trigger system alerts"""
        from core.redis_client import get_redis
        
        redis_client = get_redis()
        if not redis_client:
            return
            
        try:
            for alert in alerts:
                task_data = {
                    'action': 'send_system_alert',
                    'message': alert,
                    'priority': 'high'
                }
                
                await redis_client.lpush(
                    'agent_email_send_agent_queue',
                    json.dumps(task_data)
                )
                
        except Exception as e:
            logger.error(f"Error triggering system alerts: {e}")
            
    async def _get_rfq_comprehensive_data(self, rfq_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive RFQ data"""
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
            logger.error(f"Error getting RFQ data: {e}")
            return None