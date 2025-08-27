from fastapi import APIRouter, Depends, HTTPException, status
from uuid import uuid4
import json

from app.core.auth import get_current_user_profile
from app.core.database import get_db
from app.core.redis_client import RedisService, get_redis
from app.models.common import APIResponse, Job, JobCreate, JobStatus
from supabase import Client
from loguru import logger


router = APIRouter()


@router.post("/orchestrate", response_model=APIResponse[Job])
async def orchestrate_workflow(
    job_data: JobCreate,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    """Agent workflow'unu başlat"""
    try:
        job_id = str(uuid4())
        job_payload = {
            "id": job_id,
            "job_type": job_data.job_type,
            "status": JobStatus.PENDING.value,
            "data": job_data.data,
            "priority": job_data.priority,
            "user_id": current_user["id"],
            "company_id": current_user["company_id"],
            "created_at": "now()",
        }
        success = await RedisService.enqueue_task("agent_jobs", job_payload)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Job kuyruğa eklenemedi",
            )
        await RedisService.set_json(f"job:{job_id}", job_payload, expire=3600)
        job_response = Job(
            id=job_id,
            job_type=job_data.job_type,
            status=JobStatus.PENDING,
            data=job_data.data,
            priority=job_data.priority,
            created_at=job_payload["created_at"],
        )
        logger.info(f"Job {job_id} orchestrated for user {current_user['id']}")
        return APIResponse(success=True, data=job_response, message=f"Workflow başlatıldı. Job ID: {job_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orchestration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Workflow başlatılırken hata oluştu")


@router.get("/status/{job_id}", response_model=APIResponse[Job])
async def get_job_status(
    job_id: str,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    """Job durumunu sorgula"""
    try:
        job_data = await RedisService.get_json(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job bulunamadı")
        if job_data.get("user_id") != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu job'u görme yetkiniz yok")
        job_response = Job(
            id=job_data["id"],
            job_type=job_data["job_type"],
            status=JobStatus(job_data["status"]),
            data=job_data.get("data", {}),
            result=job_data.get("result"),
            error=job_data.get("error"),
            priority=job_data.get("priority", 1),
            created_at=job_data["created_at"],
            updated_at=job_data.get("updated_at"),
            completed_at=job_data.get("completed_at"),
        )
        return APIResponse(success=True, data=job_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job status error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Job durumu sorgulanırken hata oluştu")


@router.post("/cancel/{job_id}", response_model=APIResponse[Job])
async def cancel_job(
    job_id: str,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    """Job'u iptal et"""
    try:
        job_data = await RedisService.get_json(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job bulunamadı")
        if job_data.get("user_id") != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu job'u iptal etme yetkiniz yok")
        current_status = job_data.get("status")
        if current_status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bu durumda ({current_status}) job iptal edilemez")
        job_data["status"] = JobStatus.CANCELLED.value
        job_data["updated_at"] = "now()"
        job_data["completed_at"] = "now()"
        await RedisService.set_json(f"job:{job_id}", job_data, expire=3600)
        cancel_signal = {"action": "cancel", "job_id": job_id, "cancelled_by": current_user["id"]}
        await RedisService.enqueue_task("agent_signals", cancel_signal)
        job_response = Job(
            id=job_data["id"],
            job_type=job_data["job_type"],
            status=JobStatus.CANCELLED,
            data=job_data.get("data", {}),
            result=job_data.get("result"),
            error=job_data.get("error"),
            priority=job_data.get("priority", 1),
            created_at=job_data["created_at"],
            updated_at=job_data.get("updated_at"),
            completed_at=job_data.get("completed_at"),
        )
        logger.info(f"Job {job_id} cancelled by user {current_user['id']}")
        return APIResponse(success=True, data=job_response, message="Job başarıyla iptal edildi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job cancellation error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Job iptal edilirken hata oluştu")


@router.get("/jobs", response_model=APIResponse[list])
async def get_user_jobs(
    current_user=Depends(get_current_user_profile),
    limit: int = 20,
    db: Client = Depends(get_db),
):
    """Kullanıcının job'larını Redis üzerinden basitçe listele"""
    try:
        r = get_redis()
        if r is None:
            return APIResponse(success=True, data=[], message="Redis bağlı değil")
        jobs = []
        async for key in r.scan_iter(match="job:*", count=100):
            raw = await r.get(key)
            if not raw:
                continue
            try:
                job = json.loads(raw)
            except Exception:
                continue
            if job.get("user_id") == current_user["id"]:
                jobs.append(job)
            if len(jobs) >= limit:
                break
        return APIResponse(success=True, data=jobs)
    except Exception as e:
        logger.error(f"Get user jobs error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Job listesi alınırken hata oluştu")


@router.post("/workflows/rfq-discovery", response_model=APIResponse[Job])
async def start_rfq_discovery_workflow(
    rfq_id: str,
    current_user=Depends(get_current_user_profile),
    db: Client = Depends(get_db),
):
    """RFQ keşif workflow'unu başlat"""
    try:
        rfq_check = db.table("rfqs").select("id", "company_id", "title", "status").eq("id", rfq_id).single().execute()
        if not rfq_check.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RFQ bulunamadı")
        if rfq_check.data["company_id"] != current_user["company_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu RFQ için workflow başlatma yetkiniz yok")
        workflow_data = JobCreate(
            job_type="rfq_discovery",
            data={
                "rfq_id": rfq_id,
                "rfq_title": rfq_check.data["title"],
                "user_id": current_user["id"],
                "company_id": current_user["company_id"],
            },
        )
        return await orchestrate_workflow(workflow_data, current_user, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RFQ workflow error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Workflow başlatılırken hata oluştu")

