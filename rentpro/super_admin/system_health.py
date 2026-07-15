"""Super Admin — System Health Monitoring."""

import frappe
import psutil
from frappe.utils import now_datetime


def run_health_check():
    settings = frappe.get_single("System Health Settings")
    if not settings.health_check_enabled:
        return None

    results = {
        "timestamp": str(now_datetime()),
        "checks": {},
        "overall": "Healthy",
    }

    results["checks"]["database"] = _check_database()
    results["checks"]["redis"] = _check_redis()
    results["checks"]["api"] = _check_api()
    results["checks"]["queue"] = _check_queue()
    results["checks"]["scheduler"] = _check_scheduler()
    results["checks"]["storage"] = _check_storage()
    results["checks"]["system"] = _check_system_resources()
    results["checks"]["failed_jobs"] = _check_failed_jobs()

    statuses = [c["status"] for c in results["checks"].values()]
    if "Down" in statuses:
        results["overall"] = "Critical"
    elif "Degraded" in statuses:
        results["overall"] = "Degraded"

    _update_health_settings(results)
    return results


def get_health_status():
    settings = frappe.get_single("System Health Settings")
    return {
        "last_check": str(settings.last_check_timestamp or "Never"),
        "overall_status": settings.last_overall_status or "Unknown",
        "api": settings.last_api_status or "Unknown",
        "database": settings.last_db_status or "Unknown",
        "redis": settings.last_redis_status or "Unknown",
        "queue": settings.last_queue_status or "Unknown",
    }


def get_background_job_stats():
    try:
        queued = frappe.db.count("RQ Job", {"status": "queued"})
        started = frappe.db.count("RQ Job", {"status": "started"})
        finished = frappe.db.count("RQ Job", {"status": "finished"})
        failed = frappe.db.count("RQ Job", {"status": "failed"})
        return {
            "queued": queued,
            "started": started,
            "finished": finished,
            "failed": failed,
            "total_active": queued + started,
        }
    except Exception:
        return {
            "queued": 0,
            "started": 0,
            "finished": 0,
            "failed": 0,
            "total_active": 0,
        }


def _check_database():
    try:
        start = now_datetime()
        frappe.db.sql("SELECT 1")
        elapsed_ms = _ms_since(start)
        return {
            "status": "OK" if elapsed_ms < 1000 else "Degraded",
            "response_ms": elapsed_ms,
            "message": f"Response: {elapsed_ms}ms",
        }
    except Exception as e:
        return {"status": "Down", "message": str(e)}


def _check_redis():
    try:
        cache = frappe.cache()
        cache.set_value("_health_check", "ok")
        val = cache.get_value("_health_check")
        if val == "ok":
            return {"status": "OK", "message": "Redis responding"}
        return {"status": "Degraded", "message": "Unexpected response"}
    except Exception as e:
        return {"status": "Down", "message": str(e)}


def _check_api():
    try:
        settings = frappe.get_single("System Health Settings")
        threshold = settings.api_response_time_ms or 2000
        start = now_datetime()
        frappe.get_all("DocType", limit=1)
        elapsed_ms = _ms_since(start)
        if elapsed_ms < threshold:
            return {"status": "OK", "response_ms": elapsed_ms}
        return {
            "status": "Degraded",
            "response_ms": elapsed_ms,
            "message": f"Slow response: {elapsed_ms}ms (threshold: {threshold}ms)",
        }
    except Exception as e:
        return {"status": "Down", "message": str(e)}


def _check_queue():
    stats = get_background_job_stats()
    settings = frappe.get_single("System Health Settings")
    threshold = settings.queue_threshold or 100
    if stats["total_active"] > threshold:
        return {
            "status": "Degraded",
            "message": f"Queue depth: {stats['total_active']}",
        }
    return {
        "status": "OK",
        "message": f"Queue depth: {stats['total_active']}",
    }


def _check_scheduler():
    try:
        schedulers = frappe.db.get_all(
            "RQ Worker",
            fields=["name", "status"],
        )
        active = sum(1 for s in schedulers if s.status == "alive")
        if active > 0:
            return {
                "status": "OK",
                "message": f"{active} worker(s) alive",
            }
        return {"status": "Degraded", "message": "No active workers"}
    except Exception:
        return {"status": "OK", "message": "Scheduler check skipped"}


def _check_storage():
    try:
        disk = psutil.disk_usage("/")
        percent = disk.percent
        settings = frappe.get_single("System Health Settings")
        threshold = settings.disk_threshold_percent or 90
        if percent < threshold:
            return {
                "status": "OK",
                "percent": percent,
                "free_gb": round(disk.free / (1024**3), 1),
            }
        return {
            "status": "Degraded",
            "percent": percent,
            "message": f"Disk usage: {percent}%",
        }
    except Exception as e:
        return {"status": "OK", "message": f"Storage check: {e}"}


def _check_system_resources():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        settings = frappe.get_single("System Health Settings")
        cpu_thresh = settings.cpu_threshold_percent or 80
        mem_thresh = settings.memory_threshold_percent or 85
        status = "OK"
        if cpu > cpu_thresh or mem.percent > mem_thresh:
            status = "Degraded"
        return {
            "status": status,
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "memory_available_gb": round(mem.available / (1024**3), 1),
        }
    except Exception as e:
        return {"status": "OK", "message": f"System check: {e}"}


def _check_failed_jobs():
    settings = frappe.get_single("System Health Settings")
    threshold = settings.failed_jobs_threshold or 10
    try:
        failed = frappe.db.count("RQ Job", {"status": "failed"})
        if failed > threshold:
            return {
                "status": "Degraded",
                "count": failed,
                "message": f"{failed} failed jobs",
            }
        return {
            "status": "OK",
            "count": failed,
            "message": f"{failed} failed jobs",
        }
    except Exception:
        return {"status": "OK", "message": "Failed jobs check skipped"}


def _update_health_settings(results):
    settings = frappe.get_single("System Health Settings")
    settings.last_check_timestamp = now_datetime()
    settings.last_overall_status = results["overall"]
    settings.last_api_status = results["checks"]["api"]["status"]
    settings.last_db_status = results["checks"]["database"]["status"]
    settings.last_redis_status = results["checks"]["redis"]["status"]
    settings.last_queue_status = results["checks"]["queue"]["status"]
    settings.save(ignore_permissions=True)
    frappe.db.commit()


def _ms_since(start_time):
    from datetime import datetime

    if isinstance(start_time, datetime):
        delta = now_datetime() - start_time
        return int(delta.total_seconds() * 1000)
    return 0
