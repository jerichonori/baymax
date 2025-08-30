import uuid
import json
from datetime import datetime
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger
from app.services.audit import AuditService

logger = get_logger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        
        start_time = datetime.utcnow()
        
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    request_body = body.decode("utf-8")
                    request._body = body
            except Exception:
                pass
        
        response = await call_next(request)
        
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        if self._should_audit(request.url.path):
            await self._create_audit_log(
                request=request,
                response=response,
                trace_id=trace_id,
                duration_ms=duration_ms,
                request_body=request_body,
            )
        
        response.headers["X-Trace-Id"] = trace_id
        
        return response
    
    def _should_audit(self, path: str) -> bool:
        excluded_paths = ["/health", "/metrics", "/docs", "/openapi.json", "/redoc"]
        return not any(path.startswith(p) for p in excluded_paths)
    
    async def _create_audit_log(
        self,
        request: Request,
        response: Response,
        trace_id: str,
        duration_ms: float,
        request_body: Optional[str] = None,
    ) -> None:
        try:
            phi_accessed = self._check_phi_access(request.url.path)
            
            audit_data = {
                "trace_id": trace_id,
                "timestamp": datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "ip_address": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent"),
                "phi_accessed": phi_accessed,
            }
            
            if hasattr(request.state, "user_id"):
                audit_data["user_id"] = str(request.state.user_id)
                audit_data["user_type"] = getattr(request.state, "user_type", "unknown")
            
            logger.info("audit_log", **audit_data)
            
        except Exception as e:
            logger.error("Failed to create audit log", error=str(e), trace_id=trace_id)
    
    def _check_phi_access(self, path: str) -> bool:
        phi_paths = [
            "/patients",
            "/encounters",
            "/appointments",
            "/intake",
            "/emr",
        ]
        return any(path.startswith(f"/api/v1{p}") for p in phi_paths)