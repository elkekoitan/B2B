from fastapi import FastAPI, HTTPException, Depends, Query, Path, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
from loguru import logger

# Import local modules
from app.database import supabase, supabase_admin, supabase_client
from app.redis_client import redis_client
from app.models import (
    RFQ, RFQCreate, RFQUpdate, RFQListResponse,
    Supplier, SupplierCreate, SupplierListResponse,
    Offer, OfferCreate, OfferListResponse,
    JobCreate, JobResponse, JobStatus,
    BaseResponse, HealthCheckResponse,
    RFQAnalytics, OfferComparison
)
from app.auth import get_current_user, get_current_user_optional, require_admin
from app.services.supplier_discovery import SupplierDiscoveryService

# Configure logging
logger.add("logs/backend.log", rotation="1 day", retention="7 days", level="INFO")

# Create FastAPI app
app = FastAPI(
    title="Agentik B2B Tedarik API",
    description="AI-powered B2B supply chain management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize services
supplier_discovery = SupplierDiscoveryService()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """System health check"""
    timestamp = datetime.utcnow()
    
    # Check Supabase
    supabase_health = await supabase_client.health_check()
    
    # Check Redis
    redis_health = redis_client.health_check()
    
    # Overall status
    overall_status = "healthy" if all([
        supabase_health["status"] == "healthy",
        redis_health["status"] == "healthy"
    ]) else "unhealthy"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=timestamp,
        services={
            "supabase": supabase_health,
            "redis": redis_health,
            "api": {"status": "healthy", "version": "1.0.0"}
        }
    )

# RFQ Endpoints
@app.post("/rfqs", response_model=BaseResponse)
async def create_rfq(
    rfq: RFQCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new RFQ with automatic supplier discovery"""
    try:
        # Prepare RFQ data
        rfq_data = rfq.dict()
        rfq_data["requester_id"] = current_user["user_id"]
        
        # TODO: Set company_id from user's company or default to requester_id for now
        rfq_data["company_id"] = current_user.get("company_id", current_user["user_id"])
        
        # Convert deadline to date for database
        rfq_data["deadline_date"] = rfq_data.pop("deadline").date()
        
        rfq_data["status"] = "draft"
        rfq_data["created_at"] = datetime.utcnow().isoformat()
        rfq_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Convert requirements to JSON if string
        if rfq_data.get("requirements") and isinstance(rfq_data["requirements"], str):
            rfq_data["requirements"] = {"description": rfq_data["requirements"]}
        
        # Insert into database
        response = supabase.table("rfqs").insert(rfq_data).execute()
        
        if response.data:
            created_rfq = response.data[0]
            logger.info(f"Created RFQ {created_rfq['id']} for user {current_user['user_id']}")
            
            # 🚀 AUTOMATIC SUPPLIER DISCOVERY AND ANALYSIS
            logger.info(f"Starting supplier discovery for RFQ {created_rfq['id']}")
            supplier_analysis = await supplier_discovery.discover_suppliers(rfq_data)
            
            # Store supplier analysis in database or cache
            if supplier_analysis.get("success"):
                # Store analysis result
                analysis_data = {
                    "rfq_id": created_rfq["id"],
                    "analysis_result": supplier_analysis,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Store in mock database for now
                logger.info(f"Supplier analysis completed for RFQ {created_rfq['id']}: Found {len(supplier_analysis.get('suppliers', []))} suppliers")
            
            return BaseResponse(
                success=True,
                message="RFQ created successfully with supplier analysis",
                data={
                    "rfq": created_rfq,
                    "supplier_analysis": supplier_analysis
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to create RFQ")
            
    except Exception as e:
        logger.error(f"RFQ creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rfqs", response_model=RFQListResponse)
async def list_rfqs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """List user's RFQs with pagination and filtering"""
    try:
        # Base query
        query = supabase.table("rfqs").select("*").eq("requester_id", current_user["user_id"])
        
        # Apply filters
        if status:
            query = query.eq("status", status)
        if category:
            query = query.eq("category", category)
        
        # Get total count
        count_response = supabase.table("rfqs").select("id", count="exact").eq("requester_id", current_user["user_id"])
        if status:
            count_response = count_response.eq("status", status)
        if category:
            count_response = count_response.eq("category", category)
        
        count_result = count_response.execute()
        total = count_result.count if count_result.count else 0
        
        # Get paginated results
        offset = (page - 1) * per_page
        response = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        rfqs = [RFQ(**item) for item in response.data] if response.data else []
        
        return RFQListResponse(
            success=True,
            data=rfqs,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"RFQ listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rfqs/{rfq_id}/supplier-analysis", response_model=BaseResponse)
async def get_supplier_analysis(
    rfq_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """Get supplier analysis and comparison report for an RFQ"""
    try:
        # Get RFQ data
        rfq_response = supabase.table("rfqs").select("*").eq("id", rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
        
        if not rfq_response.data:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        rfq_data = rfq_response.data
        
        # Generate fresh supplier analysis
        logger.info(f"Generating supplier analysis for RFQ {rfq_id}")
        supplier_analysis = await supplier_discovery.discover_suppliers(rfq_data)
        
        return BaseResponse(
            success=True,
            message="Supplier analysis generated successfully",
            data={
                "rfq": rfq_data,
                "supplier_analysis": supplier_analysis
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supplier analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rfqs/{rfq_id}/comparison-report", response_model=BaseResponse)
async def get_comparison_report(
    rfq_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed comparison report for RFQ suppliers"""
    try:
        # Get RFQ data
        rfq_response = supabase.table("rfqs").select("*").eq("id", rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
        
        if not rfq_response.data:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        rfq_data = rfq_response.data
        
        # Get supplier analysis
        supplier_analysis = await supplier_discovery.discover_suppliers(rfq_data)
        
        if not supplier_analysis.get("success"):
            raise HTTPException(status_code=404, detail="No supplier analysis available")
        
        # Generate Excel-ready comparison data
        comparison_data = {
            "rfq_details": {
                "title": rfq_data.get("title"),
                "category": rfq_data.get("category"),
                "quantity": rfq_data.get("quantity"),
                "budget_range": f"${rfq_data.get('budget_min', 0):,} - ${rfq_data.get('budget_max', 0):,}",
                "deadline": rfq_data.get("deadline_date")
            },
            "suppliers_comparison": [],
            "summary_report": supplier_analysis.get("comparison_report"),
            "criteria": supplier_analysis.get("criteria")
        }
        
        # Format supplier data for Excel export
        for supplier in supplier_analysis.get("suppliers", []):
            products = supplier.get("products", {})
            first_product = list(products.values())[0] if products else {}
            
            supplier_row = {
                "Tedarikçi Adı": supplier.get("company_name"),
                "İlgili Kişi": supplier.get("contact_person"),
                "E-posta": supplier.get("email"),
                "Telefon": supplier.get("phone"),
                "Website": supplier.get("website"),
                "Ürün": first_product.get("name", "N/A"),
                "Fiyat USD/kg": first_product.get("price_usd_kg", 0),
                "MOQ": f"{first_product.get('moq_kg', 0)} kg",
                "Kalite Seviyesi": first_product.get("quality_grade"),
                "Belgeler": ", ".join(supplier.get("certifications", [])),
                "Teslim Süresi": f"{supplier.get('delivery_terms', {}).get('delivery_time_days', 0)} gün",
                "Ödeme Koşulları": supplier.get("delivery_terms", {}).get("payment_terms"),
                "Dubai Direkt": "Evet" if supplier.get("export_experience", {}).get("dubai_direct") else "Hayır",
                "İhracat Deneyimi": f"{supplier.get('export_experience', {}).get('years', 0)} yıl",
                "Teknik Destek": "Evet" if supplier.get("technical_support", {}).get("available") else "Hayır",
                "Genel Puan": supplier.get("overall_score"),
                "Eşleşme %": supplier.get("match_percentage"),
                "Güçlü Yönler": ", ".join(supplier_analysis.get("comparison_report", {}).get("best_supplier", {}).get("key_strengths", []) if supplier["company_name"] == supplier_analysis.get("comparison_report", {}).get("best_supplier", {}).get("name") else []),
                "Notlar": f"Kapasite: {supplier.get('export_experience', {}).get('monthly_capacity_tons', 0)} ton/ay"
            }
            
            comparison_data["suppliers_comparison"].append(supplier_row)
        
        return BaseResponse(
            success=True,
            message="Comparison report generated successfully",
            data=comparison_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
async def get_rfq(
    rfq_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """Get single RFQ details"""
    try:
        response = supabase.table("rfqs").select("*").eq("id", rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        rfq = RFQ(**response.data)
        
        # Get related offers
        offers_response = supabase.table("offers").select("*").eq("rfq_id", rfq_id).execute()
        offers = [Offer(**item) for item in offers_response.data] if offers_response.data else []
        
        return BaseResponse(
            success=True,
            data={
                "rfq": rfq,
                "offers": offers,
                "offers_count": len(offers)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/rfqs/{rfq_id}", response_model=BaseResponse)
async def update_rfq(
    rfq_id: str = Path(...),
    rfq_update: RFQUpdate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Update RFQ"""
    try:
        # Check if RFQ exists and belongs to user
        existing = supabase.table("rfqs").select("*").eq("id", rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        # Prepare update data
        update_data = rfq_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Update in database
            response = supabase.table("rfqs").update(update_data).eq("id", rfq_id).execute()
            
            if response.data:
                updated_rfq = response.data[0]
                logger.info(f"Updated RFQ {rfq_id} for user {current_user['user_id']}")
                
                return BaseResponse(
                    success=True,
                    message="RFQ updated successfully",
                    data={"rfq": updated_rfq}
                )
        
        return BaseResponse(
            success=True,
            message="No changes made"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/rfqs/{rfq_id}", response_model=BaseResponse)
async def delete_rfq(
    rfq_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """Delete RFQ"""
    try:
        # Check if RFQ exists and belongs to user
        existing = supabase.table("rfqs").select("*").eq("id", rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        # Delete RFQ (cascade will handle related records)
        supabase.table("rfqs").delete().eq("id", rfq_id).execute()
        
        logger.info(f"Deleted RFQ {rfq_id} for user {current_user['user_id']}")
        
        return BaseResponse(
            success=True,
            message="RFQ deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Supplier Endpoints
@app.get("/suppliers", response_model=SupplierListResponse)
async def list_suppliers(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None),
    verified_only: bool = Query(False),
    current_user: dict = Depends(get_current_user)
):
    """List suppliers with filtering"""
    try:
        # Base query
        query = supabase.table("suppliers").select("*")
        
        # Apply filters
        if category:
            query = query.contains("categories", [category])
        if verified_only:
            query = query.eq("verified", True)
        
        # Get total count
        count_response = supabase.table("suppliers").select("id", count="exact")
        if category:
            count_response = count_response.contains("categories", [category])
        if verified_only:
            count_response = count_response.eq("verified", True)
        
        count_result = count_response.execute()
        total = count_result.count if count_result.count else 0
        
        # Get paginated results
        offset = (page - 1) * per_page
        response = query.order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        suppliers = [Supplier(**item) for item in response.data] if response.data else []
        
        return SupplierListResponse(
            success=True,
            data=suppliers,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Supplier listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/suppliers", response_model=BaseResponse)
async def create_supplier(
    supplier: SupplierCreate,
    current_user: dict = Depends(require_admin)
):
    """Create new supplier (admin only)"""
    try:
        # Prepare supplier data
        supplier_data = supplier.dict()
        supplier_data["created_at"] = datetime.utcnow().isoformat()
        supplier_data["verified"] = False
        
        # Insert into database
        response = supabase_admin.table("suppliers").insert(supplier_data).execute()
        
        if response.data:
            created_supplier = response.data[0]
            logger.info(f"Created supplier {created_supplier['id']}")
            
            return BaseResponse(
                success=True,
                message="Supplier created successfully",
                data={"supplier": created_supplier}
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to create supplier")
            
    except Exception as e:
        logger.error(f"Supplier creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Offer Endpoints
@app.get("/offers", response_model=OfferListResponse)
async def list_offers(
    rfq_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """List offers for user's RFQs"""
    try:
        if rfq_id:
            # Check if RFQ belongs to user
            rfq_check = supabase.table("rfqs").select("id").eq("id", rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
            if not rfq_check.data:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Get offers for specific RFQ
            response = supabase.table("offers").select("*").eq("rfq_id", rfq_id).execute()
        else:
            # Get all offers for user's RFQs
            user_rfqs_response = supabase.table("rfqs").select("id").eq("requester_id", current_user["user_id"]).execute()
            rfq_ids = [rfq["id"] for rfq in user_rfqs_response.data] if user_rfqs_response.data else []
            
            if not rfq_ids:
                return OfferListResponse(success=True, data=[], total=0)
            
            response = supabase.table("offers").select("*").in_("rfq_id", rfq_ids).execute()
        
        offers = [Offer(**item) for item in response.data] if response.data else []
        
        return OfferListResponse(
            success=True,
            data=offers,
            total=len(offers)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Offer listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/offers/by-rfq/{rfq_id}", response_model=BaseResponse)
async def get_offers_by_rfq(
    rfq_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """Get offers for specific RFQ with comparison analysis"""
    try:
        # Check if RFQ belongs to user
        rfq_response = supabase.table("rfqs").select("*").eq("id", rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
        if not rfq_response.data:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        # Get offers
        offers_response = supabase.table("offers").select("*").eq("rfq_id", rfq_id).execute()
        offers = [Offer(**item) for item in offers_response.data] if offers_response.data else []
        
        # Perform basic analysis
        analysis = {}
        if offers:
            prices = [offer.total_price for offer in offers]
            delivery_times = [offer.delivery_time for offer in offers]
            
            analysis = {
                "total_offers": len(offers),
                "price_range": {"min": min(prices), "max": max(prices), "avg": sum(prices) / len(prices)},
                "delivery_time_range": {"min": min(delivery_times), "max": max(delivery_times), "avg": sum(delivery_times) / len(delivery_times)},
                "best_price_offer_id": min(offers, key=lambda x: x.total_price).id,
                "fastest_delivery_offer_id": min(offers, key=lambda x: x.delivery_time).id
            }
        
        return BaseResponse(
            success=True,
            data={
                "rfq": rfq_response.data,
                "offers": offers,
                "analysis": analysis
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Offers retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent Orchestration Endpoints
@app.post("/orchestrate", response_model=BaseResponse)
async def trigger_agent_workflow(
    job: JobCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Trigger agent workflow for RFQ processing"""
    try:
        # Verify RFQ belongs to user
        rfq_response = supabase.table("rfqs").select("*").eq("id", job.rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
        if not rfq_response.data:
            raise HTTPException(status_code=404, detail="RFQ not found")
        
        rfq = rfq_response.data
        
        # Create job in Redis queue
        job_payload = {
            "rfq": rfq,
            "user_id": current_user["user_id"],
            **job.payload
        }
        
        job_id = redis_client.create_job(
            job_type=job.job_type,
            payload=job_payload,
            user_id=current_user["user_id"]
        )
        
        # Update RFQ status
        supabase.table("rfqs").update({
            "status": "in_progress",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", job.rfq_id).execute()
        
        logger.info(f"Started agent workflow {job_id} for RFQ {job.rfq_id}")
        
        return BaseResponse(
            success=True,
            message="Agent workflow started successfully",
            data={
                "job_id": job_id,
                "status": "queued",
                "rfq_id": job.rfq_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """Get job status and results"""
    try:
        job_data = redis_client.get_job_status(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Verify job belongs to user
        if job_data["data"].get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus(job_data["status"]),
            created_at=datetime.fromisoformat(job_data["created_at"]),
            updated_at=datetime.fromisoformat(job_data["updated_at"]) if job_data["updated_at"] else None,
            result=job_data["result"],
            error=job_data["error"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints
@app.get("/analytics/rfqs", response_model=BaseResponse)
async def get_rfq_analytics(
    current_user: dict = Depends(get_current_user)
):
    """Get RFQ analytics for user"""
    try:
        user_id = current_user["user_id"]
        
        # Get RFQ statistics
        total_response = supabase.table("rfqs").select("id", count="exact").eq("requester_id", user_id).execute()
        active_response = supabase.table("rfqs").select("id", count="exact").eq("requester_id", user_id).in_("status", ["published", "in_progress"]).execute()
        completed_response = supabase.table("rfqs").select("id", count="exact").eq("requester_id", user_id).eq("status", "completed").execute()
        
        # Get category breakdown
        category_response = supabase.table("rfqs").select("category").eq("requester_id", user_id).execute()
        categories = {}
        for rfq in (category_response.data or []):
            cat = rfq.get("category", "Unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        
        analytics = RFQAnalytics(
            total_rfqs=total_response.count or 0,
            active_rfqs=active_response.count or 0,
            completed_rfqs=completed_response.count or 0,
            avg_response_time=None,  # Would need more complex query
            avg_offers_per_rfq=None,  # Would need more complex query
            top_categories=[{"category": cat, "count": count} for cat, count in top_categories]
        )
        
        return BaseResponse(
            success=True,
            data=analytics.dict()
        )
        
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Admin Endpoints
@app.get("/admin/rfqs", response_model=RFQListResponse)
async def admin_list_all_rfqs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_admin)
):
    """Admin: List all RFQs"""
    try:
        # Get total count
        count_response = supabase_admin.table("rfqs").select("id", count="exact").execute()
        total = count_response.count if count_response.count else 0
        
        # Get paginated results
        offset = (page - 1) * per_page
        response = supabase_admin.table("rfqs").select("*").order("created_at", desc=True).range(offset, offset + per_page - 1).execute()
        
        rfqs = [RFQ(**item) for item in response.data] if response.data else []
        
        return RFQListResponse(
            success=True,
            data=rfqs,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Admin RFQ listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
