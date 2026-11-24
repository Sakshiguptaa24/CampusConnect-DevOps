import time
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import create_all_tables, async_session_maker
from app.core.seed import seed_database
from app.api.routes.auth import router as auth_router
from app.api.routes.events import router as events_router
from app.api.routes.registrations import router as registrations_router
from app.api.routes.attendance import router as attendance_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("campusconnect")

# In-memory Prometheus metrics collectors
metrics_data = {
    "requests_total": 0,
    "requests_by_status": {},
    "requests_by_path": {},
    "errors_total": 0,
    "total_duration_seconds": 0.0,
    "start_time": time.time(),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize schema and seed initial data."""
    logger.info("Starting CampusConnect API Server...")
    await create_all_tables()
    async with async_session_maker() as db:
        await seed_database(db)
    yield
    logger.info("Shutting down CampusConnect API Server...")


app = FastAPI(
    title="CampusConnect API",
    description="Smart College Event Registration & Management System API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to track HTTP request metrics, latency, and status codes."""
    start_time = time.time()
    path = request.url.path
    metrics_data["requests_total"] += 1
    metrics_data["requests_by_path"][path] = metrics_data["requests_by_path"].get(path, 0) + 1

    try:
        response = await call_next(request)
        duration = time.time() - start_time
        metrics_data["total_duration_seconds"] += duration
        status_code = response.status_code

        metrics_data["requests_by_status"][status_code] = metrics_data["requests_by_status"].get(status_code, 0) + 1
        if status_code >= 400:
            metrics_data["errors_total"] += 1

        response.headers["X-Response-Time"] = f"{duration:.4f}s"
        return response
    except Exception as exc:
        duration = time.time() - start_time
        metrics_data["total_duration_seconds"] += duration
        metrics_data["errors_total"] += 1
        metrics_data["requests_by_status"][500] = metrics_data["requests_by_status"].get(500, 0) + 1
        raise exc


# Health, Readiness, and Metrics endpoints
@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for liveness probes."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "CampusConnect API",
        "version": "1.0.0",
        "uptime_seconds": round(time.time() - metrics_data["start_time"], 2),
    }


@app.get("/ready", tags=["system"])
async def readiness_check():
    """Readiness check endpoint for service availability and DB connectivity."""
    db_status = "ok"
    try:
        async with async_session_maker() as db:
            await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        return Response(
            content='{"status": "not_ready", "database": "' + db_status + '"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )

    return {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "database": db_status,
            "application": "ok",
        },
    }


@app.get("/metrics", tags=["system"])
async def prometheus_metrics():
    """Prometheus-compatible plain text metrics endpoint."""
    uptime = time.time() - metrics_data["start_time"]
    total_reqs = metrics_data["requests_total"]
    avg_latency = metrics_data["total_duration_seconds"] / total_reqs if total_reqs > 0 else 0.0

    lines = [
        "# HELP campusconnect_uptime_seconds Total application uptime in seconds",
        "# TYPE campusconnect_uptime_seconds gauge",
        f"campusconnect_uptime_seconds {uptime:.2f}",
        "# HELP campusconnect_requests_total Total number of HTTP requests processed",
        "# TYPE campusconnect_requests_total counter",
        f"campusconnect_requests_total {total_reqs}",
        "# HELP campusconnect_errors_total Total number of HTTP requests resulting in 4xx/5xx",
        "# TYPE campusconnect_errors_total counter",
        f"campusconnect_errors_total {metrics_data['errors_total']}",
        "# HELP campusconnect_average_latency_seconds Average request response time in seconds",
        "# TYPE campusconnect_average_latency_seconds gauge",
        f"campusconnect_average_latency_seconds {avg_latency:.6f}",
    ]

    for status_code, count in metrics_data["requests_by_status"].items():
        lines.append(f'campusconnect_requests_by_status{{status="{status_code}"}} {count}')

    return Response(content="\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")


# Include API Routers
app.include_router(auth_router)
app.include_router(events_router)
app.include_router(registrations_router)
app.include_router(attendance_router)
app.include_router(analytics_router)
app.include_router(admin_router)


@app.get("/", tags=["system"])
async def root():
    return {
        "name": "CampusConnect API",
        "description": "Smart College Event Registration & Management System",
        "docs_url": "/docs",
        "health_url": "/health",
        "metrics_url": "/metrics",
    }
