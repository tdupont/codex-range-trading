from __future__ import annotations

from app.core.settings import get_settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.services.scan_service import ScanService


def main() -> None:
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    with SessionLocal() as session:
        summary = ScanService(settings).run(session)
    print(summary)


if __name__ == "__main__":
    main()
