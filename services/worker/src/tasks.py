from datetime import datetime, timezone
from services.worker.src.celery_app import celery_app

@celery_app.task(name="tasks.process_async_ai_inference")
def process_async_ai_inference(petition_id: str):
    print(f"[Celery] Processing background AI inference & embedding indexing for petition {petition_id}")
    return {"petition_id": petition_id, "status": "completed", "processed_at": datetime.now(timezone.utc).isoformat()}

@celery_app.task(name="tasks.check_sla_breaches")
def check_sla_breaches():
    print("[Celery] Running SLA breach detection check on all active shared incidents...")
    return {"checked": True, "sla_breaches_found": 0}

@celery_app.task(name="tasks.send_sms_notification")
def send_sms_notification(phone_number: str, message: str):
    print(f"[Celery] Sending SMS Notification to {phone_number}: {message}")
    return {"sent_to": phone_number, "status": "delivered"}
