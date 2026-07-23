from collections.abc import Callable
from typing import Any

from app.core.config import settings

try:
    from celery import Celery

    celery_app = Celery(
        "issueradar_workers",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,
    )
except ImportError:

    class DummyTask:
        def __init__(self, fn: Callable):
            self.fn = fn

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return self.fn(self, *args, **kwargs)

        def retry(self, exc: Exception | None = None, **kwargs: Any) -> Any:
            if exc:
                raise exc

    class DummyCelery:
        def task(self, *args: Any, **kwargs: Any) -> Callable:
            def decorator(fn: Callable) -> DummyTask:
                return DummyTask(fn)

            return decorator

    celery_app = DummyCelery()  # type: ignore
