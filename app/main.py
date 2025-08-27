from fastapi import FastAPI, HTTPException, Depends, Query, Path, BackgroundTasks, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
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
    RFQAnalytics, OfferComparison,
    CatalogCreate, CatalogUpdate, CatalogItem, CatalogListResponse,
)
from app.auth import get_current_user, get_current_user_optional, require_admin, require_permission
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
_env = os.getenv("ENVIRONMENT", "development").lower()
_origins_env = os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ALLOW_ORIGINS")
if _origins_env:
    _origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    _origins = ["*"] if _env != "production" else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if _origins else ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Orchestrator (simple) endpoints using Redis jobs
from pydantic import BaseModel

class OrchestrateRequest(BaseModel):
    job_type: str
    rfq_id: Optional[str] = None
    payload: Dict[str, Any] = {}

@app.delete("/orchestrate/{job_id}", response_model=BaseResponse, dependencies=[Depends(require_permission("workflow", "cancel"))])
async def orchestrate_cancel(job_id: str, current_user: dict = Depends(get_current_user)):
    try:
        st = redis_client.get_job_status(job_id)
        if not st:
            raise HTTPException(status_code=404, detail="Job not found")
        if st.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        cancelled = False
        try:
            cancelled = redis_client.cancel_job(job_id)
        except Exception as e:
            logger.warning(f"cancel_job failed: {e}")
        return BaseResponse(success=True, message="Job cancelled" if cancelled else "Job marked as failed", data={"job_id": job_id})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/orchestrate", response_model=BaseResponse, dependencies=[Depends(require_permission("workflow", "start"))])
async def orchestrate_job(req: OrchestrateRequest, current_user: dict = Depends(get_current_user)):
    try:
        job_payload = {"rfq_id": req.rfq_id, **(req.payload or {})}
        # RFQ sağlama ve payload'a ekleme (varsa)
        if req.rfq_id:
            rfq_resp = supabase.table("rfqs").select("*").eq("id", req.rfq_id).eq("requester_id", current_user["user_id"]).maybe_single().execute()
            if not rfq_resp.data:
                raise HTTPException(status_code=404, detail="RFQ not found")
            job_payload["rfq"] = rfq_resp.data
            # RFQ durumunu güncelle (best-effort)
            try:
                supabase.table("rfqs").update({
                    "status": "in_progress",
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", req.rfq_id).execute()
            except Exception as e:
                logger.warning(f"RFQ status update failed: {e}")
        job_id = redis_client.create_job(req.job_type, job_payload, current_user["user_id"])
        # record mapping for recent jobs
        try:
            redis_client.record_user_job(current_user["user_id"], job_id)
        except Exception as e:
            logger.warning(f"record_user_job failed: {e}")
        # persist job row (best-effort) in Supabase
        try:
            supabase.table("jobs").insert({
                "id": job_id,
                "user_id": current_user["user_id"],
                "company_id": current_user.get("metadata", {}).get("company_id"),
                "rfq_id": req.rfq_id,
                "job_type": req.job_type,
                "status": "queued",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.warning(f"persist job failed: {e}")
        return BaseResponse(success=True, message="Job enqueued", data={"job_id": job_id})
    except Exception as e:
        logger.error(f"Orchestrate failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orchestrate/status/{job_id}", response_model=BaseResponse, dependencies=[Depends(require_permission("workflow", "read"))])
async def orchestrate_status(job_id: str, current_user: dict = Depends(get_current_user)):
    try:
        st = redis_client.get_job_status(job_id)
        if not st:
            raise HTTPException(status_code=404, detail="Job not found")
        if st.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        # best-effort persist status update
        try:
            supabase.table("jobs").update({
                "status": st.get("status"),
                "updated_at": datetime.utcnow().isoformat(),
                "result": st.get("result"),
                "error": st.get("error"),
            }).eq("id", job_id).execute()
        except Exception as e:
            logger.warning(f"update job row failed: {e}")
        return BaseResponse(success=True, data={"job": st})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orchestrate/recent", response_model=BaseResponse, dependencies=[Depends(require_permission("workflow", "read"))])
async def orchestrate_recent(
    limit: int = Query(10, ge=1, le=50),
    job_type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    try:
        jobs = []
        try:
            jobs = redis_client.list_user_jobs(current_user["user_id"], limit=limit)
        except Exception as e:
            logger.warning(f"list_user_jobs failed: {e}")
        if job_type:
            jobs = [j for j in jobs if j.get("job_type") == job_type]
        return BaseResponse(success=True, data={"jobs": jobs})
    except Exception as e:
        logger.error(f"Recent jobs failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orchestrate/history", response_model=BaseResponse, dependencies=[Depends(require_permission("workflow", "read"))])
async def orchestrate_history(
    limit: int = Query(20, ge=1, le=100),
    job_type: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """List persisted jobs from Supabase (if available)."""
    try:
        rows = []
        try:
            query = supabase.table("jobs").select("*").eq("user_id", current_user["user_id"]).order("updated_at", desc=True).limit(limit)
            if job_type:
                query = query.eq("job_type", job_type)
            resp = query.execute()
            rows = resp.data or []
        except Exception as e:
            logger.warning(f"history fetch failed: {e}")
        return BaseResponse(success=True, data={"jobs": rows})
    except Exception as e:
        logger.error(f"History failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orchestrate/queues", response_model=BaseResponse, dependencies=[Depends(require_permission("workflow", "read"))])
async def orchestrate_queues(current_user: dict = Depends(get_current_user)):
    """Return snapshot of orchestrator queues to aid visibility and debugging."""
    try:
        snapshot = {"main": 0, "agents": {}}
        r = getattr(redis_client, 'redis', None)
        if r is not None and hasattr(r, 'llen'):
            snapshot["main"] = r.llen('agentik:jobs')
            for q in [
                'rfq_intake', 'supplier_discovery', 'email_send',
                'inbox_parser', 'supplier_verifier', 'aggregation_report'
            ]:
                try:
                    snapshot["agents"][q] = r.llen(f'agentik:agent:{q}')
                except Exception:
                    snapshot["agents"][q] = None
        return BaseResponse(success=True, data=snapshot)
    except Exception as e:
        logger.error(f"Queue snapshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orchestrate/heartbeat", response_model=BaseResponse, dependencies=[Depends(require_permission("workflow", "read"))])
async def orchestrate_heartbeat(current_user: dict = Depends(get_current_user)):
    """Return last heartbeat published by the agent orchestrator (if any)."""
    try:
        hb = None
        try:
            r = getattr(redis_client, 'redis', None)
            if r is not None and hasattr(r, 'get'):
                raw = r.get('agentik:heartbeat')
                if raw:
                    hb = json.loads(raw) if isinstance(raw, str) else raw
        except Exception as e:
            logger.warning(f"read heartbeat failed: {e}")
        return BaseResponse(success=True, data={"heartbeat": hb, "available": hb is not None})
    except Exception as e:
        logger.error(f"Heartbeat read failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """System health check"""
    timestamp = datetime.utcnow()
    
    # Check Supabase
    supabase_health = await supabase_client.health_check()
    
    # Check Redis + queue metrics (best-effort)
    redis_health = redis_client.health_check()
    try:
        # Try to read main queue length and agent queues
        r = getattr(redis_client, 'redis', None)
        if r is not None and hasattr(r, 'llen'):
            q_main = r.llen('agentik:jobs')
            queues = {
                'main': q_main,
            }
            for q in [
                'rfq_intake', 'supplier_discovery', 'email_send',
                'inbox_parser', 'supplier_verifier', 'aggregation_report'
            ]:
                try:
                    queues[q] = r.llen(f'agentik:agent:{q}')
                except Exception:
                    pass
            if isinstance(redis_health, dict):
                redis_health["queues"] = queues
    except Exception as e:
        logger.warning(f"queue metrics failed: {e}")
    
    # Orchestrator heartbeat (best-effort)
    orchestrator_health = {"status": "unknown"}
    try:
        r = getattr(redis_client, 'redis', None)
        if r is not None and hasattr(r, 'get'):
            raw = r.get('agentik:heartbeat')
            if raw:
                hb = json.loads(raw) if isinstance(raw, str) else raw
                orchestrator_health = {"status": "healthy", "last_seen": hb.get("ts"), "queues": hb.get("queues")}
            else:
                orchestrator_health = {"status": "unavailable"}
    except Exception as e:
        logger.warning(f"orchestrator heartbeat read failed: {e}")
        orchestrator_health = {"status": "unavailable"}

    # Overall status
    overall_status = "healthy" if all([
        supabase_health["status"] == "healthy",
        redis_health["status"] == "healthy"
    ]) else "unhealthy"
    
    # Optional: jobs metrics (best-effort)
    jobs_metrics = {}
    try:
        resp = supabase.table("jobs").select("*").limit(200).execute()
        rows = resp.data or []
        total = len(rows)
        def c(st):
            return sum(1 for r in rows if (r.get("status") or "").lower() == st)
        jobs_metrics = {
            "total": total,
            "queued": c("queued"),
            "in_progress": c("in_progress"),
            "completed": c("completed"),
            "failed": c("failed"),
        }
    except Exception as e:
        logger.warning(f"jobs metrics failed: {e}")

    return HealthCheckResponse(
        status=overall_status,
        timestamp=timestamp,
        services={
            "supabase": supabase_health,
            "redis": redis_health,
            "api": {"status": "healthy", "version": "1.0.0"},
            "orchestrator": orchestrator_health,
            "jobs": jobs_metrics,
        }
    )

# Basic API info (used by smoke script)
@app.get("/api/v1/info", response_model=BaseResponse)
async def api_info():
    try:
        data = {
            "name": "Agentik B2B API",
            "version": "1.0.0",
            "environment": _env,
            "docs_url": app.docs_url,
            "redoc_url": app.redoc_url,
        }
        return BaseResponse(success=True, data=data)
    except Exception as e:
        logger.warning(f"api_info failed: {e}")
        return BaseResponse(success=True, data={"name": "Agentik B2B API"})

# Role Management Endpoints
@app.get("/roles", response_model=BaseResponse, dependencies=[Depends(require_admin)])
async def list_roles(current_user: dict = Depends(get_current_user)):
    """List all available roles"""
    try:
        response = supabase.table("user_roles").select("*").execute()
        roles = [UserRoleModel(**role) for role in response.data] if response.data else []
        return BaseResponse(success=True, data={"roles": roles})
    except Exception as e:
        logger.error(f"Failed to fetch roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/roles", response_model=BaseResponse, dependencies=[Depends(require_admin)])
async def create_role(role: UserRoleModel, current_user: dict = Depends(get_current_user)):
    """Create a new role"""
    try:
        role_data = role.dict(exclude_unset=True)
        role_data["created_at"] = datetime.utcnow().isoformat()
        role_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("user_roles").insert(role_data).execute()
        created_role = UserRoleModel(**response.data[0]) if response.data else None
        
        return BaseResponse(success=True, message="Role created successfully", data={"role": created_role})
    except Exception as e:
        logger.error(f"Failed to create role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/roles/{role_id}", response_model=BaseResponse, dependencies=[Depends(require_admin)])
async def update_role(role_id: str, role: UserRoleModel, current_user: dict = Depends(get_current_user)):
    """Update an existing role"""
    try:
        role_data = role.dict(exclude_unset=True)
        role_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("user_roles").update(role_data).eq("id", role_id).execute()
        updated_role = UserRoleModel(**response.data[0]) if response.data else None
        
        return BaseResponse(success=True, message="Role updated successfully", data={"role": updated_role})
    except Exception as e:
        logger.error(f"Failed to update role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/roles/{role_id}", response_model=BaseResponse, dependencies=[Depends(require_admin)])
async def delete_role(role_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a role"""
    try:
        supabase.table("user_roles").delete().eq("id", role_id).execute()
        return BaseResponse(success=True, message="Role deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/{user_id}/roles", response_model=BaseResponse, dependencies=[Depends(require_admin)])
async def assign_role_to_user(user_id: str, role_id: str, current_user: dict = Depends(get_current_user)):
    """Assign a role to a user"""
    try:
        # Check if user exists
        user_response = supabase.table("users").select("*").eq("id", user_id).maybe_single().execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if role exists
        role_response = supabase.table("user_roles").select("*").eq("id", role_id).maybe_single().execute()
        if not role_response.data:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Create role assignment
        assignment_data = {
            "user_id": user_id,
            "role_id": role_id,
            "assigned_by": current_user["user_id"],
            "assigned_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        response = supabase.table("role_assignments").insert(assignment_data).execute()
        assignment = RoleAssignment(**response.data[0]) if response.data else None
        
        # Update user's role in users table
        supabase.table("users").update({"role": role_response.data["name"]}).eq("id", user_id).execute()
        
        return BaseResponse(success=True, message="Role assigned successfully", data={"assignment": assignment})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}/roles/{role_id}", response_model=BaseResponse, dependencies=[Depends(require_admin)])
async def remove_role_from_user(user_id: str, role_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a role from a user"""
    try:
        # Check if user exists
        user_response = supabase.table("users").select("*").eq("id", user_id).maybe_single().execute()
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Deactivate role assignment
        supabase.table("role_assignments").update({
            "is_active": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", user_id).eq("role_id", role_id).execute()
        
        # Reset user's role to default
        supabase.table("users").update({"role": "user"}).eq("id", user_id).execute()
        
        return BaseResponse(success=True, message="Role removed successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove role: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/roles", response_model=BaseResponse)
async def get_user_roles(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get roles assigned to a user"""
    try:
        # Check if requesting user has permission to view this user's roles
        if current_user["user_id"] != user_id and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get active role assignments for the user
        response = supabase.table("role_assignments").select("*").eq("user_id", user_id).eq("is_active", True).execute()
        assignments = [RoleAssignment(**assignment) for assignment in response.data] if response.data else []
        
        # Get role details
        roles = []
        for assignment in assignments:
            role_response = supabase.table("user_roles").select("*").eq("id", assignment.role_id).maybe_single().execute()
            if role_response.data:
                roles.append(UserRoleModel(**role_response.data))
        
        return BaseResponse(success=True, data={"roles": roles, "assignments": assignments})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch user roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# RFQ Endpoints
@app.post("/rfqs", response_model=BaseResponse, dependencies=[Depends(require_permission("rfq", "create"))])
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

@app.get("/rfqs", response_model=RFQListResponse, dependencies=[Depends(require_permission("rfq", "read"))])
async def list_rfqs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_dir: Optional[str] = Query("desc"),
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
        
        # Sorting (allowlist)
        sort_field = (sort_by or "created_at").lower()
        allowed = {"created_at", "updated_at", "deadline_date"}
        if sort_field not in allowed:
            sort_field = "created_at"
        descending = (sort_dir or "desc").lower() != "asc"
        
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
        response = query.order(sort_field, desc=descending).range(offset, offset + per_page - 1).execute()
        
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
@app.get("/rfqs/{rfq_id}", response_model=BaseResponse, dependencies=[Depends(require_permission("rfq", "read"))])
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

@app.put("/rfqs/{rfq_id}", response_model=BaseResponse, dependencies=[Depends(require_permission("rfq", "update"))])
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

@app.delete("/rfqs/{rfq_id}", response_model=BaseResponse, dependencies=[Depends(require_permission("rfq", "delete"))])
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

# Catalog Endpoints
@app.get("/catalog/mine", response_model=CatalogListResponse, dependencies=[Depends(require_permission("catalog", "read"))])
async def list_my_catalog(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Base query
        query = supabase.table("supplier_products").select("*", count="exact").eq("supplier_id", current_user["user_id"]).order("updated_at", desc=True)
        # Execute base to get rows and count
        resp = query.execute()
        rows = resp.data or []
        # Client-side filtering for search/category/currency
        if category:
            rows = [r for r in rows if (r.get("category") or "").lower() == category.lower()]
        if currency:
            rows = [r for r in rows if (r.get("currency") or "").upper() == currency.upper()]
        if search:
            s = search.lower()
            rows = [r for r in rows if s in (r.get("product_name") or "").lower()]
        total = len(rows)
        # Pagination
        start = (page - 1) * size
        paged = rows[start:start + size]
        items = [CatalogItem(**{
            "id": r.get("id"),
            "supplier_id": r.get("supplier_id") or current_user["user_id"],
            "product_name": r.get("product_name"),
            "category": r.get("category"),
            "price": r.get("price"),
            "currency": r.get("currency") or "USD",
            "created_at": datetime.fromisoformat(r.get("created_at")) if isinstance(r.get("created_at"), str) else r.get("created_at") or datetime.utcnow(),
            "updated_at": datetime.fromisoformat(r.get("updated_at")) if isinstance(r.get("updated_at"), str) else r.get("updated_at"),
        }) for r in paged]
        return CatalogListResponse(success=True, data=items, total=total)
    except Exception as e:
        logger.error(f"List my catalog failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/catalog/supplier/{supplier_id}", response_model=CatalogListResponse, dependencies=[Depends(require_permission("catalog", "read"))])
async def list_catalog_by_supplier(
    supplier_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    try:
        query = supabase.table("supplier_products").select("*", count="exact").eq("supplier_id", supplier_id).order("updated_at", desc=True)
        resp = query.execute()
        rows = resp.data or []
        if category:
            rows = [r for r in rows if (r.get("category") or "").lower() == category.lower()]
        if currency:
            rows = [r for r in rows if (r.get("currency") or "").upper() == currency.upper()]
        if search:
            s = search.lower()
            rows = [r for r in rows if s in (r.get("product_name") or "").lower()]
        total = len(rows)
        start = (page - 1) * size
        paged = rows[start:start + size]
        items = [CatalogItem(**{
            "id": r.get("id"),
            "supplier_id": r.get("supplier_id") or supplier_id,
            "product_name": r.get("product_name"),
            "category": r.get("category"),
            "price": r.get("price"),
            "currency": r.get("currency") or "USD",
            "created_at": datetime.fromisoformat(r.get("created_at")) if isinstance(r.get("created_at"), str) else r.get("created_at") or datetime.utcnow(),
            "updated_at": datetime.fromisoformat(r.get("updated_at")) if isinstance(r.get("updated_at"), str) else r.get("updated_at"),
        }) for r in paged]
        return CatalogListResponse(success=True, data=items, total=total)
    except Exception as e:
        logger.error(f"List supplier catalog failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/catalog", response_model=BaseResponse, dependencies=[Depends(require_permission("catalog", "create"))])
async def create_catalog_item(item: CatalogCreate, current_user: dict = Depends(get_current_user)):
    try:
        data = item.dict(exclude_unset=True)
        data["supplier_id"] = data.get("supplier_id") or current_user["user_id"]
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = datetime.utcnow().isoformat()
        resp = supabase.table("supplier_products").insert(data).execute()
        created = resp.data[0] if resp and resp.data else data
        return BaseResponse(success=True, message="Catalog item created", data={"item": created})
    except Exception as e:
        logger.error(f"Create catalog item failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/catalog/{item_id}", response_model=BaseResponse, dependencies=[Depends(require_permission("catalog", "update"))])
async def update_catalog_item(item_id: str, updates: CatalogUpdate, current_user: dict = Depends(get_current_user)):
    try:
        data = updates.dict(exclude_unset=True)
        if data:
            data["updated_at"] = datetime.utcnow().isoformat()
        resp = supabase.table("supplier_products").update(data).eq("id", item_id).execute()
        updated = resp.data[0] if resp and resp.data else None
        return BaseResponse(success=True, message="Catalog item updated" if updated else "No changes", data={"item": updated})
    except Exception as e:
        logger.error(f"Update catalog item failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/catalog/{item_id}", response_model=BaseResponse, dependencies=[Depends(require_permission("catalog", "delete"))])
async def delete_catalog_item(item_id: str, current_user: dict = Depends(get_current_user)):
    try:
        supabase.table("supplier_products").delete().eq("id", item_id).execute()
        return BaseResponse(success=True, message="Catalog item deleted")
    except Exception as e:
        logger.error(f"Delete catalog item failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utils
@app.post("/utils/upload", response_model=BaseResponse, dependencies=[Depends(require_permission("utils", "upload"))])
async def utils_upload(f: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        # Save under logs/uploads for convenience (mounted volume in Docker)
        import uuid, aiofiles
        base_dir = os.path.join("logs", "uploads")
        os.makedirs(base_dir, exist_ok=True)
        safe_name = f.filename or "file.bin"
        key = f"{uuid.uuid4()}_{safe_name}"
        path = os.path.join(base_dir, key)
        async with aiofiles.open(path, 'wb') as out:
            while True:
                chunk = await f.read(1024 * 1024)
                if not chunk:
                    break
                await out.write(chunk)
        # Return both legacy and UI-expected keys
        return BaseResponse(
            success=True,
            message="Uploaded",
            data={
                "path": path,
                "filename": safe_name,
                "file_path": path,
                "file_name": safe_name,
            },
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Verification (light)
@app.post("/verification/request", response_model=BaseResponse, dependencies=[Depends(require_permission("verification", "request"))])
async def verification_request(body: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_user)):
    try:
        docs = body.get("documents") or []
        notes = body.get("notes") or ""
        company_id = current_user.get("metadata", {}).get("company_id") or current_user["user_id"]
        row = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["user_id"],
            "company_id": company_id,
            "status": "pending",
            "documents": docs,
            "notes": notes,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        try:
            supabase.table("verification_requests").insert(row).execute()
        except Exception as e:
            logger.warning(f"persist verification request failed: {e}")
        return BaseResponse(success=True, message="Verification requested", data={"request": row})
    except Exception as e:
        logger.error(f"Verification request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verification/requests", response_model=BaseResponse, dependencies=[Depends(require_permission("verification", "read"))])
async def verification_requests(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100), current_user: dict = Depends(get_current_user)):
    try:
        items = []
        total = 0
        try:
            resp = supabase.table("verification_requests").select("*", count="exact").order("created_at", desc=True).execute()
            rows = resp.data or []
            # Only pending by default
            rows = [r for r in rows if (r.get("status") or "").lower() == "pending"]
            total = len(rows)
            start = (page - 1) * size
            rows = rows[start:start + size]
            for r in rows:
                items.append({
                    "id": r.get("id"),
                    "title": "Company verification requested",
                    "message": (r.get("notes") or "")[:140],
                    "data": {"company_id": r.get("company_id")},
                    "created_at": r.get("created_at"),
                })
        except Exception as e:
            logger.warning(f"fetch verification requests failed: {e}")
        return BaseResponse(success=True, data={"items": items, "total": total})
    except Exception as e:
        logger.error(f"Verification requests failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verification/approve", response_model=BaseResponse, dependencies=[Depends(require_permission("verification", "approve"))])
async def verification_approve(body: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_user)):
    try:
        company_id = body.get("company_id")
        if not company_id:
            raise HTTPException(status_code=400, detail="company_id required")
        try:
            supabase.table("verification_requests").update({
                "status": "approved",
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("company_id", company_id).execute()
        except Exception as e:
            logger.warning(f"approve verification persist failed: {e}")
        return BaseResponse(success=True, message="Verification approved", data={"company_id": company_id})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification approve failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verification/reject", response_model=BaseResponse, dependencies=[Depends(require_permission("verification", "reject"))])
async def verification_reject(body: Dict[str, Any] = Body(...), current_user: dict = Depends(get_current_user)):
    try:
        company_id = body.get("company_id")
        if not company_id:
            raise HTTPException(status_code=400, detail="company_id required")
        try:
            supabase.table("verification_requests").update({
                "status": "rejected",
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("company_id", company_id).execute()
        except Exception as e:
            logger.warning(f"reject verification persist failed: {e}")
        return BaseResponse(success=True, message="Verification rejected", data={"company_id": company_id})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification reject failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Supplier Endpoints
@app.get("/suppliers", response_model=SupplierListResponse, dependencies=[Depends(require_permission("supplier", "read"))])
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
@app.get("/offers", response_model=OfferListResponse, dependencies=[Depends(require_permission("offer", "read"))])
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

@app.get("/offers/by-rfq/{rfq_id}", response_model=BaseResponse, dependencies=[Depends(require_permission("offer", "read"))])
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

## Agent Orchestration
# Tek giriş noktaları: POST /orchestrate ve GET /orchestrate/status/{job_id}

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

@app.get("/analytics/jobs", response_model=BaseResponse)
async def get_jobs_analytics(
    days: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user)
):
    """Return timeseries of job status counts for the last N days and queue snapshot."""
    try:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        days_list = [(now - timedelta(days=i)).date().isoformat() for i in range(days-1, -1, -1)]
        series = {"queued": [0]*days, "in_progress": [0]*days, "completed": [0]*days, "failed": [0]*days}

        rows = []
        try:
            resp = supabase.table("jobs").select("*").execute()
            rows = resp.data or []
        except Exception as e:
            logger.warning(f"jobs analytics fetch failed: {e}")

        for r in rows:
            ts = r.get("updated_at") or r.get("created_at")
            st = (r.get("status") or "").lower()
            if not ts:
                continue
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                d = dt.date().isoformat()
                if d in days_list and st in series:
                    idx = days_list.index(d)
                    series[st][idx] += 1
            except Exception:
                continue

        queues = {}
        try:
            r = getattr(redis_client, 'redis', None)
            if r is not None and hasattr(r, 'llen'):
                queues["main"] = r.llen('agentik:jobs')
                for q in [
                    'rfq_intake', 'supplier_discovery', 'email_send',
                    'inbox_parser', 'supplier_verifier', 'aggregation_report'
                ]:
                    try:
                        queues[q] = r.llen(f'agentik:agent:{q}')
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"queue snapshot failed: {e}")

        return BaseResponse(success=True, data={
            "days": days_list,
            "series": series,
            "queues": queues,
        })
    except Exception as e:
        logger.error(f"Jobs analytics failed: {e}")
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
