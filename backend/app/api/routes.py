from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "range-trading-screener-api",
        "version": "0.1.0",
    }


# Additional range, opportunity, and alert endpoints should be added after
# the persistence layer and domain services are in place.
