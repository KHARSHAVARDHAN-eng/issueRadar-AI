from pydantic import BaseModel


class ComponentStatus(BaseModel):
    status: str  # connected | disconnected | unknown
    message: str | None = None
    latency_ms: float | None = None


class SystemHealthResponse(BaseModel):
    status: str  # healthy | degraded | unhealthy
    service: str
    timestamp: str
    version: str
    components: dict[str, ComponentStatus]
